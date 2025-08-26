#!/usr/bin/env python3
"""
HuggingFace Spaces Deployment for Polyglot Meeting Assistant

This file enables deployment to HuggingFace Spaces for free hosting.
"""

import gradio as gr
import subprocess
import threading
import time
import requests
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend" / "src"))

def start_fastapi_server():
    """Start FastAPI server in background"""
    try:
        import uvicorn
        from api import app
        
        # Run FastAPI on port 8000
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")

def wait_for_server(url="http://localhost:8000/api/v1/health", timeout=30):
    """Wait for FastAPI server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def create_gradio_interface():
    """Create Gradio interface for the meeting assistant"""
    
    def process_audio_file(audio_file):
        """Process uploaded audio file"""
        if audio_file is None:
            return "No file uploaded", "", "", ""
        
        try:
            # Use the FastAPI backend
            with open(audio_file, "rb") as f:
                files = {"file": (os.path.basename(audio_file), f, "audio/mpeg")}
                response = requests.post("http://localhost:8000/api/v1/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                # Format action items
                action_items = result.get('action_items', [])
                action_items_text = "\n".join([
                    f"• {item['text']} (confidence: {item['confidence']:.2f})"
                    for item in action_items
                ]) if action_items else "No action items detected"
                
                return (
                    result.get('transcript', ''),
                    result.get('language', 'Unknown'),
                    result.get('summary', ''),
                    action_items_text
                )
            else:
                return f"Error: {response.text}", "", "", ""
                
        except Exception as e:
            return f"Error: {str(e)}", "", "", ""

    def search_meetings(query):
        """Search through meeting transcripts"""
        if not query.strip():
            return "Please enter a search query"
        
        try:
            response = requests.post("http://localhost:8000/api/v1/search", 
                                   json={"query": query, "top_k": 5})
            
            if response.status_code == 200:
                results = response.json()
                
                if not results.get('results'):
                    return "No results found"
                
                formatted_results = []
                for i, result in enumerate(results['results'][:5], 1):
                    formatted_results.append(
                        f"{i}. **Score: {result['relevance_score']:.3f}** | {result['meeting_title']}\n"
                        f"   {result['snippet'][:200]}...\n"
                    )
                
                return "\n".join(formatted_results)
            else:
                return f"Search error: {response.text}"
                
        except Exception as e:
            return f"Search error: {str(e)}"

    def get_statistics():
        """Get system statistics"""
        try:
            response = requests.get("http://localhost:8000/api/v1/statistics")
            
            if response.status_code == 200:
                stats = response.json()
                return f"""
**System Statistics:**
- Total Meetings: {stats.get('total_meetings', 0)}
- Total Documents: {stats.get('total_documents', 0)}
- Index Size: {stats.get('index_size_mb', 0):.2f} MB
- Model: {stats.get('model_name', 'Unknown')}
                """
            else:
                return f"Error loading statistics: {response.text}"
                
        except Exception as e:
            return f"Error: {str(e)}"

    # Create Gradio interface
    with gr.Blocks(title="Polyglot Meeting Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎙️ Polyglot Meeting Assistant")
        gr.Markdown("Upload meeting recordings for automatic transcription, summarization, and intelligent search.")
        
        with gr.Tab("📁 Upload & Process"):
            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(
                        label="Upload Meeting Recording",
                        type="filepath"
                    )
                    process_btn = gr.Button("Process Recording", variant="primary")
                
                with gr.Column():
                    language_output = gr.Textbox(label="Detected Language", interactive=False)
                    transcript_output = gr.Textbox(
                        label="Full Transcript", 
                        lines=8, 
                        interactive=False
                    )
            
            with gr.Row():
                summary_output = gr.Textbox(
                    label="Meeting Summary", 
                    lines=4, 
                    interactive=False
                )
                actions_output = gr.Textbox(
                    label="Action Items", 
                    lines=4, 
                    interactive=False
                )
            
            process_btn.click(
                fn=process_audio_file,
                inputs=[audio_input],
                outputs=[transcript_output, language_output, summary_output, actions_output]
            )
        
        with gr.Tab("🔍 Search Meetings"):
            with gr.Row():
                search_input = gr.Textbox(
                    label="Search Query",
                    placeholder="e.g., 'budget discussion' or 'action items for next week'"
                )
                search_btn = gr.Button("Search", variant="primary")
            
            search_output = gr.Textbox(
                label="Search Results",
                lines=10,
                interactive=False
            )
            
            search_btn.click(
                fn=search_meetings,
                inputs=[search_input],
                outputs=[search_output]
            )
        
        with gr.Tab("📊 Statistics"):
            with gr.Column():
                refresh_btn = gr.Button("Refresh Statistics", variant="secondary")
                stats_output = gr.Markdown(label="System Statistics")
                
                refresh_btn.click(
                    fn=get_statistics,
                    outputs=[stats_output]
                )
                
                # Auto-load on tab open
                app.load(get_statistics, outputs=[stats_output])
    
    return app

if __name__ == "__main__":
    # Start FastAPI in background thread
    print("🚀 Starting Polyglot Meeting Assistant...")
    fastapi_thread = threading.Thread(target=start_fastapi_server, daemon=True)
    fastapi_thread.start()
    
    # Wait for server to be ready
    if wait_for_server():
        print("✅ FastAPI server is ready!")
    else:
        print("❌ FastAPI server failed to start")
    
    # Launch Gradio interface
    interface = create_gradio_interface()
    interface.launch(
        share=False,  # HF Spaces handles sharing
        server_port=7860,
        server_name="0.0.0.0"
    )
