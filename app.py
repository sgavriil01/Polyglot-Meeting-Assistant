import gradio as gr
import requests
import json
import os
from typing import List, Dict, Any

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

def process_file(file):
    """Process uploaded file through the API"""
    if file is None:
        return "Please upload a file first."
    
    try:
        # Prepare file for upload
        files = {'file': (file.name, file.read(), 'application/octet-stream')}
        
        # Upload file
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            return f"""
## ✅ File Processed Successfully!

**File:** {result.get('filename', 'Unknown')}
**Processing Time:** {result.get('message', '').split('in ')[-1] if 'in ' in result.get('message', '') else 'N/A'}

### 📝 Summary
{result.get('summary', 'No summary available')}

### ✅ Action Items
{chr(10).join([f"- {item}" for item in result.get('action_items', [])])}

### 🔍 Meeting ID
`{result.get('meeting_id', 'N/A')}`
            """
        else:
            return f"❌ Error: {response.text}"
    
    except Exception as e:
        return f"❌ Error processing file: {str(e)}"

def search_meetings(query: str, top_k: int = 5):
    """Search across meetings"""
    if not query.strip():
        return "Please enter a search query."
    
    try:
        # Search request
        search_data = {
            "query": query,
            "top_k": top_k
        }
        
        response = requests.post(f"{API_BASE_URL}/search", json=search_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('total_results', 0) == 0:
                return "🔍 No results found for your query."
            
            # Format results
            formatted_results = f"## 🔍 Search Results ({result.get('total_results', 0)} found)\n\n"
            
            for i, item in enumerate(result.get('results', []), 1):
                formatted_results += f"### {i}. {item.get('title', 'Untitled Meeting')}\n"
                formatted_results += f"**Relevance:** {item.get('score', 0):.2f}\n"
                formatted_results += f"**Content:** {item.get('content', 'No content')[:200]}...\n\n"
            
            return formatted_results
        else:
            return f"❌ Error: {response.text}"
    
    except Exception as e:
        return f"❌ Error searching: {str(e)}"

def get_statistics():
    """Get session statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            
            return f"""
## 📊 Session Statistics

**Total Meetings:** {stats.get('total_meetings', 0)}
**Total Documents:** {stats.get('total_documents', 0)}
**Search Index Size:** {stats.get('index_size_mb', 0):.2f} MB
**Model:** {stats.get('model_name', 'Unknown')}
**Embedding Dimension:** {stats.get('embedding_dimension', 0)}
            """
        else:
            return f"❌ Error: {response.text}"
    
    except Exception as e:
        return f"❌ Error getting statistics: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Polyglot Meeting Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎙️ Polyglot Meeting Assistant
    
    An AI-powered meeting transcription and analysis tool that automatically transcribes audio, extracts key insights, and provides semantic search across your meetings.
    """)
    
    with gr.Tabs():
        # Upload Tab
        with gr.TabItem("📁 Upload & Process"):
            gr.Markdown("### Upload your meeting files for AI-powered analysis")
            
            with gr.Row():
                with gr.Column():
                    file_input = gr.File(
                        label="Upload File",
                        file_types=[".txt", ".md", ".rtf", ".mp3", ".wav", ".m4a", ".ogg", ".flac"],
                        file_count="single"
                    )
                    upload_btn = gr.Button("🚀 Process File", variant="primary")
                
                with gr.Column():
                    output_text = gr.Markdown(label="Processing Results")
            
            upload_btn.click(
                fn=process_file,
                inputs=[file_input],
                outputs=[output_text]
            )
        
        # Search Tab
        with gr.TabItem("🔍 Search Meetings"):
            gr.Markdown("### Search across all your processed meetings")
            
            with gr.Row():
                with gr.Column():
                    search_query = gr.Textbox(
                        label="Search Query",
                        placeholder="Enter your search terms...",
                        lines=2
                    )
                    top_k = gr.Slider(
                        minimum=1,
                        maximum=20,
                        value=5,
                        step=1,
                        label="Number of Results"
                    )
                    search_btn = gr.Button("🔍 Search", variant="primary")
                
                with gr.Column():
                    search_results = gr.Markdown(label="Search Results")
            
            search_btn.click(
                fn=search_meetings,
                inputs=[search_query, top_k],
                outputs=[search_results]
            )
        
        # Statistics Tab
        with gr.TabItem("📊 Statistics"):
            gr.Markdown("### View session statistics and system information")
            
            stats_btn = gr.Button("📊 Get Statistics", variant="primary")
            stats_output = gr.Markdown(label="Statistics")
            
            stats_btn.click(
                fn=get_statistics,
                inputs=[],
                outputs=[stats_output]
            )
    
    gr.Markdown("""
    ---
    **Features:**
    - 🎙️ Audio transcription (MP3, WAV, M4A, OGG, FLAC)
    - 📄 Text processing (TXT, MD, RTF)
    - 🧠 AI-powered summarization and action item extraction
    - 🔍 Semantic search across all meetings
    - 👥 Session-based data isolation
    
    **Built with:** FastAPI, React, OpenAI Whisper, HuggingFace Transformers, FAISS
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
