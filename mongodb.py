import pymongo
from django.conf import settings

my_client = pymongo.MongoClient('mongodb')

db = my_client['chatbot']

class Table:
    def __init__(self,table,requrieditems):
        self.table = db[table]
        self.requireditems = requrieditems
    def find(self,**terms):
        return self.table.find(terms)
    def find_one(self,**terms):
        return self.table.find_one(terms)
    def write(self,**terms):
        """writes a document to the table of the instance of the class calling the function
        these terms are required for the 3 tables:
        users:
            user
        conversations:
            userID
        messages:
            convID
            prompt
            response
        
        IDs for the written document will be created on the fly and can be accessed with the `.inserted_id` method

        Raises:
            Exception: Missing Argument if not all required items are passed as terms

        Returns:
            InsertOneResult: the result from mongodb for inserting the document
        """
        for item in self.requireditems:
            if item not in terms:
                raise KeyError(f"missing argument: {item}")
        return self.table.insert_one(terms)
            
messagesTable = Table('messages',[
    'convID',
    'prompt',
    'response'
])
conversationsTable = Table('conversations',[
    'userID'
])
usersTable = Table('users',[
    'user'
])
