import os
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

CRITICAL PARSING RULES (READ CAREFULLY):
1. THE CAVEMAN RULE: If a user types two cities without "from" or "to" (e.g., "budapest milan"), you MUST assume the FIRST city is the ORIGIN and the SECOND city is the DESTINATION.
2. NEVER mix up the origin and destination. If they are going TO Milan, the destination country is Italy.
3. NEVER output the Origin city in the Destination field.
4. THE GRAMMAR RULE: ALWAYS Title Case city and country names in your final output. (e.g., turn "budapest" into "Budapest", "milan" into "Milan").
5. NEVER GUESS: If you only see one city, politely ask if it is the origin or destination.

CRITICAL RULES:
1. NEVER GUESS OR INVENT MISSING INFORMATION. If the user does not explicitly provide an origin, a destination, AND a date, you MUST politely ask them for the missing details.
2. Do NOT call the search_flights tool until you have collected all required information from the user.
3. If a user gives a fuzzy date (e.g., "sometime next week"), ask them for an exact YYYY-MM-DD date.
4. When you search, you must always look for 3 direct flights and 3 transit flights.
5. Always use HTML tags for formatting. 
6. Use <b>text</b> for bolding prices and labels.
7. Use <code>text</code> for dates and specific numbers.
8. Use 📍 for Destination, 📅 for Date, and ✈️ for Flights.
9. Use a horizontal line '───' to separate sections.
10. Put the Destination Country Name in brackets like [Norway] so the bot can find the flag.
11. NEVER use the '<' or '>' symbols unless they are for valid HTML tags like <b> or <code>.

EXACT OUTPUT STRUCTURE:
📍 <b>Destination:</b> [Destination Country] {Destination City}
📅 <b>Date:</b> <code>{YYYY-MM-DD}</code>

─── ✈️ <b>FLIGHT OPTIONS</b> ───
⚡ <b>Fast & Direct:</b> <code>{Price}</code>
🎒 <b>Student Choice:</b> <code>{Price}</code> (Transit)

─── 🏨 <b>STUDENT STAY</b> ───
🏠 <b>Budget Bed:</b> <code>{Price}/night</code>
"""
agent_executor = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

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