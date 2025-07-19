# from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure
# from typing import Optional,List
# import json
# import re

# def connect_mongodb(
#     connection_string: str,
#     db_name: Optional[str] = None,
#     timeout_ms: int = 5000
# ) -> MongoClient:
#     """
#     Establishes a connection to MongoDB.
    
#     Args:
#         connection_string: MongoDB connection URI
#         db_name: Name of the database to connect to
#         timeout_ms: Connection timeout in milliseconds
        
#     Returns:
#         MongoDB client object
        
#     Raises:
#         ConnectionFailure: If connection to MongoDB fails
#         Exception: For any other unexpected errors
#     """
#     try:
#         # Create a MongoDB client with timeout settings
#         client = MongoClient(connection_string, serverSelectionTimeoutMS=timeout_ms)
        
#         # Verify connection is working by sending a ping
#         client.admin.command('ping')
#         print(f"Connected to MongoDB at {connection_string}")
#         return client
    
#     except ConnectionFailure as e:
#         raise ConnectionFailure(f"Failed to connect to MongoDB: {str(e)}")
#     except Exception as e:
#         raise Exception(f"An unexpected error occurred: {str(e)}")
    


# # Custom parser
# def parse_JSON(message: str) -> List[dict]:
#     """Extracts JSON content from a string where JSON is embedded between \`\`\`json and \`\`\` tags.

#     Parameters:
#         text (str): The text containing the JSON content.

#     Returns:
#         list: A list of extracted JSON strings.
#     """
#     text = message
#     # Define the regular expression pattern to match JSON blocks
#     pattern = r"\`\`\`json(.*?)\`\`\`"

#     # Find all non-overlapping matches of the pattern in the string
#     matches = re.findall(pattern, text, re.DOTALL)

#     # Return the list of matched JSON strings, stripping any leading or trailing whitespace
#     try:
#         return [json.loads(match.strip()) for match in matches][0]
#     except Exception:
#         raise ValueError(f"Failed to parse: {message}")
    

# # if __name__ == "__main__":
# #     txt="""```json
# #             {
# #               "session_id": "session_id_here",
# #               "name": "user name",
# #               "rank": "user rank",
# #               "email": "user email",
# #               "interested_colleges": ["college1", "college2"],
# #               "interested_places": ["place1", "place2"],
# #               "career_streams": ["stream1", "stream2"],
# #               "category": "user category"
# #             }
# #             ```"""
# #     # res = parse_json(txt)

# #     print(res[0])
# #     print(type(res[0]))