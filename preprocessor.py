import pandas as pd
import re
import datetime

def preprocess(data):
    """
    Preprocess WhatsApp chat data to convert it into a structured DataFrame
    Supports multiple date-time formats
    """
    # First try with standard format: DD/MM/YY, 12-hour format (e.g., 01/02/21, 3:04 pm - )
    pattern1 = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\u202f|\s)?[ap]m\s-\s'
    
    # Alternative format: DD/MM/YY, 24-hour format (e.g., 01/02/21, 15:04 - )
    pattern2 = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    
    # Try first pattern
    dates = re.findall(pattern1, data)
    pattern_used = pattern1
    
    # If first pattern doesn't match, try second pattern
    if not dates:
        dates = re.findall(pattern2, data)
        pattern_used = pattern2
    
    # If we have matches, split the messages
    if dates:
        messages = re.split(pattern_used, data)
        
        # Remove the first empty message (before the first timestamp)
        if messages and messages[0] == '':
            messages.pop(0)
        
        # Clean dates (remove Unicode spaces and trailing dash)
        cleaned_dates = [d.replace('\u202f', ' ').replace(' -', '').strip() for d in dates]
        
        # Create DataFrame
        df = pd.DataFrame({'user_message': messages, 'message_date': cleaned_dates})
        
        # Convert dates to datetime
        try:
            # First try 12-hour format
            df['date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p', errors='coerce')
            
            # If that fails, try 24-hour format
            if df['date'].isna().all():
                df['date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M', errors='coerce')
            
            # If there are still NAs, try another common format
            if df['date'].isna().any():
                mask = df['date'].isna()
                df.loc[mask, 'date'] = pd.to_datetime(
                    df.loc[mask, 'message_date'], format='%m/%d/%y, %I:%M %p', errors='coerce')
            
            # Try yet another format if needed
            if df['date'].isna().any():
                mask = df['date'].isna()
                df.loc[mask, 'date'] = pd.to_datetime(
                    df.loc[mask, 'message_date'], format='%d/%m/%Y, %I:%M %p', errors='coerce')
            
        except Exception as e:
            print(f"Error converting dates: {e}")
            # Fallback to a more flexible parser
            try:
                df['date'] = pd.to_datetime(df['message_date'], errors='coerce')
            except:
                # Last resort: create dummy dates
                print("Failed to parse dates, using dummy values")
                start_date = datetime.datetime(2020, 1, 1)
                df['date'] = [start_date + datetime.timedelta(minutes=i) for i in range(len(df))]
        
        # Drop rows with invalid dates and the original message_date column
        df = df.dropna(subset=['date'])
        df.drop(columns=['message_date'], inplace=True)
        
        # Extract users and messages
        users = []
        messages_content = []
        
        for message in df['user_message']:
            # Try to split on first colon (sender: message)
            entry = re.split(r'(.*?):\s', message, maxsplit=1)
            
            if len(entry) >= 3:
                # Format is correct: [empty or previous text, sender, message]
                # Get the last two elements if there are more than 3
                sender = entry[-2]
                message_content = entry[-1]
                users.append(sender)
                messages_content.append(message_content)
            else:
                # System or group notification (no sender)
                users.append('group_notification')
                messages_content.append(message.strip())
        
        # Add to DataFrame
        df['user'] = users
        df['message'] = messages_content
        
        # Drop the raw user_message column
        df.drop(columns=['user_message'], inplace=True)
        
        # Extract date features
        df['year'] = df['date'].dt.year
        df['month_num'] = df['date'].dt.month
        df['month'] = df['date'].dt.month_name()
        df['day'] = df['date'].dt.day
        df['day_name'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute
        
        return df
    else:
        # If no timestamps found, return empty DataFrame with correct columns
        return pd.DataFrame(columns=['date', 'user', 'message', 'year', 'month_num', 
                                    'month', 'day', 'day_name', 'hour', 'minute'])