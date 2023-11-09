import pymongo
from django.conf import settings

my_client = pymongo.MongoClient('mongodb')

db = my_client['chatbot']

class Table:
    def __init__(self,table,requrieditems):
        self.table = db[table]
        self.requireditems = requrieditems
    def find(self,**terms):
        self.table.find(terms)
    def write(self,**terms):
        for item in self.requireditems:
            if item not in terms:
                raise Exception("missing arguments")
            
messagesTable = Table('messages',[
    'user',
    'prompt',
    'response'
])
conversationsTable = Table('conversations',[
    'user',
    'conversationID'
])
usersTable = Table('users',[
    'user'
])
