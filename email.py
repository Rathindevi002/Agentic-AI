import streamlit as st
import google.generativeai as genai
from io import BytesIO
from fpdf import FPDF

# Gemini API key initialization
GEMINI_API_KEY = "your-gemini-api-key-here"  # Replace with your actual Gemini API key
genai.configure(api_key=AIzaSyD4JbmGIIsB02nfJWODw8OgBL9rcJenjcw)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# Streamlit app
st.title("📧 AI Email Generator with Gemini")

# Instructions
st.markdown("Enter your message below and select the desired **email format** and **tone**.")

# Input fields
user_input = st.text_area("Enter your text:", height=200)
email_format = st.selectbox("Select Email Format:", ["Formal", "Informal", "Follow-up", "Apology", "Request"])
email_tone = st.selectbox("Select Tone:", ["Professional", "Friendly", "Concise", "Empathetic", "Persuasive"])

# Session state to keep track of the last input
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = ""

def generate_email(input_text, format_style, tone_style):
    prompt = f"Write a {format_style.lower()} email with a {tone_style.lower()} tone based on the following content:\n\n{input_text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Generate Email
if st.button("Generate Email"):
    if not user_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Generating email..."):
            st.session_state.generated_email = generate_email(user_input, email_format, email_tone)
            st.success("Email generated!")

# Regenerate Email
if st.button("Regenerate Email"):
    if not user_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Regenerating email with new settings..."):
            st.session_state.generated_email = generate_email(user_input, email_format, email_tone)
            st.success("Email regenerated!")

# Display generated email
if st.session_state.generated_email:
    st.subheader("📨 Generated Email")
    st.text_area("Your Email:", st.session_state.generated_email, height=300)

    # Download as PDF
    def convert_to_pdf(text):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in text.split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer

    pdf_file = convert_to_pdf(st.session_state.generated_email)
    st.download_button("📥 Download Email as PDF", data=pdf_file, file_name="generated_email.pdf", mime="application/pdf")

