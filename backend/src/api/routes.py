"""
API Routes for Polyglot Meeting Assistant

This module contains all the FastAPI route handlers for the meeting assistant API.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import tempfile
import uuid
import json
from datetime import datetime
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from pydantic import BaseModel

from models.asr import WhisperASR
from models.nlp import NLPProcessor
from models.search import MeetingSearchEngine
from session_manager import SessionManager
from utils.language_detection import detect_text_language, get_language_name

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    content_types: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    participants: Optional[List[str]] = None
    min_relevance: Optional[float] = None

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
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[List[Dict]] = None
    language: Optional[str] = None

class StatisticsResponse(BaseModel):
    total_documents: int
    total_meetings: int
    content_type_distribution: Dict[str, int]
    index_size_mb: float
    embedding_dimension: int
    model_name: str
    session_id: Optional[str] = None
    session_meetings: Optional[int] = None

# Create router
router = APIRouter(prefix="/api/v1", tags=["meetings"])

# Global variables for model instances (will be set by dependency injection)
asr_processor: Optional[WhisperASR] = None
nlp_processor: Optional[NLPProcessor] = None
search_engine: Optional[MeetingSearchEngine] = None
session_manager: Optional[SessionManager] = None

def get_asr_processor() -> WhisperASR:
    """Get cached ASR processor instance"""
    global asr_processor
    if asr_processor is None:
        # Initialize cached singleton instance
        asr_processor = WhisperASR(model_size="base")
    return asr_processor

def get_nlp_processor() -> NLPProcessor:
    """Get cached NLP processor instance"""
    global nlp_processor
    if nlp_processor is None:
        # Initialize cached singleton instance
        nlp_processor = NLPProcessor()
    return nlp_processor

def get_search_engine() -> MeetingSearchEngine:
    if search_engine is None:
        raise HTTPException(
            status_code=503, 
            detail="Search engine not initialized. Please wait a moment and try again."
        )
    return search_engine

def get_session_manager() -> SessionManager:
    if session_manager is None:
        raise HTTPException(
            status_code=503, 
            detail="Session manager not initialized. Please wait a moment and try again."
        )
    return session_manager

def get_or_create_session(request: Request, session_mgr: SessionManager = Depends(get_session_manager)) -> str:
    """Get existing session ID from cookies, headers, or create new one"""
    # Debug: Print all request info
    print(f"🔍 Session debug:")
    print(f"   Cookies: {dict(request.cookies)}")
    print(f"   Headers: {dict(request.headers)}")
    
    # Try to get session from multiple sources
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = request.headers.get("X-Session-ID")
    if not session_id:
        session_id = request.query_params.get("session_id")
    
    print(f"🔍 Session lookup - ID: {session_id[:8] if session_id else 'None'}...")
    
    if not session_id or not session_mgr.get_session(session_id):
        # Create new session
        session_id = session_mgr.create_session()
        print(f"🆕 Created new session: {session_id[:8]}...")
    else:
        print(f"✅ Using existing session: {session_id[:8]}...")
    
    return session_id

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/sessions/info")
async def get_sessions_info(session_mgr: SessionManager = Depends(get_session_manager)):
    """Get information about all sessions (for debugging)"""
    return session_mgr.get_all_sessions_info()

@router.post("/sessions/clear-all")
async def clear_all_sessions(session_mgr: SessionManager = Depends(get_session_manager)):
    """Clear all sessions and search indexes (for testing/maintenance)"""
    success = session_mgr.clear_all_sessions()
    return {
        "success": success,
        "message": "All sessions cleared" if success else "Failed to clear sessions"
    }

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    asr: WhisperASR = Depends(get_asr_processor),
    nlp: NLPProcessor = Depends(get_nlp_processor),
    search: MeetingSearchEngine = Depends(get_search_engine),
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Upload and process audio or text files
    
    Supports: mp3, wav, m4a, ogg, flac, txt, md
    Languages: 100+ languages supported including English, Spanish, French, German, Chinese, etc.
    """
    start_time = time.time()
    
    # Validate file type
    audio_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
    text_extensions = {'.txt', '.md', '.rtf'}
    allowed_extensions = audio_extensions | text_extensions
    
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (50MB limit)
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 50MB allowed.")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            # Read and write file content
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Get or create session
        session_id = get_or_create_session(request, session_mgr)
        meeting_id = str(uuid.uuid4())
        
        # Process file based on type
        transcript_text = ""
        language = "unknown"
        duration = 0
        
        if file_extension in audio_extensions:
            # Process audio with ASR
            print(f"🎙️ Transcribing audio: {file.filename}")
            transcription_result = asr.transcribe(tmp_path)
            transcript_text = transcription_result["text"]
            language = transcription_result.get("language", "unknown")
            duration = transcription_result.get("duration", 0)
            
            # Also analyze the transcribed text for additional language detection
            if transcript_text and len(transcript_text.strip()) > 20:
                text_language_result = detect_text_language(transcript_text)
                text_detected_lang = text_language_result.get('language', 'unknown')
                text_confidence = text_language_result.get('confidence', 0.0)
                
                # If text detection has higher confidence and different result, log both
                if text_detected_lang != language and text_confidence > 0.8:
                    print(f"🌍 Whisper detected: {get_language_name(language)} ({language})")
                    print(f"🌍 Text analysis detected: {get_language_name(text_detected_lang)} ({text_detected_lang}) with {text_confidence:.2f} confidence")
                    # Use text detection if significantly more confident
                    if text_confidence > 0.9:
                        language = text_detected_lang
                        print(f"🔄 Using text detection result: {get_language_name(language)}")
                else:
                    print(f"🌍 Language confirmed: {get_language_name(language)} ({language})")
            else:
                print(f"🌍 Detected language: {get_language_name(language)} ({language})")
        else:
            # Process text file with size optimization
            print(f"📄 Reading text file: {file.filename}")
            
            # For large text files, process in chunks to avoid memory issues
            file_size = os.path.getsize(tmp_path)
            if file_size > 1024 * 1024:  # 1MB threshold
                print(f"📏 Large file detected ({file_size / 1024 / 1024:.1f}MB), processing in chunks...")
                
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    # Read in chunks and process
                    chunk_size = 1024 * 1024  # 1MB chunks
                    transcript_text = ""
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        transcript_text += chunk
            else:
                # Small file, read normally
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    transcript_text = f.read()
            
            # Detect language from text content
            text_language_result = detect_text_language(transcript_text)
            language = text_language_result.get('language', 'unknown')
            print(f"🌍 Detected language: {get_language_name(language)} ({language}) with {text_language_result.get('confidence', 0.0):.2f} confidence")
        
        # Process with NLP in parallel for better performance
        print(f"🧠 Processing with NLP (parallel)...")
        print(f"📄 Text length: {len(transcript_text)} characters")
        
        # Use ThreadPoolExecutor for CPU-intensive NLP tasks with timeout
        with ThreadPoolExecutor(max_workers=2) as executor:  # Reduced workers for HuggingFace
            # Submit all NLP tasks in parallel
            summary_future = executor.submit(nlp.summarize_text, transcript_text)
            action_items_future = executor.submit(nlp.extract_action_items, transcript_text)
            key_decisions_future = executor.submit(nlp.extract_key_decisions, transcript_text)
            timelines_future = executor.submit(nlp.extract_timelines, transcript_text)
            participants_future = executor.submit(nlp.extract_participants, transcript_text)
            
            # Wait for all tasks to complete with timeout (180 seconds for large files)
            try:
                print("🔄 Waiting for NLP results...")
                summary = summary_future.result(timeout=180)
                print("✅ Summary completed")
                action_items = action_items_future.result(timeout=180)
                print("✅ Action items completed")
                key_decisions = key_decisions_future.result(timeout=180)
                print("✅ Key decisions completed")
                timelines = timelines_future.result(timeout=180)
                print("✅ Timelines completed")
                participants = participants_future.result(timeout=180)
                print("✅ Participants completed")
            except Exception as e:
                print(f"⚠️ NLP processing timeout or error: {e}")
                import traceback
                traceback.print_exc()
                # Provide fallback values that match expected data types
                summary = "Summary generation failed due to timeout or processing error"
                action_items = [{"task": "Action items extraction failed", "assignee": "N/A", "deadline": "N/A"}]
                key_decisions = [{"decision": "Key decisions extraction failed", "context": "N/A"}]
                timelines = [{"event": "Timeline extraction failed", "date": "N/A"}]
                participants = []
        
        # Prepare meeting data for search index
        meeting_data = {
            "id": meeting_id,
            "title": f"Meeting - {file.filename}",
            "date": datetime.now().isoformat(),
            "transcript": transcript_text,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": key_decisions,
            "timelines": timelines,
            "participants": participants,
            "filename": file.filename,
            "language": language,
            "duration": duration
        }
        
        # Get or create session-specific search engine
        session_search = session_mgr.get_or_create_search_engine(session_id)
        search_success = session_search.add_meeting(meeting_data) if session_search else False
        
        # Add meeting to session
        session_mgr.add_meeting_to_session(session_id, meeting_data)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        if not search_success:
            print("⚠️ Warning: Failed to add meeting to search index")
        
        processing_time = time.time() - start_time
        print(f"⚡ Processing completed in {processing_time:.2f} seconds")
        
        response_data = UploadResponse(
            success=True,
            message=f"File processed successfully in {processing_time:.2f}s",
            meeting_id=meeting_id,
            filename=file.filename,
            transcript=transcript_text,
            summary=summary,
            action_items=action_items,
            language=language
        )
        
        # Set session in both cookie and header
        from fastapi.responses import Response
        response_obj = Response(content=response_data.json(), media_type="application/json")
        response_obj.set_cookie(
            key="session_id", 
            value=session_id, 
            max_age=3600, 
            httponly=False,  # Allow JS access for debugging
            samesite="lax",  # Allow cross-site for HF Spaces
            secure=False     # HTTP for local dev, HTTPS for production
        )
        response_obj.headers["X-Session-ID"] = session_id
        
        return response_obj
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        print(f"❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/search")
async def search_meetings(
    request: Request,
    search_request: SearchRequest,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Search across all meeting content
    """
    try:
        # Get session ID
        session_id = get_or_create_session(request, session_mgr)
        
        # Get or create session-specific search engine
        session_search = session_mgr.get_or_create_search_engine(session_id)
        
        if not session_search:
            return {"success": True, "query": search_request.query, "total_results": 0, "results": []}
        
        results = session_search.search(
            query=search_request.query,
            top_k=search_request.top_k,
            content_types=search_request.content_types,
            date_from=search_request.date_from,
            date_to=search_request.date_to,
            participants=search_request.participants,
            min_relevance=search_request.min_relevance
        )
        
        response_data = {
            "success": True,
            "query": search_request.query,
            "total_results": len(results),
            "results": results
        }
        
        # Set session in both cookie and header
        from fastapi.responses import Response
        response_obj = Response(content=json.dumps(response_data), media_type="application/json")
        response_obj.set_cookie(
            key="session_id", 
            value=session_id, 
            max_age=3600, 
            httponly=False,  # Allow JS access for debugging
            samesite="lax",  # Allow cross-site for HF Spaces
            secure=False     # HTTP for local dev, HTTPS for production
        )
        response_obj.headers["X-Session-ID"] = session_id
        
        return response_obj
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search/filters")
async def get_search_filters(
    request: Request,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Get available filter options for search
    """
    try:
        # Get session ID
        session_id = get_or_create_session(request, session_mgr)
        
        # Get session-specific search engine
        session_search = session_mgr.get_or_create_search_engine(session_id)
        
        if not session_search:
            return {
                "participants": [],
                "date_range": {"earliest": "", "latest": ""},
                "content_types": ["transcript", "summary", "action_item", "decision", "timeline"]
            }
        
        participants = session_search.get_all_participants()
        date_range = session_search.get_date_range()
        
        return {
            "participants": participants,
            "date_range": date_range,
            "content_types": ["transcript", "summary", "action_item", "decision", "timeline"]
        }
        
    except Exception as e:
        print(f"❌ Error getting search filters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get filters: {str(e)}")

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    request: Request,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Get search index statistics
    """
    try:
        # Get session ID
        session_id = get_or_create_session(request, session_mgr)
        
        # Get session-specific statistics
        session_stats = session_mgr.get_session_stats(session_id)
        
        # Get or create session-specific search engine for additional stats
        session_search = session_mgr.get_or_create_search_engine(session_id)
        search_stats = session_search.get_search_statistics() if session_search else {
            "total_documents": 0,
            "content_type_distribution": {},
            "index_size_mb": 0.0,
            "embedding_dimension": 384,
            "model_name": "all-MiniLM-L6-v2"
        }
        
        # Combine session and search stats
        combined_stats = {
            **search_stats,
            "session_id": session_stats["session_id"],
            "session_meetings": session_stats["total_meetings"],
            # Ensure all required fields are present
            "content_type_distribution": search_stats.get("content_type_distribution", {}),
            "index_size_mb": search_stats.get("index_size_mb", 0.0),
            "embedding_dimension": search_stats.get("embedding_dimension", 384),
            "model_name": search_stats.get("model_name", "all-MiniLM-L6-v2")
        }
        
        response_data = StatisticsResponse(**combined_stats)
        
        # Set session in both cookie and header
        from fastapi.responses import Response
        response_obj = Response(content=response_data.json(), media_type="application/json")
        response_obj.set_cookie(
            key="session_id", 
            value=session_id, 
            max_age=3600, 
            httponly=False,  # Allow JS access for debugging
            samesite="lax",  # Allow cross-site for HF Spaces
            secure=False     # HTTP for local dev, HTTPS for production
        )
        response_obj.headers["X-Session-ID"] = session_id
        
        return response_obj
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/meetings")
async def list_meetings(
    search: MeetingSearchEngine = Depends(get_search_engine)
):
    """
    List all indexed meetings
    """
    try:
        stats = search.get_search_statistics()
        
        # Get unique meetings from metadata
        meetings = []
        seen_meetings = set()
        
        for metadata in search.metadata:
            meeting_id = metadata['meeting_id']
            if meeting_id not in seen_meetings:
                meetings.append({
                    "id": meeting_id,
                    "title": metadata['meeting_title'],
                    "date": metadata['meeting_date'],
                    "participants": metadata['participants']
                })
                seen_meetings.add(meeting_id)
        
        return {
            "success": True,
            "total_meetings": len(meetings),
            "meetings": meetings
        }
        
    except Exception as e:
        print(f"❌ Error listing meetings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list meetings: {str(e)}")

@router.get("/meetings/{meeting_id}")
async def get_meeting(
    meeting_id: str,
    search: MeetingSearchEngine = Depends(get_search_engine)
):
    """
    Get detailed information about a specific meeting
    """
    try:
        meeting_content = search.search_by_meeting_id(meeting_id)
        
        if not meeting_content:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Organize content by type
        organized_content = {
            "transcript": [],
            "summary": [],
            "action_items": [],
            "decisions": [],
            "timelines": []
        }
        
        for content in meeting_content:
            content_type = content['content_type']
            if content_type in organized_content:
                organized_content[content_type].append(content['text'])
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "title": meeting_content[0]['meeting_title'] if meeting_content else "Unknown",
            "date": meeting_content[0]['meeting_date'] if meeting_content else "",
            "participants": meeting_content[0]['participants'] if meeting_content else [],
            "content": organized_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting meeting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get meeting: {str(e)}")

@router.get("/meetings/{meeting_id}/similar")
async def get_similar_meetings(
    meeting_id: str,
    top_k: int = 5,
    search: MeetingSearchEngine = Depends(get_search_engine)
):
    """
    Find meetings similar to the specified meeting
    """
    try:
        similar_meetings = search.get_similar_meetings(meeting_id, top_k)
        
        return {
            "success": True,
            "reference_meeting": meeting_id,
            "similar_meetings": similar_meetings
        }
        
    except Exception as e:
        print(f"❌ Error finding similar meetings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar meetings: {str(e)}")

@router.get("/analytics")
async def get_analytics(
    request: Request,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Get comprehensive analytics data for dashboard
    """
    try:
        from collections import defaultdict
        from datetime import datetime, timedelta
        import calendar
        
        # Get session ID
        session_id = get_or_create_session(request, session_mgr)
        
        # Get session meetings
        meetings = session_mgr.get_session_meetings(session_id)
        
        if not meetings:
            return {
                "success": True,
                "total_meetings": 0,
                "meeting_timeline": [],
                "content_distribution": {},
                "participant_activity": {},
                "language_distribution": {},
                "monthly_activity": [],
                "action_items_stats": {},
                "average_meeting_length": 0,
                "recent_activity": []
            }
        
        # Process meetings for analytics
        meeting_timeline = []
        content_distribution = defaultdict(int)
        participant_counts = defaultdict(int)
        language_counts = defaultdict(int)
        monthly_counts = defaultdict(int)
        action_items_total = 0
        total_duration = 0
        duration_count = 0
        
        for meeting in meetings:
            # Timeline data
            meeting_date = datetime.fromisoformat(meeting['date'].replace('Z', '+00:00'))
            meeting_timeline.append({
                "date": meeting_date.strftime('%Y-%m-%d'),
                "title": meeting['title'],
                "participants": len(meeting.get('participants', [])),
                "language": meeting.get('language', 'unknown')
            })
            
            # Content type distribution
            if meeting.get('action_items'):
                content_distribution['action_items'] += len(meeting['action_items'])
                action_items_total += len(meeting['action_items'])
            if meeting.get('key_decisions'):
                content_distribution['decisions'] += len(meeting['key_decisions'])
            if meeting.get('timelines'):
                content_distribution['timelines'] += len(meeting['timelines'])
            if meeting.get('summary'):
                content_distribution['summaries'] += 1
            if meeting.get('transcript'):
                content_distribution['transcripts'] += 1
            
            # Participant activity - count actual mentions in transcript
            participants = meeting.get('participants', [])
            transcript_lower = meeting.get('transcript', '').lower()
            
            for participant in participants:
                # Count how many times this participant speaks in the transcript
                # Look for patterns like "NAME:" or "NAME said" or "NAME mentioned"
                participant_lower = participant.lower()
                patterns = [
                    f"{participant_lower}:",  # Direct speech
                    f"{participant_lower} said",
                    f"{participant_lower} mentioned",
                    f"{participant_lower} reported",
                    f"{participant_lower} proposed",
                    f"{participant_lower} agreed",
                    f"{participant_lower} suggested"
                ]
                
                mention_count = sum(transcript_lower.count(pattern) for pattern in patterns)
                if mention_count > 0:
                    participant_counts[participant] += mention_count
                else:
                    # If no direct mentions found, still count them as present
                    participant_counts[participant] += 1
            
            # Language distribution
            language = meeting.get('language', 'unknown')
            language_counts[language] += 1
            
            # Monthly activity
            month_key = meeting_date.strftime('%Y-%m')
            monthly_counts[month_key] += 1
            
            # Duration tracking
            if meeting.get('duration', 0) > 0:
                total_duration += meeting['duration']
                duration_count += 1
        
        # Sort timeline by date
        meeting_timeline.sort(key=lambda x: x['date'])
        
        # Prepare monthly activity chart (last 6 months)
        now = datetime.now()
        monthly_activity = []
        for i in range(5, -1, -1):
            target_date = now - timedelta(days=i*30)
            month_key = target_date.strftime('%Y-%m')
            month_name = calendar.month_abbr[target_date.month]
            monthly_activity.append({
                "month": f"{month_name} {target_date.year}",
                "meetings": monthly_counts.get(month_key, 0),
                "date": month_key
            })
        
        # Top participants (limit to top 10)
        top_participants = dict(sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Recent activity (last 10 meetings)
        recent_activity = sorted(meeting_timeline, key=lambda x: x['date'], reverse=True)[:10]
        
        # Calculate average meeting length
        avg_duration = (total_duration / duration_count) if duration_count > 0 else 0
        
        analytics_data = {
            "success": True,
            "total_meetings": len(meetings),
            "meeting_timeline": meeting_timeline,
            "content_distribution": dict(content_distribution),
            "participant_activity": top_participants,
            "language_distribution": dict(language_counts),
            "monthly_activity": monthly_activity,
            "action_items_stats": {
                "total_action_items": action_items_total,
                "avg_per_meeting": action_items_total / len(meetings) if meetings else 0
            },
            "average_meeting_length": round(avg_duration / 60, 1) if avg_duration > 0 else 0,  # Convert to minutes
            "recent_activity": recent_activity
        }
        
        # Set session in response
        from fastapi.responses import Response
        response_obj = Response(content=json.dumps(analytics_data), media_type="application/json")
        response_obj.set_cookie(
            key="session_id", 
            value=session_id, 
            max_age=3600, 
            httponly=False,
            samesite="lax",
            secure=False
        )
        response_obj.headers["X-Session-ID"] = session_id
        
        return response_obj
        
    except Exception as e:
        print(f"❌ Error getting analytics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.delete("/meetings/{meeting_id}")
async def delete_meeting(
    meeting_id: str,
    search: MeetingSearchEngine = Depends(get_search_engine)
):
    """
    Delete a meeting from the search index
    """
    try:
        # This would require implementing delete functionality in the search engine
        # For now, return a placeholder response
        return {
            "success": True,
            "message": f"Meeting {meeting_id} deleted successfully",
            "note": "Delete functionality not yet implemented"
        }
        
    except Exception as e:
        print(f"❌ Error deleting meeting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete meeting: {str(e)}")
