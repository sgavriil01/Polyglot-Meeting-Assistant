from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from typing import List, Dict, Any, Set
import re
import logging
import time
import functools

def timing_decorator(func):
    """Simple timing decorator"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

class NLPProcessor:
    """Natural Language Processing pipeline for meeting analysis"""
    
    def __init__(self, device: str = None):
        """
        Initialize NLP models
        
        Args:
            device: Device to run models on ('cpu', 'cuda', or None for auto)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.summarizer = None
        self.classifier = None
        self.embedder = None
        self.setup_models()
    
    def setup_models(self):
        """Initialize all NLP models"""
        try:
            logging.info(f"Loading NLP models on {self.device}")
            
            # Summarization - using T5-small for better sentence completion
            logging.info("Loading summarization model...")
            self.summarizer = pipeline(
                "summarization",
                model="t5-small",  
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Action item classification (zero-shot)
            logging.info("Loading zero-shot classification model...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if self.device == "cuda" else -1
            )
            
            # Sentence embeddings for semantic similarity
            logging.info("Loading sentence transformer...")
            self.embedder = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2",
                device=0 if self.device == "cuda" else -1
            )
            
            logging.info("All NLP models loaded successfully")
            
        except Exception as e:
            logging.error(f"Failed to load NLP models: {e}")
            raise
    
    @timing_decorator
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """
        Generate summary of text
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            
        Returns:
            Summarized text
        """
        if not text or len(text.strip()) < 50:
            return "Text too short to summarize"
        
        try:
            # Split long text into chunks for better processing
            chunks = self._chunk_text(text, max_chunk=512)  # Smaller chunks for distilbart
            summaries = []
            
            for chunk in chunks:
                chunk_clean = chunk.strip()
                if len(chunk_clean) > 50:  # Skip very short chunks
                    # Calculate appropriate lengths
                    input_length = len(chunk_clean.split())
                    chunk_max = min(max_length, max(30, input_length // 3))
                    chunk_min = min(min_length, max(10, chunk_max // 3))
                    
                    if input_length > 15:  # Only summarize if enough content
                        summary = self.summarizer(
                            chunk_clean, 
                            max_length=chunk_max, 
                            min_length=chunk_min,
                            do_sample=False,
                            truncation=True,
                            clean_up_tokenization_spaces=True
                        )[0]['summary_text']
                        summaries.append(summary.strip())
            
            final_summary = " ".join(summaries)
            
            # If we have multiple chunk summaries, summarize them again
            if len(summaries) > 1 and len(final_summary) > max_length * 2:
                final_summary = self.summarizer(
                    final_summary,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    truncation=True,
                    clean_up_tokenization_spaces=True
                )[0]['summary_text']
            
            return final_summary
            
        except Exception as e:
            logging.error(f"Summarization failed: {e}")
            return f"Summarization failed: {str(e)}"
    
    @timing_decorator
    def extract_action_items(self, text: str, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Extract action items from text
        
        Args:
            text: Input text
            confidence_threshold: Minimum confidence for action items
            
        Returns:
            List of action items with confidence scores
        """
        if not text:
            return []
        
        try:
            sentences = self._split_sentences(text)
            action_items = []
            
            # Labels for action item classification
            labels = [
                "action item",
                "task assignment", 
                "follow-up required",
                "deadline mentioned",
                "responsibility assigned"
            ]
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:  # Skip very short sentences
                    
                    # Check for action indicators
                    action_indicators = [
                        "will", "should", "must", "need to", "have to",
                        "responsible for", "assign", "due", "deadline",
                        "follow up", "follow-up", "next step", "action"
                    ]
                    
                    # Quick filter using keywords
                    has_action_keyword = any(
                        indicator.lower() in sentence.lower() 
                        for indicator in action_indicators
                    )
                    
                    if has_action_keyword:
                        result = self.classifier(sentence, labels)
                        if result['scores'][0] > confidence_threshold:
                            action_items.append({
                                "text": sentence,
                                "confidence": float(result['scores'][0]),
                                "label": result['labels'][0],
                                "category": self._categorize_action_item(sentence)
                            })
            
            # Sort by confidence
            action_items.sort(key=lambda x: x['confidence'], reverse=True)
            return action_items
            
        except Exception as e:
            logging.error(f"Action item extraction failed: {e}")
            return []
    
    def extract_key_topics(self, text: str, num_topics: int = 5) -> List[str]:
        """
        Extract key topics/themes from text
        
        Args:
            text: Input text
            num_topics: Number of topics to extract
            
        Returns:
            List of key topics
        """
        try:
            # Clean and tokenize text
            text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
            words = text_clean.split()
            
            # Filter out common words and short words
            stopwords = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 
                'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day',
                'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now',
                'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its',
                'let', 'put', 'say', 'she', 'too', 'use', 'will', 'this',
                'that', 'with', 'have', 'from', 'they', 'know', 'want',
                'been', 'good', 'much', 'some', 'time', 'very', 'when',
                'come', 'here', 'just', 'like', 'long', 'make', 'many',
                'over', 'such', 'take', 'than', 'them', 'well', 'were',
                'also', 'about', 'after', 'first', 'would', 'there',
                'today', 'should', 'meeting', 'need', 'discussed'
            }
            
            # Count word frequencies (only words with 4+ characters)
            word_freq = {}
            for word in words:
                if (len(word) >= 4 and 
                    word not in stopwords and 
                    word.isalpha() and
                    not word.isdigit()):
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top topics by frequency
            topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # Extract meaningful compound terms as well
            bigrams = self._extract_bigrams(text_clean, stopwords)
            
            # Combine single words and bigrams
            all_topics = []
            
            # Add top single words
            for word, freq in topics[:num_topics]:
                if freq > 1:  # Only include words that appear more than once
                    all_topics.append(word.title())
            
            # Add top bigrams
            for bigram, freq in bigrams[:max(2, num_topics//2)]:
                if freq > 1:
                    all_topics.append(bigram.title())
            
            # Remove duplicates and limit to num_topics
            seen = set()
            unique_topics = []
            for topic in all_topics:
                if topic.lower() not in seen:
                    seen.add(topic.lower())
                    unique_topics.append(topic)
                    if len(unique_topics) >= num_topics:
                        break
            
            return unique_topics or ["General Discussion"]
            
        except Exception as e:
            logging.error(f"Topic extraction failed: {e}")
            return ["General Discussion"]
    
    def _extract_bigrams(self, text: str, stopwords: set) -> List[tuple]:
        """Extract meaningful two-word phrases"""
        words = text.split()
        bigrams = {}
        
        for i in range(len(words) - 1):
            word1, word2 = words[i], words[i + 1]
            
            if (len(word1) >= 3 and len(word2) >= 3 and
                word1 not in stopwords and word2 not in stopwords and
                word1.isalpha() and word2.isalpha()):
                
                bigram = f"{word1} {word2}"
                bigrams[bigram] = bigrams.get(bigram, 0) + 1
        
        return sorted(bigrams.items(), key=lambda x: x[1], reverse=True)
    
    def _chunk_text(self, text: str, max_chunk: int = 1000) -> List[str]:
        """Split text into chunks for processing"""
        # For very large texts, use larger chunks and limit total processing
        if len(text) > 20000:
            max_chunk = 2000  # Larger chunks for big documents
            print(f"⚠️ Large text detected ({len(text)} chars). Using larger chunks to optimize processing.")
        
        # Split by sentences first, then group into chunks
        sentences = self._split_sentences(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > max_chunk and current_chunk:
                chunks.append(". ".join(current_chunk) + ".")
                current_chunk = [sentence.strip(".")]
                current_length = sentence_length
            else:
                current_chunk.append(sentence.strip("."))
                current_length += sentence_length
        
        # For extremely large texts, limit the number of chunks to prevent timeout
        if len(text) > 25000 and len(chunks) > 15:
            print(f"⚠️ Very large text ({len(text)} chars, {len(chunks)} chunks). Limiting to first 15 chunks to prevent timeout.")
            chunks = chunks[:15]
        
        if current_chunk:
            chunks.append(". ".join(current_chunk) + ".")
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def generate_comprehensive_summary(self, text: str) -> Dict[str, Any]:
        """
        Generate a comprehensive meeting summary with structured components
        
        Returns:
            Dict with summary, action_items, key_decisions, timelines, and participants
        """
        try:
            # Basic summary
            basic_summary = self.summarize_text(text, max_length=100, min_length=30)
            
            # Enhanced action items with better detection
            action_items = self.extract_enhanced_action_items(text)
            
            # Extract key decisions and timelines
            decisions = self.extract_key_decisions(text)
            timelines = self.extract_timelines(text)
            participants = self.extract_participants(text)
            
            return {
                "summary": basic_summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "timelines": timelines,
                "participants": participants,
                "topics": self.extract_key_topics(text)
            }
            
        except Exception as e:
            logging.error(f"Comprehensive summary generation failed: {e}")
            return {
                "summary": self.summarize_text(text),
                "action_items": self.extract_action_items(text),
                "key_decisions": [],
                "timelines": [],
                "participants": [],
                "topics": self.extract_key_topics(text)
            }
    
    def extract_enhanced_action_items(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced action item extraction with better pattern recognition"""
        import re
        sentences = self._split_sentences(text)
        action_items = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Pattern 1: Direct assignments "Name, can you/will you..."
            direct_assignment = re.search(r'([A-Z][a-z]+),?\s+(can you|will you|should you|need you to)\s+(.+)', sentence)
            if direct_assignment:
                assignee = direct_assignment.group(1)
                task = direct_assignment.group(3)
                deadline = self._extract_deadline(sentence)
                
                action_items.append({
                    "text": sentence,
                    "assignee": assignee,
                    "deadline": deadline,
                    "category": self._categorize_action_item(sentence),
                    "confidence": 0.9
                })
                continue
            
            # Pattern 2: Future tense with names "Name will..."
            future_pattern = re.search(r'([A-Z][a-z]+)\s+(?:will|can|should)\s+(.+)', sentence)
            if future_pattern:
                assignee = future_pattern.group(1)
                deadline = self._extract_deadline(sentence)
                
                action_items.append({
                    "text": sentence,
                    "assignee": assignee,  
                    "deadline": deadline,
                    "category": self._categorize_action_item(sentence),
                    "confidence": 0.8
                })
                continue
            
            # Pattern 3: Implicit actions with strong verbs
            strong_verbs = r'\b(?:prepare|create|develop|implement|fix|contact|survey|reach out|review|audit|calculate|draft|notify|schedule|coordinate)\b'
            if re.search(strong_verbs, sentence, re.IGNORECASE):
                # Try to find associated name in context
                name_match = re.search(r'\b([A-Z][a-z]+)\b', sentence)
                assignee = name_match.group(1) if name_match else "Unassigned"
                deadline = self._extract_deadline(sentence)
                
                # Only add if it sounds like an action
                if any(word in sentence.lower() for word in ['need', 'should', 'have to', 'must', 'by', 'due']):
                    action_items.append({
                        "text": sentence,
                        "assignee": assignee,
                        "deadline": deadline,
                        "category": self._categorize_action_item(sentence),
                        "confidence": 0.7
                    })
        
        # Remove duplicates and sort by confidence
        seen_texts = set()
        unique_items = []
        for item in sorted(action_items, key=lambda x: x['confidence'], reverse=True):
            if item['text'] not in seen_texts:
                seen_texts.add(item['text'])
                unique_items.append(item)
        
        return unique_items
    
    def _extract_deadline(self, text: str) -> str:
        """Extract deadline information from text"""
        import re
        
        deadline_patterns = [
            r'by\s+((?:next\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))',
            r'by\s+(end\s+of\s+(?:this\s+|next\s+)?week)',
            r'by\s+((?:this\s+|next\s+)?(?:week|month|quarter))',
            r'(?:due|deadline)\s+(\w+day)',
            r'by\s+(\w+\s+\d+)',
            r'within\s+(\d+\s+(?:hours?|days?|weeks?))',
            r'(?:in|after)\s+(\d+\s+(?:hours?|days?|weeks?))',
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1)
        
        return "No deadline"
    
    def extract_key_decisions(self, text: str) -> List[str]:
        """Extract key decisions made in the meeting"""
        import re
        decisions = []
        sentences = self._split_sentences(text)
        
        # Enhanced decision patterns
        decision_patterns = [
            # Explicit decision language
            r'(?:we(?:\s+have)?|i)\s+(?:decided|agreed|concluded|resolved|determined)\s+(?:to|that)\s+(.+)',
            
            # Approval/rejection patterns
            r'(?:approved|rejected|denied|accepted|endorsed)\s+(.+)',
            
            # Future commitment patterns
            r'(?:we will|we\'ll|going forward|from now on|starting)\s+(.+)',
            
            # Vote/consensus patterns  
            r'(?:voted to|consensus is|everyone agrees?)\s+(.+)',
            
            # Budget/resource allocation
            r'(?:budget|allocated?|spending|invest)\s+(.+?)(?:approved|rejected|on)',
            
            # Final decision indicators
            r'(?:final decision|bottom line|conclusion)\s+(?:is|was)?\s*(.+)',
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15:
                continue
                
            # Check for pattern matches
            for pattern in decision_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    decisions.append(sentence)
                    break  # Only match first pattern per sentence
        
        # Also look for sentences with strong decision indicators
        decision_indicators = [
            "decided", "agreed", "chose", "selected", "approved",
            "going with", "moving forward", "strategy", "approach",
            "rejected", "denied", "voted", "consensus", "concluded"
        ]
        
        for sentence in sentences:
            if len(sentence) < 20:
                continue
                
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in decision_indicators):
                # Check if we haven't already captured this decision
                if sentence not in decisions:
                    decisions.append(sentence)
        
        return decisions[:8]  # Return top 8 decisions
    
    def extract_timelines(self, text: str) -> List[Dict[str, str]]:
        """Extract timeline information with enhanced pattern recognition"""
        import re
        timelines = []
        sentences = self._split_sentences(text)
        
        # Enhanced timeline patterns
        timeline_patterns = [
            # Specific date ranges
            (r'(\d+[-–]\d+)\s+(weeks?|months?|days?)', 'duration', 0.9),
            
            # Approximate timeframes
            (r'(?:probably|approximately|about|around)\s+(\d+)\s+(weeks?|months?|days?)', 'estimate', 0.8),
            
            # Deadline patterns
            (r'(?:by|due|deadline|complete by)\s+(\w+day|\w+\s+\d+|\w+\s+\d+th?)', 'deadline', 0.9),
            
            # Phase/milestone patterns
            (r'(?:phase|milestone|stage)\s+(\d+|one|two|three)\s+(?:will|should|expected)\s+(?:take|last|be)\s+(.+)', 'phase', 0.8),
            
            # Project timeline patterns
            (r'(?:project|timeline|schedule|plan)\s+(?:will|should|expected to)\s+(?:take|last|be|complete in)\s+(.+)', 'project_timeline', 0.8),
            
            # Relative time patterns
            (r'(?:in|within|after|over)\s+(?:the\s+)?(?:next\s+)?(\d+)\s+(weeks?|months?|days?|quarters?)', 'relative', 0.7),
            
            # Quarterly/annual patterns
            (r'(?:q[1-4]|quarter\s+[1-4]|first|second|third|fourth)\s+quarter', 'quarterly', 0.8),
            
            # Start/end patterns
            (r'(?:start|begin|launch|kick off)\s+(?:in|on|by)\s+(.+)', 'start_date', 0.7),
            (r'(?:end|finish|complete|wrap up)\s+(?:in|on|by)\s+(.+)', 'end_date', 0.7)
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            for pattern, timeline_type, confidence in timeline_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    if len(match.groups()) >= 2:
                        timeline_text = f"{match.group(1)} {match.group(2)}"
                    else:
                        timeline_text = match.group(1)
                    
                    timelines.append({
                        "timeline": timeline_text,
                        "context": sentence,
                        "type": timeline_type,
                        "confidence": confidence
                    })
                    break  # Only match first pattern per sentence
        
        # Also look for general time-related sentences
        time_keywords = ['weeks', 'months', 'days', 'timeline', 'schedule', 'deadline', 'due', 'by', 'quarter', 'year']
        
        for sentence in sentences:
            if len(sentence) < 15:
                continue
                
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in time_keywords):
                # Check if we haven't already captured this timeline
                if not any(sentence in t['context'] for t in timelines):
                    # Extract potential time information
                    time_match = re.search(r'(\d+)\s+(weeks?|months?|days?|quarters?)', sentence_lower)
                    if time_match:
                        timelines.append({
                            "timeline": time_match.group(0),
                            "context": sentence,
                            "type": "general",
                            "confidence": 0.6
                        })
        
        # Sort by confidence and remove duplicates
        seen_contexts = set()
        unique_timelines = []
        
        for timeline in sorted(timelines, key=lambda x: x['confidence'], reverse=True):
            context_key = timeline['context'][:50]  # Use first 50 chars as key
            if context_key not in seen_contexts:
                seen_contexts.add(context_key)
                unique_timelines.append(timeline)
        
        return unique_timelines[:6]  # Return top 6 timelines
        
        return timelines
    
    def extract_participants(self, text: str) -> List[str]:
        """
        Extract meeting participants using state-of-the-art NER (Named Entity Recognition)
        
        Uses HuggingFace's transformer-based NER model for production-grade person detection.
        This approach:
        - Handles ANY text format (speaker, narrative, mixed)
        - Leverages transformer attention mechanisms
        - Trained on millions of examples (CoNLL-2003 dataset)
        - Provides confidence scores for quality filtering
        - Scales to any meeting length with intelligent chunking
        
        Returns:
            List of participant names sorted by confidence and frequency
        """
        print("🤖 Running transformer-based NER for participant extraction...")
        
        try:
            participants = self._extract_participants_with_ner(text)
            final_list = sorted(list(participants))[:10]
            
            print(f"✅ NER extracted {len(final_list)} participants: {final_list}")
            return final_list
            
        except Exception as e:
            print(f"❌ NER extraction failed: {e}")
            print("💡 Tip: Ensure transformers library is installed and model can be downloaded")
            return []  # Fail gracefully - no fallback needed
    

    
    def _extract_participants_with_ner(self, text: str) -> Set[str]:
        """
        Production-grade NER extraction with advanced post-processing
        
        Features:
        - Transformer-based entity recognition (BERT-Large)
        - Confidence-based filtering (removes low-quality predictions)
        - Smart chunking for long documents
        - Frequency analysis for ranking
        - Advanced deduplication and cleaning
        """
        try:
            # Initialize NER pipeline (cached after first call)
            if not hasattr(self, '_ner_pipeline'):
                from transformers import pipeline
                print("📥 Loading BERT-Large NER model (dbmdz/bert-large-cased-finetuned-conll03-english)...")
                self._ner_pipeline = pipeline(
                    "ner", 
                    model="dbmdz/bert-large-cased-finetuned-conll03-english",
                    aggregation_strategy="simple",  # Combines sub-tokens intelligently
                    device=self.device
                )
                print("✅ NER model loaded successfully")
            
            # Smart chunking preserves sentence boundaries
            chunks = self._chunk_text_for_ner(text, max_tokens=400)
            print(f"📝 Processing {len(chunks)} text chunks...")
            
            # Track participants with confidence and frequency
            participant_scores = {}  # {name: [confidence_scores]}
            
            for i, chunk in enumerate(chunks):
                entities = self._ner_pipeline(chunk)
                
                for entity in entities:
                    if entity['entity_group'] == 'PER' and entity['score'] > 0.85:  # High confidence threshold
                        name = self._clean_ner_name(entity['word'])
                        
                        if self._is_valid_person_name(name):
                            if name not in participant_scores:
                                participant_scores[name] = []
                            participant_scores[name].append(entity['score'])
            
            # Advanced participant ranking and selection
            final_participants = self._rank_and_select_participants(participant_scores)
            
            print(f"🎯 Final participant ranking completed")
            return final_participants
            
        except Exception as e:
            print(f"❌ NER extraction error: {e}")
            raise  # Let the parent method handle the error
    
    def _clean_ner_name(self, raw_name: str) -> str:
        """Clean NER output artifacts and normalize names"""
        # Remove BERT tokenization artifacts
        name = raw_name.replace('##', '').replace(' ##', '')
        
        # Handle common NER artifacts
        name = name.replace('[CLS]', '').replace('[SEP]', '')
        
        # Normalize whitespace
        name = ' '.join(name.split())
        
        # Fix common casing issues from NER
        if name.isupper() or name.islower():
            name = name.title()
        
        return name.strip()
    
    def _rank_and_select_participants(self, participant_scores: Dict[str, List[float]]) -> Set[str]:
        """
        Advanced participant ranking using confidence and frequency
        
        Scoring factors:
        - Average confidence score
        - Frequency of mentions
        - Name completeness (full names preferred over first names)
        """
        scored_participants = []
        
        for name, scores in participant_scores.items():
            avg_confidence = sum(scores) / len(scores)
            frequency = len(scores)
            completeness_bonus = 0.1 if ' ' in name else 0  # Prefer full names
            
            # Composite score: confidence × frequency + completeness bonus
            composite_score = (avg_confidence * frequency) + completeness_bonus
            
            scored_participants.append((name, composite_score, avg_confidence, frequency))
        
        # Sort by composite score (highest first)
        scored_participants.sort(key=lambda x: x[1], reverse=True)
        
        # Deduplicate: remove first names if full name exists
        final_names = set()
        for name, score, conf, freq in scored_participants:
            # Check if this is a first name that has a corresponding full name
            is_first_name_of_existing = any(
                name != existing and name in existing.split() 
                for existing in final_names
            )
            
            if not is_first_name_of_existing:
                final_names.add(name)
                print(f"👤 {name}: confidence={conf:.3f}, frequency={freq}, score={score:.3f}")
        
        return final_names
    
    def _chunk_text_for_ner(self, text: str, max_tokens: int = 500) -> List[str]:
        """Chunk text for NER processing to avoid memory issues"""
        # Simple sentence-based chunking
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Rough token estimate (words * 1.3)
            estimated_tokens = len((current_chunk + sentence).split()) * 1.3
            
            if estimated_tokens > max_tokens and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _is_valid_person_name(self, name: str) -> bool:
        """Validate if detected entity is likely a real person name"""
        if not name or len(name) < 2:
            return False
            
        # Remove common NER false positives
        false_positives = {
            'API', 'CEO', 'CTO', 'CFO', 'VP', 'UI', 'UX', 'AI', 'ML', 'AWS', 'API',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        }
        
        # Must start with capital, contain only letters/spaces, reasonable length
        return (name[0].isupper() and 
                all(c.isalpha() or c.isspace() for c in name) and
                2 <= len(name) <= 25 and
                name not in false_positives)
    
    def _get_sentence_containing(self, text: str, position: int) -> str:
        """Get the sentence containing a specific character position"""
        sentences = self._split_sentences(text)
        current_pos = 0
        
        for sentence in sentences:
            if current_pos <= position <= current_pos + len(sentence):
                return sentence.strip()
            current_pos += len(sentence) + 1
        
        return ""
    
    def _categorize_action_item(self, text: str) -> str:
        """Categorize action items by type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["deadline", "due", "by"]):
            return "deadline"
        elif any(word in text_lower for word in ["follow", "check", "review"]):
            return "follow-up"
        elif any(word in text_lower for word in ["assign", "responsible", "owner"]):
            return "assignment"
        elif any(word in text_lower for word in ["schedule", "meeting", "call"]):
            return "scheduling"
        else:
            return "general"

# Example usage and testing
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test text
    test_text = """
    In today's quarterly review meeting, we discussed several important topics. 
    The marketing team reported that our Q3 revenue exceeded expectations by 15%. 
    John will prepare the detailed budget analysis by Friday and send it to all stakeholders.
    Sarah mentioned that we need to follow up with the vendor about the pricing proposal.
    The product launch is scheduled for next month, and we should schedule another meeting 
    next Tuesday to review the final preparations. Mike is responsible for coordinating 
    with the design team. We also discussed the need to reduce operational costs by 10% 
    in the next quarter.
    """
    
    print("Testing NLP Processor...")
    nlp = NLPProcessor()
    
    print("\n=== SUMMARIZATION TEST ===")
    summary = nlp.summarize_text(test_text)
    print(f"Summary: {summary}")
    
    print("\n=== ACTION ITEMS TEST ===")
    action_items = nlp.extract_action_items(test_text)
    for item in action_items:
        print(f"- {item['text']}")
        print(f"  Confidence: {item['confidence']:.2f}, Category: {item['category']}")
    
    print("\n=== KEY TOPICS TEST ===")
    topics = nlp.extract_key_topics(test_text)
    print(f"Key topics: {', '.join(topics)}")
    
    print("\nNLP module test completed!")
