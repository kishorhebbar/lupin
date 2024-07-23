import requests
import pandas as pd
from datetime import datetime, timedelta

# Replace these variables with your own
GITHUB_API_URL = "https://github.lupin.com/api/v3"  # Your GitHub Enterprise API URL
ACCESS_TOKEN = "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"  # Your GitHub Access Token

def get_active_users(since_days=30):
    # Set the headers for authentication
    headers = {
        "Authorization": f"token {ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the current date and calculate the date 'since_days' ago
    since_date = datetime.now() - timedelta(days=since_days)
    since_date_iso = since_date.isoformat()

    # Get the list of users
    users_url = f"{GITHUB_API_URL}/users"
    users_response = requests.get(users_url, headers=headers)

    if users_response.status_code != 200:
        print(f"Failed to fetch users: {users_response.status_code}")
        return []

    users = users_response.json()
    active_users = []

    for user in users:
        username = user['login']
        events_url = f"{GITHUB_API_URL}/users/{username}/events"

        # Fetch user events
        events_response = requests.get(events_url, headers=headers)

        if events_response.status_code != 200:
            print(f"Failed to fetch events for {username}: {events_response.status_code}")
            continue

        events = events_response.json()

        # Filter events that occurred since the specified date
        recent_events = [event for event in events if event['created_at'] >= since_date_iso]

        if recent_events:
            # Add user and their activities to the active users list
            active_users.append({
                "username": username,
                "activity_count": len(recent_events),
                "activities": recent_events
            })

    return active_users

def save_to_excel(active_users, file_name="github_activity.xlsx"):
    data = []
    for user in active_users:
        for event in user['activities']:
            data.append({
                "Username": user['username'],
                "Event Type": event['type'],
                "Repository": event['repo']['name'],
                "Created At": event['created_at']
            })

    # Create a DataFrame and save to Excel
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)

if __name__ == "__main__":
    # Fetch and display active users
    since_days = 30  # Number of days to check for activity
    active_users = get_active_users(since_days=since_days)
    save_to_excel(active_users)
    print("User activity has been saved to github_activity.xlsx")
