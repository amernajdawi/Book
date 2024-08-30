from langchain_openai import OpenAIEmbeddings 
from langchain_qdrant import Qdrant
from langchain.schema import Document

def create_db(documents):
    """
    Create a vector database from the given documents.
    
    This function takes a list of documents (each containing a book title and reviews),
    converts them into Document objects, embeds them using OpenAI's embedding model,
    and stores them in a Qdrant vector database.
    
    Args:
    documents (list): A list of dictionaries containing book titles and reviews.
    
    Returns:
    Qdrant: A Qdrant vector store containing the embedded documents.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    doc_objects = [
        Document(
            page_content=f"{doc['title']}\n\n{doc['reviews']}",
            metadata={'title': doc['title']}
        ) for doc in documents
    ]

    return Qdrant.from_documents(
        documents=doc_objects,
        embedding=embeddings,
        collection_name="my_documents",
        location=":memory:",  
        force_recreate=False,  
    )
