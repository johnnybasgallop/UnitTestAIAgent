import os

from llama_index.core.tools import FunctionTool

# FunctionTool allows us to use a python function as a tool for the LLM


# Code reader function, takes in the file_name as a parameter
# Gets the path via os.join, combining it with out "data" dir
# Trys to open and read the file, then it returns contents as a dict response, assigning the content to "file_content"
# Returns Exceptions as a dict, assigning the str of e as the "error"
def code_reader(file_name):
    path = os.path.join("data", file_name)
    try:
        with open(path, "r") as f:
            content = f.read()
            return {"file_content": content}
    except Exception as e:
        return {"error occured": str(e)}


# Wrapping the function as a tool
# Define the tool as a FunctionTool utilising the from_defaults method
# We pass in the python function in the fn (stands for function)
# The rest of the arguments are the same as defining the tool in main.py (name of the tool and description of when its used)
code_reader = FunctionTool.from_defaults(
    fn=code_reader,
    name="code_reader",
    description="""this tool can read the contents of code files and return
    their results. Use this when you need to read the contents of a file""",
)
