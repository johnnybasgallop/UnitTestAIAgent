import ast
import os
import openai
from dotenv import load_dotenv
from llama_index.core import PromptTemplate, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_parse import LlamaParse
from pydantic import BaseModel

from code_reader import code_reader
from prompts import code_parser_template, context

def load_dotenv():
    """
    Loads the Llama cloud API key from the environment variables.
    """
    load_dotenv()

def main():
    """
    Main function that orchestrates the process of interacting with the Llama cloud API and OpenAI.
    """
    modelname = "gpt-3.5-turbo-0125"

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    # Other code here...

if __name__ == "__main__":
    main()