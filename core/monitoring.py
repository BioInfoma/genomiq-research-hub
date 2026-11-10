"""
Web and Research Monitoring Engine for GenomIQ Research Hub.
Tracks:
- GitHub Releases of core bioinformatics tools (Hifiasm, VG, Minimap2, GATK, etc.)
- RSS feeds from preprint archives (bioRxiv, medRxiv) and leading genomics journals
- Institutional announcements and funding feeds
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
import httpx
import feedparser
from config import GITHUB_TOKEN, HTTP_TIMEOUT
from database.connection import get_db
from database.models import MonitoredEntity

logger = logging.getLogger(__name__)


class WebMonitoringService:
    def __init__(self):
        self.headers = {"User-Agent": "GenomIQ-Hub/1.0"}
        if GITHUB_TOKEN:
            self.headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    def check_github_repo_release(self, repo_identifier: str) -> Dict[str, Any]:
        """
        Fetches the latest software release from GitHub API (e.g. 'lh3/minimap2').
        Uses unauthenticated public API (or optional token) with rate-limit handling.
        """
        url = f"https://api.github.com/repos/{repo_identifier}/releases/latest"
        try:
            with httpx.Client(timeout=HTTP_TIMEOUT, headers=self.headers) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    tag = data.get("tag_name", "")
                    title = data.get("name") or tag
                    body = data.get("body", "")
                    html_url = data.get("html_url", f"https://github.com/{repo_identifier}")
                    published = data.get("published_at", "")
                    return {
                        "status": "success",
                        "title": f"Release {tag}: {title}",
                        "link": html_url,
                        "published_at": published,
                        "snippet": (body[:280] + "...") if len(body) > 280 else body,
                    }
                elif resp.status_code == 404:
                    return {
                        "status": "no_releases",
                        "title": f"{repo_identifier} (No formal releases published)",
                        "link": f"https://github.com/{repo_identifier}",
                        "snippet": "Repository exists but has no formal GitHub releases.",
                    }
                else:
                    return {"status": "error", "message": f"HTTP {resp.status_code}"}
        except Exception as e:
            logger.warning(f"Error checking GitHub {repo_identifier}: {e}")
            return {"status": "error", "message": str(e)}

    def check_rss_feed(self, feed_url: str) -> Dict[str, Any]:
        """Parses an RSS feed (e.g., bioRxiv or Nature Genetics)."""
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                latest = feed.entries[0]
                title = latest.get("title", "Untitled Feed Item")
                link = latest.get("link", feed_url)
                summary = latest.get("summary", "")
                return {
                    "status": "success",
                    "title": title,
                    "link": link,
                    "published_at": latest.get("published", ""),
                    "snippet": (summary[:280] + "...") if len(summary) > 280 else summary,
                }
            return {"status": "empty", "title": "No feed items", "link": feed_url, "snippet": ""}
        except Exception as e:
            logger.warning(f"Error reading RSS {feed_url}: {e}")
            return {"status": "error", "message": str(e)}

    def refresh_all_monitors(self) -> List[Dict[str, Any]]:
        """Scans all active monitored entities and updates database records."""
        results = []
        with get_db() as db:
            entities = db.query(MonitoredEntity).filter(MonitoredEntity.is_active == True).all()
            for entity in entities:
                update_info = None
                if entity.entity_type == "github_repo":
                    repo_id = entity.feed_or_repo or entity.url.replace("https://github.com/", "")
                    update_info = self.check_github_repo_release(repo_id)
                elif entity.entity_type in ["rss_feed", "journal", "lab"]:
                    update_info = self.check_rss_feed(entity.url)

                if update_info and update_info.get("status") == "success":
                    entity.latest_title = update_info.get("title", "")
                    entity.latest_link = update_info.get("link", "")
                    entity.latest_snippet = update_info.get("snippet", "")
                    entity.last_checked = datetime.utcnow()
                    results.append({
                        "name": entity.name,
                        "type": entity.entity_type,
                        "latest": entity.latest_title,
                        "link": entity.latest_link
                    })

            db.commit()
        return results
