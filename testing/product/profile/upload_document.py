import requests

from testing.company.get_company import get_first_company
from testing.authentication.login_refresh_token import login_refresh_token
from testing.environment import environment
from testing.product.get_product import get_first_product


test_file_path = "/Users/macbookpro/Downloads/slack-2020.pdf"


def get_product_upload_url(access_token: str, company_id: str, product_id: str):
    file_name = test_file_path.split("/")[-1]
    url = f"{environment.base_url}/product/{product_id}/profile/document/upload-url?file_name={file_name}&category=product"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Company-ID": company_id,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]


def upload_file(upload_url: str, file_path: str) -> None:
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.put(upload_url, files)
        response.raise_for_status()
        print("File uploaded successfully.")


def test() -> None:
    access_token = login_refresh_token()
    company_id = get_first_company(access_token)["id"]
    product_id = get_first_product(access_token, company_id)["id"]
    product_upload_url = get_product_upload_url(
        access_token,
        company_id,
        product_id,
    )
    print(f"product_upload_url: {product_upload_url}")
    upload_file(
        product_upload_url,
        test_file_path,
    )
