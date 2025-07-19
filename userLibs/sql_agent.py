from dotenv import load_dotenv
import getpass
import os

from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain import hub
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from IPython.display import display, Markdown #to render results
from pprint import pprint
env_path = "../.env"

def render(text):
    display(Markdown(text))

class SQL_Agent:

    def __init__(self, model_provider = None, model_name=None, dialect=None, database_uri=None, top_k = 10):
        
        self.llm = None
        if model_provider and model_name:
            self.set_llm(model_provider, model_name)

        self.db = None
        if database_uri:
            self.set_db(database_uri)

        self.tools = None
        self.prompt_template = None
        self.system_message = None
        self.agent_executor = None
        if self.db and self.llm:
            self.set_tools()
            if dialect:
                self.set_prompts(dialect, top_k)
                if self.system_message:
                    self.initialize_agent()
        
    def set_llm(self, model_provider, model_name):
        load_dotenv(env_path)
        self.llm = init_chat_model(model_name, model_provider=model_provider,temperature=0.1)

    def set_db(self,database_uri):
        self.db = SQLDatabase.from_uri(database_uri, view_support = True)

    def set_tools(self):
        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.tools = toolkit.get_tools()

    def set_prompts(self, dialect, top_k):
        self.prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        assert len(self.prompt_template.messages) == 1
        self.system_message = self.prompt_template.format(dialect=dialect, top_k=top_k)

    def set_custom_system_message(self, custom_system_message):
        self.system_message = custom_system_message

    def initialize_agent(self):
        self.agent_executor = create_react_agent(self.llm, self.tools, prompt=self.system_message)

    def answer(self,question):
        response = self.agent_executor.invoke({"messages": [{"role": "user", "content": question}]})
        return(response["messages"][-1].content)
    
    def answer_full(self,question):
        response = self.agent_executor.invoke({"messages": [{"role": "user", "content": question}]})
        return(response)
    
    def stream_answer(self, question):
        last_message = None
        thinking_process = []
        
        for step in self.agent_executor.stream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
        ):
            # Extract useful info from the step
            if "messages" in step and step["messages"]:
                current_message = step["messages"][-1]
                
                # For AIMessage with function calls
                if hasattr(current_message, "additional_kwargs") and "function_call" in current_message.additional_kwargs:
                    function_info = {
                        "type": "function_call",
                        "name": current_message.additional_kwargs["function_call"]["name"],
                        "arguments": current_message.additional_kwargs["function_call"]["arguments"]
                    }
                    thinking_process.append(function_info)
                
                # For ToolMessage (function outputs)
                elif hasattr(current_message, "name") and hasattr(current_message, "content"):
                    tool_info = {
                        "type": "tool_output",
                        "name": current_message.name,
                        "content": current_message.content
                    }
                    thinking_process.append(tool_info)
                
                # # Store final answer content if it's the final message
                # if hasattr(current_message, "content") and current_message.content:
                #     if not any([hasattr(current_message, name) for name in ["tool_calls", "function_call"]]):
                #         thinking_process.append({
                #             "type": "answer",
                #             "content": current_message.content
                #         })
                
                last_message = current_message
            
            # print(f"Thinking: {thinking_process[-1] if thinking_process else 'No thinking yet'}")
        
        # for thinking_step in thinking_process:
        #     pprint(thinking_step)

        return {
            "answer": last_message.content if last_message else None,
            "thinking": thinking_process
        }
