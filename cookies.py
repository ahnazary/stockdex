import requests

# Create a session to persist cookies
session = requests.Session()

# Step 1: Load the page to get cookies and crumb (CSRF token)
url = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/SPY"  # or any protected page

response = session.get(url)
cookies = session.cookies.get_dict()

# Print cookies
print("Cookies:", cookies)
