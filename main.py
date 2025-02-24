# imports
import ast
import json
import os
import re
from datetime import datetime

import openai
from dotenv import load_dotenv
from llama_index.core import PromptTemplate, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.gemini import Gemini
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_parse import LlamaParse
from pydantic import BaseModel

from code_reader import code_reader
from prompts import code_parser_template, context

# Loading in the Llama cloud api key, Llamaparse will use it automatically when loaded in
load_dotenv()

modelname = "models/gemini-1.5-flash"

# Check for OpenAI API Key
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

# 1. Load in and parse the PDF into logical portions&chunks
# 2. Create a vector store index, which is like a database that allows us to find info we're looking for
# 3. The the llm can extract only the information it needs to answer a query or a prompt
# 4 The vector store index will utilise vector embeddings, these allow us to take our data, embed it into multidimensional space
# 5 These vector embeddings allow us to query the data based on things like context, sentiment etc. (black box esque process)


# Define the llm object passing in the model name and request_timeout
llm = Gemini(model=modelname)
# Define a parser and pass in a result type format e.g. markdown
# Takes documents, pushes them out to the cloud, parses them and returns the parse
# Provides better results for unstructured data like our pdfs
parser = LlamaParse(result_type="markdown")

# Dictionary that essentially says when we find a .pdf file, we want to use the parser on it
file_extractor = {".pdf": parser}

# Uses the simple directory reader that takes in a path as input and a file extractor
# Collects relevant files from the directory and applys the above file extractor to it
# Loads the data and assigns the content to the documents variable
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

# Creating the vector index using the VectorStoreIndex.from_documents function and passing in our documents
# Also passing in the local embed_model we just defined manually, to avoid it using the default ones
vector_index = VectorStoreIndex.from_documents(documents)

# All of this will then be wrapped in a query_engine which will take in our llm object defined above
# We will utilise the vector_index.as_query_engine function for this
# Now our vector index can be utilised for Questions and Answers via the query_engine object
query_engine = vector_index.as_query_engine(llm=llm)

# Defining a list of tools we can provide to the AI Agent
# When answering a query, the AI Agent will automatically pick the best option from these tools
# First Tool is a QueryEngineTool object taking in our query_engine object and also some metadata
# The metadata is a ToolMetaData object which takes in a name and a description of the tools purpose
# Second tool is the code reader tool, as defined in code_reader.py
tools = [
    QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="api_documentation",
            description="this gives documentation about code for an API. Use this for reading docs for the API",
        ),
    ),
    code_reader,
]

# Defining a new llm object which is more suited to code generation as oppposed to Q&A
code_llm = Gemini(model=modelname)

# Defining the agent which is a ReActAgent object calling the from_tools function
# We pass our array of tools, new llm object, Verbose (Boolean) for if you want to see the agents thoughts and a context string.
# The context string can be found in prompts.py and it describes the agents purpose
agent = ReActAgent.from_tools(tools=tools, llm=code_llm, verbose=True, context=context)


# Define the pydantic object, using the Basemodel as the base class
# Contains the code, description and relevant filename
class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str


# Defining the parser to be a PydanticOutputParser, accepting CodeOutput as the output class
# Defines the format of the parser to be the CodeOutput class
parser = PydanticOutputParser(CodeOutput)

# Uses the parser (and by extention the CodeOutput class) to format the returned json_prompt_str
# parser.format will find the JSON representation that conforms to CodeOutput and will format it appropriately
# it will then inject it into the code_parser_template
json_prompt_str = parser.format(code_parser_template)

# Creating the prompt template using our previoulsly defined json_prompt_str
json_prompt_tmpl = PromptTemplate(json_prompt_str)

# Defining our query pipeline to determine the chain of events
# Setting the chain to take our json template and pass it to our llm (not the code llm)
output_pipeline = QueryPipeline(chain=[json_prompt_tmpl, llm])

# While loop for taking in user prompts
# Takes in a user input, Calls the agent.query() method passing the user input via the prompt variable
# Assigns the return of the agent.query() call to the result variable
# Passed the result to our output pipeline and run it, saying our response (in the parser template) = to the result
# The output pipeline should then pass that code_parser_template through to the llm and assigns the llms response to next_result
# q to quit the loop

# prompt: read the contents of the test.py file and write a python script that calls the post endpoint in that file to make a new item
while (prompt := input("Enter filename (q to quit): ")) != "q":

    dt = datetime.now()  # for date and time
    ts = datetime.timestamp(dt)

    adjusted_prompt = f"""
    Read the contents of the file {prompt} then Generate and add comprehensive Google-style docstrings to all functions, classes, and the module itself. Ensure that each function docstring includes a description of the function's purpose, arguments, return values, and any exceptions raised. For classes, describe the class's purpose and its methods. ensure the returned file contains **exactly** *all of the code content of the originally provided file*, plus the new docstrings.
    """
    retries = 0

    while retries < 3:
        try:
            result = agent.query(adjusted_prompt)
            next_result = output_pipeline.run(response=result)
            print(f"{next_result}")
            cleaned_json = ast.literal_eval(str(next_result).replace("assistant:", ""))
            break
        except Exception as e:
            retries += 1
            print(f"Error occured, retry #{retries}:", e)

    if retries >= 3:
        print("Unable to process request, try again...")
        continue

    print("Code generated")
    print(cleaned_json["code"])
    print("\n\nDesciption:", cleaned_json["description"])

    filename = cleaned_json["filename"]

    try:
        with open(os.path.join("review", f"{prompt[:-3]}_{ts}_review.py"), "w") as f:
            f.write(cleaned_json["code"])
        print("Saved file", filename)
    except:
        print("Error saving file...")
