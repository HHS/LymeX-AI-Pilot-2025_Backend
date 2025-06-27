import json
from time import time
from typing import Callable
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from src.infrastructure.database import init_db
from src.modules.health.router import router as health_router
from src.modules.authentication.router import router as authentication_router
from src.modules.totp.router import router as totp_router
from src.modules.user.router import router as user_router
from src.modules.email.router import router as email_router
from src.modules.company.router import router as company_router
from src.modules.product.router import router as product_router
from src.modules.support.router import router as support_router
from src.modules.system_data.router import router as system_data_router
from src.modules.dashboard.router import router as dashboard_router
from src.modules.search_bar.router import router as search_bar_router
from contextlib import asynccontextmanager
from src.environment import environment
from fastapi.exceptions import RequestValidationError
from loguru import logger


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


def friendly_message(error):
    type_ = error.get("type", "")
    field = error.get("loc", [""])[-1]

    if type_ == "value_error.email":
        return "Email format is invalid"
    elif type_ == "value_error.any_str.min_length":
        min_len = error["ctx"].get("limit_value")
        return f"{field.capitalize()} must be at least {min_len} characters"
    elif type_ == "value_error.missing":
        return f"{field.capitalize()} is required"
    else:
        return error["msg"]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    friendly_messages = []

    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        issue = friendly_message(error)
        details.append({"field": field, "issue": issue})
        friendly_messages.append(f"Field {field}: {issue}")

    summary_message = "; ".join(friendly_messages)
    response = {
        "success": False,
        "data": None,
        "error": {
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "One or more fields are invalid.",
            "details": details,
        },
        "message": summary_message,
    }
    logger.error(f"Validation error")
    logger.error(json.dumps(response, indent=2))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(response),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "success": False,
                "data": None,
                "error": {
                    "code": exc.status_code,
                    "message": "One or more fields are invalid.",
                    "details": exc.detail,
                },
                "message": exc.detail,
            }
        ),
    )


class SuccessResponseWrapper(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        # Only wrap JSON responses (status code 200–299)
        if (
            200 <= response.status_code < 300
            and response.headers.get("content-type") == "application/json"
            and request.url.path != "/openapi.json"
        ):
            body = [section async for section in response.body_iterator]
            original_data = json.loads(b"".join(body).decode("utf-8"))
            new_body = {
                "success": True,
                "data": original_data,
                "error": None,
                "message": "OK",
            }
            return JSONResponse(content=new_body, status_code=response.status_code)
        return response


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        begin_time = time()
        body = await request.body()
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Handle body logging based on content type
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            logger.info(f"Body: [Multipart form data - {len(body)} bytes]")
        elif body:
            try:
                logger.info(f"Body: {body.decode('utf-8')}")
            except UnicodeDecodeError:
                logger.info(f"Body: [Binary data - {len(body)} bytes]")
        else:
            logger.info("Body: No Body")

        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        end_time = time()
        duration = end_time - begin_time
        logger.info(f"Request duration: {duration:.2f} seconds")
        return response


app.add_middleware(SuccessResponseWrapper)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LogRequestMiddleware)


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
app.include_router(product_router, prefix="/product", tags=["Product"])
app.include_router(support_router, prefix="/support", tags=["Support"])
app.include_router(system_data_router, prefix="/system-data", tags=["System Data"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(search_bar_router, prefix="/search", tags=["Search"])

if not environment.is_production:
    app.include_router(email_router, prefix="/email", tags=["Email"])
