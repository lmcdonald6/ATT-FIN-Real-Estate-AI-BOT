"""
Real Estate Bot Entry Point
"""
import asyncio
import os
from dotenv import load_dotenv
from src.simple_chat import RealEstateChatInterface

# Load environment variables
load_dotenv()

async def main():
    """Main entry point"""
    # Verify ATTOM API key is set
    if not os.getenv("ATTOM_API_KEY"):
        print("Error: ATTOM_API_KEY environment variable not set")
        return
        
    try:
        chat = RealEstateChatInterface()
        print("\nWelcome to the Real Estate AI Bot!")
        print("Ask me about properties in Bessemer, AL")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("> ")
                if user_input.lower() in ['quit', 'exit']:
                    break
                
                response = await chat.process_natural_query(user_input)
                print("\n" + chat.format_response(response) + "\n")
                
            except EOFError:
                print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}\n")
                
    except Exception as e:
        print(f"Failed to initialize chat interface: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except EOFError:
        print("\nGoodbye!")
