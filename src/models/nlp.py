from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from typing import List, Dict, Any
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
            
            # Summarization - using a lightweight model
            logging.info("Loading summarization model...")
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
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
            chunks = self._chunk_text(text, max_chunk=1000)
            summaries = []
            
            for chunk in chunks:
                if len(chunk.strip()) > 50:  # Skip very short chunks
                    # Adjust lengths based on chunk size
                    chunk_max = min(max_length, len(chunk.split()) // 4)
                    chunk_min = min(min_length, chunk_max // 3)
                    
                    if chunk_max > chunk_min:
                        summary = self.summarizer(
                            chunk, 
                            max_length=chunk_max, 
                            min_length=chunk_min,
                            do_sample=False,
                            truncation=True
                        )[0]['summary_text']
                        summaries.append(summary)
            
            final_summary = " ".join(summaries)
            
            # If we have multiple chunk summaries, summarize them again
            if len(summaries) > 1 and len(final_summary) > max_length * 2:
                final_summary = self.summarizer(
                    final_summary,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    truncation=True
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
            # Simple keyword extraction based on frequency
            words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
            
            # Filter out common words
            stopwords = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 
                'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day',
                'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now',
                'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its',
                'let', 'put', 'say', 'she', 'too', 'use', 'will', 'this',
                'that', 'with', 'have', 'from', 'they', 'know', 'want',
                'been', 'good', 'much', 'some', 'time', 'very', 'when',
                'come', 'here', 'just', 'like', 'long', 'make', 'many',
                'over', 'such', 'take', 'than', 'them', 'well', 'were'
            }
            
            # Count word frequencies
            word_freq = {}
            for word in words:
                if word not in stopwords and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top topics
            topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [topic[0].title() for topic, _ in topics[:num_topics]]
            
        except Exception as e:
            logging.error(f"Topic extraction failed: {e}")
            return []
    
    def _chunk_text(self, text: str, max_chunk: int = 1000) -> List[str]:
        """Split text into chunks for processing"""
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
        
        if current_chunk:
            chunks.append(". ".join(current_chunk) + ".")
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
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
