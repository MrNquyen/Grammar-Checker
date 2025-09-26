from typing import List

from langchain_core.prompts import (
    #-- Create prompt
    ChatPromptTemplate, 
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,

    # Chat history
    MessagesPlaceholder  
)

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


class ConversationChatPromptCreator:
    def __init__(self):
        pass

    #-- CREATE ROLE PROMPT
    def create_role_prompt_chain(self, role: str, prompt_template: str):
        """
            Create a role chat JSON template for the corresponding role for chaining 
            (without input_variables).

            Args:
                role (str): Role type ('human', 'system', 'ai').
                prompt_template (str): Template for your prompt.

            Returns:
                PromptTemplate: A prompt instance with matching input variables.
        """
        role_map = {
            "system": SystemMessagePromptTemplate,
            "human": HumanMessagePromptTemplate,
            "ai": AIMessagePromptTemplate,
        }

        try:
            PromptTemplateFunction = role_map[role]
        except KeyError:
            raise ValueError(f"Invalid role '{role}'. Expected one of {list(role_map.keys())}.")

        return PromptTemplateFunction.from_template(prompt_template)


    def create_role_prompt(self, role: str, prompt_template: str, input_variables: dict = {}):
        """
        Create role chat json template for corresponding role - with input_variables

        Args:
            role (str): Your role (human | system | ai)
            prompt_template (str): Template for your prompt
            input_variables (dict, optional): Input variables for prompt_template. Defaults to {}.

        Returns:
            str: Prompt with matching inout variables
        """
        #-- Load prompt
        prompt = self.create_role_prompt_chain(
            role=role,
            prompt_template=prompt_template
        )

        #-- Check and Create
        def isInputVariablesFitted(
            prompt_object, 
            input_variables: dict
        ):
            template_input_variables = prompt_object.input_variables
            input_variables_keys = input_variables.keys()
            
            #~ Check length
            if not len(template_input_variables) == len(input_variables_keys):
                raise ValueError(f"Number of input_variables must fit the input_variables of template")
            
            #~ Check input_variables keys match all input_variables in template 
            for template_input_variable in template_input_variables:
                if template_input_variable not in input_variables_keys:
                    raise ValueError(f"Template has variable {template_input_variable}, but no value match for {template_input_variable}")

        isInputVariablesFitted(
            prompt_object=prompt, 
            input_variables=input_variables
        )
        return prompt.format_messages(**input_variables)


    def create_multiple_role_prompt(self, multiple_conversations: List[dict]):
        """
        Create multi-turn conversations prompts

        Args:
            multiple_conversations (List[dict]): List of each turn informations
        
        Examples:
            multiple_conversations (List[dict]): [
                {"role": ..., "prompt_template": ..., "input_variables": ...},
                {"role": ..., "prompt_template": ..., "input_variables": ...},
                {"role": ..., "prompt_template": ..., "input_variables": ...},
            ]
        """
        conversation_prompts = []
        for turn in multiple_conversations:
            conversation_prompts += self.create_role_prompt(**turn)
        return conversation_prompts
    
    
    def create_multiple_role_prompt_chain(self, multiple_conversations: List[dict]):
        """
        Create multi-turn conversations prompts without input_variables

        Args:
            multiple_conversations (List[dict]): List of each turn informations
        
        Examples:
            multiple_conversations (List[dict]): [
                {"role": ..., "prompt_template": ...},
                {"role": ..., "prompt_template": ...},
                {"role": ..., "prompt_template": ...},
            ]
        """
        conversation_prompts = []
        for turn in multiple_conversations:
            conversation_prompts += [self.create_role_prompt_chain(**turn)] # Return MessagePromptTemplate not a list like when format_messages 
        return conversation_prompts


    #-- MODIFYING CONVERSATIONS
    def add_turn(self, origin_chat_prompt_template, added_template):
        """
        Add one more turn to existing multiturn conversation

        Args:
            origin_chat_prompt_template (ChatPromptTemplate): Original multiturn conversations
            added_template (ChatPromptTemplate): Added turn 
        """
        pass

    #-- INSTRUCTIONS



class SchemaCreator:
    #-- Response Schema
    def create_response_schema(self, name: str, description: str) -> ResponseSchema:
        """
        Get Response Schema Info instance

        Args:
            name (str): _description_
            description (str): _description_

        Returns:
            ResponseSchema: ResponseSchema instance
        """
        return ResponseSchema(name=name, description=description)


    def create_multiple_response_schema(self, schema_infos: List[dict]) -> List[ResponseSchema]:
        """
        Get List of Response Schema Info for model response

        Args:
            schema_infos (List[dict]): List of ResponseSchema params

        Returns:
            List[ResponseSchema]: List of ResponseSchema instances
        """
        return [self.create_response_schema(**schema_info) for schema_info in schema_infos]
