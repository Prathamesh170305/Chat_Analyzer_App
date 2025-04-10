import emoji.unicode_codes
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import re
import string
import emoji

extract=URLExtract()
def fetch_stats(selected_user,df):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]

    #fetch nummber of msgs
    num_msgs=df.shape[0]
    #fetch number of words
    words=[]
    for msg in df['message']:
        words.extend(msg.split())

    #fetch number of media messages:
    num_media_msgs=df[df['message']=='<Media omitted>\n'].shape[0]

    #fetch number of links
    links=[]
    for msg in df['message']:
        links.extend(extract.find_urls(msg))

    return num_msgs,len(words),num_media_msgs,len(links)
    
def most_busy_user(df):
    x=df['user'].value_counts().head()
    df=round((df['user'].value_counts()/df.shape[0])*100,2).reset_index()
    return x,df

def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()  # split into list

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    
    def remove_stop_words(msg):
        y=[]
        for word in msg.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='black')
    temp['message']=temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()  # split into list

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for msg in temp['message']:
        # Remove punctuation using regex
        msg = re.sub(f"[{re.escape(string.punctuation)}]", "", msg)
        for word in msg.lower().split():
            if word not in stop_words:
                words.append(word)

    return_df = pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Count'])
    return return_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis=[]
    for msg in df['message']:
        emojis.extend([c for c in msg if emoji.is_emoji(c)])
    emoji_df=pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline=df.groupby(['year','month_num','month']).count()['message'].reset_index()

    time=[]
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+"-"+str(timeline['year'][i]))
    
    timeline['time']=time
    
    return timeline

def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()