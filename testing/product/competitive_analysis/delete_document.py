import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


def delete_document(
    access_token: str,
    company_id: str,
    product_id: str,
    document_name: str,
):
    url = f"{environment.base_url}/product/{product_id}/competitive-analysis/document/{document_name}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    data = response.json()


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    delete_document(
        access_token,
        company_id,
        product_id,
        "HHNsYWNrLTIwMjAucGRmKGhvdGhpZW5sYWNAZ21haWwuY29tDnByb2R1Y3Q.pdf",
    )
    print("Test completed.")
