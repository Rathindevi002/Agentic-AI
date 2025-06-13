import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory

# ---- HARDCODED API KEY ----
os.environ["GOOGLE_API_KEY"] = "AIzaSyD4JbmGIIsB02nfJWODw8OgBL9rcJenjcw"

# ---- INIT LLM ----
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

# ---- STREAMLIT PAGE CONFIG ----
st.set_page_config(page_title="Gemini RAG Chat", layout="wide")
st.title("📄 Gemini RAG Chatbot with Memory")

# ---- PDF UPLOAD ----
uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    st.info("Processing PDF...")
    loader = PyPDFLoader("temp.pdf")
    pages = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(pages)

    st.success(f"{len(chunks)} text chunks created.")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever()

    # ---- CHAT MEMORY ----
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            return_messages=True,
            input_key="question",
            memory_key="chat_history"
        )

    memory = st.session_state.memory

    # ---- PROMPT TEMPLATE ----
    prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Use the provided context and chat history to answer the user's question.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Answer:""")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def format_chat_history(messages):
        history = ""
        for msg in messages:
            if msg.type == "human":
                history += f"User: {msg.content}\n"
            elif msg.type == "ai":
                history += f"AI: {msg.content}\n"
        return history.strip()

    # ---- USER INPUT ----
    question = st.text_input("Ask a question based on the document:")

    if question:
        with st.spinner("Thinking..."):
            # Format input for prompt
            docs = retriever.get_relevant_documents(question)
            context = format_docs(docs)
            chat_history = format_chat_history(memory.chat_memory.messages)

            input_values = {
                "context": context,
                "chat_history": chat_history,
                "question": question
            }

            final_prompt = prompt.format(**input_values)
            response = llm.invoke(final_prompt)

            # Save to memory
            memory.chat_memory.add_user_message(question)
            memory.chat_memory.add_ai_message(response.content)

            # ---- OUTPUT ----
            st.subheader("📌 Answer")
            st.write(response.content)

    # ---- DISPLAY CHAT HISTORY ----
    if memory.chat_memory.messages:
        st.subheader("🧠 Previous Q&A")
        messages = memory.chat_memory.messages
        for i in range(0, len(messages), 2):
            user_msg = messages[i].content if i < len(messages) else ""
            ai_msg = messages[i+1].content if i+1 < len(messages) else ""
            st.markdown(f"**User:** {user_msg}")
            st.markdown(f"**AI:** {ai_msg}")
            st.markdown("---")

