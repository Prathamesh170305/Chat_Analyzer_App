import pandas as pd
import re

def preprocess(data):
        pattern = r'\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}(?:\u202f|\s)?[ap]m\s-\s'
        dates = re.findall(pattern, data)
        messages = re.split(pattern, data)

        # Remove the first message (before the first timestamp, like system notice)
        if len(messages) > len(dates):
            messages = messages[1:]

        # Step 3: Clean dates by removing unwanted Unicode spaces
        cleaned_dates = [d.replace('\u202f', '').replace(' -', '').strip() for d in dates]

        # Step 4: Create DataFrame
        df = pd.DataFrame({'user message': messages, 'message_dates': cleaned_dates})

        # Step 5: Convert to datetime
        df['message_dates'] = pd.to_datetime(df['message_dates'], format='%d/%m/%y, %I:%M%p', errors='coerce')
        df.rename(columns={'message_dates': 'date'}, inplace=True)

        

        users = []
        messages_content = []

        for message in df['user message']:
            # Try to split on first colon (sender: message)
            entry = re.split(r'^(.*?):\s', message, maxsplit=1)

            if len(entry) == 3:
                # If format is correct: [empty, sender, message]
                users.append(entry[1])
                messages_content.append(entry[2])
            else:
                # System or group notification (no sender)
                users.append('group_notification')
                messages_content.append(message)

        # Add to DataFrame
        df['user'] = users
        df['message'] = messages_content

        # Drop the raw 'user message' column
        df.drop(columns=['user message'], inplace=True)

        df['year']=df['date'].dt.year
        df['month_num']=df['date'].dt.month
        df['month']=df['date'].dt.month_name()
        df['day_name']=df['date'].dt.day_name()
        df['day']=df['date'].dt.day
        df['hour']=df['date'].dt.hour
        df['minute']=df['date'].dt.minute

        return df



