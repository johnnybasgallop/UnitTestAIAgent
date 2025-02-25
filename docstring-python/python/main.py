# python/main.py
import ast
import json
import os
import sys
from datetime import datetime

from llama_index.core import PromptTemplate
from llama_index.core.agent import ReActAgent
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.llms.gemini import Gemini
from pydantic import BaseModel

# Import prompts from the separate prompts.py file
from prompts import code_parser_template, context

api_key = sys.stdin.readline().strip()

modelname = "models/gemini-1.5-flash"

llm = Gemini(model=modelname, api_key=api_key)

# We are no longer loading documents from the "data" directory.
tools = []  # No tools needed
code_llm = Gemini(
    model=modelname, api_key=api_key
)  # Could use the same LLM, but kept separate for clarity
agent = ReActAgent.from_tools(tools=tools, llm=code_llm, verbose=True, context=context)


class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str


parser = PydanticOutputParser(CodeOutput)

# --- Read filename and content from stdin ---
filename = sys.stdin.readline().strip()
file_content = sys.stdin.read()

# --- Construct the prompt ---
#  Remove file extension
if "." in filename:
    filename_without_extension = filename.rsplit(".", 1)[0]
else:
    filename_without_extension = filename

json_prompt_str = parser.format(code_parser_template)
json_prompt_tmpl = PromptTemplate(json_prompt_str)


query_pipeline = QueryPipeline(chain=[json_prompt_tmpl, llm])  # Parser first!

retries = 0
while retries < 3:
    try:
        # Run the query pipeline directly with the formatted prompt
        result = query_pipeline.run(response=file_content)
        cleaned_json = ast.literal_eval(
            str(result)
            .replace("assistant:", "")
            .replace("```json", "")
            .replace("```", "")
        )
        # result is ALREADY the parsed JSON object, thanks to the PydanticOutputParser
        break
    except Exception as e:
        retries += 1
        print(f"Error occurred, retry #{retries}:", e, file=sys.stderr)

if retries >= 3:
    print("Unable to process request, try again...", file=sys.stderr)
    sys.exit(1)

# --- Output the JSON to stdout ---
print(json.dumps(cleaned_json))  # Output the Pydantic model as a dictionary, then to JSON
