"""
This is the source code for processing SAP Data using Autogen and Chainlit
Features:
- Continuous messaging
- Multithreading 
Written by: Antoine Ross - October 2023.
"""

from typing import Dict, Optional, Union

import autogen
from autogen import Agent, AssistantAgent, UserProxyAgent, config_list_from_json
import chainlit as cl

# Edit the URL Here
URL = "https://www.w3schools.com/xml/simple.xml"

WELCOME_MESSAGE = f"""Datascience Agent Team 👾
\n\n
What can we do for you today?
"""

# We plug a context to the Code Planner so that it understands the File Format. This saves us money from tokens since read is cheaper than write.
CONTEXT = f"""Access the XML data from the following link: {URL}. Utilize the libraries 'urllib.request' and 'xml.etree.ElementTree' for sending a GET request and parsing the XML data, respectively.

Ensure to always check the length of the context to avoid hitting the context limit. Do not express gratitude in responses. If "Thank you" or "You're welcome" are said in the conversation, send a final response. Your final response is just "TERMINATE", do not add other sentences."""

# Agents
USER_PROXY_NAME = "Query Agent"
CODING_PLANNER = "Code Planner"
CODING_RUNNER = "Code Runner"
DATA_ANALYZER = "Analysis Agent"

async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res

class ChainlitAssistantAgent(AssistantAgent):
    """
    Wrapper for AutoGens Assistant Agent
    """
    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        cl.run_sync(
            cl.Message(
                content=f'*Sending message to "{recipient.name}":*\n\n{message}',
                author=self.name,
            ).send()
        )
        super(ChainlitAssistantAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )

class ChainlitUserProxyAgent(UserProxyAgent):
    """
    Wrapper for AutoGens UserProxy Agent. Simplifies the UI by adding CL Actions. 
    """
    def get_human_input(self, prompt: str) -> str:
        if prompt.startswith(
            "Provide feedback to chat_manager. Press enter to skip and use auto-reply"
        ):
            res = cl.run_sync(
                ask_helper(
                    cl.AskActionMessage,
                    content="Continue or provide feedback?",
                    actions=[
                        cl.Action( name="continue", value="continue", label="✅ Continue" ),
                        cl.Action( name="feedback",value="feedback", label="💬 Provide feedback"),
                        cl.Action( name="exit",value="exit", label="🔚 Exit Conversation" )
                    ],
                )
            )
            if res.get("value") == "continue":
                return ""
            if res.get("value") == "exit":
                return "exit"

        reply = cl.run_sync(ask_helper(cl.AskUserMessage, content=prompt, timeout=60))

        return reply["content"].strip()

    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        cl.run_sync(
            cl.Message(
                content=f'*Sending message to "{recipient.name}"*:\n\n{message}',
                author=self.name,
            ).send()
        )
        super(ChainlitUserProxyAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )

@cl.on_chat_start
async def on_chat_start():
  try:
    config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
    coding_assistant = ChainlitAssistantAgent(
        name="Code_Planner", llm_config={"config_list": config_list},
        system_message="""Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. 
                The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the SAP_DATA_and_AI Engineer.
                Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the SAP_DATA_and_AI Engineer.
                If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code.""" + CONTEXT
    )
    coding_runner = ChainlitUserProxyAgent(
        name="Code_Runner", llm_config={"config_list": config_list}, human_input_mode="NEVER",
        code_execution_config={
            "last_n_messages": 3,
            "work_dir": "workspace",
            "use_docker": True,
        },
        system_message="""A Coding Engineer. Use python to run code. Interact with the Code_Planner to run code. Report the result.
                You are an AI model capable of executing code."""
    )
    analysis_agent = ChainlitAssistantAgent(
        name="Analysis_Agent", llm_config={"config_list": config_list},
        system_message="""Analysis agent. You analyse the data outputted by Code_Runner when necessary. Be concise and always summarize the data when possible.
                Communicate with the Query_Agent when the data is analyzed."""
    )
    user_proxy = ChainlitUserProxyAgent(
        name="Query_Agent",
        # human_input_mode="TERMINATE",
        # max_consecutive_auto_reply=3,
        # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
        system_message="""Manager. Administrate the agents on a plan. Communicate with the Code_Planner to plan the code. 
                Communicate with the Analysis_Agent when we want to analyse the data. Reply TERMINATE at the end of your sentence if the task has been solved at full satisfaction. 
                Otherwise, reply CONTINUE, or the reason why the task is not solved yet.""" 
    )
    
    cl.user_session.set(USER_PROXY_NAME, user_proxy)
    cl.user_session.set(CODING_PLANNER, coding_assistant)
    cl.user_session.set(CODING_RUNNER, coding_runner)
    cl.user_session.set(DATA_ANALYZER, analysis_agent)
    
    await cl.Message(content=WELCOME_MESSAGE, author="Query_Agent").send()
    
  except Exception as e:
    print("Error: ", e)
    pass

@cl.on_message
async def run_conversation(message: cl.Message):
  try:
    TASK = message.content
    print("Task: ", TASK)
    coding_assistant = cl.user_session.get(CODING_PLANNER)
    user_proxy = cl.user_session.get(USER_PROXY_NAME)
    coding_runner = cl.user_session.get(CODING_RUNNER)
    analysis_agent = cl.user_session.get(DATA_ANALYZER)
    
    groupchat = autogen.GroupChat(agents=[user_proxy, coding_assistant, coding_runner, analysis_agent], messages=[], max_round=50)
    manager = autogen.GroupChatManager(groupchat=groupchat)
    
    print("GC messages: ", len(groupchat.messages))
    
    if len(groupchat.messages) == 0:
      await cl.Message(content=f"""Starting agents on task: {TASK}...""").send()
      await cl.make_async(user_proxy.initiate_chat)( manager, message=TASK, )
    else:
      await cl.make_async(user_proxy.send)( manager, message=TASK, )
      
  except Exception as e:
    print("Error: ", e)
    pass