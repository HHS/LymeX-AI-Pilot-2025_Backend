import json
import requests

from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment


def get_companies(access_token: str):
    response = requests.get(
        f"{environment.base_url}/company/list",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]


def get_first_company(access_token: str):
    companies = get_companies(access_token)
    if not companies:
        raise ValueError("No companies found.")
    return companies[0]


def test() -> None:
    try:
        access_token = login_refresh_token()
        companies = get_companies(access_token)
        print(f"Companies: {json.dumps(companies, indent=4)}")
    except requests.RequestException as e:
        print(f"Error during get companies: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("Test completed.")
