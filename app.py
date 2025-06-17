import streamlit as st
from pymongo import MongoClient
import urllib.parse

# MongoDB credentials from Streamlit secrets
username = st.secrets["mongodb"]["username"]
password = urllib.parse.quote_plus(st.secrets["mongodb"]["password"])
ADMIN_USERNAME = st.secrets["mongodb"]["admin_username"]

uri = f"mongodb+srv://{username}:{password}@cluster0.0d7syo5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['ebooks_db']
collection = db['books']

st.title("📚 E-Books Library")

# Username login (no password)
if "username" not in st.session_state:
    st.session_state["username"] = ""

with st.sidebar:
    st.subheader("🔐 Login")
    st.session_state["username"] = st.text_input("Enter your username")

st.markdown(f"👤 Logged in as: **{st.session_state['username'] or 'Guest'}**")

# Admin - Add Book form
if st.session_state["username"] == ADMIN_USERNAME:
    with st.expander("➕ Add New Book"):
        with st.form("add_book_form"):
            title = st.text_input("Title")
            author = st.text_input("Author")
            language = st.text_input("Language")
            domain = st.text_input("Domain")
            published_year = st.text_input("Published Year")
            link = st.text_input("Book Link (URL)")
            submit = st.form_submit_button("Add Book")

            if submit:
                if title and author and language and domain and published_year and link:
                    collection.insert_one({
                        "title": title,
                        "author": author,
                        "language": language,
                        "domain": domain,
                        "published_year": published_year,
                        "link": link
                    })
                    st.success(f"'{title}' has been added!")
                    st.experimental_rerun()
                else:
                    st.error("All fields are required.")

# -------- TITLE SEARCH WITH AUTOCOMPLETE --------
all_books = list(collection.find({}, {"title": 1, "author": 1, "language": 1, "link": 1}))
all_titles = sorted(set(book["title"] for book in all_books))

st.subheader("🔍 Search by Title (autocomplete)")

title_search = st.text_input("Type to search titles")

filtered_titles = [t for t in all_titles if t.lower().startswith(title_search.lower())] if title_search else []

if title_search:
    if filtered_titles:
        st.write(f"Books starting with '{title_search}':")
        for t in filtered_titles:
            matching_books = [b for b in all_books if b["title"] == t]
            for book in matching_books:
                st.markdown(f"**{book['title']}** by *{book.get('author', 'Unknown')}* ({book.get('language', 'N/A')})")
                st.write(f"[Open Book]({book.get('link','')})")

                if st.session_state.get("username") == ADMIN_USERNAME:
                    if st.button(f"❌ Delete '{book['title']}'", key=str(book['_id'])):
                        collection.delete_one({"_id": book["_id"]})
                        st.success(f"'{book['title']}' deleted.")
                        st.experimental_rerun()
    else:
        st.info("No titles found starting with that input.")

# -------- ADVANCED SEARCH --------
with st.expander("⚙️ Advanced Search (Domain, Author, Language, Published Year)"):
    domain_search = st.text_input("Domain")
    author_search = st.text_input("Author")
    language_search = st.text_input("Language")
    published_year_search = st.text_input("Published Year")

    if st.button("Search Advanced"):
        query = {}
        if domain_search.strip():
            query["domain"] = {"$regex": domain_search.strip(), "$options": "i"}
        if author_search.strip():
            query["author"] = {"$regex": author_search.strip(), "$options": "i"}
        if language_search.strip():
            query["language"] = {"$regex": language_search.strip(), "$options": "i"}
        if published_year_search.strip():
            query["published_year"] = {"$regex": published_year_search.strip(), "$options": "i"}

        if query:
            books = list(collection.find(query))
            if books:
                st.subheader("📖 Matching Books (Advanced Search)")
                for book in books:
                    st.markdown(
                        f"**{book['title']}** by *{book['author']}* "
                        f"({book['language']}) - Domain: {book.get('domain', 'N/A')} - "
                        f"Published: {book.get('published_year', 'N/A')}"
                    )
                    st.write(f"[Open Book]({book['link']})")

                    if st.session_state.get("username") == ADMIN_USERNAME:
                        if st.button(f"❌ Delete '{book['title']}'", key=str(book["_id"])):
                            collection.delete_one({"_id": book["_id"]})
                            st.success(f"'{book['title']}' deleted.")
                            st.experimental_rerun()
            else:
                st.info("No books found matching the advanced criteria.")
        else:
            st.warning("Please enter at least one field to search.")
