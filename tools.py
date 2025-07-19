import os
# from utils import connect_mongodb, parse_JSON
from dotenv import load_dotenv
load_dotenv()

def kcet_chat_db(user_input):
    from userLibs.sql_agent import SQL_Agent,render
    import warnings
    from prompts import KCET_SQL_AGENT_SYSTEM_PROMPT

    warnings.filterwarnings("ignore")
    db_uri=os.getenv("KCET_DB_URI")
    db_dialect = "PostgreSQL"  # or "MySQL", "SQLite", etc. based on your database
    my_agent = SQL_Agent(model_provider="google_genai",model_name="gemini-2.5-flash",database_uri=db_uri, dialect=db_dialect, top_k=15)

    my_agent.set_custom_system_message(KCET_SQL_AGENT_SYSTEM_PROMPT)
    my_agent.initialize_agent()

    response = my_agent.stream_answer(user_input)
    # print(f"Response keys: {list(response.keys())}")
    # print(f"Thinking : {response['thinking']}")
    # print(f"KCET Model Response: {response}")
    return response



    




# def chat_db(user_input: str,db_uri: str):
#     from langchain_community.agent_toolkits import create_sql_agent,SQLDatabaseToolkit
#     from langchain.agents.agent_types import AgentType
#     from langchain_community.utilities.sql_database import SQLDatabase
#     from langchain_google_genai import ChatGoogleGenerativeAI

#     """
#     Function to interact with database using a SQL agent that can
#     reason about the database schema and generate appropriate queries.
#     """
#     try:
#         # Initialize the database connection
#         db = SQLDatabase.from_uri(db_uri)

#         if not db:
#             raise ValueError("Database connection could not be established.")
        
#         prefix = """
#             You are a master KCET‑DB expert using PostgreSQL.  
#             KCET is the Karnataka CET exam for admission into engineering, medical, pharmacy, veterinary, agriculture and related fields.  
#             Students receive ranks based on test marks. During KCET counselling, students fill in their preferences (college, branch, category).  
#             Seats are allotted sequentially from rank 1 down: a student gets a seat in General Merit if available; otherwise their own category (e.g., 1A, 2G, SC, ST).  
#             This continues over multiple rounds. We store past years’ cut‑off ranks (the closing ranks) for each college‑branch‑category combination.

#             You are here to help students using this database; always:
#             - Run **only READ (SELECT)** queries—no INSERT/UPDATE/DELETE.
            
#             - Translate English questions into secure SQL.
#             - If the user requests a write/delete, refuse with a clear response.
#             - If no matching data exists, respond: "not in the database."
#         """

#         llm = ChatGoogleGenerativeAI(
#             model='gemini-2.5-flash',
#             )

#         toolkit = SQLDatabaseToolkit(llm=llm, db=db)

#         # Create SQL Agent
#         agent = create_sql_agent(
#             llm=llm,
#             agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#             toolkit=toolkit,
#             verbose=True,
#             handle_parsing_errors=True,
#             max_iterations=20,
#             prefix=prefix
#         ) 
#         # Run the agent with user input
#         result = agent.invoke(user_input)

#         return result
#     except Exception as e:
#         return {
#             "error": True,
#             "message": str(e)
#         }
    


# def user_profiling(user_input:str, session_id:str):
    from langchain_google_genai import ChatGoogleGenerativeAI
    """
    This function retrieves user profile information from a MongoDB databased based on session_id.
    and passes the 'user profile' information and 'user query' to the LLM.
    The LLM will analyse the input, and decides whether any further information can be added to the user profile based on user query.
    User profile information includes: 
        - name , 
        - rank , 
        - email, 
        interested 
        - colleges,
        - places
        - career_streams - Engineering, Medical, Architecture, etc
        - category - 1A, 2A, GM etc. 
    Args:
        user_input (str): User's query or message
        session_id (str): Unique session identifier
    """
    # Initialize this to capture user profile data
    user_profile = None
    
    try: 
        mongo_db_uri = os.getenv("MONGO_DB_URI")
        if not mongo_db_uri:
            return {"error": True, "message": "MongoDB URI not found in environment variables"}
            
        db_client = connect_mongodb(mongo_db_uri)
        db_name = "mini_project"
        collection_name = "users"

        db = db_client.get_database(db_name)
        if db is None:
            return {"error": True, "message": f"Database '{db_name}' does not exist or could not be accessed."}
        
        collection = db.get_collection(collection_name)
        if collection is None:
            return {"error": True, "message": f"Collection '{collection_name}' does not exist or could not be accessed."}

        print(f"Looking for user profile with session_id: {session_id}")
        # Retrieve user profile based on session_id
        user_profile = collection.find_one({"session_id": session_id})
        print(f"User profile found: {user_profile is not None}")

        if not user_profile:
            # If no profile exists, create a new one
            user_profile = {
                "session_id": session_id,
                "name": "",
                "rank": "",
                "email": "",
                "interested_colleges": [],
                "interested_places": [],
                "career_streams": [],
                "category": ""
            }
            insert_result = collection.insert_one(user_profile)
            print(f"Created new profile with ID: {insert_result.inserted_id}")
            # Retrieve the newly created profile to ensure we have the complete document
            user_profile = collection.find_one({"_id": insert_result.inserted_id})
            if not user_profile:
                return {"error": True, "message": "Failed to create and retrieve new user profile"}

        # Continue with LLM processing
        try:
            # LLM logic to analyze user input and update profile
            llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')
            
            # Format prompt for structured output
            system_prompt = f"""
            # User Profiling Agent

            ## Your Task
            You are an advanced user profiling assistant. Analyze the user's input to extract relevant personal details and update their profile accordingly. Be precise and attentive to details mentioned by the user.

            ## Current User Profile
            {user_profile}

            ## User's Latest Input
            "{user_input}"

            ## Instructions
            1. Analyze the user's input for any information that could update their profile
            2. For each field in the profile:
            - If new information is detected, extract and format it appropriately
            - If information contradicts existing data, prefer the newer information
            - Leave fields unchanged if no relevant information is found
            - For list fields (colleges, places, career_streams), add new items without removing existing ones unless explicitly instructed
            
            ## Fields to Monitor
            - session_id: Keep unchanged
            - name: type:String Full name of the user.
            - rank: type:Number, Any numerical rank in examinations (e.g., "1034"), Conver to Number : Ex:- 10K -> 10000, AIR 20 -> 20, ten Thousand -> 10000
            - email: Email address in standard format
            - interested_colleges: Names of colleges/universities mentioned with positive sentiment
            - interested_places: Geographical locations of interest
            - career_streams: Career paths like Engineering, Medical, Architecture, etc.
            - category: Indian reservation categories like 1A, 2A, GM, SC, ST, OBC, etc. Convert to actual category codes, general -> GM, category 1 -> 1A, etc.
            
            ## Response Format
            Respond ONLY with a valid JSON object containing the updated profile.
            Make sure to include all the fields from the current profile, even if they remain unchanged.
            ```json
            {{
              "session_id": "session_id_here",
              "name": "user name",
              "rank": "user rank",
              "email": "user email",
              "interested_colleges": ["college1", "college2"],
              "interested_places": ["place1", "place2"],
              "career_streams": ["stream1", "stream2"],
              "category": "user category"
            }}
            ```
            """
            
            
            
            # Invoke LLM
            response = llm.invoke(system_prompt)
            
            print(f"LLM response: {response.content}")
            try:
                # Parse the response using our parse_JSON function
                updated_profile = parse_JSON(response.content)
                
                print(f"Parsed updated profile: {updated_profile}")

                if not updated_profile or not isinstance(updated_profile, dict):
                    raise ValueError("LLM response did not return a valid JSON object.")
                
                # Update the MongoDB collection with the new profile
                collection.update_one({"session_id": session_id}, {"$set": updated_profile})
                
                return {
                    "error": False,
                    "message": "User profile updated successfully.",
                    "profile": updated_profile
                }
            except ValueError as e:
                # If our parser fails, return the error
                return {
                    "error": True,
                    "message": f"Failed to parse LLM response: {str(e)}",
                    "raw_content": response.content
                }
    
        except Exception as e:
            return {
                "error": True,
                "message": f"LLM processing failed: {str(e)}"
            }

    except Exception as e:
        return {
            "error": True,
            "message": f"Database operation failed: {str(e)}"
        }


if __name__ == "__main__":
    # Example usage
    user_input = "How many colleges in Mysuru?"
    print(kcet_chat_db(user_input))