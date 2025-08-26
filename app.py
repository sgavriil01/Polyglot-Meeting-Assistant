import os
import sys
from pathlib import Path
from datetime import datetime

# Set up cache directory with proper permissions BEFORE importing any AI models
cache_dir = os.path.join(os.getcwd(), ".cache")
os.makedirs(cache_dir, exist_ok=True)

# Create subdirectories with proper permissions
whisper_cache = os.path.join(cache_dir, "whisper")
transformers_cache = os.path.join(cache_dir, "huggingface")
os.makedirs(whisper_cache, exist_ok=True)
os.makedirs(transformers_cache, exist_ok=True)

# Set permissions recursively
import stat
for root, dirs, files in os.walk(cache_dir):
    for d in dirs:
        os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    for f in files:
        os.chmod(os.path.join(root, f), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

os.environ["TRANSFORMERS_CACHE"] = cache_dir
os.environ["HF_HOME"] = cache_dir
os.environ["XDG_CACHE_HOME"] = cache_dir
os.environ["WHISPER_CACHE_DIR"] = cache_dir
print(f"📁 Cache directory set to: {cache_dir}")
print(f"📁 Whisper cache: {whisper_cache}")
print(f"📁 Transformers cache: {transformers_cache}")

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
        # Initialize components with timeout handling
        print("🔄 Loading Whisper ASR model...")
        asr_processor = WhisperASR()
        print("✅ Whisper loaded")
        
        print("🔄 Loading NLP models...")
        nlp_processor = NLPProcessor()
        print("✅ NLP models loaded")
        
        print("🔄 Initializing search engine...")
        search_engine = MeetingSearchEngine()
        print("✅ Search engine ready")
        
        print("🔄 Setting up session manager...")
        session_manager = SessionManager()
        print("✅ Session manager ready")
        
        # Set global instances in api.routes for dependency injection
        api_router.asr_processor = asr_processor
        api_router.nlp_processor = nlp_processor
        api_router.search_engine = search_engine
        api_router.session_manager = session_manager
        
        print("✅ All components initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        import traceback
        traceback.print_exc()

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

# Simple status check
@app.get("/status")
async def status_check():
    """Simple status check that doesn't require AI models"""
    return {
        "status": "running",
        "message": "Server is responding",
        "timestamp": str(datetime.now())
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
