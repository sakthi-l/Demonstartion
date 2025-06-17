from pymongo import MongoClient

uri = "mongodb+srv://SakthiLoganathan:mypassword123@cluster1.gdrhxx1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"

client = MongoClient(uri)
db = client['ebooks_db']  # Your database name — create/use ebooks_db
collection = db['books']
