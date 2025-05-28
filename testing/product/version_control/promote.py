import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


def promote_major_version_handler(access_token: str, company_id: str, product_id: str):
    url = f"{environment.base_url}/product/{product_id}/version-control/promote-major-version"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]


def get_first_analyze_product_version_control(
    access_token: str, company_id: str, product_id: str
):
    product_version_controls = promote_major_version_handler(
        access_token, company_id, product_id
    )
    if not product_version_controls:
        raise ValueError("No version control Product version controls found.")
    # As 0 is self
    return product_version_controls[1]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    product_version_control = promote_major_version_handler(
        access_token, company_id, product_id
    )
    print(
        f"Product Version Control Product version control: {json.dumps(product_version_control, indent=4)}"
    )
    print("Test completed.")
