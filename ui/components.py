"""
Reusable UI Components and Academic Styling for GenomIQ Research Hub.
"""
import streamlit as st


def apply_custom_css():
    """Injects refined scientific styling, badge styles, and responsive layout enhancements."""
    st.markdown("""
        <style>
        /* General page layout adjustments */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1250px;
        }

        /* Metric card styling */
        .kpi-card {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 15px;
            transition: transform 0.15s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
        }
        .kpi-title {
            color: #64748b;
            font-size: 0.85rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.05em;
        }
        .kpi-value {
            color: #0f172a;
            font-size: 1.85rem;
            font-weight: 700;
            margin-top: 4px;
        }
        .kpi-subtitle {
            color: #94a3b8;
            font-size: 0.78rem;
            margin-top: 4px;
        }

        /* Publication card */
        .pub-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }
        .pub-title {
            font-size: 1.12rem;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.4;
            margin-bottom: 6px;
        }
        .pub-authors {
            font-size: 0.88rem;
            color: #475569;
            margin-bottom: 8px;
        }
        .pub-meta {
            font-size: 0.82rem;
            color: #64748b;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }

        /* Status Badges */
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-core { background: #dbeafe; color: #1e40af; }
        .badge-comp { background: #fef3c7; color: #92400e; }
        .badge-compl { background: #dcfce7; color: #166534; }
        .badge-landmark { background: #fae8ff; color: #86198f; }
        .badge-oa { background: #e0e7ff; color: #3730a3; }
        .badge-completed { background: #dcfce7; color: #15803d; }
        .badge-reading { background: #fef08a; color: #854d0e; }
        .badge-pending { background: #f1f5f9; color: #475569; }

        /* Recommendation explanation box */
        .rec-rationale-box {
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 14px 18px;
            margin-top: 10px;
            margin-bottom: 14px;
        }
        </style>
    """, unsafe_allow_html=True)


def render_kpi(col, title: str, value: Any, subtitle: str = ""):
    """Renders a sleek scientific KPI block."""
    with col:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-subtitle">{subtitle}</div>
            </div>
        """, unsafe_allow_html=True)
