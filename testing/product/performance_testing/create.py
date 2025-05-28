import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


def create_performance_testing(access_token: str, company_id: str, product_id: str):
    url = f"{environment.base_url}/product/{product_id}/performance-testing/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.post(
        url,
        headers=headers,
        json={
            "test_name": "TEST-001",
            "risk_level": "Medium",
            "status": "Pending",
            "test_description": "This is a test performance testing.",
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    create_performance_testing(access_token, company_id, product_id)
    print("Test completed.")
