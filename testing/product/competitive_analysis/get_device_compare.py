import json
import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.competitive_analysis.get_result import (
    get_first_analyze_result,
    get_result,
)
from testing.product.get_product import get_first_product


def get_first_device_compare(
    access_token: str, company_id: str, product_id: str, competitive_analysis_id: str
) -> dict:
    url = f"{environment.base_url}/product/{product_id}/competitive-analysis/result/{competitive_analysis_id}/compare-device-analysis"
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
    first_analyze_result = get_first_analyze_result(
        access_token, company_id, product_id
    )
    first_analyze_result_id = first_analyze_result["id"]
    print(f"First Analyze Result ID: {first_analyze_result_id}")
    result = get_first_device_compare(
        access_token, company_id, product_id, first_analyze_result_id
    )
    print(f"Product Competitive Analysis Result: {json.dumps(result, indent=4)}")
    print("Test completed.")
