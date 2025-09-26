#==== IMPORT ====
#-- Import
import os
import json
import re 
import time

#-- From
from tqdm import tqdm
from typing import Dict, Any, Optional, Tuple, List
from icecream import ic

#=-- Langchain Library 
from langchain_openai import AzureChatOpenAI
from langchain.chains import LLMChain
from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import (
    StrOutputParser, 
    JsonOutputParser
)

#=-- Custom
from projects.modules.chatprompt import ConversationChatPromptCreator, SchemaCreator
# from chatbot.modules.knowledge_graph import KnowledgeGraphSource
from utils.registry import registry
from utils.general import save_json


#==== ENVIRONMENT VARIABLES  ====
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_VERSION = os.getenv("API_VERSION")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_DEVELOPMENT = os.getenv("AZURE_DEVELOPMENT")

os.environ["http_proxy"] = "http://127.0.0.1:3128"
os.environ["https_proxy"] = "http://127.0.0.1:3128"
os.environ["AZURE_OPENAI_API_KEY"] = API_KEY
os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_ENDPOINT


#==== BASE AGENT ====
class BaseAgent:
    def __init__(self):
        self.load_config()
        self.load_model()
        self.build_modules()

    #-- BUILD
    def load_config(self):
        #-- Header
        self.llm_config = {
            "openai_api_key": API_KEY,
            "openai_api_version": API_VERSION,
            "azure_endpoint": AZURE_ENDPOINT,
            "azure_deployment": AZURE_DEVELOPMENT,
            "temperature": 0.0
        }

    # def load_model(self):
    #     self.gpt_llm = AzureChatOpenAI(**self.llm_config)
    
    def load_model(self):
        self.gpt_llm = AzureChatOpenAI(
            openai_api_key=self.llm_config["openai_api_key"],
            openai_api_version=self.llm_config["openai_api_version"],
            azure_endpoint=self.llm_config["azure_endpoint"],
            azure_deployment=self.llm_config["azure_deployment"],
            temperature=self.llm_config["temperature"]
        )

    def build_modules(self):
        self.prompt_creator = ConversationChatPromptCreator()
        self.schema_creator = SchemaCreator()

    def create_fixed_chain(self):
        self.chain = self.gpt_llm


    #-- INIT MESSAGE AND HELPER FUNCTIONS
    def create_simple_prompt(
        self, 
        system_prompt_template: str, 
        user_prompt_template: str, 
        input_variables_info: Dict = {},
        with_input_variables: bool = True
    ):
        """
        Prompt only has two roles: system and human

        Args:
            system_prompt_template (str): System Prompt Template
            user_prompt_template (str): User Prompt Template
            input_variables_info (dict): Mapping input variables for <user> and <human>

        Examples:
            input_variables_info = {
                "system": {...},
                "human": {...},
            }

        Returns:
            _type_: List of PromptTemplate
        """
        if with_input_variables:
            messages = self.prompt_creator.create_multiple_role_prompt([
                {"role": "system", "prompt_template": system_prompt_template, "input_variables": input_variables_info.get("system", {})},
                {"role": "human", "prompt_template": user_prompt_template, "input_variables": input_variables_info.get("human", {})},       
            ])
        else:
            messages = self.prompt_creator.create_multiple_role_prompt_chain([
                {"role": "system", "prompt_template": system_prompt_template},
                {"role": "human", "prompt_template": user_prompt_template},       
            ])
        return ChatPromptTemplate.from_messages(messages)
    

    def create_multiturn_prompt(
        self, 
        multiturn_infos: List[dict],
        with_input_variables: bool = True
    ):
        """
        Create multiturn prompt to invoke LLM models

        Args:
            multiturn_infos (List[Dict]): Ordering turn list that contain information of the each turn prompt

        Examples:
            multiturn_infos = [
                {
                    "role": ...,
                    "template": ...,
                    "input_variables": ...
                }
                ...
            ]

        Returns:
            List[PromptTemplate]: List of PrompTemplate
        """

        if with_input_variables:
            multiturn_chat_dict_format = [
                {"role": info.get("role", "human"), "prompt_template": info.get("template", ""), "input_variables": info.get("input_variables", {})}
                for info in multiturn_infos
            ]
            return self.prompt_creator.create_multiple_role_prompt(multiturn_chat_dict_format)
        else:
            multiturn_chat_dict_format = [
                {"role": info.get("role", "human"), "prompt_template": info.get("template", "")}
                for info in multiturn_infos
            ]
            return self.prompt_creator.create_multiple_role_prompt_chain(multiturn_chat_dict_format)
        

    def create_response_schemas(
        self,
        schema_infos: List[dict]
    ):
        """
            Get List of Response Schema Info for model response

            Args:
                schema_infos (List[dict]): List of ResponseSchema params
            
            Examples:
                schema_infos (List[dict]): [
                    {"name": ..., "description": ...},
                    {"name": ..., "description": ...},
                    ...
                ]

            Returns:
                List[ResponseSchema]: List of ResponseSchema instances
        """
        return self.schema_creator.create_multiple_response_schema(schema_infos=schema_infos)


    #-- INVOKE
    def chaining(
        self,
        chat_prompts: List,
        output_parser,
        schemas=None,
        **kwargs
    ):
        """
        Chaining LLM with output parser format

        Args:
            chat_prompts (List): List of ChatPromptTemplate
            output_parser (langchain_core.output_parsers): Output parser for formatting LLM response 
            schemas (List[ResponseSchema]): List of Response Schema

        Returns:
            _type_: _description_
        """
        #~ Format Prompt
        if type(chat_prompts) == list:
            chat_prompts = ChatPromptTemplate.from_messages(chat_prompts)
        
        if schemas:
            parser = StructuredOutputParser.from_response_schemas(schemas)
            reponse_format_instructions = parser.get_format_instructions()
            safe_reponse_format_instructions = reponse_format_instructions.replace("{", "{{").replace("}", "}}")

            #~ Format adding response prompt to postfix
            chat_prompts = ChatPromptTemplate.from_messages(
                chat_prompts.messages + self.prompt_creator.create_role_prompt("system", safe_reponse_format_instructions)
            )

        #~ Create Chain
        chat_chain = LLMChain(
            llm=self.gpt_llm, 
            prompt=chat_prompts,
            output_parser=output_parser
        )
        
        #~ Setup schema
        # Handle input depending on whether variables exist
        if chat_prompts.input_variables:
            response = chat_chain.invoke(kwargs) # If has input variables
        else:
            response = chat_chain.invoke({}) # If dont have input variables

        return response

    #-- FORMAT OUTPUT
    def get_output_parser(self, parser_type="json", return_base_parser = False):
        parser = None
        if parser_type=="json":
            parser = JsonOutputParser()
        elif parser_type=="string":
            parser = StrOutputParser()
        else:
            raise ValueError(f"Invalid parser type {parser_type}")

        #-- Fixing parser
        fixing_parser = OutputFixingParser.from_llm(
            parser=parser, 
            llm=self.gpt_llm
        )
        return (parser, fixing_parser) if return_base_parser else fixing_parser

