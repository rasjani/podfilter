"""Main PodFilter application."""

from pathlib import Path
from typing import Dict, Any

from litestar import Litestar, Request, get
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from litestar.response import Template, Response
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from .database import Base, DATABASE_URL, engine
from .routes import auth, feeds
from .routes import auth, feeds


async def create_tables() -> None:
  """Create database tables."""
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


@get("/")
async def homepage(request: Request) -> Response:
  """Simple homepage for testing."""
  html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PodFilter</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Welcome to PodFilter</h1>
            <p>Podcast feed filtering service</p>
            <a href="/register" class="btn btn-primary">Register</a>
            <a href="/login" class="btn btn-outline-primary">Login</a>
        </div>
    </body>
    </html>
    """
  return Response(content=html_content, media_type="text/html")


@get("/login")
async def login_page(request: Request) -> Response:
  """Login page."""
  html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - PodFilter</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h4>Login to PodFilter</h4>
                        </div>
                        <div class="card-body">
                            <form id="loginForm">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Username</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Login</button>
                            </form>
                            <div class="text-center mt-3">
                                <p>Don't have an account? <a href="/register">Register here</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    localStorage.setItem('access_token', result.access_token);
                    window.location.href = '/dashboard';
                } else {
                    const error = await response.json();
                    alert(error.detail || 'Login failed');
                }
            } catch (error) {
                alert('Login failed: ' + error.message);
            }
        });
        </script>
    </body>
    </html>
    """
  return Response(content=html_content, media_type="text/html")


@get("/dashboard")
async def dashboard(request: Request) -> Response:
  """Dashboard page for authenticated users."""
  html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - PodFilter</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">PodFilter</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="#" onclick="logout()">Logout</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <h1>Welcome to your Dashboard!</h1>
            <p class="lead">Manage your podcast feeds and filtering rules.</p>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-primary" onclick="showAddFeedModal()">Add RSS Feed</button>
                            <button class="btn btn-outline-secondary ms-2" onclick="showImportOPML()">Import OPML</button>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Your Activity</h5>
                        </div>
                        <div class="card-body">
                            <p>No feeds added yet. <a href="#" onclick="showAddFeedModal()">Add your first feed!</a></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function logout() {
            localStorage.removeItem('access_token');
            window.location.href = '/';
        }
        
        async function showAddFeedModal() {
            const url = prompt('Enter RSS feed URL:');
            if (url) {
                try {
                    const response = await fetch('/api/feeds', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                        },
                        body: JSON.stringify({url: url})
                    });
                    
                    if (response.ok) {
                        alert('Feed added successfully!');
                        location.reload();
                    } else {
                        const error = await response.json();
                        alert('Failed to add feed: ' + (error.detail || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Failed to add feed: ' + error.message);
                }
            }
        }
        
        function showImportOPML() {
            alert('OPML import functionality coming soon!');
        }
        
        // Load feeds on page load
        async function loadFeeds() {
            try {
                const response = await fetch('/api/feeds', {
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });
                
                if (response.ok) {
                    const feeds = await response.json();
                    const activityDiv = document.querySelector('.card-body p');
                    if (feeds.length > 0) {
                        activityDiv.innerHTML = `You have ${feeds.length} feed(s). <a href="#" onclick="listFeeds()">View all feeds</a>`;
                    }
                }
            } catch (error) {
                console.error('Failed to load feeds:', error);
            }
        }
        
        async function listFeeds() {
            try {
                const response = await fetch('/api/feeds', {
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });
                
                if (response.ok) {
                    const feeds = await response.json();
                    let feedList = '<h5>Your Feeds:</h5><ul>';
                    feeds.forEach(feed => {
                        feedList += `<li><strong>${feed.title}</strong><br><small>${feed.original_url}</small></li>`;
                    });
                    feedList += '</ul>';
                    
                    const activityCard = document.querySelector('.card-body');
                    activityCard.innerHTML = feedList;
                }
            } catch (error) {
                alert('Failed to load feeds: ' + error.message);
            }
        }
        
        // Load feeds when page loads
        document.addEventListener('DOMContentLoaded', loadFeeds);
        </script>
    </body>
    </html>
    """
  return Response(content=html_content, media_type="text/html")


async def register_page(request: Request) -> Response:
  """Registration page."""
  html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - PodFilter</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h4>Register for PodFilter</h4>
                        </div>
                        <div class="card-body">
                            <form id="registerForm">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Username</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                </div>
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email</label>
                                    <input type="email" class="form-control" id="email" name="email" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Register</button>
                            </form>
                            <div class="text-center mt-3">
                                <p>Already have an account? <a href="/login">Login here</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Registration successful! Please login.');
                    window.location.href = '/login';
                } else {
                    const error = await response.json();
                    alert(error.detail || 'Registration failed');
                }
            } catch (error) {
                alert('Registration failed: ' + error.message);
            }
        });
        </script>
    </body>
    </html>
    """
  return Response(content=html_content, media_type="text/html")


# Static files configuration
static_files_router = create_static_files_router(path="/static", directories=[Path(__file__).parent / "static"])

# CORS configuration for API access
cors_config = CORSConfig(
  allow_origins=["*"], allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["*"], allow_credentials=True
)

# Create Litestar application
app = Litestar(
  route_handlers=[
    static_files_router,
    homepage,
    login_page,
    dashboard,
    # API routes
    auth.register,
    auth.login,
    auth.logout,
  ],
  cors_config=cors_config,
  on_startup=[create_tables],
  debug=True,
)


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
