from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai import ChatOpenAI

from config import OPENAI_API_KEY


def setup_retriever(db):
    """
    Set up a retriever for the given database.

    This function configures a retriever with Maximal Marginal Relevance (MMR) search.
    MMR aims to balance relevance and diversity in the retrieved documents.

    Args:
    db: The database to set up the retriever for.

    Returns:
    A configured retriever object.
    """
    return db.as_retriever(search_type="mmr", search_kwargs={"k": 2, "lambda_mult": 0.25})


def setup_qa_chain(retriever):
    """
    Set up a question-answering chain using the provided retriever.

    This function creates a chain that:
    1. Retrieves relevant context using the retriever
    2. Formats a prompt with the context and user question
    3. Sends the prompt to the language model
    4. Parses the response

    Args:
    retriever: The retriever to use for fetching relevant context.

    Returns:
    A configured QA chain that can answer questions based on the retrieved context.
    """
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2, api_key=OPENAI_API_KEY)

    template = """Act as a senior librarian. Use the following context from book reviews to answer the question. If the answer isn't directly in the context, infer a response. If unsure, explain what you know based on the context and make sure to give a clear and simple answer.

    Context: {context}
    Question: {question}

    Instructions:
    1. Analyze the context and question carefully.
    2. Provide a clear answer, citing specific points from the reviews when possible.
    3. If the question isn't directly addressed, use the overall sentiment and themes to formulate a response.
    4. If you can't answer fully, share insights based on available information and make sure the answer be clear.
    5. Maintain a balanced view, mentioning both positive and critical perspectives if present.
    6. Keep the answer short and clear.

    Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    )

    return chain


def query_system(qa_chain, query):
    """
    Query the QA system with a given question.

    This function takes a configured QA chain and a user query,
    and returns the system's response to the query.

    Args:
    qa_chain: The configured QA chain to use for answering.
    query: The question to ask the system.

    Returns:
    The system's response to the query.
    """
    return qa_chain.invoke(query)
