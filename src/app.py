from fastapi import FastAPI
from src.infrastructure.database import init_db
from src.modules.health.router import router as health_router
from src.modules.authentication.router import router as authentication_router
from src.modules.totp.router import router as totp_router
from src.modules.user.router import router as user_router
from src.modules.email.router import router as email_router
from src.modules.company.router import router as company_router
from src.modules.support.router import router as support_router
from contextlib import asynccontextmanager
from src.environment import environment


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # Add any cleanup logic here if needed


app = FastAPI(
    title="NOIS2-192",
    description="NOIS2-192 API",
    version="1.0.0",
)
app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Application"])
async def read_root():
    return {
        "application": "NOIS2-192",
        "version": "1.0.0",
        "description": "Still in development",
    }


app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(
    authentication_router, prefix="/authentication", tags=["Authentication"]
)
app.include_router(totp_router, prefix="/totp", tags=["TOTP"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(company_router, prefix="/company", tags=["Company"])
app.include_router(support_router, prefix="/support", tags=["Support"])

if not environment.is_production:
    app.include_router(email_router, prefix="/email", tags=["Email"])
