#!/usr/bin/env python3
"""
Chat History Module

This module provides functionality for storing and retrieving chat history,
including queries, results, and timestamps.
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# In-memory chat session storage
session_log = {}


def log_chat(query: str, result: dict, user_id: str = None) -> str:
    """
    Stores query + result to memory and returns a unique history ID.
    
    Args:
        query: The user's query string
        result: The result dictionary from the orchestrator
        user_id: Optional user identifier for multi-user systems
        
    Returns:
        A unique chat history ID
    """
    chat_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    # Create the log entry
    log_entry = {
        "timestamp": timestamp,
        "query": query,
        "result": result,
        "result_type": result.get("type", "unknown"),
        "user_id": user_id
    }
    
    # Store in memory
    session_log[chat_id] = log_entry
    
    # Also attempt to persist to disk
    try:
        persist_chat_history()
    except Exception as e:
        logger.warning(f"Failed to persist chat history: {e}")
    
    return chat_id


def get_chat_history(user_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Returns a list of recent queries and timestamps.
    
    Args:
        user_id: Optional user identifier to filter history
        limit: Maximum number of history items to return
        
    Returns:
        List of chat history items
    """
    # Filter by user_id if provided
    if user_id:
        filtered_logs = {cid: log for cid, log in session_log.items() 
                        if log.get("user_id") == user_id}
    else:
        filtered_logs = session_log
    
    # Sort by timestamp (newest first) and limit
    sorted_logs = sorted(filtered_logs.items(), 
                        key=lambda x: x[1]["timestamp"], 
                        reverse=True)
    
    # Format the history items
    history = [
        {
            "id": cid,
            "query": log["query"],
            "timestamp": log["timestamp"],
            "result_type": log.get("result_type", "unknown")
        }
        for cid, log in sorted_logs[:limit]
    ]
    
    return history


def load_chat_result(chat_id: str) -> Dict[str, Any]:
    """
    Retrieves a stored chat result by its unique ID.
    
    Args:
        chat_id: The unique chat history ID
        
    Returns:
        The stored chat result or an empty dict if not found
    """
    log_entry = session_log.get(chat_id, {})
    return log_entry.get("result", {})


def get_full_chat_entry(chat_id: str) -> Dict[str, Any]:
    """
    Retrieves the full chat entry including query, result, and metadata.
    
    Args:
        chat_id: The unique chat history ID
        
    Returns:
        The full chat entry or an empty dict if not found
    """
    return session_log.get(chat_id, {})


def clear_chat_history(user_id: str = None) -> int:
    """
    Clears chat history, optionally for a specific user only.
    
    Args:
        user_id: Optional user identifier to clear history for
        
    Returns:
        Number of history items cleared
    """
    global session_log
    
    if user_id:
        # Only clear history for the specified user
        count_before = len(session_log)
        session_log = {cid: log for cid, log in session_log.items() 
                      if log.get("user_id") != user_id}
        cleared_count = count_before - len(session_log)
    else:
        # Clear all history
        cleared_count = len(session_log)
        session_log = {}
    
    # Update persisted history
    try:
        persist_chat_history()
    except Exception as e:
        logger.warning(f"Failed to persist chat history after clearing: {e}")
    
    return cleared_count


def persist_chat_history(file_path: str = None) -> bool:
    """
    Persists the chat history to disk.
    
    Args:
        file_path: Optional path to save the history file
        
    Returns:
        True if successful, False otherwise
    """
    if file_path is None:
        # Use default path in the project directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, "data", "chat_history.json")
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(session_log, f, indent=2)
        
        logger.info(f"Chat history persisted to {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error persisting chat history: {e}")
        return False


def load_persisted_chat_history(file_path: str = None) -> bool:
    """
    Loads the chat history from disk.
    
    Args:
        file_path: Optional path to load the history file from
        
    Returns:
        True if successful, False otherwise
    """
    global session_log
    
    if file_path is None:
        # Use default path in the project directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, "data", "chat_history.json")
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.info(f"No chat history file found at {file_path}")
            return False
        
        # Read from file
        with open(file_path, 'r') as f:
            loaded_log = json.load(f)
        
        # Update session log
        session_log.update(loaded_log)
        
        logger.info(f"Chat history loaded from {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        return False


# Try to load persisted history on module import
try:
    load_persisted_chat_history()
except Exception as e:
    logger.warning(f"Failed to load persisted chat history on startup: {e}")


if __name__ == "__main__":
    # Test functionality
    print("Chat History Module Test")
    print("=" * 30)
    
    # Test logging a chat
    test_query = "What is the investment confidence in 90210?"
    test_result = {"type": "investment_analysis", "zip": "90210", "confidence_score": 85}
    
    chat_id = log_chat(test_query, test_result)
    print(f"Logged chat with ID: {chat_id}")
    
    # Test retrieving history
    history = get_chat_history()
    print(f"\nChat History ({len(history)} items):")
    for item in history:
        print(f"ID: {item['id']} | {item['timestamp']} | {item['query']}")
    
    # Test retrieving a specific result
    result = load_chat_result(chat_id)
    print(f"\nRetrieved result for {chat_id}: {result}")
    
    # Test persistence
    print("\nTesting persistence...")
    success = persist_chat_history()
    print(f"Persisted chat history: {success}")
    
    # Test clearing history
    clear_count = clear_chat_history()
    print(f"\nCleared {clear_count} history items")
