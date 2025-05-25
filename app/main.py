from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

api_prefix = settings.API_V1_STR or "/api"
app = FastAPI(
    title=settings.PROJECT_NAME or "Printer API",
    version=settings.VERSION or "1.0.0",
    openapi_url= f"{api_prefix}/openapi.json" if settings.DEBUG else None,
    docs_url= f"{api_prefix}/docs" if settings.DEBUG else None,
    redoc_url= f"{api_prefix}/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    if settings.DEBUG:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"{api_prefix}/docs")
    return {"message": "Printer API", "environment": settings.ENVIRONMENT}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

from app.routes.auth import router as auth

app.include_router(auth, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])

from app.routes.files import router as files

app.include_router(files, prefix=f"{settings.API_V1_STR}/files", tags=["Files"])

from app.routes.orders import router as orders

app.include_router(orders, prefix=f"{settings.API_V1_STR}/orders", tags=["Orders"])

from app.routes.stripe import router as stripe

app.include_router(stripe, prefix=f"{settings.API_V1_STR}/stripe", tags=["Stripe"])

from app.routes.user import router as user

app.include_router(user, prefix=f"{settings.API_V1_STR}/user", tags=["User"])
