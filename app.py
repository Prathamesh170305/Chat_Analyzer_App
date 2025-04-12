import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS Styling ----------
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #0f172a; /* Deep slate blue */
        color: #f8fafc; /* Light text */
    }

    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    h1, h2, h3, h4, p, li, span, div {
        color: #f8fafc !important;
    }

    h1 {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 2rem !important;
        text-align: center;
        color: #ffffff !important;
    }

    h2 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin: 1.5rem 0 !important;
        color: #e2e8f0 !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding: 1rem 0;
    }

    .stMetric {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        text-align: center;
    }

    .stPlotlyChart, .stAltairChart, .stPyplotChart {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .stSidebar {
        background-color: #1e293b;
        padding: 2rem;
        color: #ffffff;
    }

    .stButton>button {
        width: 100%;
        background-color: #3b82f6;
        color: #ffffff;
        border: none;
        padding: 0.75rem 1.25rem;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: background-color 0.3s;
    }

    .stButton>button:hover {
        background-color: #2563eb;
    }

    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #94a3b8;
        font-size: 0.875rem;
    }

    .creator {
        font-size: 0.9rem;
        color: #38bdf8;
    }

    ol {
        padding-left: 1.2rem;
        color: #f1f5f9 !important;
    }
    </style>
""", unsafe_allow_html=True)


# ---------- Sidebar ----------
with st.sidebar:
    st.title("📱 WhatsApp Analyzer")
    st.markdown("---")

    st.markdown("### Upload Chat File")
    uploaded_file = st.file_uploader(
        "Choose your WhatsApp chat export file",
        type=["txt"],
        help="Export your WhatsApp chat and upload the text file here"
    )

# ---------- Main Area ----------
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    with st.sidebar:
        st.markdown("### Analysis Options")
        selected_user = st.selectbox("Select User for Analysis", user_list)
        analyze = st.button("Generate Analysis", use_container_width=True)

    if analyze:
        # Use tabs for sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview", "📅 Timeline", "📝 Text Analysis", "❤️ Sentiment"
        ])

        # Fetch stats
        num_msgs, words, num_media, links = helper.fetch_stats(selected_user, df)

        with tab1:
            st.title("Chat Overview")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Messages", f"{num_msgs:,}")
            col2.metric("Total Words", f"{words:,}")
            col3.metric("Media Shared", f"{num_media:,}")
            col4.metric("Links Shared", f"{links:,}")

            st.markdown("---")
            st.subheader("📊 Activity Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Most Active Day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='#3b82f6')
                plt.xticks(rotation=45)
                st.pyplot(fig)

            with col2:
                if selected_user == 'Overall':
                    st.markdown("#### User Activity")
                    x, new_df = helper.most_busy_user(df)
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color='#10b981')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                    with st.expander("📋 Detailed User Stats"):
                        st.dataframe(new_df, use_container_width=True, hide_index=True)

        with tab2:
            st.title("Timeline Analysis")

            st.subheader("📈 Monthly Activity")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], marker='o', color='#8b5cf6')
            plt.xticks(rotation=45)
            st.pyplot(fig)

            st.subheader("🕒 Hourly Activity Pattern")
            hourly = helper.hourly_activity(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(hourly.index, hourly.values, marker='o', color='#8b5cf6')
            plt.xticks(range(24))
            st.pyplot(fig)

        with tab3:
            st.title("Text Analysis")

            st.subheader("☁️ Word Cloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis('off')
            st.pyplot(fig)

            st.subheader("📊 Most Common Words")
            most_common = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(most_common['Word'][:15], most_common['Count'][:15], color='#6366f1')
            plt.tight_layout()
            st.pyplot(fig)

            st.subheader("😊 Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(emoji_df.rename(columns={0: "Emoji", 1: "Count"}))
                with col2:
                    if len(emoji_df) > 8:
                        emoji_df = emoji_df.head(8)
                    fig, ax = plt.subplots()
                    plt.pie(emoji_df[1], labels=[f"Top {i+1}" for i in range(len(emoji_df))],
                            autopct='%1.1f%%', colors=plt.cm.Pastel1(np.linspace(0, 1, len(emoji_df))))
                    st.pyplot(fig)
            else:
                st.info("No emojis found")

        with tab4:
            st.title("Sentiment Analysis")

            try:
                sentiment_counts, sentiment_df = helper.sentiment_analysis(df, selected_user)
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("😊 Message Sentiment")
                    fig, ax = plt.subplots()
                    colors = ['#10b981', '#ef4444', '#6b7280']
                    sentiment_series = pd.Series(sentiment_counts)
                    plt.pie(sentiment_series.values, labels=sentiment_series.index, autopct='%1.1f%%', colors=colors)
                    st.pyplot(fig)

                with col2:
                    st.subheader("📈 Sentiment Trends")
                    monthly_sentiment = sentiment_df.groupby(['year', 'month_num'])['sentiment'].mean().reset_index()
                    monthly_sentiment['month_year'] = monthly_sentiment.apply(lambda x: f"{x['month_num']}-{x['year']}", axis=1)
                    fig, ax = plt.subplots()
                    plt.plot(monthly_sentiment['month_year'], monthly_sentiment['sentiment'], marker='o', color='#8b5cf6')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

            except:
                st.error("Sentiment analysis failed. Make sure `vaderSentiment` is installed.")

else:
    st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <h1 style='color: #374151'>👋 Welcome to WhatsApp Chat Analyzer!</h1>
            <p style='font-size: 1.2rem; color: #4b5563;'>
                Upload your WhatsApp chat export file to begin analyzing!
            </p>
            <div style='background-color: black; padding: 1.5rem; border-radius: 0.5rem;'>
                <h3 style='color: black;'>How to export your chat:</h3>
                <ol>
                    <li>Open the WhatsApp chat</li>
                    <li>Tap ⋮ > More > Export Chat</li>
                    <li>Select “Without Media”</li>
                    <li>Upload the downloaded .txt file here</li>
                </ol>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("---")
st.markdown(f"""
    <div class='footer'>
        WhatsApp Chat Analyzer &copy; 2025 <br/>
        <span class='creator'>Created by <strong>Prathamesh Wankhade</strong></span>
    </div>
""", unsafe_allow_html=True)
