import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


def get_note(access_token: str, company_id: str, product_id: str):
    url = f"{environment.base_url}/product/{product_id}/test-comparison/note"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    product_test_comparison = get_note(access_token, company_id, product_id)
    print(f"Product Test Comparison: {json.dumps(product_test_comparison, indent=4)}")
    print("Test completed.")
