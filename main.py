# imports
from dotenv import load_dotenv
from llama_index.core import PromptTemplate, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse

# Loading in the Llama cloud api key, Llamaparse will use it automatically when loaded in
load_dotenv()

# 1. Load in and parse the PDF into logical portions&chunks
# 2. Create a vector store index, which is like a database that allows us to find info we're looking for
# 3. The the llm can extract only the information it needs to answer a query or a prompt
# 4 The vector store index will utilise vector embeddings, these allow us to take our data, embed it into multidimensional space
# 5 These vector embeddings allow us to query the data based on things like context, sentiment etc. (black box esque process)


# Define the llm object passing in the model name and request_timeout
llm = Ollama(model="mistral", request_timeout=30.0)

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

# Retrieving the local model using the resolve_embed_model and passing in the local model
# We will use this for the vector store index and vector embeddings
embed_model = resolve_embed_model("local:BAAI/bge-m3")

# Creating the vector index using the VectorStoreIndex.from_documents function and passing in our documents
# Also passing in the local embed_model we just defined manually, to avoid it using the default ones
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# All of this will then be wrapped in a query_engine which will take in our llm object defined above
# We will utilise the vector_index.as_query_engine function for this
# Now our vector index can be utilised for Questions and Answers via the query_engine object
query_engine = vector_index.as_query_engine(llm=llm)

result = query_engine.query("what are some of the routes in the API?")
print(result)
