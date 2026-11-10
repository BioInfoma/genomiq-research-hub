"""
Background task scheduler using APScheduler for GenomIQ Research Hub.
Handles automated daily preprint discovery, weekly digest synthesis, and GitHub repo release checks.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler = None


def scheduled_daily_discovery():
    """Runs daily scan for new preprints and landmark publications."""
    try:
        from core.discovery import LiteratureDiscoveryEngine
        engine = LiteratureDiscoveryEngine()
        # Scan for latest genomics preprints
        engine.execute_unified_search(
            query="pangenome somatic variant calling colorectal cancer",
            sources=["bioRxiv", "Europe PMC"],
            limit_per_source=5,
            persist=True
        )
        logger.info("Automated daily discovery executed successfully.")
    except Exception as e:
        logger.error(f"Error in automated daily discovery: {e}")


def scheduled_web_monitoring():
    """Checks monitored software releases and RSS feeds."""
    try:
        from core.monitoring import WebMonitoringService
        service = WebMonitoringService()
        service.refresh_all_monitors()
        logger.info("Automated web monitoring executed successfully.")
    except Exception as e:
        logger.error(f"Error in automated web monitoring: {e}")


def scheduled_weekly_digest():
    """Regenerates weekly digest every Monday morning."""
    try:
        from core.digest import DigestGenerator
        gen = DigestGenerator()
        gen.generate_digest()
        logger.info("Automated weekly digest generated.")
    except Exception as e:
        logger.error(f"Error in automated weekly digest: {e}")


def start_background_scheduler():
    """Initializes and starts the background scheduler singleton."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    try:
        _scheduler = BackgroundScheduler(daemon=True)
        # Check monitored tools/feeds every 6 hours
        _scheduler.add_job(scheduled_web_monitoring, IntervalTrigger(hours=6), id="web_monitor", replace_existing=True)
        # Scan preprints daily
        _scheduler.add_job(scheduled_daily_discovery, IntervalTrigger(hours=24), id="daily_discovery", replace_existing=True)
        # Weekly digest every Monday at 08:00
        _scheduler.add_job(scheduled_weekly_digest, CronTrigger(day_of_week="mon", hour=8, minute=0), id="weekly_digest", replace_existing=True)
        _scheduler.start()
        logger.info("GenomIQ Background Scheduler started.")
    except Exception as e:
        logger.warning(f"Could not start background scheduler: {e}")

    return _scheduler
