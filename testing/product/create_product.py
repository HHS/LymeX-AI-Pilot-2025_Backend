import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment


def create_product(access_token: str, company_id: str):
    url = f"{environment.base_url}/product/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.post(
        url,
        headers=headers,
        json={
            "name": "Test Product",
            "model": "Test Product Model",
            "revision": "Test Product Revision",
            "category": "Test Product Category",
            "intend_use": "Test Product Intended Use",
            "patient_contact": True,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    created_product = create_product(access_token, company_id)
    print(f"Product Profile: {json.dumps(created_product, indent=4)}")
    print("Test completed.")
