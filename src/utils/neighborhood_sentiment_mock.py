"""
Neighborhood Sentiment Analysis Module (Mock Version)

This module provides functionality to analyze neighborhood sentiment using mock data
to avoid unnecessary API calls during testing and development.
"""

import asyncio
import logging
import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Mock data for different neighborhoods
MOCK_NEIGHBORHOOD_DATA = {
    "atlanta beltline": {
        "characteristics": {
            "location": "The Atlanta BeltLine is a former railway corridor around the core of Atlanta, Georgia, that has been transformed into a multi-use trail.",
            "demographics": "Diverse population with a mix of young professionals, families, and students.",
            "housing": "Housing prices have increased significantly along the BeltLine. Expect to find modern apartments, condos, and renovated homes.",
            "amenities": "The BeltLine features numerous parks, art installations, restaurants, and shops along its path.",
            "transportation": "Primarily accessed by walking or biking. Limited public transit connections.",
            "schools": "Varies by specific section of the BeltLine. Some areas have access to well-rated schools.",
            "safety": "Generally safe during daylight hours. Some sections may require caution at night.",
            "community": "Active community with frequent events, farmers markets, and outdoor activities."
        },
        "reviews": [
            {
                "title": "Love the BeltLine lifestyle",
                "content": "[Resident - 4.5/5 stars] I've lived near the Eastside Trail for 3 years and absolutely love it. Great for walking, biking, and there are so many restaurants and shops within easy reach. The only downside is that it gets very crowded on weekends and housing prices keep climbing.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Great amenities but expensive",
                "content": "[New homeowner - 4/5 stars] We just bought a condo near the BeltLine and love the access to Ponce City Market and Piedmont Park. It's a very walkable area with lots to do. However, we paid a premium for the location, and it can get noisy with all the foot traffic.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Mixed feelings about the development",
                "content": "[Long-time resident - 3/5 stars] I've seen the area transform over the last decade. While the BeltLine has brought nice amenities and improved safety, it's also led to gentrification and pushed out many long-time residents who can no longer afford to live here.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Perfect for active lifestyle",
                "content": "[Visitor - 5/5 stars] I visit Atlanta regularly and always stay near the BeltLine. It's perfect for morning runs and evening strolls to different restaurants. The art installations along the path make it a unique experience every time.",
                "url": None,
                "simulated": True
            }
        ],
        "sentiment_summary": "Overall sentiment score: 8/10\n\nKey themes mentioned:\n1. Walkability and accessibility\n2. Rising property values and gentrification\n3. Abundance of amenities (restaurants, shops, parks)\n4. Active lifestyle and community events\n5. Crowding during peak times\n\nPositive aspects:\n- Excellent for walking, running, and biking\n- Numerous restaurants, bars, and shops along the trail\n- Art installations and cultural attractions\n- Improved safety in previously neglected areas\n- Community events and farmers markets\n\nNegative aspects:\n- Rising housing costs and gentrification\n- Crowded during weekends and events\n- Noise from foot traffic and businesses\n- Limited parking in some areas\n- Incomplete sections in some parts of the city\n\nWho would enjoy living here:\n- Young professionals and couples who value an active, social lifestyle\n- Those who prefer walking/biking over driving\n- People who enjoy urban amenities and don't mind paying a premium\n- Art and culture enthusiasts\n\nWho might not enjoy living here:\n- Those seeking quiet, suburban environments\n- Budget-conscious individuals and families\n- People who rely heavily on cars for transportation\n- Those who prefer more space and privacy"
    },
    "midtown manhattan": {
        "characteristics": {
            "location": "Midtown Manhattan is a central neighborhood in New York City, extending from 34th Street to 59th Street.",
            "demographics": "Mix of professionals, international residents, and some families. High population density.",
            "housing": "Predominantly high-rise apartments and condos. Among the most expensive real estate in the country.",
            "amenities": "World-class shopping, dining, theaters, museums, and attractions like Times Square and the Empire State Building.",
            "transportation": "Excellent public transportation with multiple subway lines and bus routes. Very walkable.",
            "schools": "Limited public schools in the immediate area. Several private and specialized schools available.",
            "safety": "Generally safe with high police presence, especially in tourist areas. Standard urban precautions advised.",
            "community": "More transient than other NYC neighborhoods. Fast-paced environment with a mix of tourists and locals."
        },
        "reviews": [
            {
                "title": "The convenience is unmatched",
                "content": "[Resident - 4/5 stars] I've lived in Midtown for 5 years and the convenience is unbeatable. Everything is within walking distance or a short subway ride away. The downside is the constant noise and tourist crowds, but that's the trade-off for living in the center of it all.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Great for work, not for living",
                "content": "[Former resident - 3/5 stars] I lived in Midtown for 2 years while working nearby. It was convenient for work but lacks the neighborhood feel of other parts of NYC. Very few grocery stores, mostly expensive restaurants, and it feels empty on weekends when the office workers leave.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Exciting but exhausting",
                "content": "[Resident - 3.5/5 stars] Living in Midtown means you're always at the center of the action. Great theaters, restaurants, and shopping. But it's also crowded, noisy, and expensive. The buildings are beautiful but you pay a premium for small spaces.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Perfect location for NYC experience",
                "content": "[New resident - 5/5 stars] Just moved to Midtown and love being able to walk to Central Park, MoMA, and world-class shopping. Yes, it's expensive and busy, but that's what makes New York special. The energy is incredible and there's always something happening.",
                "url": None,
                "simulated": True
            }
        ],
        "sentiment_summary": "Overall sentiment score: 7/10\n\nKey themes mentioned:\n1. Unmatched convenience and central location\n2. High cost of living and small living spaces\n3. Noise and crowds, especially from tourists\n4. Excellent access to cultural attractions and amenities\n5. Lack of neighborhood feel and community\n\nPositive aspects:\n- Central location with easy access to the entire city\n- World-class entertainment, dining, and shopping options\n- Proximity to major attractions and cultural institutions\n- Excellent public transportation\n- Prestigious address and iconic architecture\n\nNegative aspects:\n- Very high cost of living, especially for housing\n- Constant noise and crowds\n- Lacks authentic neighborhood feel\n- Limited grocery stores and everyday amenities\n- Can feel empty on weekends and holidays\n\nWho would enjoy living here:\n- Professionals who work in Midtown and value short commutes\n- Those who prioritize convenience and don't mind paying for it\n- People who enjoy the energy and pace of central Manhattan\n- Cultural enthusiasts who frequent museums, theaters, and concerts\n\nWho might not enjoy living here:\n- Families with children who need more space and quieter environments\n- Those seeking a strong community feel and neighborhood identity\n- Budget-conscious individuals\n- People who prefer green spaces and a slower pace of life\n- Light sleepers sensitive to urban noise"
    },
    "mission district san francisco": {
        "characteristics": {
            "location": "The Mission District is located in east-central San Francisco, California.",
            "demographics": "Historically Latino neighborhood now experiencing significant gentrification. Mix of long-time residents and newcomers.",
            "housing": "Victorian and Edwardian houses, some apartment buildings. Housing prices have risen dramatically in recent years.",
            "amenities": "Known for excellent restaurants, bars, coffee shops, murals, and parks including Dolores Park.",
            "transportation": "Well-served by BART and Muni public transit. Relatively flat terrain makes it bicycle-friendly.",
            "schools": "Mix of public and private schools with varying performance ratings.",
            "safety": "Safety concerns vary by specific blocks. Some areas have higher crime rates than others.",
            "community": "Strong cultural identity with Latino roots. Tension exists between long-time community and newer tech industry residents."
        },
        "reviews": [
            {
                "title": "Vibrant but changing rapidly",
                "content": "[Resident - 4/5 stars] I've lived in the Mission for 7 years and love the food, culture, and energy. The murals and Dolores Park are highlights. However, it's changing quickly as tech workers move in and rents skyrocket. Many of the businesses that gave the neighborhood its character are disappearing.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Best food in the city",
                "content": "[Visitor - 5/5 stars] I don't live in the Mission but visit frequently for the incredible restaurant scene. From authentic taquerias to Michelin-starred restaurants, the food options are amazing. The murals and street art add to the experience. Can be a bit gritty in some areas.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Mixed feelings as a longtime resident",
                "content": "[Long-time resident - 3/5 stars] My family has been in the Mission for generations, and the changes are bittersweet. The neighborhood is safer in many ways, but the soul is being stripped away as rents force out families and local businesses. The contrast between extreme wealth and poverty is stark.",
                "url": None,
                "simulated": True
            },
            {
                "title": "Perfect for young professionals",
                "content": "[New resident - 4.5/5 stars] Moved here a year ago and love the convenience to downtown, great weather (less fog than other parts of SF), and amazing food and nightlife. Yes, it's expensive, but you get what you pay for in terms of lifestyle. Dolores Park on weekends is the best.",
                "url": None,
                "simulated": True
            }
        ],
        "sentiment_summary": "Overall sentiment score: 6.5/10\n\nKey themes mentioned:\n1. Cultural diversity and rich Latino heritage\n2. Rapid gentrification and changing neighborhood character\n3. Outstanding food scene and local businesses\n4. Rising housing costs and displacement concerns\n5. Vibrant arts scene, especially murals and street art\n\nPositive aspects:\n- Exceptional dining options from taquerias to fine dining\n- Sunny microclimate (less fog than other parts of SF)\n- Vibrant arts scene and colorful murals\n- Dolores Park and other community gathering spaces\n- Convenient location and good public transportation\n\nNegative aspects:\n- Rapid gentrification displacing long-time residents and businesses\n- Very high and rising housing costs\n- Visible homelessness and income inequality\n- Property crime and safety concerns in some areas\n- Tension between different community groups\n\nWho would enjoy living here:\n- Food and culture enthusiasts\n- Young professionals who value urban amenities\n- Those who appreciate diversity and cultural history\n- People who enjoy a lively, walkable neighborhood\n- Artists and creative types\n\nWho might not enjoy living here:\n- Those seeking quiet, suburban environments\n- Families needing larger homes at affordable prices\n- People uncomfortable with urban issues like homelessness\n- Those who prefer homogeneous, less changing neighborhoods\n- Residents sensitive to noise and crowds"
    }
}


async def mock_scrape_reviews(location: str) -> List[Dict[str, str]]:
    """
    Returns mock review data for the specified location.
    
    Args:
        location: The neighborhood name to get reviews for
        
    Returns:
        List of dictionaries containing mock reviews
    """
    location_key = location.lower()
    logger.info(f"Getting mock reviews for: {location}")
    
    # Check if we have mock data for this location
    if location_key in MOCK_NEIGHBORHOOD_DATA:
        return MOCK_NEIGHBORHOOD_DATA[location_key]["reviews"]
    
    # For locations we don't have specific data for, return empty list
    # In a real implementation, we might generate generic mock data
    logger.info(f"No mock data available for {location}")
    return []


async def get_mock_neighborhood_characteristics(location: str) -> Dict[str, Any]:
    """
    Returns mock neighborhood characteristics.
    
    Args:
        location: The neighborhood name
        
    Returns:
        Dictionary with mock neighborhood characteristics
    """
    location_key = location.lower()
    logger.info(f"Getting mock characteristics for: {location}")
    
    # Check if we have mock data for this location
    if location_key in MOCK_NEIGHBORHOOD_DATA:
        return MOCK_NEIGHBORHOOD_DATA[location_key]["characteristics"]
    
    # For locations we don't have specific data for, return generic data
    return {
        "location": f"{location} is a neighborhood with varying characteristics.",
        "demographics": "Mixed population demographics.",
        "housing": "Housing prices vary by specific area and property type.",
        "amenities": "Various local amenities including shops, restaurants, and parks.",
        "transportation": "Transportation options depend on the specific location.",
        "schools": "School quality varies throughout the area.",
        "safety": "Safety considerations vary by specific location and time of day.",
        "community": "Community characteristics depend on the specific neighborhood area."
    }


def get_mock_sentiment_summary(location: str) -> str:
    """
    Returns a mock sentiment summary for the specified location.
    
    Args:
        location: The neighborhood name
        
    Returns:
        Mock sentiment summary as a string
    """
    location_key = location.lower()
    logger.info(f"Getting mock sentiment summary for: {location}")
    
    # Check if we have mock data for this location
    if location_key in MOCK_NEIGHBORHOOD_DATA:
        return MOCK_NEIGHBORHOOD_DATA[location_key]["sentiment_summary"]
    
    # For locations we don't have specific data for, return generic summary
    return f"""Overall sentiment score: 7/10

Key themes mentioned:
1. Location convenience and accessibility
2. Housing quality and value
3. Local amenities and services
4. Community feel and neighbor interactions
5. Safety and security considerations

Positive aspects:
- Convenient location for many residents
- Some quality local businesses and services
- Decent housing stock with some character
- Pockets of strong community engagement
- Improving infrastructure in certain areas

Negative aspects:
- Some concerns about property values and trends
- Variable quality of public services
- Traffic and parking challenges in some areas
- Limited selection of certain amenities
- Some safety concerns in specific locations

Who would enjoy living here:
- Those who value the specific location advantages
- Residents who appreciate the particular community character
- People who prioritize the housing style available in this area

Who might not enjoy living here:
- Those seeking significantly different housing options
- People who prioritize different community characteristics
- Residents with specific needs not well-served in this area"""


async def analyze_neighborhood_sentiment(location_query: str, max_results: int = 8, use_mock: bool = True) -> Dict[str, Any]:
    """
    Main function to analyze neighborhood sentiment using mock data.
    
    Args:
        location_query: The neighborhood or location to analyze
        max_results: Maximum number of reviews to analyze (not used in mock version)
        use_mock: Whether to use mock data (always true in this version)
        
    Returns:
        Dictionary containing sentiment analysis results
    """
    logger.info(f"Analyzing sentiment for location: {location_query}")
    
    # Get mock reviews
    posts = await mock_scrape_reviews(location_query)
    
    # If no reviews found, try to generate mock data based on characteristics
    if not posts:
        logger.info(f"No reviews found for {location_query}, using generic data")
        characteristics = await get_mock_neighborhood_characteristics(location_query)
        data_source = "generic_mock"
    else:
        data_source = "specific_mock"
    
    # Get sentiment summary
    summary = get_mock_sentiment_summary(location_query)
    
    return {
        "location": location_query,
        "success": True,
        "data_source": data_source,
        "posts_analyzed": len(posts),
        "sentiment_summary": summary,
        "sources": [post.get("url") for post in posts if post.get("url")],
        "timestamp": datetime.now().isoformat(),
        "mock_data": True
    }


async def main():
    """Example usage of the mock sentiment analysis module."""
    locations = [
        "Atlanta Beltline",
        "Midtown Manhattan",
        "Mission District San Francisco",
        "Random Neighborhood"  # This will use generic mock data
    ]
    
    for location in locations:
        print(f"\n📍 Analyzing sentiment for: {location}")
        results = await analyze_neighborhood_sentiment(location)
        
        print(f"Data source: {results['data_source']}")
        print(f"Posts analyzed: {results['posts_analyzed']}")
        print("\nSentiment Summary excerpt:")
        print(results["sentiment_summary"][:200] + "...")


if __name__ == "__main__":
    asyncio.run(main())
