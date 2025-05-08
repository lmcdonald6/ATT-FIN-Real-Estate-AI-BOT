"""Main entry point for Real Estate AI Chat"""
import logging
from src.real_estate_chat import RealEstateChat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='real_estate_chat.log'
)

def main():
    """Start the Real Estate AI Chat interface"""
    chat = RealEstateChat()
    chat.chat()

if __name__ == "__main__":
    main()
