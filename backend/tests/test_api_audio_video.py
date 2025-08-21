#!/usr/bin/env python3
"""
API tests for audio/video upload functionality
"""

import asyncio
import tempfile
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from api import app

class TestAudioVideoAPI:
    """Test suite for audio/video API endpoints"""
    
    def setup_method(self):
        """Set up test environment"""
        self.client = TestClient(app)
        
    def test_health_check(self):
        """Test API health check"""
        print("🧪 Testing API health check...")
        
        response = self.client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        
        print("✅ Health check test passed")
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        print("🧪 Testing stats endpoint...")
        
        response = self.client.get("/api/stats")
        
        # Should return 200 or 503 (if search engine not available)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_documents" in data
            assert "total_meetings" in data
            print("✅ Stats endpoint test passed")
        else:
            print("⚠️ Stats endpoint returned 503 (search engine not available)")
    
    @patch('api.asr_processor')
    @patch('api.nlp_processor')
    @patch('api.search_engine')
    def test_audio_upload_mock(self, mock_search, mock_nlp, mock_asr):
        """Test audio file upload with mocked components"""
        print("🧪 Testing audio upload (mocked)...")
        
        # Mock the components
        mock_asr.transcribe.return_value = {
            'text': 'This is a test audio transcription.',
            'segments': [],
            'language': 'en',
            'duration': 10.0
        }
        
        mock_nlp.generate_comprehensive_summary.return_value = {
            'summary': 'Test meeting summary',
            'action_items': ['Action 1', 'Action 2'],
            'key_decisions': ['Decision 1'],
            'timelines': [],
            'participants': ['John', 'Jane']
        }
        
        mock_search.add_meeting.return_value = True
        
        # Create test audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(b"fake audio content")
            tmp_file.flush()
            
            try:
                # Test upload
                with open(tmp_file.name, 'rb') as f:
                    response = self.client.post(
                        "/api/upload",
                        files={"file": ("test_audio.wav", f, "audio/wav")}
                    )
                
                assert response.status_code == 200
                
                data = response.json()
                assert data["success"] == True
                assert "meeting_id" in data
                assert data["filename"] == "test_audio.wav"
                
                print("✅ Audio upload test passed")
                
            finally:
                os.unlink(tmp_file.name)
    
    @patch('api.asr_processor')
    @patch('api.nlp_processor')
    @patch('api.search_engine')
    def test_video_upload_mock(self, mock_search, mock_nlp, mock_asr):
        """Test video file upload with mocked components"""
        print("🧪 Testing video upload (mocked)...")
        
        # Mock the components
        mock_asr.transcribe.return_value = {
            'text': 'This is a test video transcription.',
            'segments': [],
            'language': 'en',
            'duration': 15.0
        }
        
        mock_nlp.generate_comprehensive_summary.return_value = {
            'summary': 'Test video meeting summary',
            'action_items': ['Video Action 1'],
            'key_decisions': ['Video Decision 1'],
            'timelines': [],
            'participants': ['Alice', 'Bob']
        }
        
        mock_search.add_meeting.return_value = True
        
        # Create test video file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
            tmp_file.write(b"fake video content")
            tmp_file.flush()
            
            try:
                # Test upload
                with open(tmp_file.name, 'rb') as f:
                    response = self.client.post(
                        "/api/upload",
                        files={"file": ("test_video.mp4", f, "video/mp4")}
                    )
                
                assert response.status_code == 200
                
                data = response.json()
                assert data["success"] == True
                assert "meeting_id" in data
                assert data["filename"] == "test_video.mp4"
                
                print("✅ Video upload test passed")
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_text_upload(self):
        """Test text file upload"""
        print("🧪 Testing text upload...")
        
        # Create test text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"This is a test meeting transcript.")
            tmp_file.flush()
            
            try:
                # Test upload
                with open(tmp_file.name, 'rb') as f:
                    response = self.client.post(
                        "/api/upload",
                        files={"file": ("test_meeting.txt", f, "text/plain")}
                    )
                
                # Should return 200 or 503 (if components not available)
                assert response.status_code in [200, 503]
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["success"] == True
                    print("✅ Text upload test passed")
                else:
                    print("⚠️ Text upload returned 503 (components not available)")
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_invalid_file_type(self):
        """Test upload with invalid file type"""
        print("🧪 Testing invalid file type...")
        
        # Create test file with invalid extension
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp_file:
            tmp_file.write(b"invalid content")
            tmp_file.flush()
            
            try:
                # Test upload
                with open(tmp_file.name, 'rb') as f:
                    response = self.client.post(
                        "/api/upload",
                        files={"file": ("test.xyz", f, "application/octet-stream")}
                    )
                
                assert response.status_code == 400
                assert "Unsupported file type" in response.json()["detail"]
                
                print("✅ Invalid file type test passed")
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_search_endpoint(self):
        """Test search endpoint"""
        print("🧪 Testing search endpoint...")
        
        search_request = {
            "query": "test search",
            "top_k": 5,
            "content_types": ["transcript", "summary"]
        }
        
        response = self.client.post("/api/search", json=search_request)
        
        # Should return 200 or 503 (if search engine not available)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "total_results" in data
            assert "results" in data
            print("✅ Search endpoint test passed")
        else:
            print("⚠️ Search endpoint returned 503 (search engine not available)")
    
    def test_meetings_endpoint(self):
        """Test meetings list endpoint"""
        print("🧪 Testing meetings endpoint...")
        
        response = self.client.get("/api/meetings")
        
        # Should return 200 or 503 (if search engine not available)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_meetings" in data
            assert "total_documents" in data
            print("✅ Meetings endpoint test passed")
        else:
            print("⚠️ Meetings endpoint returned 503 (search engine not available)")

def run_api_tests():
    """Run all API tests"""
    print("🚀 Starting Audio/Video API Tests...")
    print("=" * 50)
    
    test_suite = TestAudioVideoAPI()
    
    # Run tests
    test_methods = [
        test_suite.test_health_check,
        test_suite.test_stats_endpoint,
        test_suite.test_audio_upload_mock,
        test_suite.test_video_upload_mock,
        test_suite.test_text_upload,
        test_suite.test_invalid_file_type,
        test_suite.test_search_endpoint,
        test_suite.test_meetings_endpoint
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test_method.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 API Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All API tests passed! Audio/Video API is ready for commit.")
    else:
        print("⚠️ Some API tests failed. Please review before committing.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_api_tests()
    exit(0 if success else 1)
