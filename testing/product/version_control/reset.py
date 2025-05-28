import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


def reset_to_version_handler(access_token: str, company_id: str, product_id: str):
    url = (
        f"{environment.base_url}/product/{product_id}/version-control/reset-to-version"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.post(
        url, headers=headers, json={"version": "v5.6", "comment": "test"}
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    product_version_control = reset_to_version_handler(
        access_token, company_id, product_id
    )
    print(
        f"Product Version Control Product version control: {json.dumps(product_version_control, indent=4)}"
    )
    print("Test completed.")
