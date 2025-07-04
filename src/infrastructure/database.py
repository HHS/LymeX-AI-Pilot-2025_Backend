from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from src.infrastructure.init.init_email_template_data import init_email_template_data
from src.infrastructure.init.init_system_admin_user import init_system_admin_user
from src.modules.product.clinical_trial.model import ClinicalTrial
from src.modules.product.feature_status.model import FeaturesStatus
from src.modules.product.performance_testing.model import PerformanceTesting
from src.modules.product.regulatory_pathway.model import RegulatoryPathway
from src.modules.product.test_comparison.model import (
    TestComparison,
)
from src.modules.product.version_control.model import ProductVersionControl
from src.modules.product.claim_builder.model import (
    AnalyzeClaimBuilderProgress,
    ClaimBuilder,
)
from src.modules.product.product_profile.model import (
    AnalyzeProductProfileProgress,
    ProductProfile,
    ProductProfileAudit,
)
from src.modules.product.competitive_analysis.model import (
    CompetitiveAnalysis,
    AnalyzeCompetitiveAnalysisProgress,
)
from src.modules.product.cost_estimation.model import CostEstimation
from src.modules.product.review_program.model import ReviewProgram
from src.modules.product.models import Product
from src.modules.company.models import Company, CompanyMember
from src.modules.totp.models import UserTotp
from src.modules.user.models import User
from src.modules.email.models import EmailTemplate
from src.environment import environment
from src.modules.product.milestone_planning.model import MilestonePlanning
from src.modules.product.custom_test_plan.model import CustomTestPlan
from src.modules.notification.model import Notification
from src.modules.checklist.master_checklist_model import MasterChecklist
from src.modules.checklist.model import Checklist
from src.modules.product.regulatory_background.model import RegulatoryBackground

client = AsyncIOMotorClient(environment.mongo_uri)
db = client[environment.mongo_db]


async def init_db() -> None:
    logger.info("Initializing database connection...")
    await init_beanie(
        database=db,
        document_models=[
            User,
            EmailTemplate,
            UserTotp,
            Company,
            CompanyMember,
            Product,
            CompetitiveAnalysis,
            AnalyzeCompetitiveAnalysisProgress,
            ProductProfile,
            ProductProfileAudit,
            AnalyzeProductProfileProgress,
            ClaimBuilder,
            AnalyzeClaimBuilderProgress,
            ProductVersionControl,
            PerformanceTesting,
            TestComparison,
            ClinicalTrial,
            RegulatoryPathway,
            FeaturesStatus,
            MilestonePlanning,
            CostEstimation,
            ReviewProgram,
            CustomTestPlan,
            Notification,
            MasterChecklist,
            Checklist,
            RegulatoryBackground,
        ],
    )
    logger.info(
        "Database connection initialized successfully. Initializing email templates..."
    )
    await init_email_template_data()
    logger.info("Email templates initialized successfully.")
    await init_system_admin_user()
    logger.info("System admin user initialized successfully.")
    logger.info("Database initialization complete.")
