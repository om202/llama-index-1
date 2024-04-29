import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.conversation.base import ConversationChain

PERSIST_DIR = './persist'
llm = OpenAI()
_DEFAULT_TEMPLATE = """
The following is a friendly conversation between a human and an restaurant Server.
The Server is talkative, polite and provides lots of specific details from its context. 
If the Server does not know the answer to a question, it truthfully says it does not know.
Relevant pieces of previous conversation:

{history}

(You do not need to use these pieces of information if not relevant)

Current conversation:
Human: {input}
AI:
"""
PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_DEFAULT_TEMPLATE
)

raw_text = TextLoader('./data/data.txt').load()
text_split = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_split.split_documents(raw_text)

embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

if os.path.exists(PERSIST_DIR):
    db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding)
else:
    db = Chroma.from_documents(documents=docs, embedding=embedding, persist_directory='./persist')

retriever = db.as_retriever()
memory = VectorStoreRetrieverMemory(retriever=retriever)

chain_mem = ConversationChain(
    llm=llm,
    prompt=PROMPT,
    memory=memory,
    verbose=False
)

os.system('clear')

while True:
    q = input('ask >> ')
    chat = chain_mem(q)
    print('\n')
    print(chat)
