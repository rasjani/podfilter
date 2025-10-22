"""Main PodFilter application."""

from pathlib import Path
from typing import Dict, Any

from litestar import Litestar, Request
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from litestar.response import Template, Response
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from .database import Base, DATABASE_URL, engine
from .routes import auth, feeds, export, web


async def create_tables() -> None:
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def url_for_static_file(name: str) -> str:
    """Template function to generate static file URLs."""
    return f"/static/{name}"


async def exception_handler(request: Request, exc: HTTPException) -> Response:
    """Custom exception handler."""
    if exc.status_code == 404:
        return Template(
            template_name="404.html",
            context={"request": request},
            status_code=404
        )
    elif exc.status_code == 500:
        return Template(
            template_name="500.html", 
            context={"request": request},
            status_code=500
        )
    else:
        return Response(
            content={"detail": exc.detail},
            status_code=exc.status_code,
            media_type="application/json"
        )


# Static files configuration
static_files_router = create_static_files_router(
    path="/static",
    directories=[Path(__file__).parent / "static"]
)

# Template configuration
template_config = TemplateConfig(
    directory=Path(__file__).parent / "templates",
    engine="jinja",
)

# CORS configuration for API access
cors_config = CORSConfig(
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True
)

# Create Litestar application
app = Litestar(
    route_handlers=[
        static_files_router,
        # Web routes
        web.index,
        web.login_page,
        web.register_page,
        web.feeds_page,
        web.filters_page,
        # API routes
        auth.register,
        auth.login,
        auth.logout,
        feeds.add_feed,
        feeds.import_opml,
        feeds.list_feeds,
        feeds.add_filter_rule,
        feeds.list_filter_rules,
        feeds.delete_filter_rule,
        export.export_rss_feed,
        export.export_opml,
    ],
    template_config=template_config,
    cors_config=cors_config,
    on_startup=[create_tables],
    exception_handlers={HTTPException: exception_handler},
    debug=True,
)

# Add template globals after app creation
try:
    app.template_engine.env.globals.update({
        "url_for_static_file": url_for_static_file,
    })
except AttributeError:
    # Template engine might not be available immediately
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)