from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import router as sales_router

app = FastAPI(
    title="NeoVerse Sales Intelligence",
    description="AI-powered Sales Conversation Intelligence API",
    version="1.0.0",
)

# Enable CORS so the React frontend (including dev server) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this to ["http://localhost:5173", "http://127.0.0.1:8000"] if you like
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(sales_router)

# Frontend setup
templates = Jinja2Templates(directory="frontend")
# Mount the assets directory created by Vite
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

# SPA Catch-all route (must be defined last!)
@app.get("/{full_path:path}", response_class=HTMLResponse)
def serve_spa(request: Request, full_path: str):
    # If the request is for an API route, don't serve the React app
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    return templates.TemplateResponse("index.html", {"request": request})
