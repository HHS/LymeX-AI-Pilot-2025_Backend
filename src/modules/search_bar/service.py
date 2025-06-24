from src.modules.product.models import Product
from src.modules.product.performance_testing.model import PerformanceTesting
from src.modules.product.clinical_trial.model import ClinicalTrial
from src.modules.product.regulatory_pathway.model import RegulatoryPathway
from src.modules.search_bar.schema import UnifiedSearchResult
from src.modules.company.models import Company
from typing import List


async def unified_search(company: Company, query: str) -> List[UnifiedSearchResult]:
    results = []
    query_lower = query.lower()

    # --- Product Model Search ---
    product_fields = ["name", "model", "revision", "category"]
    products = await Product.find(Product.company_id == str(company.id)).to_list()
    for product in products:
        for field in product_fields:
            value = getattr(product, field, "")
            if value and query_lower in str(value).lower():
                results.append(
                    UnifiedSearchResult(
                        product_id=str(product.id),
                        product_name=product.name,
                        module="product_profile",
                        matched_key=field,
                        matched_value=str(value),
                    )
                )

    # --- PerformanceTesting Model Search ---
    performance_testings = await PerformanceTesting.find({}).to_list()
    for pt in performance_testings:
        # Optionally, filter by company or by product_id in products
        if pt.product_id not in [str(p.id) for p in products]:
            continue
        for field in ["test_name", "test_description"]:
            value = getattr(pt, field, "")
            if value and query_lower in str(value).lower():
                # Get product name for this product_id
                product = next(
                    (p for p in products if str(p.id) == pt.product_id), None
                )
                product_name = product.name if product else ""
                results.append(
                    UnifiedSearchResult(
                        product_id=pt.product_id,
                        product_name=product_name,
                        module="performance_testing",
                        matched_key=field,
                        matched_value=str(value),
                    )
                )

    # --- ClinicalTrial Model Search ---
    clinical_trials = await ClinicalTrial.find({}).to_list()
    for ct in clinical_trials:
        if ct.product_id not in [str(p.id) for p in products]:
            continue
        for field in ["name", "sponsor", "study_design", "outcome"]:
            value = getattr(ct, field, "")
            if value and query_lower in str(value).lower():
                product = next(
                    (p for p in products if str(p.id) == ct.product_id), None
                )
                product_name = product.name if product else ""
                results.append(
                    UnifiedSearchResult(
                        product_id=ct.product_id,
                        product_name=product_name,
                        module="clinical_trial",
                        matched_key=field,
                        matched_value=str(value),
                    )
                )

    # --- RegulatoryPathway Model Search ---
    regulatory_pathways = await RegulatoryPathway.find({}).to_list()
    for rp in regulatory_pathways:
        if rp.product_id not in [str(p.id) for p in products]:
            continue
        for field in ["recommended_pathway", "description"]:
            value = getattr(rp, field, "")
            if value and query_lower in str(value).lower():
                product = next(
                    (p for p in products if str(p.id) == rp.product_id), None
                )
                product_name = product.name if product else ""
                results.append(
                    UnifiedSearchResult(
                        product_id=rp.product_id,
                        product_name=product_name,
                        module="regulatory_pathway",
                        matched_key=field,
                        matched_value=str(value),
                    )
                )

    return results
