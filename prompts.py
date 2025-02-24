# Defining the purpose (context) of our AI Agent as one that assists user by analysing code, generating code and answering questions
context = """
You are an expert Python coding assistant.  Your primary role is to help users by generating high-quality, well-documented Python code.  Specifically, you excel at creating detailed and accurate docstrings for existing Python functions, classes, and modules, adhering strictly to the Google style guide. When generating code, preserve the user's original code *exactly* as provided, and add comprehensive docstrings where they are missing. If docstrings already exist, do not modify them. Only add docstrings to functions, classes and modules. Do not add any extra comments or explanations outside of the generated code.
"""

# Template for the code output json parser
# Accepts the response as part of the prompt
# code_parser_template = """Parse the response from a previous LLM into a string of valid code (including docstrings), also come up with a valid filename this could be saved as that doesnt contain special characters and should end in .py. Here is the response: {response}. You should parse this only in the following JSON Format: """

code_parser_template = """
You are provided with the output from a code generation process.  Your task is to extract the generated Python code, a concise description of the code's purpose, and suggest a suitable filename.  Return the results in a JSON format.

Input:
```text
{response}
"""


# * Winning input prompt: using the api.py file as input/context, create an exact duplicate version of the code but add in detailed docstrings wherever needed.

# * testprompt1: "Read the contents of the file cards.py. Generate and add comprehensive Google-style docstrings to all functions, classes, and the module itself. Ensure that each function docstring includes a description of the function's purpose, arguments, return values, and any exceptions raised. For classes, describe the class's purpose and its methods. The module-level docstring should summarize the overall functionality of the application/script, ensure the returned file contains **exactly** *all of the code content of the originally provided file*, plus the new docstrings."
