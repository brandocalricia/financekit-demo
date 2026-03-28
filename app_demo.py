"""
FinanceKit — Free Demo Version
Deploy this to Streamlit Cloud as your public landing page.
Replace GUMROAD_URL below with your actual Gumroad product link.
"""
import streamlit as st

GUMROAD_URL = "https://5207453582610.gumroad.com/l/zbnsjc"

st.set_page_config(
    page_title="FinanceKit \u2014 Personal Finance Toolkit",
    page_icon="\U0001f4b0",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    section[data-testid="stSidebar"] { background-color: #0f1117; min-width: 260px; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 1rem; padding: 0.35rem 0; color: #c4b5fd !important; }
    section[data-testid="stSidebar"] .stRadio label:hover { color: #ffffff !important; }
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span { color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] hr { border-color: #3a3a5c; }
    section[data-testid="stSidebar"] .stElementContainer small { color: #94a3b8 !important; }

    .header-title {
        font-size: 2.8rem; font-weight: 700;
        background: linear-gradient(90deg, #6366f1, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .header-subtitle { color: #94a3b8; font-size: 1.15rem; margin-bottom: 1rem; }

    .module-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        border: 1px solid #3a3a5c; border-radius: 14px;
        padding: 1.8rem 1.5rem; text-align: center;
        transition: transform 0.2s, box-shadow 0.2s; height: 100%;
    }
    .module-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(99, 102, 241, 0.25); }
    .module-card .icon { font-size: 2.6rem; margin-bottom: 0.6rem; }
    .module-card h3 { margin: 0.4rem 0 0.6rem 0; color: #e2e8f0; font-size: 1.15rem; }
    .module-card p { color: #94a3b8; font-size: 0.88rem; line-height: 1.45; }

    .cta-box {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        border-radius: 14px; padding: 2rem; text-align: center; margin: 1.5rem 0;
    }
    .cta-box h2 { color: #fff; margin-bottom: 0.5rem; }
    .cta-box p { color: #e2e8f0; margin-bottom: 1rem; font-size: 1.05rem; }
    .cta-btn {
        display: inline-block; background: #fff; color: #4f46e5;
        font-weight: 700; font-size: 1.1rem; padding: 0.75rem 2rem;
        border-radius: 8px; text-decoration: none;
        transition: transform 0.15s;
    }
    .cta-btn:hover { transform: scale(1.05); color: #4f46e5; }

    .lock-overlay {
        background: rgba(15, 17, 23, 0.85); border: 1px solid #3a3a5c;
        border-radius: 12px; padding: 3rem 2rem; text-align: center; margin: 1rem 0;
    }
    .lock-overlay h3 { color: #c4b5fd; }
    .lock-overlay p { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## \U0001f4b0 FinanceKit")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "\U0001f3e0 Home",
            "\U0001f9fe Receipt Scanner",
            "\U0001f4c8 Portfolio Tracker",
            "\U0001f4ca Report Generator",
            "\U0001f4bc Job Tracker",
            "\U0001f504 Subscription Auditor",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # Sidebar CTA
    st.markdown(
        f'<a href="{GUMROAD_URL}" target="_blank" style="'
        'display:block;background:linear-gradient(135deg,#4f46e5,#7c3aed);'
        'color:#fff;text-align:center;padding:0.7rem 1rem;border-radius:8px;'
        'text-decoration:none;font-weight:600;font-size:0.95rem;margin-top:0.5rem;'
        '">Get Full Version \u2014 $29.99</a>',
        unsafe_allow_html=True,
    )
    st.caption("Free demo \u2022 FinanceKit v1.0")


def _cta_block():
    """Render the upgrade CTA banner."""
    st.markdown(
        f"""
        <div class="cta-box">
            <h2>\U0001f513 Unlock the Full Version</h2>
            <p>Get all 5 modules with unlimited exports, PDF reports, live price alerts, and more.</p>
            <a class="cta-btn" href="{GUMROAD_URL}" target="_blank">Buy FinanceKit \u2014 $29.99 one-time</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _locked_module(title: str, features: list[str]):
    """Show a locked module preview."""
    st.markdown(f"## {title}")
    st.markdown("Here's what you get with the full version:")
    for f in features:
        st.markdown(f"- {f}")
    _cta_block()


# --- Pages ---

if page == "\U0001f3e0 Home":
    st.markdown('<div class="header-title">FinanceKit</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="header-subtitle">Your all-in-one personal finance toolkit \u2014 '
        '5 powerful modules, zero subscriptions. Try the demo below.</div>',
        unsafe_allow_html=True,
    )

    _cta_block()

    modules = [
        ("\U0001f9fe", "Receipt & Invoice Scanner",
         "Upload PDF receipts and extract dates, vendors, and totals \u2014 export to Excel or CSV."),
        ("\U0001f4c8", "Portfolio Tracker",
         "Track stocks and crypto with live prices, gain/loss tracking, and price alerts."),
        ("\U0001f4ca", "Financial Report Generator",
         "Upload transactions and get a polished PDF report with charts and stats."),
        ("\U0001f4bc", "Job Application Tracker",
         "Manage your job search \u2014 statuses, follow-ups, and pipeline visualization."),
        ("\U0001f504", "Subscription Auditor",
         "Auto-detect recurring charges from bank statements and calculate savings."),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(
                f'<div class="module-card">'
                f'<div class="icon">{icon}</div>'
                f'<h3>{title}</h3>'
                f'<p>{desc}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("")

    st.markdown("---")
    st.markdown("### How It Works")
    hc1, hc2, hc3 = st.columns(3)
    hc1.markdown("**1. Purchase & Download**\n\nOne-time $29.99 payment. No subscriptions. Download the toolkit instantly.")
    hc2.markdown("**2. Double-Click to Launch**\n\nRun `start.bat` (Windows) or `start.sh` (Mac/Linux). Opens in your browser automatically.")
    hc3.markdown("**3. Own Your Data**\n\nEverything runs locally on your computer. No cloud uploads, no accounts, full privacy.")

    st.markdown("---")
    st.markdown("### What's Included")
    st.markdown("""
    | Feature | Free Demo | Full Version |
    |---------|:---------:|:------------:|
    | Browse all 5 modules | \u2705 | \u2705 |
    | Subscription Auditor (limited) | \u2705 | \u2705 Unlimited |
    | Receipt Scanner | \u274c | \u2705 |
    | Portfolio Tracker with alerts | \u274c | \u2705 |
    | PDF Report Generator | \u274c | \u2705 |
    | Job Application Tracker | \u274c | \u2705 |
    | Export to Excel / CSV / PDF | \u274c | \u2705 |
    | Lifetime updates | \u274c | \u2705 |
    """)

    _cta_block()

elif page == "\U0001f504 Subscription Auditor":
    # This is the ONE free module (limited) to give people a taste
    st.markdown("## \U0001f504 Subscription Auditor \u2014 Free Preview")
    st.markdown(
        "Upload a bank statement CSV to detect recurring charges. "
        "**This demo is limited to 50 transactions.** Get the full version for unlimited analysis."
    )

    uploaded = st.file_uploader("Upload a CSV statement", type=["csv"])

    if uploaded:
        import pandas as pd
        try:
            df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Could not read file: {e}")
            st.stop()

        if len(df) > 50:
            st.warning(
                f"Your file has **{len(df):,}** transactions. "
                f"The free demo only processes the first 50. Get the full version for unlimited analysis."
            )
            df = df.head(50)

        st.success(f"Loaded **{len(df)}** transactions (demo limit: 50).")
        st.dataframe(df.head(20), use_container_width=True)

        st.markdown("---")
        _cta_block()
    else:
        st.info("Upload a CSV to try the demo.")

    _cta_block()

elif page == "\U0001f9fe Receipt Scanner":
    _locked_module("\U0001f9fe Receipt & Invoice Scanner", [
        "Upload single or multiple PDF receipts",
        "Auto-extract date, vendor, total, and category",
        "Editable table \u2014 correct any fields before exporting",
        "Export to Excel (.xlsx) or CSV with one click",
        "OCR fallback for scanned/image PDFs",
    ])

elif page == "\U0001f4c8 Portfolio Tracker":
    _locked_module("\U0001f4c8 Stock & Crypto Portfolio Tracker", [
        "Track stocks (via Yahoo Finance) and crypto (via CoinGecko)",
        "See live prices, gain/loss per holding, total portfolio value",
        "Interactive performance charts over 1mo / 3mo / 6mo / 1yr",
        "Set price alerts with on-screen + optional email notifications",
        "Portfolio data saved locally between sessions",
    ])

elif page == "\U0001f4ca Report Generator":
    _locked_module("\U0001f4ca Financial Report Generator", [
        "Upload CSV or Excel transaction files",
        "Auto-detect columns or map them manually",
        "Summary stats: income, expenses, net, top categories",
        "Charts: monthly spending, category breakdown, income vs expenses",
        "Generate a downloadable PDF report with title page, charts, and tables",
    ])

elif page == "\U0001f4bc Job Tracker":
    _locked_module("\U0001f4bc Job Application Tracker", [
        "Add, edit, and delete job applications",
        "Track status: Applied, Phone Screen, Interview, Offer, Rejected",
        "Pipeline funnel chart showing applications at each stage",
        "Auto follow-up reminders for stale applications (7+ days)",
        "Export all data to CSV",
    ])
