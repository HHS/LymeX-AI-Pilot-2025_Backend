import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment


def get_products(access_token: str, company_id: str):
    response = requests.get(
        f"{environment.base_url}/product",
        headers={
            "Authorization": f"Bearer {access_token}",
            "company-id": company_id,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]


def get_first_product(access_token: str, company_id: str):
    products = get_products(access_token, company_id)
    if not products:
        raise ValueError("No products found.")
    return products[0]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    products = get_products(access_token, company_id)
    print(f"Products: {products}")
    print("Test completed.")
