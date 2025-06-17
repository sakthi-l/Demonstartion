import streamlit as st
from pymongo import MongoClient
import urllib.parse

username = st.secrets["mongodb"]["username"]
password = urllib.parse.quote_plus(st.secrets["mongodb"]["password"])  # encode if special chars
cluster = st.secrets["mongodb"]["cluster"]
appname = st.secrets["mongodb"]["appname"]

uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName={appname}"

client = MongoClient(uri)
db = client['ebooks_db']
collection = db['books']
