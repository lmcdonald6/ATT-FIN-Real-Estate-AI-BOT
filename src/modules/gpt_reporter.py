from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(data: dict) -> dict:
    prompt = f"""
You are a real estate investment analyst. Based on the following data:

Crime Score: {data['crime_score']}
Permit Activity: {data['permit_activity']}
Zoning Info: {data['zoning_info']}
Rent vs Value Score: {data['rent_vs_value']}
Market Trend Score: {data['market_trend']}

Generate a 2-paragraph investment summary and a short risk report.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return {
        "summary": response.choices[0].message.content
    }
