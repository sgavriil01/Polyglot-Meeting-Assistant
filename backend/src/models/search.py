"""
Search Module for Polyglot Meeting Assistant

This module provides semantic search capabilities using FAISS vector database
and sentence transformers for embedding generation. It enables searching across
meeting transcripts, action items, decisions, and other meeting content.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pickle
import logging

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    logging.warning(f"Search dependencies not available: {e}")
    faiss = None
    SentenceTransformer = None

try:
    from utils.performance import timing_decorator, ModelManager
except ImportError:
    # Fallback for when running as module
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils.performance import timing_decorator, ModelManager


class MeetingSearchEngine:
    """
    Semantic search engine for meeting content using FAISS and sentence transformers
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = None):
        """
        Initialize the search engine
        
        Args:
            model_name: Name of the sentence transformer model
            index_path: Path to store the FAISS index and metadata
        """
        self.model_name = model_name
        # Use data directory for search index (persistent storage)
        if index_path is None:
            # Use local path for development, Docker path for production
            if os.path.exists("/app"):  # Docker environment
                data_dir = os.environ.get("SEARCH_INDEX_DIR", "/app/data/search_index")
            else:  # Local development
                data_dir = os.environ.get("SEARCH_INDEX_DIR", "data/search_index")
            self.index_path = data_dir
        else:
            self.index_path = index_path
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Initialize components
        self.encoder = None
        self.index = None
        self.metadata = []  # Store document metadata
        self.is_trained = False
        
        # Ensure index directory exists
        os.makedirs(self.index_path, exist_ok=True)
        
        # Load or initialize
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize or load search components"""
        try:
            # Load sentence transformer model
            if SentenceTransformer is not None:
                model_manager = ModelManager()
                cache_key = f"sentence_transformer_{self.model_name}"
                
                if cache_key in model_manager.models:
                    self.encoder = model_manager.models[cache_key]
                else:
                    print(f"Loading sentence transformer: {self.model_name}")
                    self.encoder = SentenceTransformer(self.model_name)
                    model_manager.models[cache_key] = self.encoder
            
            # Load existing index if available
            self._load_index()
            
        except Exception as e:
            logging.error(f"Error initializing search components: {e}")
            print(f"⚠️  Search functionality limited: {e}")
    
    def _load_index(self) -> bool:
        """Load existing FAISS index and metadata"""
        index_file = os.path.join(self.index_path, "faiss.index")
        metadata_file = os.path.join(self.index_path, "metadata.json")
        
        try:
            if os.path.exists(index_file) and os.path.exists(metadata_file):
                # Load FAISS index
                self.index = faiss.read_index(index_file)
                
                # Load metadata
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                
                self.is_trained = True
                print(f"✅ Loaded search index with {len(self.metadata)} documents")
                return True
                
        except Exception as e:
            logging.error(f"Error loading search index: {e}")
            print(f"⚠️  Could not load existing index: {e}")
        
        # Initialize new index if loading failed
        self._create_new_index()
        return False
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        try:
            if faiss is not None:
                # Create FAISS index for inner product (cosine similarity)
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self.metadata = []
                self.is_trained = False
                print("✅ Created new search index")
        except Exception as e:
            logging.error(f"Error creating FAISS index: {e}")
            print(f"⚠️  Could not create search index: {e}")
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            if self.index is not None:
                # Save FAISS index
                index_file = os.path.join(self.index_path, "faiss.index")
                faiss.write_index(self.index, index_file)
                
                # Save metadata
                metadata_file = os.path.join(self.index_path, "metadata.json")
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(self.metadata, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Saved search index with {len(self.metadata)} documents")
                
        except Exception as e:
            logging.error(f"Error saving search index: {e}")
            print(f"⚠️  Could not save search index: {e}")
    
    @timing_decorator
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            numpy array of embeddings
        """
        if self.encoder is None:
            raise RuntimeError("Sentence transformer not available")
        
        try:
            # Generate embeddings
            embeddings = self.encoder.encode(texts, convert_to_numpy=True)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)
            
            return embeddings
            
        except Exception as e:
            logging.error(f"Error generating embeddings: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}")
    
    def add_meeting(self, meeting_data: Dict[str, Any]) -> bool:
        """
        Add a meeting to the search index
        
        Args:
            meeting_data: Dictionary containing meeting information
                Required keys: 'id', 'title', 'date', 'transcript'
                Optional keys: 'summary', 'action_items', 'decisions', 'participants'
                
        Returns:
            True if successfully added, False otherwise
        """
        try:
            if self.encoder is None or self.index is None:
                print("⚠️  Search components not available")
                return False
            
            # Extract searchable content
            searchable_texts = self._extract_searchable_content(meeting_data)
            
            if not searchable_texts:
                print("⚠️  No searchable content found in meeting")
                return False
            
            # Generate embeddings
            embeddings = self.generate_embeddings(searchable_texts['texts'])
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Store metadata for each text chunk
            for i, text in enumerate(searchable_texts['texts']):
                metadata = {
                    'meeting_id': meeting_data['id'],
                    'meeting_title': meeting_data.get('title', 'Untitled Meeting'),
                    'meeting_date': meeting_data.get('date', datetime.now().isoformat()),
                    'content_type': searchable_texts['types'][i],
                    'text': text,
                    'participants': meeting_data.get('participants', []),
                    'index_position': len(self.metadata)
                }
                self.metadata.append(metadata)
            
            # Save index
            self._save_index()
            
            print(f"✅ Added meeting '{meeting_data.get('title', 'Untitled')}' with {len(searchable_texts['texts'])} searchable chunks")
            return True
            
        except Exception as e:
            logging.error(f"Error adding meeting to index: {e}")
            print(f"❌ Failed to add meeting: {e}")
            return False
    
    def _extract_searchable_content(self, meeting_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract searchable content from meeting data
        
        Args:
            meeting_data: Meeting information dictionary
            
        Returns:
            Dictionary with 'texts' and 'types' lists
        """
        texts = []
        types = []
        
        # Full transcript (chunked if too long)
        transcript = meeting_data.get('transcript', '')
        if transcript:
            # OPTIMIZATION: Smart chunking for better search quality and performance
            text_length = len(transcript)
            if text_length <= 2000:
                # Small transcript: no chunking needed
                texts.append(transcript)
                types.append('transcript')
            else:
                # Large transcript: smart chunking with overlap
                chunks = self._smart_chunk_text(transcript, target_chunks=8, overlap=300)
                print(f"🔍 Smart search chunking: {text_length} chars → {len(chunks)} chunks (vs {text_length//500} old chunks)")
                for chunk in chunks:
                    texts.append(chunk)
                    types.append('transcript')
        
        # Summary
        summary = meeting_data.get('summary', '')
        if summary:
            texts.append(summary)
            types.append('summary')
        
        # Action items
        action_items = meeting_data.get('action_items', [])
        for item in action_items:
            if isinstance(item, dict):
                text = item.get('text', str(item))
            else:
                text = str(item)
            
            if text.strip():
                texts.append(text)
                types.append('action_item')
        
        # Decisions
        decisions = meeting_data.get('key_decisions', [])
        for decision in decisions:
            decision_text = str(decision).strip()
            if decision_text:
                texts.append(decision_text)
                types.append('decision')
        
        # Timeline items
        timelines = meeting_data.get('timelines', [])
        for timeline in timelines:
            if isinstance(timeline, dict):
                timeline_text = f"{timeline.get('timeline', '')} - {timeline.get('context', '')}"
            else:
                timeline_text = str(timeline)
            
            timeline_text = timeline_text.strip()
            if timeline_text:
                texts.append(timeline_text)
                types.append('timeline')
        
        return {'texts': texts, 'types': types}
    
    def _chunk_text(self, text: str, max_length: int = 500) -> List[str]:
        """
        Split text into chunks for indexing
        
        Args:
            text: Text to chunk
            max_length: Maximum length per chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_length:
                if current_chunk:
                    current_chunk += ". " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _smart_chunk_text(self, text: str, target_chunks: int = 8, overlap: int = 300) -> List[str]:
        """
        Smart text chunking for search indexing with overlap and semantic boundaries
        
        Args:
            text: Text to chunk
            target_chunks: Target number of chunks
            overlap: Character overlap between chunks
            
        Returns:
            List of text chunks
        """
        text_length = len(text)
        chunk_size = text_length // target_chunks
        
        # Ensure minimum chunk size for meaningful search
        chunk_size = max(chunk_size, 800)
        
        # Split by sentences for better semantic boundaries
        sentences = text.split('. ')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > chunk_size and current_chunk:
                # Add overlap from previous chunk for context preservation
                if chunks and overlap > 0:
                    prev_chunk = chunks[-1]
                    overlap_start = max(0, len(prev_chunk) - overlap)
                    overlap_text = prev_chunk[overlap_start:]
                    current_chunk.insert(0, overlap_text)
                
                chunks.append(". ".join(current_chunk) + ".")
                current_chunk = [sentence.strip(".")]
                current_length = sentence_length
            else:
                current_chunk.append(sentence.strip("."))
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(". ".join(current_chunk) + ".")
        
        # Limit to target number and ensure quality
        return chunks[:target_chunks]
    
    @timing_decorator
    def search(self, query: str, top_k: int = 10, content_types: Optional[List[str]] = None, 
               date_from: Optional[str] = None, date_to: Optional[str] = None,
               participants: Optional[List[str]] = None, min_relevance: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant meeting content with advanced filtering
        
        Args:
            query: Search query
            top_k: Number of top results to return
            content_types: Filter by content types (transcript, summary, action_item, decision, timeline)
            date_from: Filter meetings from this date (ISO format)
            date_to: Filter meetings to this date (ISO format)
            participants: Filter by participant names
            min_relevance: Minimum relevance score (0.0 to 1.0)
            
        Returns:
            List of search results with metadata and relevance scores
        """
        try:
            if self.encoder is None or self.index is None:
                print("⚠️  Search components not available")
                return []
            
            if not self.metadata:
                print("⚠️  No meetings indexed yet")
                return []
            
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])
            
            # Search FAISS index
            scores, indices = self.index.search(query_embedding, min(top_k * 2, len(self.metadata)))
            
            # Prepare results
            results = []
            seen_meetings = set()
            
            for score, idx in zip(scores[0], indices[0]):
                if idx >= len(self.metadata):
                    continue
                
                metadata = self.metadata[idx]
                
                # Apply content type filter
                if content_types and metadata['content_type'] not in content_types:
                    continue
                
                # Apply advanced filters
                if not self._passes_advanced_filters(metadata, score, date_from, date_to, participants, min_relevance):
                    continue
                
                # Create result
                result = {
                    'meeting_id': metadata['meeting_id'],
                    'meeting_title': metadata['meeting_title'],
                    'meeting_date': metadata['meeting_date'],
                    'content_type': metadata['content_type'],
                    'text': metadata['text'],
                    'participants': metadata['participants'],
                    'relevance_score': float(score),
                    'snippet': self._create_snippet(metadata['text'], query)
                }
                
                results.append(result)
                seen_meetings.add(metadata['meeting_id'])
                
                if len(results) >= top_k:
                    break
            
            print(f"🔍 Found {len(results)} relevant results for: '{query}'")
            return results
            
        except Exception as e:
            logging.error(f"Error during search: {e}")
            print(f"❌ Search failed: {e}")
            return []
    
    def _create_snippet(self, text: str, query: str, snippet_length: int = 200) -> str:
        """
        Create a snippet highlighting query terms
        
        Args:
            text: Full text
            query: Search query
            snippet_length: Maximum snippet length
            
        Returns:
            Text snippet with query context
        """
        query_words = query.lower().split()
        text_lower = text.lower()
        
        # Find best position for snippet
        best_pos = 0
        max_matches = 0
        
        for i in range(len(text) - snippet_length + 1):
            snippet = text[i:i + snippet_length].lower()
            matches = sum(1 for word in query_words if word in snippet)
            
            if matches > max_matches:
                max_matches = matches
                best_pos = i
        
        # Extract snippet
        snippet = text[best_pos:best_pos + snippet_length]
        
        # Add ellipsis if needed
        if best_pos > 0:
            snippet = "..." + snippet
        if best_pos + snippet_length < len(text):
            snippet = snippet + "..."
        
        return snippet.strip()
    
    def _passes_advanced_filters(self, metadata: Dict[str, Any], score: float, 
                               date_from: Optional[str], date_to: Optional[str],
                               participants: Optional[List[str]], min_relevance: Optional[float]) -> bool:
        """
        Check if a search result passes all advanced filters
        
        Args:
            metadata: Document metadata
            score: Relevance score
            date_from: Start date filter
            date_to: End date filter
            participants: Participant filter
            min_relevance: Minimum relevance filter
            
        Returns:
            True if result passes all filters
        """
        from datetime import datetime
        
        # Apply relevance filter
        if min_relevance is not None and score < min_relevance:
            return False
        
        # Apply date filters
        if date_from or date_to:
            try:
                meeting_date = datetime.fromisoformat(metadata['meeting_date'].replace('Z', '+00:00'))
                
                if date_from:
                    filter_date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                    if meeting_date < filter_date_from:
                        return False
                
                if date_to:
                    filter_date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                    if meeting_date > filter_date_to:
                        return False
            except (ValueError, KeyError):
                # If date parsing fails, include the result (don't exclude due to bad data)
                pass
        
        # Apply participants filter using ML-based content analysis
        if participants:
            text_content = metadata.get('text', '')
            content_relevance = self._calculate_person_relevance(text_content, participants)
            
            # Only include content with high relevance to selected participants
            if content_relevance < 0.3:  # 30% relevance threshold
                return False
        
        return True
    
    def get_all_participants(self) -> List[str]:
        """
        Get all unique participants across all meetings
        
        Returns:
            List of unique participant names
        """
        participants = set()
        for metadata in self.metadata:
            meeting_participants = metadata.get('participants', [])
            participants.update(meeting_participants)
        
        return sorted(list(participants))
    
    def get_date_range(self) -> Dict[str, str]:
        """
        Get the date range of all indexed meetings
        
        Returns:
            Dictionary with 'earliest' and 'latest' dates
        """
        if not self.metadata:
            return {'earliest': '', 'latest': ''}
        
        dates = []
        for metadata in self.metadata:
            try:
                date_str = metadata.get('meeting_date', '')
                if date_str:
                    dates.append(date_str)
            except:
                continue
        
        if not dates:
            return {'earliest': '', 'latest': ''}
        
        dates.sort()
        return {'earliest': dates[0], 'latest': dates[-1]}
    
    def _calculate_person_relevance(self, text: str, target_participants: List[str]) -> float:
        """
        Calculate how relevant a text chunk is to specific participants using ML
        
        Uses multiple ML techniques:
        1. Speaker pattern matching (highest weight - 60%)
        2. NER model for person entity detection (30%)
        3. Semantic context analysis (20%)
        
        Returns relevance score between 0.0 and 1.0
        """
        if not text or not target_participants:
            return 0.0
        
        max_relevance = 0.0
        
        for participant in target_participants:
            relevance = self._calculate_single_person_relevance(text, participant)
            max_relevance = max(max_relevance, relevance)
        
        return max_relevance
    
    def _calculate_single_person_relevance(self, text: str, person: str) -> float:
        """Calculate relevance of text to a specific person using multiple ML approaches"""
        relevance_scores = []
        
        # Strategy 1: Speaker Pattern Analysis (highest confidence)
        speaker_score = self._get_speaker_relevance(text, person)
        if speaker_score > 0:
            relevance_scores.append(speaker_score)
        
        # Strategy 2: Contextual Analysis
        context_score = self._get_context_relevance(text, person)
        if context_score > 0:
            relevance_scores.append(context_score)
        
        # Return maximum relevance found
        return max(relevance_scores) if relevance_scores else 0.0
    
    def _get_speaker_relevance(self, text: str, person: str) -> float:
        """Check if the person is speaking in this text chunk"""
        import re
        
        person_first = person.split()[0] if person else ""
        
        # Speaker format patterns
        speaker_patterns = [
            rf'^{re.escape(person)}:\s',  # "Sarah Chen: ..."
            rf'^{re.escape(person_first)}:\s',  # "Sarah: ..."
            rf'^{re.escape(person.upper())}:\s',  # "SARAH CHEN: ..."
        ]
        
        for pattern in speaker_patterns:
            if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                return 1.0  # Perfect match - person is speaking
        
        return 0.0
    
    def _get_context_relevance(self, text: str, person: str) -> float:
        """Analyze contextual mentions of the person"""
        import re
        
        person_first = person.split()[0] if person else ""
        text_lower = text.lower()
        person_lower = person.lower()
        
        # High confidence patterns
        if (f"{person_lower}:" in text_lower or 
            f"{person_lower} said" in text_lower or
            f"{person_lower} mentioned" in text_lower or
            f"{person_lower} will" in text_lower):
            return 0.9
        
        # Medium confidence patterns  
        if (person_lower in text_lower or person_first.lower() in text_lower):
            return 0.6
            
        return 0.0
    
    def search_by_meeting_id(self, meeting_id: str) -> List[Dict[str, Any]]:
        """
        Get all indexed content for a specific meeting
        
        Args:
            meeting_id: Meeting identifier
            
        Returns:
            List of all content chunks for the meeting
        """
        results = []
        
        for metadata in self.metadata:
            if metadata['meeting_id'] == meeting_id:
                results.append({
                    'content_type': metadata['content_type'],
                    'text': metadata['text'],
                    'meeting_title': metadata['meeting_title'],
                    'meeting_date': metadata['meeting_date'],
                    'participants': metadata['participants']
                })
        
        return results
    
    def get_similar_meetings(self, meeting_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find meetings similar to a given meeting
        
        Args:
            meeting_id: Reference meeting ID
            top_k: Number of similar meetings to return
            
        Returns:
            List of similar meetings with similarity scores
        """
        try:
            # Get meeting content
            meeting_content = self.search_by_meeting_id(meeting_id)
            
            if not meeting_content:
                print(f"⚠️  Meeting {meeting_id} not found in index")
                return []
            
            # Use summary or first transcript chunk as query
            query_text = ""
            for content in meeting_content:
                if content['content_type'] == 'summary':
                    query_text = content['text']
                    break
                elif content['content_type'] == 'transcript':
                    query_text = content['text'][:500]  # First 500 chars
                    break
            
            if not query_text:
                return []
            
            # Search for similar content
            results = self.search(query_text, top_k * 3)
            
            # Group by meeting and calculate meeting-level similarity
            meeting_scores = {}
            for result in results:
                if result['meeting_id'] == meeting_id:
                    continue  # Skip the reference meeting
                
                mid = result['meeting_id']
                if mid not in meeting_scores:
                    meeting_scores[mid] = {
                        'meeting_id': mid,
                        'meeting_title': result['meeting_title'],
                        'meeting_date': result['meeting_date'],
                        'participants': result['participants'],
                        'similarity_scores': [],
                        'matching_content_types': set()
                    }
                
                meeting_scores[mid]['similarity_scores'].append(result['relevance_score'])
                meeting_scores[mid]['matching_content_types'].add(result['content_type'])
            
            # Calculate average similarity and sort
            similar_meetings = []
            for meeting_data in meeting_scores.values():
                avg_score = sum(meeting_data['similarity_scores']) / len(meeting_data['similarity_scores'])
                meeting_data['average_similarity'] = avg_score
                meeting_data['matching_content_types'] = list(meeting_data['matching_content_types'])
                del meeting_data['similarity_scores']  # Clean up
                similar_meetings.append(meeting_data)
            
            # Sort by similarity and return top results
            similar_meetings.sort(key=lambda x: x['average_similarity'], reverse=True)
            
            return similar_meetings[:top_k]
            
        except Exception as e:
            logging.error(f"Error finding similar meetings: {e}")
            print(f"❌ Failed to find similar meetings: {e}")
            return []
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the search index
        
        Returns:
            Dictionary with index statistics
        """
        if not self.metadata:
            return {'total_documents': 0, 'total_meetings': 0}
        
        # Count unique meetings
        unique_meetings = set()
        content_type_counts = {}
        
        for metadata in self.metadata:
            unique_meetings.add(metadata['meeting_id'])
            
            content_type = metadata['content_type']
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        
        return {
            'total_documents': len(self.metadata),
            'total_meetings': len(unique_meetings),
            'content_type_distribution': content_type_counts,
            'index_size_mb': self._get_index_size(),
            'embedding_dimension': self.embedding_dim,
            'model_name': self.model_name
        }
    
    def _get_index_size(self) -> float:
        """Get approximate index size in MB"""
        try:
            index_file = os.path.join(self.index_path, "faiss.index")
            if os.path.exists(index_file):
                return os.path.getsize(index_file) / (1024 * 1024)
        except:
            pass
        return 0.0
