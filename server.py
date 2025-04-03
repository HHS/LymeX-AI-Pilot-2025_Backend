import uvicorn
import os

IS_PRODUCTION = os.getenv("ENV") == "production"


def main() -> None:
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=not IS_PRODUCTION,
        workers=1,
        log_level="info",
    )

if __name__ == "__main__":
    main()
