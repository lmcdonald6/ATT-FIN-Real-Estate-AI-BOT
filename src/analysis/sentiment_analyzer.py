"""
Self-Hosted Sentiment Analyzer

This module provides sentiment analysis capabilities without relying on external APIs.
It uses open-source NLP libraries to analyze neighborhood sentiment data collected
by the crawler and stored in the local database.
"""

import json
import logging
import os
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup - use the same path as the crawler
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                      'data', 'neighborhood_data.db')

# Sentiment analysis lexicons
POSITIVE_TERMS = {
    # General positive terms
    'great', 'excellent', 'good', 'nice', 'love', 'wonderful', 'fantastic', 'amazing', 'beautiful', 'enjoy',
    'happy', 'perfect', 'recommend', 'best', 'favorite', 'lovely', 'awesome', 'ideal', 'convenient', 'clean',
    
    # Neighborhood-specific positive terms
    'safe', 'friendly', 'walkable', 'quiet', 'affordable', 'diverse', 'community', 'convenient', 'accessible',
    'parks', 'restaurants', 'shops', 'transit', 'schools', 'improving', 'growing', 'trendy', 'vibrant',
    'culture', 'historic', 'charming', 'green', 'peaceful', 'family-friendly', 'nightlife', 'entertainment'
}

NEGATIVE_TERMS = {
    # General negative terms
    'bad', 'poor', 'terrible', 'horrible', 'awful', 'hate', 'dislike', 'avoid', 'disappointing', 'worst',
    'expensive', 'overpriced', 'dirty', 'rundown', 'problem', 'issue', 'complaint', 'negative', 'mediocre',
    
    # Neighborhood-specific negative terms
    'unsafe', 'dangerous', 'crime', 'noisy', 'traffic', 'congestion', 'crowded', 'homeless', 'gentrification',
    'expensive', 'overpriced', 'unaffordable', 'parking', 'pollution', 'dirty', 'trash', 'litter', 'drugs',
    'sketchy', 'boring', 'isolated', 'inconvenient', 'far', 'remote', 'flood', 'construction', 'rundown'
}

# Aspect categories for neighborhood analysis
ASPECT_CATEGORIES = {
    'safety': ['safe', 'unsafe', 'dangerous', 'crime', 'security', 'police', 'mugging', 'break-in', 'theft', 'sketchy'],
    'affordability': ['affordable', 'expensive', 'price', 'cost', 'rent', 'mortgage', 'budget', 'overpriced', 'value', 'cheap'],
    'transportation': ['transit', 'bus', 'subway', 'metro', 'commute', 'traffic', 'parking', 'car', 'bike', 'walk', 'walkable'],
    'amenities': ['restaurant', 'shop', 'store', 'grocery', 'market', 'cafe', 'bar', 'gym', 'fitness', 'mall'],
    'schools': ['school', 'education', 'university', 'college', 'student', 'teacher', 'academic', 'district'],
    'community': ['neighbor', 'community', 'people', 'friendly', 'family', 'diverse', 'diversity', 'culture', 'demographic'],
    'noise': ['quiet', 'noisy', 'loud', 'peaceful', 'siren', 'traffic', 'party', 'construction', 'sound'],
    'cleanliness': ['clean', 'dirty', 'trash', 'litter', 'garbage', 'maintained', 'upkeep', 'rundown', 'pristine'],
    'parks': ['park', 'green', 'outdoor', 'nature', 'tree', 'garden', 'playground', 'trail', 'recreation'],
    'nightlife': ['nightlife', 'bar', 'club', 'restaurant', 'entertainment', 'venue', 'concert', 'theater', 'activity']
}

# Negation words that flip sentiment
NEGATION_WORDS = {'not', 'no', "n't", 'never', 'none', 'nobody', 'nothing', 'neither', 'nor', 'nowhere', 'hardly', 'barely', 'rarely', 'seldom'}

# Intensifiers that strengthen sentiment
INTENSIFIERS = {'very', 'really', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally', 'utterly', 'highly', 'especially'}


class SentimentAnalyzer:
    """Self-hosted sentiment analyzer for neighborhood data."""
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the sentiment analyzer.
        
        Args:
            db_path: Path to the SQLite database with neighborhood data
        """
        self.db_path = db_path
        self._ensure_cache_table()
    
    def _ensure_cache_table(self):
        """
        Ensure the sentiment cache table exists in the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            neighborhood TEXT PRIMARY KEY,
            analysis_data TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _tokenize_text(self, text: str) -> List[str]:
        """
        Simple tokenization of text into words.
        
        Args:
            text: The text to tokenize
            
        Returns:
            List of tokens (words)
        """
        # Convert to lowercase
        text = text.lower()
        
        # Replace certain punctuation with spaces
        text = re.sub(r'[,.;:!?()\[\]{}]', ' ', text)
        
        # Split on whitespace
        tokens = text.split()
        
        # Remove tokens that are just numbers or single characters (except 'a' and 'i')
        tokens = [t for t in tokens if not (t.isdigit() or (len(t) == 1 and t not in ['a', 'i']))]
        
        return tokens
    
    def _analyze_sentiment_lexicon(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Analyze sentiment using lexicon-based approach.
        
        Args:
            tokens: List of tokens from the text
            
        Returns:
            Dictionary with sentiment scores
        """
        positive_count = 0
        negative_count = 0
        
        # Track whether we're in a negation context
        negation_active = False
        intensifier_active = False
        
        for i, token in enumerate(tokens):
            # Check for negation words
            if token in NEGATION_WORDS:
                negation_active = True
                continue
                
            # Check for intensifiers
            if token in INTENSIFIERS:
                intensifier_active = True
                continue
            
            # Reset negation after 3 tokens or at punctuation
            if negation_active and i > 0 and i - tokens.index(list(NEGATION_WORDS)[0]) > 3:
                negation_active = False
            
            # Reset intensifier after the next token
            if intensifier_active and i > 0:
                intensifier_active = False
            
            # Check sentiment of token
            sentiment_value = 0
            
            if token in POSITIVE_TERMS:
                sentiment_value = 1
            elif token in NEGATIVE_TERMS:
                sentiment_value = -1
                
            # Apply negation if active
            if negation_active:
                sentiment_value = -sentiment_value
                
            # Apply intensifier if active
            if intensifier_active and sentiment_value != 0:
                sentiment_value = sentiment_value * 1.5
                
            # Update counts
            if sentiment_value > 0:
                positive_count += sentiment_value
            elif sentiment_value < 0:
                negative_count -= sentiment_value
        
        # Calculate sentiment scores
        total_sentiment_terms = positive_count + negative_count
        if total_sentiment_terms > 0:
            positive_score = positive_count / total_sentiment_terms
            negative_score = negative_count / total_sentiment_terms
            compound_score = (positive_count - negative_count) / total_sentiment_terms
        else:
            positive_score = 0
            negative_score = 0
            compound_score = 0
            
        return {
            "positive_score": positive_score,
            "negative_score": negative_score,
            "compound_score": compound_score,
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    def _extract_aspects(self, tokens: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Extract aspect-based sentiment from tokens.
        
        Args:
            tokens: List of tokens from the text
            
        Returns:
            Dictionary with aspect categories and their sentiment
        """
        aspects = {}
        
        # Initialize aspect counters
        for category in ASPECT_CATEGORIES:
            aspects[category] = {
                "mentions": 0,
                "positive": 0,
                "negative": 0,
                "score": 0
            }
        
        # Analyze each token for aspect categories
        for i, token in enumerate(tokens):
            # Check which aspect categories this token belongs to
            for category, terms in ASPECT_CATEGORIES.items():
                if any(term in token or token in term for term in terms):
                    aspects[category]["mentions"] += 1
                    
                    # Look for sentiment words in context (window of 5 words before and after)
                    context_start = max(0, i - 5)
                    context_end = min(len(tokens), i + 6)
                    context = tokens[context_start:context_end]
                    
                    # Check for sentiment in context
                    negation_in_context = any(neg in context for neg in NEGATION_WORDS)
                    
                    pos_sentiment = sum(1 for t in context if t in POSITIVE_TERMS)
                    neg_sentiment = sum(1 for t in context if t in NEGATIVE_TERMS)
                    
                    # Apply negation if present
                    if negation_in_context:
                        pos_sentiment, neg_sentiment = neg_sentiment, pos_sentiment
                    
                    aspects[category]["positive"] += pos_sentiment
                    aspects[category]["negative"] += neg_sentiment
        
        # Calculate scores for each aspect
        for category in aspects:
            total_sentiment = aspects[category]["positive"] + aspects[category]["negative"]
            if total_sentiment > 0:
                aspects[category]["score"] = (aspects[category]["positive"] - aspects[category]["negative"]) / total_sentiment
        
        return aspects
    
    def _extract_key_phrases(self, tokens: List[str], top_n: int = 10) -> List[str]:
        """
        Extract key phrases from tokens.
        
        Args:
            tokens: List of tokens from the text
            top_n: Number of top phrases to extract
            
        Returns:
            List of key phrases
        """
        # Simple approach: find bigrams and trigrams that occur frequently
        bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
        trigrams = [' '.join(tokens[i:i+3]) for i in range(len(tokens)-2)]
        
        # Count occurrences
        bigram_counter = Counter(bigrams)
        trigram_counter = Counter(trigrams)
        
        # Combine and get top phrases
        all_phrases = list(bigram_counter.items()) + list(trigram_counter.items())
        all_phrases.sort(key=lambda x: x[1], reverse=True)
        
        # Filter out phrases with stop words only
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of', 'is', 'are'}
        filtered_phrases = [phrase for phrase, count in all_phrases 
                          if not all(word in stop_words for word in phrase.split())]
        
        return filtered_phrases[:top_n]
    
    def analyze_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment for a single post.
        
        Args:
            post: Dictionary containing post data
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # Combine title and content for analysis
        title = post.get("title", "")
        content = post.get("content", "")
        full_text = f"{title} {content}"
        
        # Tokenize text
        tokens = self._tokenize_text(full_text)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment_lexicon(tokens)
        
        # Extract aspects
        aspects = self._extract_aspects(tokens)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(tokens)
        
        # Determine overall sentiment label
        compound_score = sentiment["compound_score"]
        if compound_score >= 0.05:
            sentiment_label = "positive"
        elif compound_score <= -0.05:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        return {
            "post_id": post.get("id"),
            "source": post.get("source"),
            "sentiment": sentiment,
            "sentiment_label": sentiment_label,
            "aspects": aspects,
            "key_phrases": key_phrases
        }
    
    def analyze_neighborhood(self, neighborhood: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Analyze sentiment for a neighborhood using stored posts.
        
        Args:
            neighborhood: The neighborhood to analyze
            force_refresh: Whether to force a fresh analysis even if cached
            
        Returns:
            Dictionary with neighborhood sentiment analysis
        """
        # Check for cached analysis unless force_refresh is True
        if not force_refresh:
            cached_analysis = self._get_cached_analysis(neighborhood)
            if cached_analysis:
                logger.info(f"Using cached sentiment analysis for {neighborhood}")
                return cached_analysis
        
        # Get posts for the neighborhood
        posts = self._get_neighborhood_posts(neighborhood)
        if not posts:
            logger.warning(f"No posts found for {neighborhood}")
            return self._generate_empty_analysis(neighborhood)
        
        logger.info(f"Analyzing {len(posts)} posts for {neighborhood}")
        
        # Analyze each post
        post_analyses = [self.analyze_post(post) for post in posts]
        
        # Aggregate results
        aggregated = self._aggregate_analyses(post_analyses, neighborhood)
        
        # Cache the results
        self._cache_analysis(neighborhood, aggregated)
        
        return aggregated
    
    def _get_cached_analysis(self, neighborhood: str) -> Optional[Dict[str, Any]]:
        """
        Get cached sentiment analysis for a neighborhood.
        
        Args:
            neighborhood: The neighborhood to get analysis for
            
        Returns:
            Dictionary with cached analysis or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT analysis_data FROM sentiment_analysis
        WHERE neighborhood = ?
        ''', (neighborhood,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def _cache_analysis(self, neighborhood: str, analysis: Dict[str, Any]):
        """
        Cache sentiment analysis for a neighborhood.
        
        Args:
            neighborhood: The neighborhood to cache analysis for
            analysis: The analysis data to cache
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert analysis to JSON
        analysis_json = json.dumps(analysis)
        
        # Update or insert
        cursor.execute('''
        INSERT OR REPLACE INTO sentiment_analysis
        (neighborhood, analysis_data, last_updated)
        VALUES (?, ?, ?)
        ''', (neighborhood, analysis_json, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cached sentiment analysis for {neighborhood}")
    
    def _get_neighborhood_posts(self, neighborhood: str) -> List[Dict[str, Any]]:
        """
        Get posts for a neighborhood from the database.
        
        Args:
            neighborhood: The neighborhood to get posts for
            
        Returns:
            List of post dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM neighborhood_posts
        WHERE neighborhood = ?
        ORDER BY crawl_date DESC
        ''', (neighborhood,))
        
        rows = cursor.fetchall()
        posts = [dict(row) for row in rows]
        
        conn.close()
        
        return posts
    
    def _generate_empty_analysis(self, neighborhood: str) -> Dict[str, Any]:
        """
        Generate an empty analysis when no posts are found.
        
        Args:
            neighborhood: The neighborhood name
            
        Returns:
            Empty analysis dictionary
        """
        return {
            "neighborhood": neighborhood,
            "post_count": 0,
            "overall_sentiment": {
                "label": "neutral",
                "score": 0,
                "confidence": 0
            },
            "aspect_sentiment": {},
            "key_themes": [],
            "sources": [],
            "analysis_date": datetime.now().isoformat()
        }
    
    def _aggregate_analyses(self, post_analyses: List[Dict[str, Any]], neighborhood: str) -> Dict[str, Any]:
        """
        Aggregate individual post analyses into an overall neighborhood analysis.
        
        Args:
            post_analyses: List of individual post analyses
            neighborhood: The neighborhood name
            
        Returns:
            Aggregated analysis dictionary
        """
        if not post_analyses:
            return self._generate_empty_analysis(neighborhood)
        
        # Calculate overall sentiment
        compound_scores = [a["sentiment"]["compound_score"] for a in post_analyses]
        avg_compound = sum(compound_scores) / len(compound_scores)
        
        # Count sentiment labels
        sentiment_counts = Counter([a["sentiment_label"] for a in post_analyses])
        total_posts = len(post_analyses)
        
        # Determine overall sentiment label
        if avg_compound >= 0.05:
            overall_label = "positive"
        elif avg_compound <= -0.05:
            overall_label = "negative"
        else:
            overall_label = "neutral"
            
        # Calculate confidence based on agreement
        majority_count = sentiment_counts.most_common(1)[0][1]
        confidence = majority_count / total_posts
        
        # Aggregate aspect sentiment
        aspect_sentiment = defaultdict(lambda: {"mentions": 0, "positive": 0, "negative": 0, "score": 0})
        
        for analysis in post_analyses:
            for aspect, data in analysis["aspects"].items():
                aspect_sentiment[aspect]["mentions"] += data["mentions"]
                aspect_sentiment[aspect]["positive"] += data["positive"]
                aspect_sentiment[aspect]["negative"] += data["negative"]
        
        # Calculate aspect scores
        for aspect in aspect_sentiment:
            total = aspect_sentiment[aspect]["positive"] + aspect_sentiment[aspect]["negative"]
            if total > 0:
                aspect_sentiment[aspect]["score"] = (aspect_sentiment[aspect]["positive"] - 
                                                 aspect_sentiment[aspect]["negative"]) / total
        
        # Sort aspects by mentions
        sorted_aspects = {k: v for k, v in sorted(aspect_sentiment.items(), 
                                               key=lambda item: item[1]["mentions"], 
                                               reverse=True)}
        
        # Extract key themes (phrases that appear in multiple posts)
        all_phrases = [phrase for analysis in post_analyses for phrase in analysis["key_phrases"]]
        phrase_counter = Counter(all_phrases)
        key_themes = [phrase for phrase, count in phrase_counter.most_common(10) if count > 1]
        
        # Get sources
        sources = list(set(a["source"] for a in post_analyses))
        
        return {
            "neighborhood": neighborhood,
            "post_count": total_posts,
            "overall_sentiment": {
                "label": overall_label,
                "score": avg_compound,
                "confidence": confidence,
                "distribution": {
                    "positive": sentiment_counts.get("positive", 0) / total_posts,
                    "neutral": sentiment_counts.get("neutral", 0) / total_posts,
                    "negative": sentiment_counts.get("negative", 0) / total_posts
                }
            },
            "aspect_sentiment": sorted_aspects,
            "key_themes": key_themes,
            "sources": sources,
            "analysis_date": datetime.now().isoformat()
        }
    
    def generate_text_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a human-readable text summary of the sentiment analysis.
        
        Args:
            analysis: The sentiment analysis dictionary
            
        Returns:
            Text summary of the analysis
        """
        if analysis["post_count"] == 0:
            return f"No data available for {analysis['neighborhood']}."
        
        # Format overall sentiment
        overall = analysis["overall_sentiment"]
        sentiment_text = f"Overall sentiment: {overall['label']} (score: {overall['score']:.2f}, confidence: {overall['confidence']:.2f})"
        
        # Format distribution
        dist = overall["distribution"]
        distribution_text = f"Sentiment distribution: {dist['positive']*100:.1f}% positive, {dist['neutral']*100:.1f}% neutral, {dist['negative']*100:.1f}% negative"
        
        # Format top aspects
        top_aspects = list(analysis["aspect_sentiment"].items())[:5]  # Top 5 aspects
        aspects_text = "Top aspects mentioned:\n"
        for aspect, data in top_aspects:
            if data["mentions"] > 0:
                sentiment = "positive" if data["score"] > 0 else "negative" if data["score"] < 0 else "neutral"
                aspects_text += f"- {aspect}: {sentiment} (score: {data['score']:.2f}, mentions: {data['mentions']})\n"
        
        # Format key themes
        themes_text = "Key themes mentioned:\n"
        for theme in analysis["key_themes"][:5]:  # Top 5 themes
            themes_text += f"- {theme}\n"
        
        # Format sources
        sources_text = f"Data sources: {', '.join(analysis['sources'])}"
        
        # Combine all sections
        summary = f"""Neighborhood Sentiment Analysis for {analysis['neighborhood']}

Based on {analysis['post_count']} posts analyzed on {analysis['analysis_date'][:10]}

{sentiment_text}
{distribution_text}

{aspects_text}
{themes_text}
{sources_text}
"""
        
        return summary


def main():
    """
    Example usage of the sentiment analyzer.
    """
    analyzer = SentimentAnalyzer()
    
    # Example neighborhoods to analyze
    neighborhoods = ["Atlanta Beltline", "Midtown Manhattan", "Mission District San Francisco"]
    
    for neighborhood in neighborhoods:
        print(f"\nAnalyzing sentiment for {neighborhood}...")
        
        # This would normally use real data from the database
        # For demonstration, we'll create a mock analysis
        mock_post = {
            "id": 1,
            "source": "demo",
            "title": f"Living in {neighborhood}",
            "content": f"I really love living in {neighborhood}. The area is very safe and has great restaurants. "
                      f"Public transportation is convenient. The only downside is that it's getting expensive "
                      f"and parking can be difficult to find. Overall it's a wonderful place to live."
        }
        
        # Analyze the mock post
        post_analysis = analyzer.analyze_post(mock_post)
        
        # Create a mock aggregated analysis
        mock_aggregated = analyzer._aggregate_analyses([post_analysis], neighborhood)
        
        # Generate and print the summary
        summary = analyzer.generate_text_summary(mock_aggregated)
        print(summary)


if __name__ == "__main__":
    main()
