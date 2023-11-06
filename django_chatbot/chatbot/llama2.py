from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
import sys

DB_FAISS_PATH = 'vectorstore/db_Torch'

llm=CTransformers(model="llama-2-7b-chat.ggmlv3.q8_0.bin",
                  model_type="llama",
                  config={'max_new_tokens':150,
                          'temperature':0.01})

template="""Use the following pieces of information to answer the user's question.
If you dont know the answer just say you know, don't try to make up an answer.

Context:{context}
Question:{question}

Only return the helpful answer below and nothing else
Helpful answer
"""
embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device':'cpu'})

qa_prompt=PromptTemplate(template=template, input_variables=['context', 'question'])

vector_store = FAISS.load_local(DB_FAISS_PATH, embeddings)

chain = RetrievalQA.from_chain_type(llm=llm,
                                   chain_type='stuff',
                                   retriever=vector_store.as_retriever(search_kwargs={'k': 2}),
                                   return_source_documents=True,
                                   chain_type_kwargs={'prompt': qa_prompt})

def ask(query):
    if query=='exit':
        print('Exiting')
        sys.exit()

    result=chain({'query':query})
    print(f"Answer:{result['result']}")

print(ask('what is soft computing'))