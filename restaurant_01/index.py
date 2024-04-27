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
from llama_index.core.memory.chat_memory_buffer import ChatMemoryBuffer


llm = OpenAI(model='gpt-4')
memory = ChatMemoryBuffer(token_limit=3000)

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
    chat_mode="context",
    memory=memory,
    llm=llm,
    context_prompt=(
        "You are a server at Colorado Curry Indian Restaurant. You act polite and are always ready to assist customers with their needs. When cusomter say Hi, you say Welcome to Colorado Curry."
    ),
    verbose=False,
)

os.system('clear')

while True:
    q = input('\n\nask > ')
    response = bj_engine.chat(q)
    print(response)
    # r = bj_engine.query(q)
    # r.print_response_stream()
    if q == '/q':
        break
