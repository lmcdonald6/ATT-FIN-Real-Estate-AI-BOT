"""
Local Sentiment Fine-Tuner

This module provides functionality to fine-tune a local sentiment analysis model
using the proprietary neighborhood data collected by the crawler.

It reduces dependency on external APIs by training a custom model that understands
real estate and neighborhood-specific language.
"""

import json
import logging
import os
import pickle
import random
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                      'data', 'neighborhood_data.db')

# Model paths
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                         'models')
VECTORIZER_PATH = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
MODEL_PATH = os.path.join(MODELS_DIR, 'sentiment_model.pkl')


class SentimentFineTuner:
    """Fine-tunes a local sentiment analysis model using proprietary neighborhood data."""
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the sentiment fine-tuner.
        
        Args:
            db_path: Path to the SQLite database with neighborhood data
        """
        self.db_path = db_path
        self.vectorizer = None
        self.model = None
        
        # Ensure models directory exists
        os.makedirs(MODELS_DIR, exist_ok=True)
    
    def prepare_training_data(self) -> Tuple[List[str], List[int]]:
        """
        Prepare training data from the neighborhood posts database.
        
        Returns:
            Tuple of (texts, labels) where labels are:
            1 = positive, 0 = neutral, -1 = negative
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all posts
        cursor.execute('SELECT title, content FROM neighborhood_posts')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            logger.warning("No posts found in database for training")
            return [], []
        
        texts = []
        labels = []
        
        # Basic lexicon for labeling
        positive_terms = {'great', 'good', 'excellent', 'love', 'best', 'safe', 'clean', 'friendly', 'recommend'}
        negative_terms = {'bad', 'poor', 'terrible', 'unsafe', 'dangerous', 'avoid', 'dirty', 'expensive', 'crime'}
        
        for title, content in rows:
            # Combine title and content
            full_text = f"{title} {content}".lower()
            texts.append(full_text)
            
            # Simple rule-based labeling for initial training
            pos_count = sum(1 for term in positive_terms if term in full_text)
            neg_count = sum(1 for term in negative_terms if term in full_text)
            
            if pos_count > neg_count:
                labels.append(1)  # Positive
            elif neg_count > pos_count:
                labels.append(-1)  # Negative
            else:
                labels.append(0)  # Neutral
        
        logger.info(f"Prepared {len(texts)} posts for training")
        logger.info(f"Label distribution: Positive={labels.count(1)}, Neutral={labels.count(0)}, Negative={labels.count(-1)}")
        
        return texts, labels
    
    def train_model(self, test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """
        Train a sentiment analysis model on the prepared data.
        
        Args:
            test_size: Fraction of data to use for testing
            random_state: Random seed for reproducibility
            
        Returns:
            Dictionary with training metrics
        """
        # Prepare data
        texts, labels = self.prepare_training_data()
        
        if not texts:
            logger.error("No training data available")
            return {"success": False, "error": "No training data available"}
        
        # Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=random_state, stratify=labels
        )
        
        # Create and fit TF-IDF vectorizer
        logger.info("Creating and fitting TF-IDF vectorizer")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        # Train logistic regression model
        logger.info("Training logistic regression model")
        self.model = LogisticRegression(
            C=1.0,
            class_weight='balanced',
            solver='liblinear',
            random_state=random_state,
            max_iter=1000
        )
        self.model.fit(X_train_tfidf, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        logger.info(f"Model trained with accuracy: {accuracy:.4f}")
        
        # Save model and vectorizer
        self._save_model()
        
        return {
            "success": True,
            "accuracy": accuracy,
            "report": report,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "model_path": MODEL_PATH,
            "vectorizer_path": VECTORIZER_PATH,
            "training_date": datetime.now().isoformat()
        }
    
    def _save_model(self):
        """Save the trained model and vectorizer to disk."""
        if self.model is None or self.vectorizer is None:
            logger.error("No model or vectorizer to save")
            return False
        
        # Save vectorizer
        with open(VECTORIZER_PATH, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Save model
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
        
        logger.info(f"Model saved to {MODEL_PATH}")
        logger.info(f"Vectorizer saved to {VECTORIZER_PATH}")
        
        return True
    
    @classmethod
    def load_model(cls) -> 'SentimentFineTuner':
        """
        Load a trained model from disk.
        
        Returns:
            SentimentFineTuner instance with loaded model
        """
        instance = cls()
        
        try:
            # Load vectorizer
            with open(VECTORIZER_PATH, 'rb') as f:
                instance.vectorizer = pickle.load(f)
            
            # Load model
            with open(MODEL_PATH, 'rb') as f:
                instance.model = pickle.load(f)
            
            logger.info("Model and vectorizer loaded successfully")
            return instance
        except FileNotFoundError:
            logger.error("Model or vectorizer file not found")
            return instance
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return instance
    
    def predict_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment for a text using the trained model.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with sentiment prediction
        """
        if self.model is None or self.vectorizer is None:
            logger.error("No model available for prediction")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0
            }
        
        # Transform text
        text_tfidf = self.vectorizer.transform([text])
        
        # Predict
        label = self.model.predict(text_tfidf)[0]
        probabilities = self.model.predict_proba(text_tfidf)[0]
        
        # Map label to text
        label_map = {
            -1: "negative",
            0: "neutral",
            1: "positive"
        }
        
        # Get confidence (probability of predicted class)
        confidence = max(probabilities)
        
        # Calculate score from -1 to 1
        if label == -1:
            score = -confidence
        elif label == 1:
            score = confidence
        else:
            score = 0.0
        
        return {
            "label": label_map.get(label, "neutral"),
            "score": score,
            "confidence": confidence
        }


def fine_tune_local_sentiment_model(dataset_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Fine-tune a local sentiment analysis model using proprietary neighborhood data.
    
    Args:
        dataset_path: Optional path to a dataset file. If None, uses the database.
        
    Returns:
        Dictionary with training results
    """
    logger.info(f"Starting fine-tuning using: {dataset_path or 'database'}")
    
    tuner = SentimentFineTuner()
    
    if dataset_path:
        # TODO: Implement loading from external dataset
        logger.info(f"Loading data from {dataset_path}")
        # This would load data from the specified file
        pass
    
    # Train the model
    results = tuner.train_model()
    
    if results["success"]:
        logger.info(f"Custom model trained and saved to {MODELS_DIR}")
        logger.info(f"Accuracy: {results['accuracy']:.4f}")
    else:
        logger.error(f"Model training failed: {results.get('error', 'Unknown error')}")
    
    return results


if __name__ == "__main__":
    # Example usage
    results = fine_tune_local_sentiment_model()
    print(f"Model training {'succeeded' if results.get('success', False) else 'failed'}")
    
    if results.get("success", False):
        # Test the model
        tuner = SentimentFineTuner.load_model()
        
        test_texts = [
            "This neighborhood is great! Safe streets and friendly neighbors.",
            "The area is okay, some good restaurants but traffic is bad.",
            "Avoid this neighborhood. High crime and dirty streets."
        ]
        
        for text in test_texts:
            sentiment = tuner.predict_sentiment(text)
            print(f"\nText: {text}")
            print(f"Sentiment: {sentiment['label']} (score: {sentiment['score']:.2f}, confidence: {sentiment['confidence']:.2f})")
