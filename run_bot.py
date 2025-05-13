"""
Real Estate Bot Entry Point

Usage:
    python run_bot.py analyze --zipcode=90210
    python run_bot.py chat
"""
import asyncio
import os
from typing import Optional
import fire
from dotenv import load_dotenv
from src.simple_chat import RealEstateChatInterface
from src.analyzers.neighborhood import analyze_neighborhood_potential

# Load environment variables
load_dotenv()

class RealEstateBot:
    """Real Estate Analysis Bot CLI"""
    
    async def analyze(self, zipcode: str) -> None:
        """
        Analyze neighborhood potential for a given zipcode.
        
        Args:
            zipcode: The zipcode to analyze
        """
        try:
            print(f"\nAnalyzing neighborhood potential for {zipcode}...\n")
            
            results = await analyze_neighborhood_potential(zipcode)
            
            # Print overall score
            print(f"Overall Score: {results['overall_score']}/100\n")
            
            # Print signal scores
            print("Signal Scores:")
            for signal, data in results['signals'].items():
                score_key = f"{signal}_score"
                if score_key in data:
                    print(f"- {signal.title()}: {data[score_key]}/100")
            print()
            
            # Print recommendations
            print("Recommendations:")
            for rec in results['recommendations']:
                print(f"- {rec}")
            
        except Exception as e:
            print(f"Error analyzing neighborhood: {str(e)}")
    
    async def chat(self) -> None:
        """Start interactive chat session with the bot."""
        if not os.getenv("ATTOM_API_KEY"):
            print("Error: ATTOM_API_KEY environment variable not set")
            return
            
        try:
            chat = RealEstateChatInterface()
            print("\nWelcome to the Real Estate AI Bot!")
            print("Ask me about properties or neighborhoods")
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

def main():
    """CLI entry point"""
    bot = RealEstateBot()
    fire.Fire({
        'analyze': lambda zipcode: asyncio.run(bot.analyze(zipcode)),
        'chat': lambda: asyncio.run(bot.chat())
    })

if __name__ == "__main__":
    main()
