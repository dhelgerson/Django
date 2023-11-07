# tell me about torch tech?
# what are the benefits of working with torch tech?
# benefits of torch if you are a military personnel?
# what does the ceo of the torch has to say about the company?
# what does Torch Cybersecurity works for DoD?

from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpRequest
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone
from django.test.client import RequestFactory

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.llms.ctransformers import CTransformers
import sys


DB_FAISS_PATH = '../vectorstore/db_Torch'

llm=CTransformers(model="../llama-2-7b-chat.ggmlv3.q8_0.bin",
                  model_type="llama",
                  config={'max_new_tokens':512,
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
                                   retriever=vector_store.as_retriever(
                                       search_type="mmr",
                                       search_kwargs={'k': 2, 'fetch_k': 50}
                                   ),
                                   return_source_documents=True,
                                   chain_type_kwargs={'prompt': qa_prompt})


# Create your views here.
def chatbot(request:HttpRequest):
    chats = Chat.objects.filter(user=request.user.id)

    if request.method == 'POST':
        message = request.POST.get('message')
        # response = chain({'query':message})
        print("working")
        temp = chain({'query': message})
        response = str(temp['result'])
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()

        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html' , {'chats': chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
