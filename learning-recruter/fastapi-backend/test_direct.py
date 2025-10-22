from composio import Composio

composio = Composio(api_key="ak_nsf-0GU62pD5RCWVXyRN")
user_id = "abhishekbabushetty_gmail_com"

result = composio.tools.execute(
    "TWITTER_USER_LOOKUP_ME",
    user_id=user_id,
    arguments={}
)

print("RESULT:", result)