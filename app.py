# app.py

import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose File")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    st.write("File uploaded successfully!")
    data=bytes_data.decode("utf-8")
    #st.text(data)
    df=preprocessor.preprocess(data)

    #st.dataframe(df)

    #fetch unique users
    user_list=df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user=st.sidebar.selectbox("Show analysis w.r.t:",user_list)
    
    if st.sidebar.button("Show Analysis"):
        num_msgs,words,num_media,links=helper.fetch_stats(selected_user,df)
        st.title("Top Stats")
        col1,col2,col3,col4=st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_msgs)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media)
        with col4:
            st.header("Links Shared")
            st.title(links)

        #timeline
        timeline=helper.monthly_timeline(selected_user,df)
        fig,ax=plt.subplots()
        ax.plot(timeline['time'],timeline['message'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        #activity map
        st.title('Activity Map')
        col1 , col2 =st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day=helper.week_activity_map(selected_user,df)
            fig,ax=plt.subplots()
            ax.bar(busy_day.index,busy_day.values)
            st.pyplot(fig)
        
        with col2:
            st.dataframe(busy_day)

        if selected_user=='Overall':
            st.title("Most Busy User")
            x,new_df=helper.most_busy_user(df)
            fig,ax=plt.subplots()
            col1,col2=st.columns(2)

            with col1:
                ax.bar(x.index,x.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)
        
        #wordcloud
        st.title("WordCloud")
        df_wc=helper.create_wordcloud(selected_user,df)
        fig,ax=plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        #most common words
        most_com_df=helper.most_common_words(selected_user,df)
        fig,ax=plt.subplots()
        ax.barh(most_com_df['Word'], most_com_df['Count'])
        plt.xticks(rotation='vertical')
        st.title("Most common words")
        st.pyplot(fig)
       #st.dataframe(most_com_df)

       #emoji analysis 
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            # Set emoji-compatible font (for Windows)
            plt.rcParams['font.family'] = 'Segoe UI Emoji'

            # Create pie chart
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            st.pyplot(fig)

