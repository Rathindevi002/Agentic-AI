import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessage

# ✅ HARDCODED GEMINI API KEY (for demo purposes)
GEMINI_API_KEY = "AIzaSyD4JbmGIIsB02nfJWODw8OgBL9rcJenjcw"

# ✅ Initialize Gemini LLM
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY
    )
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini: {e}")
    st.stop()

# ✅ Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that translates English to French."),
    ("human", "Translate the following sentence to French:\n\n{english_sentence}")
])

# ✅ Combine prompt and model into a chain
translation_chain: Runnable = prompt | llm

# ✅ Streamlit UI
st.set_page_config(page_title="English to French Translator", page_icon="🌍")
st.title("🌍 English to French Translator")
st.markdown("Enter an English sentence and click *Translate* to get the French version.")

# ✅ Input box
english_input = st.text_input("Enter English Sentence:", placeholder="e.g., How are you?")

# ✅ Translate button
if st.button("Translate"):
    if not english_input.strip():
        st.warning("⚠️ Please enter a sentence before clicking Translate.")
    else:
        try:
            # Run the translation chain
            response = translation_chain.invoke({"english_sentence": english_input})
            french_output = response.content if isinstance(response, AIMessage) else str(response)

            # Show result
            st.success("✅ Translation successful!")
            st.text_area("French Translation:", value=french_output, height=150)
        except Exception as e:
            st.error(f"❌ Error during translation: {e}")
