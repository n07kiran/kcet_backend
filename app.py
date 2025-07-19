from email.mime import message
from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# @app.post("/chat")
# def chat_endpoint(user_input: str):
#     """
#     A initial User endpoint to the chatBot
#     """
#     from tools import user_profiling

#     user_input = user_input.strip()

#     # Get session_id from the request ??
    
#     updated_user_profile = user_profiling(user_input=user_input, session_id="12345")

#     print(f"Updated User Profile: {updated_user_profile}")
    
#     updated_user_profile = updated_user_profile.get("profile")

#     return {"message": f"You said: {user_input}", "profile": updated_user_profile}


from fastapi import Form, Request

@app.post("/kcet_db")
async def kcet_db_endpoint(request: Request, user_input: str = Form(None)):
    """
    Endpoint to interact with the KCET database using a SQL agent.
    Accepts both JSON and form input.
    """
    from tools import kcet_chat_db

    # Try to get user_input from form, if not present, try JSON
    if user_input is None:
        try:
            data = await request.json()
            user_input = data.get("user_input")
        except Exception:
            user_input = None

    if not user_input:
        return {"error": "No user_input provided."}

    llm_response = kcet_chat_db(user_input)

    # print(f"LLM Thinking: {llm_response['thinking']}")
    # print(f"LLM Response: {llm_response['answer']}")
    frontend_response = {
        "message": llm_response
    }
    
    return frontend_response


# @app.get("/try_db")
# def try_db_endpoint():
#     """
#     Endpoint to interact with the KCET database using a SQL agent.
#     """
#     kcet_db_uri = os.getenv("KCET_DB_URI")

#     # Connect to the database - postgres
#     try:
#         import sqlalchemy
#         from sqlalchemy import text
        
#         # Create engine and connect
#         engine = sqlalchemy.create_engine(kcet_db_uri)
#         conn = engine.connect()
        
#         # Execute a simple query based on user input
#         # Warning: This is vulnerable to SQL injection in a real app
#         # You should use parameterized queries
#         query = text(f"SELECT * FROM information_schema.tables LIMIT 10;")  # Example query to list tables
#         result = conn.execute(query)

#         print(f"result: {result}")
        
#         # Process results - fix the dictionary conversion
#         tables = []
#         for row in result:
#             # Use _mapping or properly convert row to dict
#             if hasattr(row, "_mapping"):
#                 tables.append(dict(row._mapping))
#             else:
#                 # Alternative approach using column names
#                 row_dict = {}
#                 for column, value in zip(result.keys(), row):
#                     row_dict[column] = value
#                 tables.append(row_dict)
        
#         conn.close()
        
#         return {
#             "status": "success",
#             "message": f"Database query executed for input:",
#             "tables": tables
#         }
#     except Exception as e:
#         print(f"Database error: {str(e)}")  # Add this for debugging
#         return {
#             "status": "error",
#             "message": f"Database connection failed: {str(e)}"
#         }

