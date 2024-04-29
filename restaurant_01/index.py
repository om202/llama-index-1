import os
from llama_index.llms.openai import OpenAI
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
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
bj_index.as_chat_engine(
    chat_mode='context',
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
