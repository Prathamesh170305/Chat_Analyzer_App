# app.py (with fixes)

import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Set page configuration
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# Apply custom CSS for better appearance
st.markdown("""
    <style>
    .main {padding-top: 1rem;}
    .stTabs [data-baseweb="tab-panel"] {padding-top: 1rem;}
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose File")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    st.write("File uploaded successfully!")
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for:", user_list)
    
    # Add tabs for better organization
    if st.sidebar.button("Show Analysis"):
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Timeline Analysis", "Text Analysis", "Sentiment & Response"])
        
        with tab1:
            st.title("Overview Statistics")
            num_msgs, words, num_media, links = helper.fetch_stats(selected_user, df)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Messages", num_msgs)
            with col2:
                st.metric("Total Words", words)
            with col3:
                st.metric("Media Shared", num_media)
            with col4:
                st.metric("Links Shared", links)

            # Activity map - FIX: Most Active Day
            st.subheader('Activity Map')
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Most Active Day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='skyblue')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            
            # FIX: Most Active Users
            with col2:
                st.subheader("Most Active Users")
                if selected_user == 'Overall':
                    x, new_df = helper.most_busy_user(df)
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color='lightgreen')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                    with st.expander("View Detailed User Stats"):
                        st.dataframe(new_df)
                else:
                    st.info(f"Showing data for user: {selected_user}")
        
        with tab2:
            st.title("Timeline Analysis")
            
            # FIX: Monthly timeline
            timeline = helper.monthly_timeline(selected_user, df)
            st.subheader("Monthly Activity")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(timeline['time'], timeline['message'], marker='o', linewidth=2, color='purple')
            plt.xticks(rotation=90)
            plt.tight_layout()
            st.pyplot(fig)
            
            # FIX: Hourly activity analysis
            st.subheader("Hourly Activity")
            hourly_activity = helper.hourly_activity(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(hourly_activity['hour'], hourly_activity['message'], marker='o', linewidth=2, color='orange')
            plt.xticks(range(0, 24))
            ax.set_xlabel('Hour of Day')
            ax.set_ylabel('Number of Messages')
            plt.tight_layout()
            st.pyplot(fig)

        with tab3:
            st.title("Text Analysis")
            
            # WordCloud
            st.subheader("Word Cloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis('off')
            st.pyplot(fig)

            # Most common words
            st.subheader("Most Common Words")
            most_com_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(most_com_df['Word'], most_com_df['Count'], color='teal')
            plt.tight_layout()
            st.pyplot(fig)
            
            # FIX: Emoji analysis with pie chart
            st.subheader("Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)
            
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(emoji_df.rename(columns={0: "Emoji", 1: "Count"}))
                with col2:
                    # FIX: Simplified pie chart without emoji labels
                    fig, ax = plt.subplots()
                    if len(emoji_df) > 10:  # Limit to top 10 emojis
                        emoji_df = emoji_df.head(10)
                    
                    # Create a simpler pie chart with counts and no emoji labels
                    counts = emoji_df[1].values
                    # Use numbers as labels instead of emojis which can cause display issues
                    labels = [f"Top {i+1}" for i in range(len(emoji_df))]
                    
                    ax.pie(counts, labels=labels, autopct='%1.1f%%')
                    ax.set_title("Top Emoji Distribution")
                    st.pyplot(fig)
            else:
                st.info("No emojis found in the selected messages")
                
        with tab4:
            st.title("Sentiment & Response Analysis")
            
            # FIX: Sentiment analysis
            try:
                sentiment_counts, sentiment_df = helper.sentiment_analysis(df, selected_user)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Sentiment Distribution")
                    fig, ax = plt.subplots()
                    sentiment_counts.plot(kind='bar', color=['green', 'blue', 'red'], ax=ax)
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                with col2:
                    st.subheader("Sentiment Over Time")
                    # Group by month and calculate average sentiment
                    try:
                        monthly_sentiment = sentiment_df.groupby(['year', 'month_num'])['sentiment'].mean().reset_index()
                        monthly_sentiment['month_year'] = monthly_sentiment['month_num'].astype(str) + '-' + monthly_sentiment['year'].astype(str)
                        
                        fig, ax = plt.subplots()
                        ax.plot(monthly_sentiment['month_year'], monthly_sentiment['sentiment'], marker='o', linestyle='-')
                        plt.xticks(rotation=90)
                        plt.tight_layout()
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error in sentiment over time: {e}")
                        st.info("Not enough data to show sentiment trends over time")
            except Exception as e:
                st.error(f"Error in sentiment analysis: {e}")
                st.info("Could not perform sentiment analysis. Make sure vaderSentiment is installed.")
            
            # FIX: Response Time Analysis
            st.subheader("Response Time Analysis")
            try:
                avg_response_time, response_df = helper.response_time_analysis(df, selected_user)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Response Time", f"{avg_response_time} minutes")
                    
                    if not response_df.empty:
                        # Filter out extremely long response times
                        filtered_response = response_df[response_df['response_mins'] < 60]
                        
                        if not filtered_response.empty:
                            fig, ax = plt.subplots()
                            sns.boxplot(y=filtered_response['response_mins'], ax=ax)
                            ax.set_ylabel('Response Time (minutes)')
                            plt.tight_layout()
                            st.pyplot(fig)
                        else:
                            st.info("No suitable response time data available")
                    else:
                        st.info("No response time data available")
                    
                with col2:
                    st.subheader("Response Time Sample")
                    if not response_df.empty:
                        st.dataframe(response_df.head(10))
                    else:
                        st.info("No response time data available")
            except Exception as e:
                st.error(f"Error in response time analysis: {e}")
                st.info("Could not perform response time analysis")

# Add footer with credits
st.markdown("---")
st.markdown("WhatsApp Chat Analyzer - Created with Streamlit")