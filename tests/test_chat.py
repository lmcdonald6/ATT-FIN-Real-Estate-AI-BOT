"""
Test script for the Real Estate Chat Interface
"""
import asyncio
from src.simple_chat import RealEstateChatInterface

async def test_chat():
    chat = RealEstateChatInterface()
    
    # Test queries covering all major categories
    test_queries = [
        # Property Analysis & Valuation
        "what is the value of 123 Main St Bessemer?",
        "show me property details for 456 Oak Ave",
        "get tax assessment for 123 Main St",
        
        # Seller & Ownership Insights
        "who owns 123 Main St?",
        "tell me about the owner of 456 Oak Ave",
        "is 123 Main St occupied?",
        
        # Distressed Property & Off-Market Leads
        "show me distressed properties in Bessemer",
        "find vacant houses in 35020",
        "list pre-foreclosures in Bessemer AL",
        
        # Neighborhood & Market Trends
        "how is the market in Bessemer?",
        "what are price trends in 35020?",
        "show me sales velocity in Bessemer",
        
        # Investment & Wholesale Strategy
        "calculate ARV for 123 Main St",
        "what repairs are needed at 456 Oak Ave?",
        "what's the maximum offer for 123 Main St?",
        
        # Complex Multi-Intent Queries
        "find distressed properties with high equity in Bessemer",
        "show me vacant properties with motivated sellers in 35020",
        "list properties with tax liens and absentee owners"
    ]
    
    print("\nTesting Real Estate Chat Interface")
    print("==================================")
    
    for query in test_queries:
        print(f"\nTEST QUERY: {query}")
        print("-" * 50)
        
        try:
            response = await chat.process_natural_query(query)
            print("\nRESPONSE:")
            print(chat.format_response(response))
            print("\n" + "=" * 80 + "\n")
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            print("\n" + "=" * 80 + "\n")
        
        # Brief pause between queries
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_chat())
