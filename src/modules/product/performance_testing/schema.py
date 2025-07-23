from __future__ import annotations

import enum
from datetime import date, datetime
from typing import List, Literal

from pydantic import BaseModel, Field

from src.modules.product.analyzing_status import AnalyzingStatus


class RiskLevel(str, enum.Enum):
    """Overall risk assessment for a test or group of tests."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModuleStatus(str, enum.Enum):
    """Lifecycle state for the entire performance‑testing module."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"


class PerformanceTestingSection(str, enum.Enum):
    """
    Canonical keys for each sub-section.  Keeping the names **exactly**
    in sync with the attribute names in PerformanceTestingDocument.
    """

    ANALYTICAL = "analytical"
    COMPARISON = "comparison"
    CLINICAL = "clinical"
    ANIMAL_TESTING = "animal_testing"
    EMC_SAFETY = "emc_safety"
    WIRELESS = "wireless"
    SOFTWARE = "software"
    INTEROPERABILITY = "interoperability"
    BIOCOMPATIBILITY = "biocompatibility"
    STERILITY = "sterility"
    SHELF_LIFE = "shelf_life"
    CYBERSECURITY = "cybersecurity"


class PerfTestingDocumentResponse(BaseModel):
    """
    Tiny DTO used by storage.py to return a single presigned URL.
    """

    url: str


class PerformanceTestingDocumentResponse(BaseModel):
    document_name: str = Field(
        ..., description="Name of the performance testing document"
    )
    file_name: str = Field(..., description="Name of the document")
    url: str = Field(..., description="URL to access the document")
    uploaded_at: str = Field(
        ..., description="Date and time when the document was uploaded"
    )
    author: str = Field(..., description="Author of the document")
    content_type: str = Field(
        ..., description="Content type of the document (e.g., PDF, DOCX)"
    )
    size: int = Field(..., description="Size of the document in bytes")


# ------------------------------ Primitive nested objects – reused by multiple sub‑schemas ------------------------------


class AttachmentRef(BaseModel):
    """Reference to a file stored in the vector DB / S3 bucket etc."""

    id: str
    description: str | None = None


class PageRef(BaseModel):
    """Explicit page references for traceability."""

    page: int
    comment: str | None = None


# Wireless‑specific helper
class WirelessFunction(BaseModel):
    name: str
    risk_tier: Literal["a", "b", "c"]


# Interoperability‑specific helper
class ElectronicInterface(BaseModel):
    name: str
    purpose: str
    status: Literal["active", "service", "inactive"]


# Biocompatibility‑specific helper
class BioMaterial(BaseModel):
    name: str
    tissue_type: Literal[
        "circulating_blood",
        "blood_path",
        "bone",
        "breast_milk",
        "dentin",
        "gas_mucosa",
        "communicating_mucosa",
        "contacting_skin",
    ]
    exposure_duration: Literal["≤24h", ">24h ≤30d", ">30d"]


# Sterility‑specific helper
class SterilizationMethod(BaseModel):
    method_name: str
    parameters_summary: str | None = None


# ------------------------------ 1. Analytical studies ------------------------------


class AnalyticalStudy(BaseModel):
    study_type: Literal[
        "precision",
        "linearity",
        "sensitivity",
        "measuring_range",
        "cut_off",
        "traceability",
        "stability",
        "usability",
        "other",
    ]
    performed: bool = False
    attachments: List[AttachmentRef] = Field([])
    pages: List[PageRef] = Field([])
    confidence: float | None = None

    product_name: str | None = None
    product_identifier: str | None = None
    protocol_id: str | None = None
    objective: str | None = None
    specimen_description: str | None = None
    specimen_collection: str | None = None
    samples_replicates_sites: str | None = None
    positive_controls: str | None = None
    negative_controls: str | None = None
    calibration_requirements: str | None = None
    assay_steps: str | None = None
    data_analysis_plan: str | None = None
    statistical_analysis_plan: str | None = None
    acceptance_criteria: str | None = None
    consensus_standards: str | None = None

    deviations: str | None = None
    discussion: str | None = None
    conclusion: str | None = None

    key_results: str | None = None


# ------------------------------ 2. Comparison studies ------------------------------


class ComparisonStudy(BaseModel):
    study_type: Literal["method", "matrix"]
    performed: bool = False
    attachments: List[AttachmentRef] = Field([])
    comparator_device_k_number: str | None = None
    summary: str | None = None
    confidence: float | None = None


# ------------------------------ 3. Clinical studies ------------------------------


class ClinicalStudy(BaseModel):
    sensitivity: float | None = None
    specificity: float | None = None
    clinical_cut_off: str | None = None
    pro_included: bool | None = None
    ppi_included: bool | None = None
    attachments: List[AttachmentRef] = Field([])
    summary: str | None = None
    confidence: float | None = None


# ------------------------------ 4. Animal testing (GLP) ------------------------------


class AnimalTesting(BaseModel):
    glp_compliant: bool | None = None
    justification_if_not_glp: str | None = None
    attachments: List[AttachmentRef] = Field([])
    confidence: float | None = None


# ------------------------------ 5. EMC / Electrical / Mechanical / Thermal safety ------------------------------


class EMCSafety(BaseModel):
    num_dut: int | None = None
    worst_harm: Literal["death_serious", "non_serious", "no_harm"] | None = None
    iec_edition: str | None = None
    asca: bool | None = None
    essential_performance: List[str] = Field([])
    pass_fail_pages: List[PageRef] = Field([])
    degradations_observed: str | None = None
    allowances: str | None = None
    deviations: str | None = None
    final_version_tested: bool | None = None
    attachments: List[AttachmentRef] = Field([])
    confidence: float | None = None


# ------------------------------ 6. Wireless coexistence ------------------------------


class WirelessCoexistence(BaseModel):
    functions: List[WirelessFunction] = Field([])
    coexistence_tier_met: bool | None = None
    fwp_summary: str | None = None
    eut_exposed: bool | None = None
    fwp_maintained: bool | None = None
    risk_mitigations_pages: List[PageRef] = Field([])
    attachments: List[AttachmentRef] = Field([])
    confidence: float | None = None


# 7. ------------------------------ Software & cyber‑security performance ------------------------------


class SoftwarePerformance(BaseModel):
    contains_software: bool | None = None
    digital_health: bool | None = None
    documentation_level: str | None = None
    architecture_views_present: bool | None = None
    unresolved_anomalies_attachment: AttachmentRef | None = None
    sbom_attachment: AttachmentRef | None = None
    risk_assessment_attachment: AttachmentRef | None = None
    patch_plan_pages: List[PageRef] = Field([])
    confidence: float | None = None


# ------------------------------ 8. Interoperability ------------------------------


class Interoperability(BaseModel):
    interfaces: List[ElectronicInterface] | None = None
    risk_assessment_attachment: AttachmentRef | None = None
    labeling_pages: List[PageRef] | None = None
    confidence: float | None = None


# ------------------------------ 9. Biocompatibility ------------------------------


class Biocompatibility(BaseModel):
    tissue_contacting: bool | None = None
    components: List[BioMaterial] | None = None
    repeat_exposure: bool | None = None
    test_reports: List[AttachmentRef] | None = None
    rationale_if_no_test: str | None = None
    confidence: float | None = None


# ------------------------------ 10. Sterility validation ------------------------------


class SterilityValidation(BaseModel):
    packaged_as_sterile: bool | None = None
    methods: List[SterilizationMethod] | None = None
    sal: str | None = None
    validation_method: str | None = None
    pyrogenicity_test: bool | None = None
    packaging_description: str | None = None
    modifications_warning_confirmed: bool | None = None
    attachments: List[AttachmentRef] = Field([])
    confidence: float | None = None


# ------------------------------ 11. Shelf‑life / accelerated aging ------------------------------


class ShelfLife(BaseModel):
    assessed_before: bool | None = None
    proposed_shelf_life_months: int | None = None
    attachments: List[AttachmentRef] = Field([])
    rationale_if_no_test: str | None = None
    confidence: float | None = None


# ------------------------------ 12. Cyber‑security (separate from SW performance as per questionnaire) ------------------------------


class CyberSecurity(BaseModel):
    threat_model_attachment: AttachmentRef | None = None
    sbom_attachment: AttachmentRef | None = None
    architecture_views_present: bool | None = None
    risk_assessment_attachment: AttachmentRef | None = None
    patch_plan_pages: List[PageRef] = Field([])
    eol_support_doc_attachment: AttachmentRef | None = None
    security_controls_pages: List[PageRef] = Field([])
    confidence: float | None = None


# ------------------------------ Aggregate document – what gets persisted in the DB ------------------------------


class PerformanceTestingResponse(BaseModel):
    id: str
    product_id: str
    analytical: List[AnalyticalStudy] = Field([])
    comparison: List[ComparisonStudy] = Field([])
    clinical: List[ClinicalStudy] = Field([])
    animal_testing: AnimalTesting | None = None
    emc_safety: EMCSafety | None = None
    wireless: WirelessCoexistence | None = None
    software: SoftwarePerformance | None = None
    interoperability: Interoperability | None = None
    biocompatibility: Biocompatibility | None = None
    sterility: SterilityValidation | None = None
    shelf_life: ShelfLife | None = None
    cybersecurity: CyberSecurity | None = None
    overall_risk_level: RiskLevel | None = None
    status: ModuleStatus = ModuleStatus.PENDING
    missing_items: List[str] = Field([])


class AnalyzePerformanceTestingProgressResponse(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(
        ..., description="Number of files that have been processed"
    )
    updated_at: datetime = Field(
        ..., description="Date and time when the progress was last updated"
    )
    analyzing_status: AnalyzingStatus = Field(
        ..., description="Current status of the product analysis"
    )


class UploadTextInputDocumentRequest(BaseModel):
    text: str = Field(..., description="Text input for the document")
