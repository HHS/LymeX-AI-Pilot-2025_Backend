import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


def accept_draft(access_token: str, company_id: str, product_id: str):
    url = f"{environment.base_url}/product/{product_id}/claim-builder/draft/accept"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    try:
        result = accept_draft(access_token, company_id, product_id)
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        print(json.dumps(json.loads(e.response.text), indent=4))
        return
    print(f"Product Claim Builder Result: {json.dumps(result, indent=4)}")
    print("Test completed.")
