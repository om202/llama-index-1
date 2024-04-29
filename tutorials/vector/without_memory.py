import os
from dotenv import load_dotenv
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

VECTOR_DIR = './vector_store'

# API KEYS
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

if os.path.exists(VECTOR_DIR):
    vectorstore = Chroma(persist_directory=VECTOR_DIR, embedding_function=OpenAIEmbeddings())
else:
    # LOAD -> Load data, split
    loader = WebBaseLoader(
        web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
        bs_kwargs=dict(
            parse_only=bs4.SoupStrainer(
                class_=("post-content", "post-title", "post-header")
            )
        ),
    )
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # vector store
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory=VECTOR_DIR)

# prepare to chat
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

# ret_docs = retriever.invoke("What are the approaches to Task Decomposition?")
#
# for docs in ret_docs:
#     print('\n\n')
#     print(docs)

prompt = hub.pull("rlm/rag-prompt")


def format_docs(_docs):
    return "\n\n".join(doc.page_content for doc in _docs)


rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

chat = rag_chain.invoke("What is Task Decomposition?")

print(chat)
