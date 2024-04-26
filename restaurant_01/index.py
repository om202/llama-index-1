import os
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.core.memory import ChatMemoryBuffer


Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.llm = OpenAI(model='gpt-3.5-turbo')
memory = ChatMemoryBuffer(token_limit=1500)

try: 
    storage_context = StorageContext.from_defaults(persist_dir='./storage/bj')
    bj_index = load_index_from_storage(storage_context)
    index_loaded = True
except:
    index_loaded = False
    
if not index_loaded:
    bj_docs = SimpleDirectoryReader(input_files=['./data/bj.pdf']).load_data()
    bj_index = VectorStoreIndex.from_documents(bj_docs)
    bj_index.storage_context.persist(persist_dir='./storage/bj')

# bj_engine = bj_index.as_query_engine(similarity_top_k=3, streaming=True)
bj_engine = bj_index.as_chat_engine(
    chat_mode="condense_plus_context",
    memory=memory,
    context_prompt=(
        "You are a very polite server. Start the conversation by saying: Welcome to BJ Restaurant. How can I help you?. You know all menu items and their price. You are good at maths and can calculate the total price."
    ),
)

os.system('clear')

while True:
    q = input('\n\nask > ')
    response = bj_engine.chat(q)
    print(response.response)
    if q == '/q':
        break
