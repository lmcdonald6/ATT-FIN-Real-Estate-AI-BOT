"""
Real Estate AI Bot
Main entry point for the chat interface.
"""

import asyncio
import logging
from src.chat_interface import RealEstateChatInterface

async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='real_estate_chat.log'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # Initialize chat interface
    chat = RealEstateChatInterface()
    
    print("\nReal Estate AI Bot")
    print("=" * 50)
    print("\nEnter your property queries. Type 'exit' to quit.\n")

    while True:
        try:
            # Get user input
            query = input("\nQuery: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("\nThank you for using Real Estate AI Bot!")
                break
                
            # Process query
            response = await chat.process_query(query)
            
            if response['status'] == 'success':
                # Print formatted response
                print("\nRESPONSE:")
                print("-" * 50)
                print("\n".join(response['response']))
                print("\n" + "=" * 80 + "\n")
            else:
                print(f"\nError: {response['message']}")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except EOFError:
            print("\n\nInput stream ended. Exiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            logging.error(f"Unexpected error: {str(e)}", exc_info=True)
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
