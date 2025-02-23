# Defining the purpose (context) of our AI Agent as one that assists user by analysing code, generating code and answering questions
context = """Purpose: The primary role of this agent is to assist users by analyzing code. It should Act as a talented software engineer and be able to generate high quality and detailed code and answer questions about code provided. """

# Template for the code output json parser
# Accepts the response as part of the prompt
code_parser_template = """Parse the response from a previous LLM into a description and a string of valid code, also come up with a valid filename this could be saved as that doesnt contain special characters. Here is the response: {response}. You should parse this only in the following JSON Format: """
