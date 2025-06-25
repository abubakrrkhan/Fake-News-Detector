import re
import os
import string
from typing import Dict, List, Any, Optional
from loguru import logger
import nltk

# Check for safe mode
SAFE_MODE = os.environ.get("SAFE_MODE", "false").lower() == "true"

# Set default value for HAVE_TRANSFORMERS
HAVE_TRANSFORMERS = False

# Try to download NLTK data if not already present
try:
    nltk.download('vader_lexicon', quiet=True)
    HAVE_VADER = True
except:
    HAVE_VADER = False
    logger.warning("NLTK VADER lexicon not available - sentiment analysis will be limited")

# Try importing advanced NLP libraries
try:
    if SAFE_MODE:
        raise ImportError("Running in safe mode - skipping transformer imports")
        
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HAVE_TRANSFORMERS = True
    logger.info("Transformers and PyTorch are available. Using advanced sentiment analysis.")
except ImportError as e:
    HAVE_TRANSFORMERS = False
    logger.warning(f"Advanced NLP libraries not available: {e}. Using simplified sentiment analysis.")

class SentimentAnalyzer:
    """
    Analyzes sentiment, emotion, and sensationalism in text
    """
    
    def __init__(self):
        """
        Initialize sentiment analyzer with available models
        """
        logger.info("Initializing SentimentAnalyzer")
        
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        
        # Setup NLTK based VADER sentiment analyzer as fallback
        if HAVE_VADER:
            try:
                from nltk.sentiment.vader import SentimentIntensityAnalyzer
                self.vader = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.error(f"Failed to initialize VADER: {e}")
                self.vader = None
        else:
            self.vader = None
            
        # Try loading transformers models if available
        if HAVE_TRANSFORMERS and not SAFE_MODE:
            try:
                # Load sentiment analysis model
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    truncation=True
                )
                
                # Try loading emotion detection model
                try:
                    self.emotion_pipeline = pipeline(
                        "text-classification", 
                        model="j-hartmann/emotion-english-distilroberta-base", 
                        top_k=3,
                        truncation=True
                    )
                except Exception as e:
                    logger.warning(f"Emotion detection model failed to load: {e}")
                    self.emotion_pipeline = None
                
            except Exception as e:
                logger.warning(f"Error loading transformer models: {e}")
                self.sentiment_pipeline = None
                self.emotion_pipeline = None
        else:
            logger.warning("Running in safe mode - skipping transformer models")
            
        # Basic lexicons for rule-based fallback
        self.positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic", 
            "terrific", "outstanding", "superb", "brilliant", "exceptional",
            "positive", "success", "win", "victory", "breakthrough"
        ]
        
        self.negative_words = [
            "bad", "terrible", "horrible", "awful", "poor", "disappointing",
            "catastrophic", "disaster", "fail", "failure", "crisis", "problem",
            "negative", "worst", "corrupt", "false", "fake"
        ]
        
        self.sensational_words = [
            "shocking", "incredible", "unbelievable", "explosive", "bombshell",
            "secret", "exclusive", "breaking", "urgent", "emergency", "disaster",
            "catastrophe", "crisis", "miracle", "revolutionary", "game-changing",
            "mind-blowing", "devastating", "massive", "horrific", "epic"
        ]
        
        self.emotion_lexicons = {
            "anger": ["angry", "mad", "furious", "outraged", "rage"],
            "fear": ["afraid", "scared", "frightened", "terrified", "panic"],
            "joy": ["happy", "delighted", "pleased", "joyful", "excited"],
            "sadness": ["sad", "unhappy", "depressed", "miserable", "grief"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "startled"]
        }
        
        logger.info("SentimentAnalyzer initialized successfully")
        
    def _count_lexicon_matches(self, text: str, word_list: List[str]) -> int:
        """Count occurrences of words from a lexicon in text"""
        text = text.lower()
        count = 0
        for word in word_list:
            # Count whole word matches using regex
            count += len(re.findall(r'\b' + re.escape(word) + r'\b', text))
        return count
        
    def _rule_based_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple rule-based sentiment analysis"""
        text = text.lower()
        positive_count = self._count_lexicon_matches(text, self.positive_words)
        negative_count = self._count_lexicon_matches(text, self.negative_words)
        
        # Determine sentiment based on counts
        if positive_count > negative_count * 1.5:
            sentiment = "POSITIVE"
        elif negative_count > positive_count * 1.5:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
            
        # Calculate confidence (simplified)
        total_words = len(text.split())
        if total_words > 0:
            confidence = min(0.7, max(0.3, (positive_count + negative_count) / total_words))
        else:
            confidence = 0.0
            
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "positive_score": positive_count,
            "negative_score": negative_count
        }
    
    def _rule_based_emotion(self, text: str) -> Dict[str, Any]:
        """Simple rule-based emotion detection"""
        text = text.lower()
        emotions = {}
        
        for emotion, words in self.emotion_lexicons.items():
            count = self._count_lexicon_matches(text, words)
            emotions[emotion] = count
            
        # Find top emotion
        top_emotion = max(emotions.items(), key=lambda x: x[1])
        
        # If no emotions detected, return none
        if top_emotion[1] == 0:
            return {
                "top_emotion": "none",
                "emotions": emotions
            }
        
        return {
            "top_emotion": top_emotion[0],
            "emotions": emotions
        }
    
    def _analyze_sensationalism(self, text: str) -> float:
        """Analyze sensationalism in text"""
        # Count sensational words
        count = self._count_lexicon_matches(text, self.sensational_words)
        
        # Calculate score (normalized by text length)
        total_words = len(text.split())
        if total_words > 0:
            score = min(1.0, count / (total_words / 10))  # Scale by 1 per 10 words
        else:
            score = 0.0
            
        # Add score for ALL CAPS words
        words = text.split()
        caps_count = sum(1 for word in words if len(word) > 3 and word.isupper())
        if total_words > 0:
            caps_score = min(1.0, caps_count / (total_words / 5))
        else:
            caps_score = 0.0
            
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        if total_words > 0:
            punct_score = min(1.0, (exclamation_count + question_count) / (total_words / 5))
        else:
            punct_score = 0.0
            
        # Combine scores
        final_score = min(1.0, (score + caps_score + punct_score) / 3)
        
        return round(final_score, 2)
        
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment, emotion and sensationalism in text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing sentiment and emotion")
        
        # Initialize results
        results = {
            "sentiment": "NEUTRAL",
            "confidence": 0.0,
            "top_emotion": "none",
            "emotions": {},
            "sensationalism_score": 0.0
        }
        
        if not text or len(text) < 3:
            return results
            
        # Use appropriate analysis method based on availability
        try:
            # First try transformer-based sentiment analysis
            if self.sentiment_pipeline:
                pipeline_result = self.sentiment_pipeline(text[:512])
                results["sentiment"] = pipeline_result[0]["label"].upper()
                results["confidence"] = round(pipeline_result[0]["score"], 2)
            # Then try VADER
            elif self.vader:
                scores = self.vader.polarity_scores(text)
                if scores["compound"] >= 0.05:
                    results["sentiment"] = "POSITIVE"
                elif scores["compound"] <= -0.05:
                    results["sentiment"] = "NEGATIVE"
                else:
                    results["sentiment"] = "NEUTRAL"
                results["confidence"] = round(abs(scores["compound"]), 2)
            # Fallback to rule-based
            else:
                rule_results = self._rule_based_sentiment(text)
                results.update(rule_results)
                
            # Emotion analysis
            if self.emotion_pipeline:
                emotion_result = self.emotion_pipeline(text[:512])
                if emotion_result[0]:
                    results["top_emotion"] = emotion_result[0][0]["label"]
                    results["emotions"] = {item["label"]: round(item["score"], 2) for item in emotion_result[0]}
            else:
                emotion_results = self._rule_based_emotion(text)
                results.update(emotion_results)
                
            # Sensationalism analysis (rule-based for all modes)
            results["sensationalism_score"] = self._analyze_sensationalism(text)
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            # If error occurs, use simple rule-based as final fallback
            rule_results = self._rule_based_sentiment(text)
            results.update(rule_results)
            
        logger.info(f"Analysis complete: sentiment={results['sentiment']}, top_emotion={results['top_emotion']}, sensationalism_score={results['sensationalism_score']:.2f}")
        return results 