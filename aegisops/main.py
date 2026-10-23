from fastapi import FastAPI

import aegisops.models  # noqa: F401
from aegisops.api.routes import router
from aegisops.config import settings
from aegisops.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title=settings.app_name,
    description=(
        "Network reliability, observability, "
        "and incident response toolkit."
    ),
    version="0.1.0",
)

app.include_router(router)


@app.get("/", tags=["General"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "environment": settings.environment,
    }
