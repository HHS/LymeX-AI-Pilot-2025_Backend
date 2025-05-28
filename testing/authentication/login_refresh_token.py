import requests

from testing.environment import environment


def login_refresh_token() -> str:
    response = requests.post(
        f"{environment.base_url}/authentication/login/refresh-token",
        json={
            "refresh_token": environment.refresh_token,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["access_token"]


def test() -> None:
    """
    Test the login refresh token functionality.
    """
    try:
        access_token = login_refresh_token()
        print(f"Access token: {access_token}")
    except requests.RequestException as e:
        print(f"Error during login refresh token: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("Test completed.")
