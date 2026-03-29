import os
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

@tool
def search_flights(origin: str, destination: str, exact_date: str, max_stops: int) -> str:
    """
    Searches for real-time flight data. 
    Dates MUST be in YYYY-MM-DD format.
    """
    print(f"\n--> [SYSTEM: Running Tool] Searching flights from {origin} to {destination} on {exact_date} with max {max_stops} stops...\n")
    return f"Found flights: $300 direct, $150 with {max_stops} stops." #dummy data for now

# The AI Model (Free Gemini)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
tools = [search_flights]

system_prompt = """
You are a highly efficient, professional Travel Agent API assistant. 

CRITICAL RULES:
1. NEVER GUESS OR INVENT MISSING INFORMATION. If the user does not explicitly provide an origin, a destination, AND a date, you MUST politely ask them for the missing details.
2. Do NOT call the search_flights tool until you have collected all required information from the user.
3. If a user gives a fuzzy date (e.g., "sometime next week"), ask them for an exact YYYY-MM-DD date.
4. When you search, you must always look for 3 direct flights and 3 transit flights.
5. When you present results, ALWAYS use this exact format:
    Destination📍: <destination>
    Date📅: <YYYY-MM-DD>
    -*Direct Flights (0 stops)✈️:* <price>
    -*Transit Flights (1+ stops)🛬🛫:* <price>
"""
agent_executor = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

def get_city_image(city):
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": city,
        "client_id": access_key,
        "orientation": "landscape"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["results"]:
            return data["results"][0]["urls"]["regular"]
        else:
            return None
    except:
        return None

if __name__ == "__main__":
    print("Travel Agent Brain (V1.0 Edition) is online. Type 'quit' to exit.")
    
    while True:
        user_message = input("\nYou: ")
        if user_message.lower() == 'quit':
            break
            
        try:
            response = agent_executor.invoke({"messages": [("user", user_message)]})
            print("\nAgent:\n", response["messages"][-1].content)
            
        except Exception as e:
            print(f"\nAn error occurred: {e}")