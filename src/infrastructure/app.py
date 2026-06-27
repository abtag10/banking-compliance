"""FastAPI Application Factory."""

from fastapi import FastAPI
from src.infrastructure.container import create_injector


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Banking Compliance System",
        description="DDD + Hexagonal + Clean Architecture",
        version="0.1.0",
    )

    # Create dependency injector
    injector = create_injector()

    # Get HTTP adapter and register routes
    from src.adapters.inbound.http_adapter import HTTPAdapter
    http_adapter = injector.get(HTTPAdapter)
    app.include_router(http_adapter.get_router())

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
