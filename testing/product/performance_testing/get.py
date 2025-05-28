import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


def get(access_token: str, company_id: str, product_id: str):
    url = f"{environment.base_url}/product/{product_id}/performance-testing/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]


def get_first_product_performance_testing(
    access_token: str, company_id: str, product_id: str
):
    product_performance_testings = get(access_token, company_id, product_id)
    if not product_performance_testings:
        raise ValueError("No performance testing found for the product.")
    return product_performance_testings[0]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    product_performance_testing = get(access_token, company_id, product_id)
    print(
        f"Product Performance Testing: {json.dumps(product_performance_testing, indent=4)}"
    )
    print("Test completed.")
