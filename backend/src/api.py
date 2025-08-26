#!/usr/bin/env python3
"""
Polyglot Meeting Assistant - FastAPI Backend

Clean API backend for React frontend integration.
"""

import os
import sys
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from models.search import MeetingSearchEngine
from models.asr import WhisperASR
from models.nlp import NLPProcessor
from session_manager import SessionManager

# Pydantic models for API
class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    content_types: Optional[List[str]] = None

class SearchResult(BaseModel):
    meeting_id: str
    meeting_title: str
    meeting_date: str
    content_type: str
    text: str
    participants: List[str]
    relevance_score: float
    snippet: str

class UploadResponse(BaseModel):
    success: bool
    message: str
    meeting_id: Optional[str] = None
    filename: Optional[str] = None

class StatisticsResponse(BaseModel):
    total_documents: int
    total_meetings: int
    content_type_distribution: Dict[str, int]
    index_size_mb: float
    embedding_dimension: int
    model_name: str

# Initialize components
search_engine = None
asr_processor = None
nlp_processor = None
session_manager = None

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    global search_engine, asr_processor, nlp_processor, session_manager
    
    print("🚀 Starting Polyglot Meeting Assistant API...")
    
    try:
        # Initialize search engine
        search_engine = MeetingSearchEngine()
        print("✅ Search engine initialized")
        
        # Initialize ASR processor
        asr_processor = WhisperASR()
        print("✅ ASR processor initialized")
        
        # Initialize NLP processor
        nlp_processor = NLPProcessor()
        print("✅ NLP processor initialized")
        
        # Initialize session manager
        session_manager = SessionManager()
        print("✅ Session manager initialized")
        
        # Set global variables for routes
        import api.routes
        api.routes.asr_processor = asr_processor
        api.routes.nlp_processor = nlp_processor
        api.routes.search_engine = search_engine
        api.routes.session_manager = session_manager
        
        print("🎉 API ready!")
        
        # Add a small delay to ensure everything is properly initialized
        import time
        time.sleep(1)
        print("✅ All components initialized and ready to serve requests!")
        
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    print("🛑 Shutting down Polyglot Meeting Assistant API...")

# Initialize FastAPI app
app = FastAPI(
    title="Polyglot Meeting Assistant API",
    description="AI-powered meeting search and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
from api.routes import router as api_router
app.include_router(api_router)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Polyglot Meeting Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "search_engine": search_engine is not None,
        "asr_processor": asr_processor is not None,
        "nlp_processor": nlp_processor is not None,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a meeting file"""
    try:
        # Validate file type
        allowed_types = [
            "audio/", "video/", "text/", 
            "application/pdf", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if not any(file.content_type.startswith(t) for t in allowed_types):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Save file temporarily
        file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process file based on type
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
            # Audio file - for now, return placeholder
            transcript = f"[Audio file: {file.filename}] - Processing audio files requires additional setup."
        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            # Video file - for now, return placeholder
            transcript = f"[Video file: {file.filename}] - Processing video files requires additional setup."
        else:
            # Text file
            with open(file_path, "r", encoding="utf-8") as f:
                transcript = f.read()
        
        # Process with NLP
        if nlp_processor and transcript:
            analysis = nlp_processor.generate_comprehensive_summary(transcript)
        else:
            analysis = {
                "summary": transcript[:200] + "..." if len(transcript) > 200 else transcript,
                "action_items": [],
                "key_decisions": [],
                "timelines": [],
                "participants": []
            }
        
        # Add to search index
        meeting_data = {
            "id": str(uuid.uuid4()),
            "title": file.filename,
            "date": datetime.now().isoformat(),
            "transcript": transcript,
            "summary": analysis.get("summary", ""),
            "action_items": analysis.get("action_items", []),
            "key_decisions": analysis.get("key_decisions", []),
            "timelines": analysis.get("timelines", []),
            "participants": analysis.get("participants", [])
        }
        
        if search_engine:
            success = search_engine.add_meeting(meeting_data)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to index meeting")
        else:
            raise HTTPException(status_code=503, detail="Search engine not available")
        
        # Clean up uploaded file
        file_path.unlink()
        
        return UploadResponse(
            success=True,
            message="File uploaded and processed successfully",
            meeting_id=meeting_data["id"],
            filename=file.filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_meetings(request: SearchRequest):
    """Search across all indexed meetings"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not available")
    
    try:
        results = search_engine.search(
            request.query, 
            top_k=request.top_k, 
            content_types=request.content_types
        )
        
        # Convert to Pydantic models
        search_results = []
        for result in results:
            search_results.append(SearchResult(**result))
        
        return {
            "query": request.query,
            "total_results": len(search_results),
            "results": search_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings")
async def list_meetings():
    """List all indexed meetings"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not available")
    
    try:
        stats = search_engine.get_search_statistics()
        return {
            "total_meetings": stats.get("total_meetings", 0),
            "total_documents": stats.get("total_documents", 0),
            "content_distribution": stats.get("content_type_distribution", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", response_model=StatisticsResponse)
async def get_stats():
    """Get search engine statistics"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not available")
    
    try:
        stats = search_engine.get_search_statistics()
        return StatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export")
async def export_results(q: str, format: str = "json"):
    """Export search results"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not available")
    
    try:
        results = search_engine.search(q, top_k=100)
        
        if format == "json":
            return {"query": q, "results": results}
        elif format == "csv":
            # TODO: Implement CSV export
            raise HTTPException(status_code=501, detail="CSV export not implemented yet")
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
