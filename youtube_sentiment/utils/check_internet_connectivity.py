import requests

def check_internet_connectivity():
    try:
        response = requests.get("https://www.google.com")
        return response.status_code == 200
    except requests.ConnectionError:
        return False