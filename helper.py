import re
import string
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
from urlextract import URLExtract
import matplotlib.pyplot as plt
import numpy as np

# Initialize URL extractor
extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Fetch number of msgs
    num_msgs = df.shape[0]
    
    # Fetch number of words
    words = []
    for msg in df['message']:
        words.extend(msg.split())

    # Fetch number of media messages
    num_media_msgs = df[df['message'] == '<Media omitted>\n'].shape[0]

    # Fetch number of links
    links = []
    for msg in df['message']:
        try:
            links.extend(extract.find_urls(msg))
        except:
            pass  # Handle potential errors with URL extraction

    return num_msgs, len(words), num_media_msgs, len(links)
    
def most_busy_user(df):
    # FIX: Ensure proper calculation of user message counts
    user_counts = df['user'].value_counts()
    x = user_counts.head()
    
    # Calculate percentages
    df_percent = pd.DataFrame({
        'User': user_counts.index, 
        'Percent of Messages': np.round((user_counts.values / df.shape[0]) * 100, 2)

    })
    
    return x, df_percent

def create_wordcloud(selected_user, df):
    # Basic stopwords if file not found
    stop_words = ["the", "and", "is", "in", "to", "of", "a", "for", "hai", "ki", "ko", "ka", "tha", 
                "this", "that", "it", "me", "my", "you", "your", "na", "se", "ha", "was", "ho", "par"]
    
    try:
        with open('stop_hinglish.txt', 'r') as f:
            stop_words = f.read().splitlines()
    except FileNotFoundError:
        pass  # Use default stopwords
        
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Filter out group notifications and media messages
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    
    def remove_stop_words(msg):
        # Remove URLs and punctuation
        msg = re.sub(r'http\S+', '', msg)
        msg = re.sub(f"[{re.escape(string.punctuation)}]", "", msg)
        
        # Filter out stopwords
        words = []
        for word in msg.lower().split():
            if word not in stop_words:
                words.append(word)
        return " ".join(words)

    # Create a word cloud
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='black')
    
    # Clean and combine messages
    temp['message'] = temp['message'].apply(remove_stop_words)
    text = temp['message'].str.cat(sep=" ")
    
    # Generate word cloud or empty one if no text
    if text.strip():
        df_wc = wc.generate(text)
    else:
        df_wc = wc.generate("No text available")
    
    return df_wc

def most_common_words(selected_user, df):
    # Basic stopwords if file not found
    stop_words = ["the", "and", "is", "in", "to", "of", "a", "for", "hai", "ki", "ko", "ka", "tha", 
                "this", "that", "it", "me", "my", "you", "your", "na", "se", "ha", "was", "ho", "par"]
    
    try:
        with open('stop_hinglish.txt', 'r') as f:
            stop_words = f.read().splitlines()
    except FileNotFoundError:
        pass  # Use default stopwords

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Filter out group notifications and media messages
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for msg in temp['message']:
        # Remove URLs and punctuation
        msg = re.sub(r'http\S+', '', msg)
        msg = re.sub(f"[{re.escape(string.punctuation)}]", "", msg)
        
        # Filter out stopwords and single characters
        for word in msg.lower().split():
            if word not in stop_words and len(word) > 1:
                words.append(word)

    # Return top 20 most common words
    word_counts = Counter(words).most_common(20)
    if word_counts:
        return_df = pd.DataFrame(word_counts, columns=['Word', 'Count'])
    else:
        # Return empty DataFrame with proper columns if no words found
        return_df = pd.DataFrame(columns=['Word', 'Count'])
    
    return return_df

def emoji_helper(selected_user, df):
    # FIX: Use regex to extract emojis since we can't rely on emoji module
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Simple emoji detection using regex pattern
    # This won't catch all emojis but will work for basic ones
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        u"\U0001F780-\U0001F7FF"  # Geometric Shapes
        u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA00-\U0001FA6F"  # Chess Symbols
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE)
    
    emojis = []
    for message in df['message']:
        found_emojis = emoji_pattern.findall(message)
        emojis.extend(found_emojis)
    
    if emojis:
        emoji_counts = Counter(emojis).most_common(len(Counter(emojis)))
        emoji_df = pd.DataFrame(emoji_counts)
        return emoji_df
    else:
        # Return empty DataFrame with proper structure
        return pd.DataFrame(columns=[0, 1])

def monthly_timeline(selected_user, df):
    # FIX: Ensure proper monthly timeline generation
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Group by year and month
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    
    # Sort chronologically
    timeline = timeline.sort_values(['year', 'month_num'])
    
    # Create a time column for display
    timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)
    
    return timeline

def hourly_activity(selected_user, df):
    # FIX: Create hourly activity analysis
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Create a count of messages by hour
    hourly = df.groupby('hour').count()['message'].reset_index()
    
    # Ensure all hours are represented (0-23)
    all_hours = pd.DataFrame({'hour': range(0, 24)})
    hourly = pd.merge(all_hours, hourly, on='hour', how='left').fillna(0)
    
    return hourly

def week_activity_map(selected_user, df):
    # FIX: Create weekly activity map
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Define day order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Count messages by day
    day_counts = df['day_name'].value_counts()
    
    # Ensure all days are represented
    day_counts = day_counts.reindex(day_order, fill_value=0)
    
    return day_counts

def sentiment_analysis(df, selected_user='Overall'):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>\n']
    
    if df.empty:
        return {'Positive': 0, 'Negative': 0, 'Neutral': 0}, df
    
    df = df.copy()
    
    positive_words = ['happy', 'love', 'great', 'good', 'nice', 'thanks', 'awesome', 'amazing', 'excellent', 'wonderful', 'joy']
    negative_words = ['sad', 'bad', 'hate', 'terrible', 'awful', 'sorry', 'angry', 'upset', 'disappointed', 'problem', 'fail']
    
    def basic_sentiment(text):
        text = text.lower()
        words = text.split()
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        if pos_count > neg_count:
            return 0.5, 'Positive'
        elif neg_count > pos_count:
            return -0.5, 'Negative'
        else:
            return 0, 'Neutral'
    
    sentiments = []
    labels = []
    
    for msg in df['message']:
        score, label = basic_sentiment(msg)
        sentiments.append(score)
        labels.append(label)
    
    df['sentiment'] = sentiments
    df['sentiment_label'] = labels
    
    sentiment_counts = df['sentiment_label'].value_counts().to_dict()
    
    # Ensure all categories are included
    for label in ['Positive', 'Negative', 'Neutral']:
        sentiment_counts.setdefault(label, 0)
    
    return sentiment_counts, df


def response_time_analysis(df, selected_user='Overall'):
    # FIX: Calculate response times between users
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Skip group notifications
    df = df[df['user'] != 'group_notification']
    
    # Sort by date
    df = df.sort_values('date')

    # Calculate time difference between messages
    df['time_diff'] = df['date'].diff()
    
    # Add next user column
    df['next_user'] = df['user'].shift(-1)
    
    # Filter for actual responses (different users)
    df_responses = df[df['user'] != df['next_user']].copy()
    
    # Convert time difference to minutes
    df_responses['response_mins'] = df_responses['time_diff'].dt.total_seconds() / 60
    
    # Filter out unreasonably long times (>24 hours)
    df_responses = df_responses[df_responses['response_mins'] < 24*60]
    
    if len(df_responses) > 0:
        avg_response_time = df_responses['response_mins'].mean()
        response_df = df_responses[['user', 'next_user', 'response_mins']].copy()
        return np.round(avg_response_time, 2), response_df
    else:
        # Return defaults if no valid responses
        return 0, pd.DataFrame(columns=['user', 'next_user', 'response_mins'])