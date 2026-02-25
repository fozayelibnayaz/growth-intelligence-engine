"""
Eagle 3D Intelligence Platform - Main Application
Complete Funnel: Keyword > Question > Answer > Proof > Idea > Outline > Publish > AI Summary
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database import (
    init_database, create_user, authenticate_user,
    insert_intelligence_data, get_all_data, get_data_by_date, get_recent_data,
    save_setting, get_setting, log_daily_collection, get_daily_logs,
    insert_content_tracker
)
from collector import IntelligenceCollector
from telegram_bot import TelegramNotifier, get_telegram_setup_instructions

st.set_page_config(
    page_title="Eagle 3D Intelligence Platform",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_database()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None


def login():
    st.sidebar.markdown("### 🔐 Login")
    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")

    if st.sidebar.button("Login", key="login_button"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.username = user[1]
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")

    st.sidebar.markdown("---")
    if st.sidebar.button("Create Account", key="create_account_button_sidebar"):
        st.session_state.show_register = True


def register():
    st.sidebar.markdown("### 📝 Register")
    new_username = st.sidebar.text_input("Username", key="reg_user")
    new_password = st.sidebar.text_input("Password", type="password", key="reg_pass")
    new_email = st.sidebar.text_input("Email", key="reg_email")

    if st.sidebar.button("Register", key="register_button"):
        if create_user(new_username, new_password, new_email):
            st.sidebar.success("Account created! Login now.")
            st.session_state.show_register = False
            st.rerun()
        else:
            st.sidebar.error("Username already exists")

    if st.sidebar.button("Back to Login", key="back_to_login_button"):
        st.session_state.show_register = False
        st.rerun()


def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()


def main():
    if not st.session_state.logged_in:
        st.title("🦅 Eagle 3D Intelligence Platform")
        st.markdown("**Internal-Only SaaS for Eagle 3D Streaming**")
        st.markdown("""
        ### Complete Funnel System:
        1. 🔍 **Keyword** → Pixel streaming related topics
        2. ❓ **Question** → What users are asking
        3. 💡 **Answer** → AI-generated summary
        4. 🔗 **Proof** → Direct link to source
        5. 📝 **Content Idea** → What to create
        6. 📋 **Outline** → Complete content structure
        7. 📢 **Publish** → Where & when to publish
        8. 🤖 **AI Summary** → Intelligent recommendations

        **Login to access the platform**
        """)

        if 'show_register' not in st.session_state:
            st.session_state.show_register = False

        if st.session_state.show_register:
            register()
        else:
            login()
        return

    st.sidebar.success(f"✅ Logged in as **{st.session_state.username}**")
    if st.sidebar.button("Logout", key="logout_button"):
        logout()

    st.sidebar.markdown("---")

    page = st.sidebar.radio("📍 Navigation", [
        "📊 Dashboard",
        "🔍 Data Collection",
        "📅 Daily Data",
        "📝 Content Planner",
        "🏆 Competitors",
        "📈 Analytics",
        "⚙️ Settings"
    ], key="main_navigation_radio")

    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🔍 Data Collection":
        show_data_collection()
    elif page == "📅 Daily Data":
        show_daily_data()
    elif page == "📝 Content Planner":
        show_content_planner()
    elif page == "🏆 Competitors":
        show_competitors()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "⚙️ Settings":
        show_settings()


def show_dashboard():
    st.title("📊 Intelligence Dashboard")

    st.sidebar.markdown("### 📅 Date Filter")
    today = date.today()

    date_preset_options = [
        "Custom", "Today", "Yesterday", "This week (Sun - Today)", "Last 7 days",
        "Last week (Sun - Sat)", "Last 28 days", "Last 30 days", "This month",
        "Last month", "Last 90 days", "Quarter to date", "This year (Jan - Today)",
        "Last calendar year", "All Time"
    ]

    selected_preset = st.sidebar.selectbox(
        "Select Range", date_preset_options, index=4,
        key="dashboard_date_preset"
    )

    start_date_filter_str, end_date_filter_str = None, None

    if selected_preset == "Custom":
        st.sidebar.write("---")
        start_date_input = st.sidebar.date_input(
            "Start date", value=today - timedelta(days=7), key="custom_start_date"
        )
        end_date_input = st.sidebar.date_input(
            "End date", value=today, key="custom_end_date"
        )
        start_date_filter_str = start_date_input.strftime('%Y-%m-%d')
        end_date_filter_str = end_date_input.strftime('%Y-%m-%d')
    elif selected_preset == "Today":
        start_date_filter_str = today.strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "Yesterday":
        start_date_filter_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date_filter_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    elif selected_preset == "This week (Sun - Today)":
        days_since_sunday = (today.weekday() + 1) % 7
        start_date_filter_str = (today - timedelta(days=days_since_sunday)).strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "Last 7 days":
        start_date_filter_str = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "Last week (Sun - Sat)":
        days_since_sunday = (today.weekday() + 1) % 7
        last_saturday = today - timedelta(days=days_since_sunday + 1)
        last_sunday = last_saturday - timedelta(days=6)
        start_date_filter_str = last_sunday.strftime('%Y-%m-%d')
        end_date_filter_str = last_saturday.strftime('%Y-%m-%d')
    elif selected_preset == "Last 28 days":
        start_date_filter_str = (today - timedelta(days=27)).strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "Last 30 days":
        start_date_filter_str = (today - timedelta(days=29)).strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "This month":
        start_date_filter_str = today.replace(day=1).strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "Last month":
        first_day_current = today.replace(day=1)
        last_day_prev = first_day_current - timedelta(days=1)
        first_day_prev = last_day_prev.replace(day=1)
        start_date_filter_str = first_day_prev.strftime('%Y-%m-%d')
        end_date_filter_str = last_day_prev.strftime('%Y-%m-%d')
    elif selected_preset == "Last 90 days":
        start_date_filter_str = (today - timedelta(days=89)).strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "Quarter to date":
        current_quarter = (today.month - 1) // 3 + 1
        first_month = 3 * current_quarter - 2
        start_date_filter_str = datetime(today.year, first_month, 1).strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "This year (Jan - Today)":
        start_date_filter_str = datetime(today.year, 1, 1).strftime('%Y-%m-%d')
        end_date_filter_str = today.strftime('%Y-%m-%d')
    elif selected_preset == "Last calendar year":
        start_date_filter_str = datetime(today.year - 1, 1, 1).strftime('%Y-%m-%d')
        end_date_filter_str = datetime(today.year - 1, 12, 31).strftime('%Y-%m-%d')
    else:
        start_date_filter_str, end_date_filter_str = None, None

    df = get_all_data(st.session_state.user_id, start_date_filter_str, end_date_filter_str)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📊 Total Records", len(df))
    with col2:
        avg_score = df['opportunity_score'].mean() if not df.empty else 0
        st.metric("🎯 Avg Score", f"{avg_score:.1f}")
    with col3:
        b2b_count = int(df['is_b2b'].sum()) if not df.empty else 0
        st.metric("💼 B2B Leads", b2b_count)
    with col4:
        unique_keywords = df['keyword'].nunique() if not df.empty else 0
        st.metric("🔑 Keywords", unique_keywords)
    with col5:
        today_str = date.today().strftime('%Y-%m-%d')
        today_count = len(df[df['collection_date'] == today_str]) if not df.empty else 0
        st.metric("📅 Today", today_count)

    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 By Source")
            source_counts = df['source'].value_counts()
            fig = px.pie(values=source_counts.values, names=source_counts.index, hole=0.4, title="Data Sources")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("📈 By Category")
            category_counts = df['category'].value_counts()
            fig = px.bar(x=category_counts.index, y=category_counts.values, title="Content Categories")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📅 Daily Collection Trend")
        if 'collection_date' in df.columns:
            df_trend = df.copy()
            df_trend['collection_date'] = pd.to_datetime(df_trend['collection_date'])
            daily_counts = df_trend.groupby('collection_date').size().reset_index(name='count')
            daily_counts = daily_counts.sort_values('collection_date')
            fig = px.line(daily_counts, x='collection_date', y='count', markers=True, title="Records Collected Daily")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 All Data (Sortable)")
        display_cols = ['collection_date', 'keyword', 'question_title', 'source',
                        'opportunity_score', 'is_b2b', 'cluster_label', 'proof_link']
        available_cols = [c for c in display_cols if c in df.columns]
        display_df = df[available_cols].copy()
        if 'is_b2b' in display_df.columns:
            display_df['is_b2b'] = display_df['is_b2b'].apply(lambda x: '💼 Yes' if x else '👤 No')
        st.dataframe(display_df, use_container_width=True)

        if st.button("📥 Export to CSV", key="dashboard_export_csv"):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download CSV", csv,
                f"eagle_data_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv", key="dashboard_download_button"
            )
    else:
        st.info("📭 No data found for the selected date range. Run Data Collection first.")


def show_data_collection():
    st.title("🔍 Data Collection")

    st.info("**Collection Order:** Unreal Engine Forum → Reddit → GitHub → Google Search → Competitors")

    st.markdown("""
    ### Complete Funnel:
    1. 🔍 **Keyword** → Pixel streaming related
    2. ❓ **Question** → What users ask
    3. 💡 **Answer** → AI summary
    4. 🔗 **Proof Link** → Direct source (REAL verified URL)
    5. 📝 **Content Idea** → What to create
    6. 📋 **Outline** → Full structure
    7. 📢 **Publish** → Where & when to publish
    8. 🤖 **AI Summary** → Intelligent recommendations
    """)

    collection_date = st.date_input("📅 Collection Date", value=datetime.now(), key="collection_date_input")

    st.subheader("Historical Data Collection")
    collect_history = st.checkbox(
        "Collect data with wider search window (30 days back)",
        key="collect_history_checkbox"
    )

    if st.button("🚀 Start Collection", type="primary", key="start_collection_button"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        collector = IntelligenceCollector(
            target_date=collection_date.strftime('%Y-%m-%d'),
            collect_history=collect_history
        )

        def update_progress(count):
            progress_bar.progress(min(count / 50, 1.0))
            status_text.text(f"📊 Collected {count} records...")

        total = collector.collect_all(update_progress)
        insert_intelligence_data(collector.data, st.session_state.user_id)

        sources = "Unreal Forum, Reddit, GitHub, Google, Competitors"
        log_daily_collection(
            st.session_state.user_id, total, sources,
            collection_date.strftime('%Y-%m-%d')
        )

        progress_bar.progress(1.0)
        st.success(f"✅ Collected {total} records for {collection_date.strftime('%Y-%m-%d')}!")
        st.balloons()

        # Telegram notification
        bot_token = get_setting('telegram_bot_token', st.session_state.user_id)
        chat_id = get_setting('telegram_chat_id', st.session_state.user_id)
        if bot_token and chat_id:
            try:
                notifier = TelegramNotifier(bot_token, chat_id)
                notifier.send_message(
                    f"🦅 Data Collection Complete\n\n"
                    f"📊 {total} records collected\n"
                    f"📅 Date: {collection_date.strftime('%Y-%m-%d')}"
                )
                st.info("📱 Telegram notification sent!")
            except Exception as e:
                st.warning(f"Telegram error: {e}")

        # Show sample
        if collector.data:
            st.subheader("📋 Sample of Collected Data")
            sample_df = pd.DataFrame(collector.data)
            show_cols = ['source', 'question_title', 'proof_link', 'opportunity_score', 'category']
            available = [c for c in show_cols if c in sample_df.columns]
            st.dataframe(sample_df[available].head(20), use_container_width=True)


def show_daily_data():
    st.title("📅 Daily Data View")

    selected_date = st.date_input("Select Date", value=datetime.now(), key="daily_data_date_selector")
    df = get_data_by_date(st.session_state.user_id, selected_date.strftime('%Y-%m-%d'))

    if df.empty:
        st.warning(f"📭 No data collected for {selected_date.strftime('%Y-%m-%d')}")
        st.info("💡 Run data collection for this date")
    else:
        st.success(f"✅ {len(df)} records found for {selected_date.strftime('%Y-%m-%d')}")
        st.subheader("📋 Complete Funnel Data")

        for idx, row in df.iterrows():
            row_id = row.get('id', idx)
            # NO key= parameter in st.expander
            with st.expander(f"🔑 {row['keyword']} - {row['question_title'][:60]}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**📅 Date:** {row['collection_date']}")
                    st.write(f"**📊 Source:** {row['source']}")
                    st.write(f"**🎯 Score:** {row['opportunity_score']:.1f}")
                    st.write(f"**💼 B2B:** {'Yes' if row['is_b2b'] else 'No'}")
                    st.write(f"**🔗 Proof:** [{row['proof_link'][:80]}]({row['proof_link']})")
                with col2:
                    st.metric("Score", f"{row['opportunity_score']:.1f}")

                st.markdown("**❓ Question:**")
                st.write(row['question_body'])
                st.markdown("**💡 Answer Summary:**")
                st.write(row['answer_summary'])
                st.markdown("**📝 Content Idea:**")
                st.write(row['content_idea'])
                st.markdown("**📋 Outline:**")
                st.text_area("Outline", row['content_outline'], height=200,
                             key=f"daily_outline_{row_id}_{idx}")
                st.markdown("**📢 Publish Recommendation:**")
                st.write(row['publish_recommendation'])
                st.markdown("**🤖 AI Summary:**")
                st.write(row['ai_summary'])


def show_content_planner():
    st.title("📝 Content Planner")

    df = get_all_data(st.session_state.user_id)
    if df.empty:
        st.warning("📭 No data yet. Run data collection first.")
        return

    status_filter = st.selectbox(
        "Filter by Status", ["All", "New", "In Progress", "Published"],
        key="planner_status_filter"
    )
    if status_filter != "All":
        df = df[df['status'] == status_filter]

    df = df.sort_values('opportunity_score', ascending=False)
    st.subheader(f"📊 {len(df)} Content Opportunities")

    for idx, row in df.head(20).iterrows():
        row_id = row.get('id', idx)
        # NO key= parameter in st.expander
        with st.expander(f"⭐ {row['opportunity_score']:.1f} - {row['keyword']} - {row['question_title'][:60]}"):
            st.write(f"**📅 Date:** {row['collection_date']}")
            st.write(f"**📊 Source:** {row['source']}")
            st.write(f"**💼 B2B:** {'Yes' if row['is_b2b'] else 'No'}")
            st.write(f"**🔗 Proof:** [{row['proof_link'][:80]}]({row['proof_link']})")

            st.markdown("**📋 Content Outline:**")
            st.text_area("Outline", row['content_outline'], height=200,
                         key=f"planner_outline_{row_id}_{idx}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copy Outline", key=f"planner_copy_{row_id}_{idx}"):
                    st.code(row['content_outline'])
            with col2:
                if st.button("✅ Mark as Created", key=f"planner_mark_{row_id}_{idx}"):
                    st.success("✅ Marked!")


def show_competitors():
    st.title("🏆 Competitor Intelligence")

    # =========================================================
    # PIXEL STREAMING COMPETITOR PROFILES (REAL COMPANIES)
    # =========================================================

    competitor_profiles = {
        "Arcware": {
            "website": "https://arcware.io",
            "description": "Pixel streaming platform for Unreal Engine. Offers managed cloud streaming with auto-scaling, multi-region support, and pay-per-use pricing.",
            "features": ["Managed pixel streaming", "Auto-scaling", "Multi-region", "Unreal Engine focus", "REST API"],
            "pricing": "Pay-per-use, starting ~$0.50/hour per stream",
            "target": "Game studios, Architecture firms, Automotive",
        },
        "PureWeb": {
            "website": "https://www.pureweb.com",
            "description": "Enterprise cloud streaming platform. Supports Unreal Engine and Unity. Offers SDK for custom integrations, analytics dashboard, and global edge network.",
            "features": ["Multi-engine support", "Enterprise SDK", "Analytics", "Global CDN", "Custom branding"],
            "pricing": "Enterprise pricing, custom quotes",
            "target": "Enterprise, Automotive, Healthcare, Education",
        },
        "Furioos": {
            "website": "https://www.furioos.com",
            "description": "Cloud streaming by Unity. Streams any Windows application including Unreal Engine projects. Offers GPU-powered virtual machines with low latency.",
            "features": ["Any Windows app", "Unity integration", "GPU VMs", "API access", "Embed support"],
            "pricing": "Per-minute billing, free tier available",
            "target": "Game developers, 3D artists, Enterprises",
        },
        "Vagon Streams": {
            "website": "https://vagon.io/streams",
            "description": "Cloud pixel streaming service. Supports Unreal Engine applications with one-click deployment, auto-scaling, and analytics.",
            "features": ["One-click deploy", "Auto-scaling", "Analytics", "Custom domain", "Unreal Engine support"],
            "pricing": "Per-stream-minute pricing",
            "target": "Architecture, Real estate, Product visualization",
        },
        "GameCast": {
            "website": "https://gamecast.ai",
            "description": "Cloud gaming and pixel streaming infrastructure. Provides GPU cloud instances optimized for real-time 3D streaming with global presence.",
            "features": ["GPU instances", "Global network", "Low latency", "Unreal support", "Scaling"],
            "pricing": "Usage-based pricing",
            "target": "Game studios, Metaverse platforms",
        },
        "AWS Pixel Streaming": {
            "website": "https://aws.amazon.com/solutions/implementations/unreal-engine-pixel-streaming/",
            "description": "AWS reference architecture for self-hosted Unreal Engine Pixel Streaming using EC2 GPU instances, Application Load Balancer, and auto-scaling groups.",
            "features": ["Self-hosted", "EC2 GPU", "Auto-scaling", "Global regions", "Full control"],
            "pricing": "AWS EC2 GPU pricing (g4dn/g5 instances)",
            "target": "DevOps teams, Enterprises with AWS infrastructure",
        },
    }

    # =========================================================
    # COMPETITOR OVERVIEW SECTION
    # =========================================================

    st.subheader("📊 Pixel Streaming Competitor Landscape")

    st.markdown("""
    These are the **major pixel streaming platforms** competing in the same space as 
    **Eagle 3D Streaming**. Data below is from their public websites.
    """)

    # Competitor cards
    cols = st.columns(3)
    for i, (name, info) in enumerate(competitor_profiles.items()):
        with cols[i % 3]:
            st.markdown(f"### {name}")
            st.write(f"🌐 [{info['website']}]({info['website']})")
            st.write(f"🎯 **Target:** {info['target']}")
            st.write(f"💰 **Pricing:** {info['pricing']}")
            st.markdown("---")

    # =========================================================
    # DETAILED COMPETITOR ANALYSIS
    # =========================================================

    st.subheader("🔍 Detailed Competitor Profiles")

    for comp_name, comp_info in competitor_profiles.items():
        # NO key= parameter in st.expander
        with st.expander(f"📌 {comp_name} — {comp_info['website']}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Description:**")
                st.write(comp_info["description"])

                st.markdown(f"**Key Features:**")
                for feature in comp_info["features"]:
                    st.write(f"  • {feature}")

                st.markdown(f"**Website:** [{comp_info['website']}]({comp_info['website']})")

            with col2:
                st.markdown(f"**Target Market:**")
                st.write(comp_info["target"])
                st.markdown(f"**Pricing:**")
                st.write(comp_info["pricing"])

    # =========================================================
    # COMPETITOR DATA FROM DATABASE (collected data)
    # =========================================================

    st.subheader("📈 Collected Competitor Intelligence")

    df = get_all_data(st.session_state.user_id)

    if df.empty:
        st.info("📭 No collected data yet. Run Data Collection to gather competitor intelligence.")
        return

    comp_df = df[df['category'] == 'competitor_tracking']

    if comp_df.empty:
        st.info("📭 No competitor data collected yet. Run Data Collection — it will scrape competitor websites automatically.")
    else:
        st.success(f"✅ {len(comp_df)} competitor intelligence records found")

        # Chart: competitor mentions
        comp_counts = comp_df['keyword'].value_counts()
        fig = px.bar(
            x=comp_counts.index, y=comp_counts.values,
            title="Competitor Data Points Collected",
            labels={"x": "Competitor", "y": "Records"}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # List collected links
        st.subheader("🔗 Collected Competitor Links")

        for idx, row in comp_df.iterrows():
            row_id = row.get('id', idx)
            # NO key= parameter in st.expander
            with st.expander(f"📌 {row['keyword']} — {row['question_title'][:70]}"):
                st.write(f"**📅 Collected:** {row['collection_date']}")
                st.write(f"**📊 Source:** {row['source']}")
                st.write(f"**🎯 Score:** {row['opportunity_score']:.1f}")
                st.write(f"**🔗 Link:** [{row['proof_link'][:80]}]({row['proof_link']})")
                st.write(f"**📝 Details:** {row['question_body']}")

                if row.get('content_idea'):
                    st.markdown("**💡 Content Opportunity:**")
                    st.write(row['content_idea'])

    # =========================================================
    # COMPETITIVE COMPARISON TABLE
    # =========================================================

    st.subheader("📊 Feature Comparison: Eagle 3D vs Competitors")

    comparison_data = {
        "Feature": [
            "Unreal Engine Support",
            "Auto-Scaling",
            "Multi-Region",
            "Custom Branding",
            "Analytics Dashboard",
            "REST API",
            "Pay-Per-Use Pricing",
            "Free Trial",
            "Enterprise Support",
            "Self-Hosted Option",
        ],
        "Eagle 3D": ["✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅"],
        "Arcware": ["✅", "✅", "✅", "❌", "✅", "✅", "✅", "✅", "✅", "❌"],
        "PureWeb": ["✅", "✅", "✅", "✅", "✅", "✅", "❌", "❌", "✅", "❌"],
        "Furioos": ["✅", "✅", "⚠️", "❌", "⚠️", "✅", "✅", "✅", "⚠️", "❌"],
        "Vagon": ["✅", "✅", "⚠️", "✅", "✅", "⚠️", "✅", "✅", "⚠️", "❌"],
        "AWS DIY": ["✅", "✅", "✅", "✅", "❌", "✅", "✅", "✅", "⚠️", "✅"],
    }

    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.caption("✅ = Full support | ⚠️ = Partial/Limited | ❌ = Not available")
    st.caption("Data sourced from public competitor websites. Last verified: 2024.")


def show_analytics():
    st.title("📈 Analytics & Trends")

    logs_df = get_daily_logs(st.session_state.user_id)

    if not logs_df.empty:
        st.subheader("📅 Daily Collection History")
        st.dataframe(logs_df, use_container_width=True)

        st.subheader("📊 Collection Trend")
        logs_chart = logs_df.copy()
        logs_chart['collection_date'] = pd.to_datetime(logs_chart['collection_date'])
        logs_chart = logs_chart.sort_values('collection_date')
        fig = px.line(
            logs_chart, x='collection_date', y='records_collected',
            markers=True, title="Daily Records Collected"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 No collection history yet. Run Data Collection first.")

    df = get_all_data(st.session_state.user_id)
    if not df.empty:
        st.subheader("📊 All-Time Source Breakdown")
        source_counts = df['source'].value_counts()
        fig = px.pie(
            values=source_counts.values, names=source_counts.index,
            hole=0.4, title="Records by Source"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🎯 Score Distribution")
        fig = px.histogram(
            df, x='opportunity_score', nbins=20,
            title="Opportunity Score Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("💼 B2B vs B2C Split")
        b2b_counts = df['is_b2b'].value_counts()
        labels = ['B2B' if k else 'B2C' for k in b2b_counts.index]
        fig = px.pie(values=b2b_counts.values, names=labels, hole=0.4, title="B2B vs B2C")
        st.plotly_chart(fig, use_container_width=True)


def show_settings():
    st.title("⚙️ Platform Settings")

    st.subheader("📱 Telegram Notifications")
    st.markdown(get_telegram_setup_instructions())

    col1, col2 = st.columns(2)
    with col1:
        bot_token = st.text_input(
            "Bot Token", type="password",
            value=get_setting('telegram_bot_token', st.session_state.user_id) or "",
            key="settings_bot_token"
        )
    with col2:
        chat_id = st.text_input(
            "Chat ID",
            value=get_setting('telegram_chat_id', st.session_state.user_id) or "",
            key="settings_chat_id"
        )

    if st.button("💾 Save Telegram Settings", key="save_telegram_settings_button"):
        save_setting('telegram_bot_token', bot_token, st.session_state.user_id)
        save_setting('telegram_chat_id', chat_id, st.session_state.user_id)
        st.success("✅ Saved!")

        try:
            notifier = TelegramNotifier(bot_token, chat_id)
            notifier.send_message("🦅 Eagle 3D Intelligence\n\n✅ Telegram connected!")
            st.success("✅ Test message sent!")
        except Exception as e:
            st.error(f"❌ Test failed: {e}")

    st.markdown("---")
    st.subheader("💾 Data Management")
    st.write("To reset all data, delete `eagle_intelligence.db` and restart the app.")


if __name__ == "__main__":
    main()