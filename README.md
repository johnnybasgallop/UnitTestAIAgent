# CodeGenAIAgent

This project provides a simple AI-powered coding assistant/agent that can help you analyze existing code, generate new code and implement it in new files, and answer your questions about code. It's designed to make coding easier and more efficient.

## Features

* **Code analysis:**
    * Finds bugs and suggests improvements.
    * Explains how code works.
* **Code generation:**
    * Creates code snippets in multiple languages (Python (reccomended), JavaScript, C++, Java).
    * Generates code based on your descriptions and input files (via filenames).
* **Question answering:**
    * Answers your questions about code and programming concepts.

## Getting Started

1. **Install:**
    * Make sure you have Python 3.8 or higher but also <=Python3.12
    * Clone this repository and install the required packages:
    ```bash
    git clone [https://github.com/johnnybasgallop/UnitTestAIAgent.git](https://github.com/johnnybasgallop/UnitTestAIAgent.git)
    pip install -r requirements.txt
    ```

2. **Set up Ollama:**
    * Install Ollama and download the `mistral` and `codellama` models, instructions can be found here: [https://github.com/ollama/ollama]
    * Download the models by running:
    ```bash
    ollama run mistral
    ollama run codellama
    ```

3. **Run:**
    * Put your code files you want as inpu or conetext in the `data` folder.
    * Run the agent: `python3 main.py`
    * Type your coding-related questions or requests.
    * Output files can be found in the dedicated output folder

## Examples

* "based off the API found in `test.py`, write me a new python script that calls the delete endpoint and passes in an item id to delete."
* "What are the main differences between Python and JavaScript?"
* "Find any potential issues in my `test.py` file."

## How it Works

This project uses:

* **LlamaIndex:** A powerful library for working with large language models (LLMs), It provides many tools used in this project.
* **Ollama:** To run large language models locally on your computer.
* **LlamaParse:** A tool for parsing documents, particularly unstructured data like PDFs.
* **Pydantic** A library for data validation and parsing using Python type hints. BaseModel is used to define the structure of the output.

## Contributing

Feel free to contribute to this project! You can report issues, suggest features, or submit code improvements.

## License

MIT License
