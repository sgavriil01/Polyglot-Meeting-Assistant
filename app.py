import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, File, UploadFile, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add backend src to path
sys.path.append(str(Path("backend/src")))

# Import backend components
from api.routes import router as api_router
from models.asr import WhisperASR
from models.nlp import NLPProcessor
from models.search import MeetingSearchEngine
from session_manager import SessionManager

# Create FastAPI app
app = FastAPI(title="Polyglot Meeting Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend components
asr_processor = None
nlp_processor = None
search_engine = None
session_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize backend components on startup"""
    global asr_processor, nlp_processor, search_engine, session_manager
    
    print("🚀 Initializing Polyglot Meeting Assistant...")
    
    try:
        # Initialize components
        asr_processor = WhisperASR()
        nlp_processor = NLPProcessor()
        search_engine = MeetingSearchEngine()
        session_manager = SessionManager()
        
        print("✅ All components initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing components: {e}")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Serve React app
build_path = Path("frontend/build")
if build_path.exists():
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(build_path / "static")), name="static")
    
    @app.get("/")
    async def serve_react_app():
        """Serve the React app"""
        return FileResponse(str(build_path / "index.html"))
    
    @app.get("/{path:path}")
    async def serve_react_routes(path: str):
        """Serve React routes"""
        # Check if it's a static file
        static_file = build_path / path
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        
        # Otherwise serve index.html for React routing
        return FileResponse(str(build_path / "index.html"))
else:
    print("❌ React build directory not found!")
    
    @app.get("/")
    async def fallback():
        return {"message": "React app not found. Please build the frontend first."}

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Polyglot Meeting Assistant is running",
        "components": {
            "asr": asr_processor is not None,
            "nlp": nlp_processor is not None,
            "search": search_engine is not None,
            "session_manager": session_manager is not None
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
