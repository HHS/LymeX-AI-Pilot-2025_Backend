import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


def get(access_token: str, company_id: str, product_id: str):
    url = f"{environment.base_url}/product/{product_id}/regulatory-pathway/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]


def get_first_product_regulatory_pathway(
    access_token: str, company_id: str, product_id: str
):
    product_regulatory_pathways = get(access_token, company_id, product_id)
    if not product_regulatory_pathways:
        raise ValueError("No regulatory pathway found for the product.")
    return product_regulatory_pathways[0]


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    product_regulatory_pathway = get(access_token, company_id, product_id)
    print(
        f"Product Regulatory Pathway: {json.dumps(product_regulatory_pathway, indent=4)}"
    )
    print("Test completed.")
