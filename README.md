---
title: Polyglot Meeting Assistant
emoji: 🎙️
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: app.py
pinned: false
---

# Polyglot Meeting Assistant

An AI-powered meeting transcription and analysis tool that automatically transcribes audio, extracts key insights, and provides semantic search across your meetings.

## ✨ Features

- **🎙️ Audio Transcription** - Upload audio files (MP3, WAV, M4A) for automatic transcription
- **📄 Text Processing** - Upload text files (TXT, MD, RTF) for analysis
- **🧠 AI-Powered Analysis** - Automatic summarization, action item extraction, and key decision identification
- **🔍 Semantic Search** - Search across all your meetings using natural language
- **👥 Session Management** - Isolated user sessions with persistent data
- **📱 Modern UI** - Clean, responsive interface built with React and Material-UI

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
git clone https://github.com/yourusername/polyglot-meeting-assistant.git
cd polyglot-meeting-assistant
docker-compose up --build
```

Visit `http://localhost:3000` to start using the application.

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn src.api:app --reload --port 8000

# Frontend
cd frontend
npm install
npm start
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: React 19, Material-UI
- **AI/ML**: OpenAI Whisper (ASR), HuggingFace Transformers (NLP), FAISS (Vector Search)
- **Deployment**: Docker, HuggingFace Spaces

## 📖 Usage

1. **Upload Files** - Drag and drop audio or text files
2. **Automatic Processing** - AI models transcribe and analyze content
3. **View Insights** - Get summaries, action items, and key decisions
4. **Search** - Use natural language to find specific content across meetings

## 🔧 API Endpoints

- `POST /api/v1/upload` - Upload and process files
- `POST /api/v1/search` - Search across meetings
- `GET /api/v1/statistics` - Get session statistics
- `GET /api/v1/health` - Health check

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---




