from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from loguru import logger

from src.modules.product.performance_testing.model import PerformanceTestPlan
from src.modules.product.performance_testing.storage import (
    TestingDocumentInfo,
    delete_performance_testing_document,
    get_performance_testing_documents,
    get_upload_performance_testing_document_url,
)
from src.celery.tasks.analyze_performance_testing import (
    analyze_performance_testing_task,
)
from src.modules.product.performance_testing.service import (
    get_analyze_performance_testing_progress,
    get_performance_test_plan,
)
from src.modules.authentication.dependencies import get_current_user
from src.modules.product.performance_testing.schema import (
    AcceptedPerformanceTestingRequest,
    CreatePerformanceTestingRequest,
    ModuleStatus,
    PerformanceTestCard,
    PerformanceTestingDocumentResponse,
    PerformanceTestingResponse,
    PerformanceTestingWithProgressResponse,
    RejectedPerformanceTestingRequest,
    UploadTextInputDocumentRequest,
    map_to_performance_testing_response,
)
from src.modules.product.product_profile.service import create_audit_record
from src.modules.user.models import User
from src.modules.product.dependencies import (
    check_product_edit_allowed,
    get_current_product,
)
from src.modules.product.models import Product


router = APIRouter()


@router.get("/")
async def get_product_performance_testings_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> PerformanceTestingWithProgressResponse:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )

    # Get progress information
    analyze_performance_testing_progress = (
        await get_analyze_performance_testing_progress(
            str(product.id),
        )
    )
    documents = await get_performance_testing_documents(
        str(product.id),
    )
    performance_testing_results = (
        [
            map_to_performance_testing_response(test, documents)
            for test in performance_test_plan.tests
        ]
        if performance_test_plan
        else []
    )

    return PerformanceTestingWithProgressResponse(
        performance_testing=performance_testing_results,
        analyze_performance_testing_progress=(
            analyze_performance_testing_progress.to_analyze_performance_testing_progress_response()
            if analyze_performance_testing_progress
            else None
        ),
    )


@router.get("/section-keys")
def get_performance_testing_section_keys_handler() -> dict[str, dict[str, str]]:
    return {
        "analytical": {
            "precision": "Precision (Repeatability / Reproducibility)",
            "linearity": "Linearity",
            "sensitivity": "Analytical Sensitivity / Detection Limit(s)",
            "measuring_range": "Assay Measuring Range",
            "cut_off": "Assay Cut-off",
            "traceability": "Traceability",
            "stability": "Stability",
            "usability": "Usability / Human-Factors",
            "other_analytical": "Other Analytical supportive data",
        },
        "comparison": {
            "method": "Method Comparison",
            "matrix": "Matrix Comparison",
        },
        "clinical": {
            "clin_sens_spec": "Clinical Sensitivity / Specificity",
            "clin_cut_off": "Clinical Cut-off",
            "other_clinical": "Other Clinical supportive data",
        },
        "animal_testing": {
            "glp_animal": "GLP-compliant Animal Testing",
        },
        "emc_safety": {
            "iec_60601_1_2": "EMC (IEC 60601-1-2 / IEC 61326-2-6)",
            "asca_summary": "ASCA Test Summary Report",
            "design_mods": "Design-modifications-to-pass report",
            "rf_risk_analysis": "EM emitter risk analysis (RFID, 5 G, …)",
        },
        "wireless": {
            "coexistence": "Wireless Coexistence / FWP",
        },
        "software": {
            "sw_description": "Software / Firmware Description",
            "risk_file": "Risk-management File",
            "srs": "Software Requirements Spec",
            "arch_view": "Architecture Diagram",
            "sds": "Software Design Spec",
            "lifecycle_desc": "Lifecycle / Config mgmt",
            "vnv_reports": "V&V Reports",
            "revision_history": "Revision History",
            "unresolved_anom": "Unresolved Anomalies List",
        },
        "cybersecurity": {
            "security_rm_report": "Security Risk-Management Report",
            "threat_model": "Threat Model Document",
            "cyber_risk": "Cybersecurity Risk Assessment",
            "sbom": "SBOM",
            "component_eos": "End-of-Support Statement",
            "vuln_assessment": "Vulnerability Assessment",
            "anom_impact": "Anomaly Impact Assessment",
            "metrics": "Security Metrics Monitoring",
            "controls": "Security Controls Categories",
            "arch_views": "Security Architecture Views",
            "test_reports": "Cybersecurity Testing Reports",
            "cyber_mgmt_plan": "Cybersecurity Management Plan",
        },
        "interoperability": {
            "interop_docs": "Interoperability V&V / Risk docs",
        },
        "biocompatibility": {
            "biocomp_tests": "Biocompatibility test reports",
            "biocomp_rationale": "Biocomp rationale (if no testing)",
        },
        "sterility": {
            "steril_validation": "Sterilization Validation",
            "pkg_description": "Packaging Description & Tests",
            "shelf_life": "Shelf-life / Aging Report",
            "pyrogenicity": "Pyrogenicity Test",
        },
        "labeling": {
            "packaging_labels": "Packaging Artwork",
            "ifu": "IFU / Directions for Use",
            "extra_labeling": "Additional labeling pieces",
            "symbols_glossary": "Symbols glossary",
        },
        "literature": {
            "references": "Literature Reference PDFs",
        },
    }


@router.post("/")
async def create_performance_testing_handler(
    payload: CreatePerformanceTestingRequest,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> PerformanceTestingResponse:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )
    if not performance_test_plan:
        performance_test_plan = PerformanceTestPlan(product_id=str(product.id))

    # Check if (test_name, test_description) already exists (as (section_key, test_code))
    if any(
        (
            test.section_key == payload.test_name
            and test.test_description == payload.test_description
        )
        for test in performance_test_plan.tests
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Test with name '{payload.test_name}' and description '{payload.test_description}' already exists.",
        )

    created_performance_test_card = PerformanceTestCard(
        product_id=str(product.id),
        section_key=payload.test_name,
        test_code=payload.test_name,
        test_description=payload.test_description,
        status=payload.status.lower(),
        risk_level=payload.risk_level.lower(),
        created_by=current_user.email,
    )
    performance_test_plan.tests.append(created_performance_test_card)
    await performance_test_plan.save()
    documents = await get_performance_testing_documents(
        str(product.id),
    )
    return map_to_performance_testing_response(created_performance_test_card, documents)


@router.get("/document")
async def get_performance_testing_document_handler(
    product: Annotated[Product, Depends(get_current_product)],
) -> list[PerformanceTestingDocumentResponse]:
    performance_testing_documents = await get_performance_testing_documents(
        str(product.id),
    )
    return performance_testing_documents


@router.get("/document/upload-url")
async def get_upload_performance_testing_document_url_handler(
    file_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
    performance_testing_id: str | None = None,
) -> str:
    upload_url = await get_upload_performance_testing_document_url(
        str(product.id),
        TestingDocumentInfo(
            file_name=file_name,
            performance_testing_id=performance_testing_id,
            author=current_user.email,
        ),
    )
    return upload_url


@router.put("/document/text-input")
async def upload_performance_testing_text_input_handler(
    payload: UploadTextInputDocumentRequest,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    upload_url = await get_upload_performance_testing_document_url(
        str(product.id),
        TestingDocumentInfo(
            file_name="TextInput.txt",
            author=current_user.email,
        ),
    )
    async with httpx.AsyncClient() as client:
        await client.put(
            upload_url,
            data=payload.text,
            headers={"Content-Type": "text/plain"},
        )
    await create_audit_record(
        product,
        current_user,
        "Upload performance testing text input",
        payload.model_dump(),
    )


@router.delete("/document/{document_name}")
async def delete_performance_testing_document_handler(
    document_name: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
):
    await delete_performance_testing_document(
        str(product.id),
        document_name,
    )
    await create_audit_record(
        product,
        current_user,
        "Delete performance testing document",
        {"document_name": document_name},
    )


@router.get("/analyze-all")
async def analyze_all_performance_testings_handler(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )
    if not performance_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test plan not found for product {product.id}.",
        )
    analyze_performance_testing_task.delay(str(product.id), None)
    await create_audit_record(
        product,
        current_user,
        "Analyze all performance testing",
        {},
    )


@router.post("/analyze-all")
async def analyze_all_performance_testings_handler_post(
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )
    if not performance_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test plan not found for product {product.id}.",
        )
    analyze_performance_testing_task.delay(str(product.id), None)
    await create_audit_record(
        product,
        current_user,
        "Analyze all performance testing",
        {},
    )


@router.get("/{performance_testing_id}")
async def get_performance_testing_handler(
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
) -> PerformanceTestingResponse:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )
    if not performance_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test plan not found for product {product.id}.",
        )
    performance_test_card = next(
        (
            test
            for test in performance_test_plan.tests
            if str(test.id) == performance_testing_id
        ),
        None,
    )
    if not performance_test_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test card not found for ID {performance_testing_id}.",
        )
    documents = await get_performance_testing_documents(
        str(product.id),
    )
    return map_to_performance_testing_response(performance_test_card, documents)


@router.delete("/{performance_testing_id}")
async def delete_performance_testing_handler(
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )
    if not performance_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test plan not found for product {product.id}.",
        )
    removed_test_cards = [
        test
        for test in performance_test_plan.tests
        if str(test.id) != performance_testing_id
    ]
    if len(removed_test_cards) == len(performance_test_plan.tests):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test card with ID {performance_testing_id} not found.",
        )
    performance_test_plan.tests = removed_test_cards
    await performance_test_plan.save()
    await create_audit_record(
        product,
        current_user,
        "Delete performance testing",
        {"performance_testing_id": performance_testing_id},
    )


@router.post("/{performance_testing_id}/analyze")
async def analyze_performance_testing_handler(
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> None:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )
    if not performance_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test plan not found for product {product.id}.",
        )
    if not any(
        str(test.id) == performance_testing_id for test in performance_test_plan.tests
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test card with ID {performance_testing_id} not found.",
        )
    logger.info(
        f"Scheduling analysis for performance testing ID: {performance_testing_id}"
    )
    analyze_performance_testing_task.delay(str(product.id), performance_testing_id)
    await create_audit_record(
        product,
        current_user,
        "Analyze performance testing",
        {
            "performance_testing_id": performance_testing_id,
        },
    )
    return


@router.post("/{performance_testing_id}/accept")
async def accept_performance_testing_handler(
    payload: AcceptedPerformanceTestingRequest,
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> PerformanceTestingResponse:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )
    if not performance_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test plan not found for product {product.id}.",
        )
    performance_test_card = next(
        (
            test
            for test in performance_test_plan.tests
            if str(test.id) == performance_testing_id
        ),
        None,
    )
    if not performance_test_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test card with ID {performance_testing_id} not found.",
        )
    performance_test_card.status = ModuleStatus.ACCEPTED
    performance_test_card.accepted_justification = payload.accepted_justification
    await performance_test_plan.save()
    await create_audit_record(
        product,
        current_user,
        "Accept performance testing",
        {
            "performance_testing_id": performance_testing_id,
            "accepted_justification": performance_test_card.accepted_justification,
        },
    )
    documents = await get_performance_testing_documents(
        str(product.id),
    )
    return map_to_performance_testing_response(performance_test_card, documents)


@router.post("/{performance_testing_id}/reject")
async def reject_performance_testing_handler(
    payload: RejectedPerformanceTestingRequest,
    performance_testing_id: str,
    product: Annotated[Product, Depends(get_current_product)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[bool, Depends(check_product_edit_allowed)],
) -> PerformanceTestingResponse:
    performance_test_plan = await get_performance_test_plan(
        product_id=product.id,
    )
    if not performance_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test plan not found for product {product.id}.",
        )
    performance_test_card = next(
        (
            test
            for test in performance_test_plan.tests
            if str(test.id) == performance_testing_id
        ),
        None,
    )
    if not performance_test_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance test card with ID {performance_testing_id} not found.",
        )
    performance_test_card.status = ModuleStatus.REJECTED
    performance_test_card.rejected_justification = payload.rejected_justification
    await performance_test_plan.save()
    await create_audit_record(
        product,
        current_user,
        "Reject performance testing",
        {
            "performance_testing_id": performance_testing_id,
            "rejected_justification": payload.rejected_justification,
        },
    )
    documents = await get_performance_testing_documents(
        str(product.id),
    )
    return map_to_performance_testing_response(performance_test_card, documents)
