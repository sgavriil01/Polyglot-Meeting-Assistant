# API Reference

Complete reference for the Polyglot Meeting Assistant REST API.

## Base URL

**Local Development**: `http://localhost:8000`

## Authentication

Currently no authentication required. Each user gets a session ID automatically managed by the frontend.

## Headers

All requests should include:
```
Content-Type: application/json
X-Session-ID: <session-id>  # Automatically handled by frontend
```

---

## Endpoints

### Health Check

Check if the API is running.

```http
GET /api/v1/health
```

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2025-09-13T10:30:00Z"
}
```

---

### Upload File

Upload and process audio, video, or text files.

```http
POST /api/v1/upload
Content-Type: multipart/form-data
```

**Parameters**:
- `file` (file, required): The file to upload

**Supported formats**:
- Audio: `.mp3`, `.wav`, `.m4a`, `.ogg`
- Video: `.mp4`, `.avi`, `.mov`, `.mkv`
- Text: `.txt`, `.md`

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
     -F "file=@meeting-recording.mp3"
```

**Response**:
```json
{
  "success": true,
  "message": "File processed successfully",
  "meeting_id": "uuid-string",
  "filename": "meeting-recording.mp3",
  "processing_time": 45.2
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "Unsupported file format",
  "error_code": "INVALID_FORMAT"
}
```

---

### Search Meetings

Search across all uploaded meeting content.

```http
POST /api/v1/search
Content-Type: application/json
```

**Request Body**:
```json
{
  "query": "budget decisions",
  "top_k": 10,
  "content_types": ["summary", "action_items", "transcript"],
  "date_from": "2025-01-01",
  "date_to": "2025-12-31",
  "participants": ["Sarah", "Mike"],
  "min_relevance": 0.5
}
```

**Parameters**:
- `query` (string, required): Search query in natural language
- `top_k` (integer, optional): Number of results to return (default: 10)
- `content_types` (array, optional): Types of content to search
  - `"transcript"`: Full transcription text
  - `"summary"`: Meeting summaries
  - `"action_items"`: Extracted action items
  - `"decisions"`: Key decisions made
- `date_from` (string, optional): Start date filter (YYYY-MM-DD)
- `date_to` (string, optional): End date filter (YYYY-MM-DD)
- `participants` (array, optional): Filter by participant names
- `min_relevance` (float, optional): Minimum relevance score (0.0-1.0)

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What decisions were made about the marketing budget?",
       "top_k": 5,
       "content_types": ["decisions", "summary"]
     }'
```

**Response**:
```json
{
  "results": [
    {
      "meeting_id": "uuid-string",
      "meeting_title": "Q4 Planning Meeting",
      "meeting_date": "2025-09-10",
      "content_type": "decisions",
      "text": "Approved $50,000 marketing budget for Q4 campaign",
      "participants": ["Sarah CEO", "Mike CFO", "Lisa VP Marketing"],
      "relevance_score": 0.95,
      "snippet": "...approved $50,000 marketing budget for Q4 campaign targeting digital channels...",
      "context": {
        "start_time": "00:15:30",
        "end_time": "00:16:45"
      }
    }
  ],
  "total_results": 1,
  "query_time": 0.234
}
```

---

### Get Statistics

Get session statistics and usage information.

```http
GET /api/v1/statistics
```

**Response**:
```json
{
  "session_id": "uuid-string",
  "total_meetings": 15,
  "total_files": 18,
  "total_audio_duration": 7200,
  "search_index_size": 1024,
  "last_activity": "2025-09-13T10:30:00Z",
  "storage_used": {
    "uploads": "250MB",
    "search_index": "50MB",
    "sessions": "5MB"
  }
}
```

---

### Get Meetings List

Get list of all uploaded meetings in current session.

```http
GET /api/v1/meetings
```

**Query Parameters**:
- `limit` (integer, optional): Number of meetings to return (default: 50)
- `offset` (integer, optional): Number of meetings to skip (default: 0)
- `sort_by` (string, optional): Sort field (`date`, `title`, `duration`)
- `sort_order` (string, optional): Sort order (`asc`, `desc`)

**Example**:
```bash
curl "http://localhost:8000/api/v1/meetings?limit=10&sort_by=date&sort_order=desc"
```

**Response**:
```json
{
  "meetings": [
    {
      "meeting_id": "uuid-string",
      "title": "Q4 Planning Meeting",
      "date": "2025-09-10",
      "duration": 3600,
      "participants": ["Sarah CEO", "Mike CFO"],
      "file_count": 2,
      "file_types": ["audio", "text"],
      "summary": "Strategic planning session for Q4 objectives...",
      "action_items_count": 5,
      "decisions_count": 3
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

---

### Export Results

Export search results or meeting data in various formats.

```http
GET /api/v1/export
```

**Query Parameters**:
- `format` (string, required): Export format (`json`, `csv`, `pdf`)
- `q` (string, optional): Search query to export results for
- `meeting_id` (string, optional): Specific meeting to export

**Examples**:
```bash
# Export search results as CSV
curl "http://localhost:8000/api/v1/export?format=csv&q=budget+decisions"

# Export specific meeting as JSON
curl "http://localhost:8000/api/v1/export?format=json&meeting_id=uuid-string"
```

**Response** (JSON format):
```json
{
  "export_id": "uuid-string",
  "format": "json",
  "data": [...],
  "generated_at": "2025-09-13T10:30:00Z"
}
```

---

### Get Search Filters

Get available filter options for search queries.

```http
GET /api/v1/search/filters
```

**Response**:
```json
{
  "content_types": [
    "transcript",
    "summary", 
    "action_items",
    "decisions"
  ],
  "participants": [
    "Sarah CEO",
    "Mike CFO",
    "Lisa VP Marketing"
  ],
  "date_range": {
    "earliest": "2025-01-15",
    "latest": "2025-09-13"
  },
  "file_types": [
    "audio",
    "video",
    "text"
  ]
}
```

---

### Get Analytics

Get detailed analytics about meeting content and usage.

```http
GET /api/v1/analytics
```

**Response**:
```json
{
  "overview": {
    "total_meetings": 15,
    "total_duration": 7200,
    "avg_meeting_duration": 480,
    "most_active_participant": "Sarah CEO"
  },
  "content_analysis": {
    "total_action_items": 45,
    "total_decisions": 23,
    "avg_participants_per_meeting": 3.2
  },
  "search_analytics": {
    "total_searches": 156,
    "avg_search_time": 0.234,
    "popular_queries": [
      "budget decisions",
      "action items for Sarah",
      "Q4 planning"
    ]
  },
  "file_analytics": {
    "by_type": {
      "audio": 12,
      "video": 2,
      "text": 4
    },
    "by_size": {
      "small": 8,
      "medium": 7,
      "large": 3
    }
  }
}
```

---

## Error Codes

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `413` - Payload Too Large (file too big)
- `415` - Unsupported Media Type (invalid file format)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

### Custom Error Codes

```json
{
  "error": {
    "code": "INVALID_FORMAT",
    "message": "Unsupported file format. Supported: mp3, wav, m4a, ogg",
    "details": {
      "supported_formats": ["mp3", "wav", "m4a", "ogg"],
      "received_format": "avi"
    }
  }
}
```

**Common Error Codes**:
- `INVALID_FORMAT` - Unsupported file format
- `FILE_TOO_LARGE` - File exceeds size limit
- `PROCESSING_FAILED` - File processing error
- `SESSION_NOT_FOUND` - Invalid session ID
- `SEARCH_FAILED` - Search query error
- `INSUFFICIENT_STORAGE` - Not enough disk space

---

## Rate Limits

Currently no rate limits implemented. For production use, consider:
- **Upload**: 10 files per minute
- **Search**: 60 requests per minute
- **Export**: 5 exports per hour

---

## SDKs and Examples

### Python Example

```python
import requests

# Upload file
with open('meeting.mp3', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/upload',
        files={'file': f}
    )
    print(response.json())

# Search meetings
search_response = requests.post(
    'http://localhost:8000/api/v1/search',
    json={
        'query': 'budget decisions',
        'top_k': 5
    }
)
print(search_response.json())
```

### JavaScript Example

```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/v1/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// Search meetings
fetch('/api/v1/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'budget decisions',
    top_k: 5
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload file
curl -X POST http://localhost:8000/api/v1/upload \
     -F "file=@meeting.mp3"

# Search
curl -X POST http://localhost:8000/api/v1/search \
     -H "Content-Type: application/json" \
     -d '{"query": "budget decisions"}'

# Get statistics
curl http://localhost:8000/api/v1/statistics
```

---

## Interactive Documentation

When running the application locally, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide interactive API documentation where you can test endpoints directly in your browser.
