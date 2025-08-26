"""
Session Manager for Polyglot Meeting Assistant

Handles isolated meetings and search indexes for each user session.
"""

import uuid
import os
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
import logging

class SessionManager:
    """Manages user sessions with isolated data"""
    
    def __init__(self, sessions_dir: str = "data/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 1 hour timeout
        self.search_engines: Dict[str, Any] = {}  # Cache search engines per session
        
        # Clean up old sessions on startup
        self._cleanup_expired_sessions()
    
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "created_at": time.time(),
            "last_activity": time.time(),
            "meetings": [],
            "search_index_path": str(self.sessions_dir / session_id / "search_index")
        }
        
        # Create session directory
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Create search index directory
        search_index_dir = session_dir / "search_index"
        search_index_dir.mkdir(exist_ok=True)
        
        # Store session data
        self.active_sessions[session_id] = session_data
        self._save_session_data(session_id, session_data)
        
        logging.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        if session_id not in self.active_sessions:
            # Try to load from disk
            session_data = self._load_session_data(session_id)
            if session_data and not self._is_session_expired(session_data):
                self.active_sessions[session_id] = session_data
                return session_data
            return None
        
        # Update last activity
        self.active_sessions[session_id]["last_activity"] = time.time()
        return self.active_sessions[session_id]
    
    def add_meeting_to_session(self, session_id: str, meeting_data: Dict[str, Any]) -> bool:
        """Add a meeting to a specific session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Add meeting to session
        meeting_data["session_id"] = session_id
        meeting_data["added_at"] = time.time()
        session["meetings"].append(meeting_data)
        
        # Update session
        self.active_sessions[session_id] = session
        self._save_session_data(session_id, session)
        
        logging.info(f"Added meeting to session {session_id}: {meeting_data.get('title', 'Untitled')}")
        return True
    
    def get_session_meetings(self, session_id: str) -> list:
        """Get all meetings for a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        return session.get("meetings", [])
    
    def get_session_search_index_path(self, session_id: str) -> Optional[str]:
        """Get the search index path for a session"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session.get("search_index_path")
    
    def get_or_create_search_engine(self, session_id: str):
        """Get or create a search engine for a session"""
        if session_id not in self.search_engines:
            from models.search import MeetingSearchEngine
            index_path = self.get_session_search_index_path(session_id)
            if index_path:
                self.search_engines[session_id] = MeetingSearchEngine(index_path=index_path)
                print(f"🔍 Created search engine for session: {session_id[:8]}...")
        
        return self.search_engines.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its data including search indexes"""
        try:
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Remove from search engines cache
            if session_id in self.search_engines:
                del self.search_engines[session_id]
            
            # Remove session directory (includes search indexes)
            session_dir = self.sessions_dir / session_id
            if session_dir.exists():
                import shutil
                shutil.rmtree(session_dir)
                logging.info(f"Deleted session directory: {session_id}")
            
            logging.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logging.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def _save_session_data(self, session_id: str, session_data: Dict[str, Any]):
        """Save session data to disk"""
        try:
            session_file = self.sessions_dir / session_id / "session.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving session data: {e}")
    
    def _load_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from disk"""
        try:
            session_file = self.sessions_dir / session_id / "session.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading session data: {e}")
        return None
    
    def _is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """Check if session has expired"""
        last_activity = session_data.get("last_activity", 0)
        return (time.time() - last_activity) > self.session_timeout
    
    def _cleanup_expired_sessions(self):
        """Clean up ONLY expired sessions, preserve search data"""
        try:
            for session_dir in self.sessions_dir.iterdir():
                if session_dir.is_dir():
                    session_file = session_dir / "session.json"
                    if session_file.exists():
                        session_data = self._load_session_data(session_dir.name)
                        if session_data and self._is_session_expired(session_data):
                            # Only delete if session is truly expired
                            self.delete_session(session_dir.name)
                    # DON'T delete orphaned directories - they might contain valuable search data
                    # Let them persist for potential recovery or manual cleanup
        except Exception as e:
            logging.error(f"Error cleaning up sessions: {e}")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        session = self.get_session(session_id)
        if not session:
            return {"total_meetings": 0, "total_documents": 0}
        
        meetings = session.get("meetings", [])
        total_documents = sum(len(meeting.get("searchable_chunks", [])) for meeting in meetings)
        
        return {
            "total_meetings": len(meetings),
            "total_documents": total_documents,
            "session_id": session_id,
            "created_at": session.get("created_at"),
            "last_activity": session.get("last_activity")
        }
    
    def clear_all_sessions(self) -> bool:
        """Clear all sessions and search indexes (for testing/maintenance)"""
        try:
            # Clear active sessions
            self.active_sessions.clear()
            self.search_engines.clear()
            
            # Remove all session directories
            import shutil
            if self.sessions_dir.exists():
                shutil.rmtree(self.sessions_dir)
                self.sessions_dir.mkdir(parents=True, exist_ok=True)
            
            logging.info("Cleared all sessions and search indexes")
            return True
        except Exception as e:
            logging.error(f"Error clearing all sessions: {e}")
            return False
    
    def get_all_sessions_info(self) -> Dict[str, Any]:
        """Get information about all sessions (for debugging)"""
        try:
            session_count = len(list(self.sessions_dir.iterdir()))
            active_count = len(self.active_sessions)
            search_engine_count = len(self.search_engines)
            
            return {
                "total_sessions_on_disk": session_count,
                "active_sessions_in_memory": active_count,
                "cached_search_engines": search_engine_count,
                "sessions_directory": str(self.sessions_dir),
                "session_timeout_seconds": self.session_timeout
            }
        except Exception as e:
            logging.error(f"Error getting sessions info: {e}")
            return {"error": str(e)}
