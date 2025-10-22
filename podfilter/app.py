"""Main PodFilter application."""

from pathlib import Path

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from litestar.contrib.jinja import JinjaTemplateEngine

from .database import Base, engine
from .routes import auth, export, feeds, web


async def create_tables() -> None:
  """Create database tables."""
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


static_files_router = create_static_files_router(path="/static", directories=[Path(__file__).parent / "static"])

cors_config = CORSConfig(
  allow_origins=["*"],
  allow_methods=["GET", "POST", "PUT", "DELETE"],
  allow_headers=["*"],
  allow_credentials=True,
)

route_handlers = [
  static_files_router,
  # Web routes
  web.index,
  web.login_page,
  web.register_page,
  web.feeds_page,
  web.filters_page,
  # Authentication routes
  auth.register,
  auth.login,
  auth.logout,
  # Feed management routes
  feeds.add_feed,
  feeds.import_opml,
  feeds.list_feeds,
  feeds.add_filter_rule,
  feeds.list_filter_rules,
  feeds.delete_filter_rule,
  # Export routes
  export.export_rss_feed,
  export.export_opml,
]

template_config = TemplateConfig(
  directory=Path(__file__).parent / "templates",
  engine=JinjaTemplateEngine,
)

app = Litestar(
  route_handlers=route_handlers,
  cors_config=cors_config,
  on_startup=[create_tables],
  template_config=template_config,
  debug=True,
)


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
