# 🔍 Polyglot Meeting Assistant

**AI-powered semantic search and analysis for your meetings**

A full-stack application that uses advanced AI/ML techniques to help you search, analyze, and extract insights from your meeting content.

## 🚀 Features

- **🤖 Semantic Search** - Find information using natural language queries
- **📁 File Upload** - Support for text, audio, and video files
- **🎯 Content Analysis** - Automatic extraction of summaries, action items, and decisions
- **📊 Analytics Dashboard** - Real-time statistics and insights
- **🌍 Multi-language Support** - Works with multiple languages
- **⚡ Fast Performance** - Vector-based search with FAISS

## 🏗️ Architecture

```
polyglot-meeting-assistant/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── models/            # AI/ML models (Search, NLP, ASR)
│   │   ├── utils/             # Utility functions
│   │   └── api.py             # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── tests/                 # Test suite
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   └── services/          # API service layer
│   └── package.json           # Node.js dependencies
└── data/                       # Search index and data
```

## 🛠️ Technology Stack

### Backend
- **Python 3.13** - Core language
- **FastAPI** - Web framework
- **Sentence Transformers** - Semantic embeddings
- **FAISS** - Vector database
- **Whisper** - Speech-to-text
- **Transformers** - NLP processing

### Frontend
- **React 18** - UI framework
- **Material-UI** - Component library
- **Axios** - HTTP client
- **React Router** - Navigation

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository
```bash
git clone <repository-url>
cd polyglot-meeting-assistant
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Start the Backend
```bash
cd backend
source venv/bin/activate
PYTHONPATH=src python src/api.py
```

The backend will start on `http://localhost:8000`

### 5. Start the Frontend
```bash
cd frontend
npm start
```

The frontend will start on `http://localhost:3000`

## 📖 Usage

### 1. Upload Files
- Navigate to the **Upload** tab
- Drag and drop or click to select files
- Supported formats: `.txt`, `.md`, `.mp3`, `.wav`, `.mp4`

### 2. Search Content
- Go to the **Search** tab
- Enter your search query in natural language
- Use filters to narrow results by content type
- View relevance scores and snippets

### 3. View Statistics
- Check the **Statistics** tab for:
  - Total meetings and documents indexed
  - Content distribution
  - Index size and performance metrics

## 🔧 API Endpoints

- `GET /api/health` - Health check
- `GET /api/stats` - Get search statistics
- `POST /api/upload` - Upload meeting files
- `POST /api/search` - Search meetings
- `GET /api/meetings` - List all meetings
- `GET /api/export` - Export search results

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
cd tests
python run_all_tests.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Backend Deployment
```bash
cd backend
pip install gunicorn
gunicorn src.api:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
```bash
cd frontend
npm run build
```

## 📊 Performance

- **Search Speed**: < 2 seconds for 1000+ documents
- **Index Size**: ~1MB for 680 documents
- **Accuracy**: 85%+ relevance scoring
- **Scalability**: Handles 1000+ meetings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🎯 Roadmap

- [ ] Audio/video processing improvements
- [ ] Advanced analytics dashboard
- [ ] Export to PDF/Word
- [ ] User authentication
- [ ] Team collaboration features
- [ ] Mobile app

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built with ❤️ for better meeting management**


