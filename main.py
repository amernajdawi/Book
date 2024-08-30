import streamlit as st
from dotenv import load_dotenv
from streamlit_chat import message

from src.insights.book.retriever import setup_qa_chain, setup_retriever
from src.insights.book.scraper import scrape_book
from src.insights.book.vector_db import create_db

load_dotenv()

CUSTOM_CSS = """
<style>
    body { background-color: #1a1a1a; color: #ffffff; }
    .stApp { background-color: #1a1a1a; }
    .stTextInput > div > div > input { background-color: #ffffff; color: #000000 !important; }
    .stButton > button { background-color: #4CAF50; color: #ffffff; }
    .stSuccess, .stMessage { background-color: #2a2a2a; }
    * { color: #ffffff !important; }
    input[type="text"], textarea { color: #000000 !important; }
</style>
"""


@st.cache_data
def load_book_data(book_title):
    """
    Load book data for a given title.

    This function is cached by Streamlit to avoid repeated scraping.

    Args:
    book_title (str): The title of the book to load data for.

    Returns:
    list: Scraped book data including reviews.
    """
    return scrape_book(book_title)


def main():
    """
    Run the BookBuddy Streamlit application.

    This function sets up the Streamlit interface, handles user input,
    and manages the chat interaction with the AI book companion.
    """
    st.set_page_config(page_title="BookBuddy", page_icon=":books:", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.title("📚 BookBuddy")
    st.subheader("Your AI-powered book companion")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Book Selection")
        book_title = st.text_input("Enter the kind of book you're interested in:", key="book_input")

        st.markdown("### Tips")
        st.info(
            """
        - Ask about themes, characters, or plot points.
        - Request summaries or analysis.
        - Ask for book recommendations based on the loaded data.
        """
        )

        if st.button("Reset"):
            st.session_state.clear()

    with col2:
        st.markdown("### Chat with BookBuddy")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for i, (role, content) in enumerate(st.session_state.messages):
            message(content, is_user=role == "user", key=str(i))

        prompt = st.text_input("Ask about the book:", key="chat_input")

        if prompt:
            st.session_state.messages.append(("user", prompt))
            message(prompt, is_user=True)

            if "qa_chain" not in st.session_state and book_title:
                with st.spinner("Loading book data..."):
                    books_data = load_book_data(book_title)
                    db = create_db(books_data)
                    retriever = setup_retriever(db)
                    st.session_state.qa_chain = setup_qa_chain(retriever)

            if "qa_chain" not in st.session_state:
                st.warning("Please enter a book title in the 'Book Selection' field.")
            else:
                try:
                    with st.spinner("Thinking..."):
                        response = st.session_state.qa_chain.invoke(prompt)
                    st.session_state.messages.append(("assistant", response))
                    message(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
