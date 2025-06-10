import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# --- Configuration ---

# Set Streamlit page configuration
st.set_page_config(
    page_title="AI Personality Quiz Generator",
    page_icon="🌟",
    layout="centered"
)

# IMPORTANT: Replace this placeholder with your own Google Gemini API Key
# Get your key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY = "AIzaSyD4JbmGIIsB02nfJWODw8OgBL9rcJenjcw" # e.g., "AIzaSy..."

# --- Main App Logic ---



# Configure the Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()


def create_badge(text, background_color="#7d3c98", text_color="#ffffff"):
    """Creates a personality badge image."""
    try:
        # Define image dimensions and create a blank image
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color=background_color)
        draw = ImageDraw.Draw(image)

        # Try to load a "better" font, otherwise fall back to default
        try:
            font = ImageFont.truetype("arial.ttf", size=60)
        except IOError:
            font = ImageFont.load_default(size=60)

        # Wrap text to fit the image width
        wrapped_text = textwrap.fill(text, width=20)
        
        # Calculate text position to center it
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        # Draw the text on the image
        draw.text((x, y), wrapped_text, font=font, fill=text_color, align="center")

        return image
    except Exception as e:
        st.error(f"Error creating badge image: {e}")
        return None

# --- Streamlit UI ---

# Title and description
st.title("🌟 AI Personality Quiz Generator")
st.markdown("""
Answer the questions below to discover your personality profile, some fun facts about you, and get a cool shareable badge!
""")

# Quiz questions
questions = {
    "q1": "What best describes your ideal weekend?",
    "q2": "How do you usually make decisions?",
    "q3": "What's your biggest motivation in life?",
    "q4": "How do your friends describe you?",
    "q5": "Pick a preferred environment:"
}

# Collect responses in a form
responses = {}
with st.form("quiz_form"):
    st.subheader("Answer the Questions")
    responses["q1"] = st.selectbox(questions["q1"], ["Exploring nature", "Reading a book at home", "Partying with friends", "Working on a creative project"])
    responses["q2"] = st.selectbox(questions["q2"], ["With logic and reasoning", "Based on my gut feeling", "After getting advice from others", "Through trial and error"])
    responses["q3"] = st.text_input(questions["q3"], placeholder="e.g., Achieving personal growth, helping others...")
    responses["q4"] = st.text_input(questions["q4"], placeholder="e.g., The funny one, the reliable one...")
    responses["q5"] = st.selectbox(questions["q5"], ["Quiet mountains", "Bustling city", "Sunny beach", "Cozy home"])
    
    submitted = st.form_submit_button("✨ Generate My Personality Profile")

# Process the form submission
if submitted:
    # Validate that text inputs are not empty
    if not responses["q3"] or not responses["q4"]:
        st.warning("Please fill out all the fields before submitting.", icon="⚠️")
    else:
        with st.spinner("Analyzing your personality... This might take a moment!"):
            # Create a structured prompt for the AI
            prompt = f"""
            Analyze the following quiz answers and generate a personality profile. Provide the output in the exact format below, using the specified headers with '###'. Do not add any other text outside this structure.

            ### PERSONALITY TYPE ###
            [A creative, single-line name for the personality type]

            ### DESCRIPTION ###
            [A detailed personality description of about 100 words based on the answers]

            ### FUN FACTS ###
            1. [Fun fact 1 related to this personality]
            2. [Fun fact 2 related to this personality]
            3. [Fun fact 3 related to this personality]

            ### BADGE TEXT ###
            [A catchy, short one-liner (max 10 words) for a social media badge]

            --- QUIZ ANSWERS ---
            1. Ideal weekend: {responses['q1']}
            2. Decision-making: {responses['q2']}
            3. Motivation: {responses['q3']}
            4. Friend description: {responses['q4']}
            5. Preferred environment: {responses['q5']}
            """

            try:
                # Call the Gemini API
                result = model.generate_content(prompt)
                output = result.text

                # --- Parse the Structured Output ---
                parts = output.split('###')
                parsed_output = {p.strip().split('\n', 1)[0].strip(): p.strip().split('\n', 1)[1].strip() for p in parts if p.strip()}
                
                # --- Display Result ---
                st.subheader("🎯 Your Personality Quiz Result")

                if "PERSONALITY TYPE" in parsed_output:
                    st.write(f"**Your Personality Type:** {parsed_output['PERSONALITY TYPE']}")
                
                if "DESCRIPTION" in parsed_output:
                    st.write("**About You:**")
                    st.write(parsed_output['DESCRIPTION'])

                if "FUN FACTS" in parsed_output:
                    st.write("**Fun Facts:**")
                    st.write(parsed_output['FUN FACTS'])

                # --- Generate and Display Badge ---
                if "BADGE TEXT" in parsed_output:
                    st.subheader("🏅 Your Shareable Badge")
                    badge_text = parsed_output['BADGE TEXT']
                    
                    # Create the image
                    badge_image = create_badge(badge_text)

                    if badge_image:
                        # Display the image
                        st.image(badge_image, caption="Share this on your social media!")

                        # Create a download button
                        buf = io.BytesIO()
                        badge_image.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        st.download_button(
                            label="Download Badge",
                            data=byte_im,
                            file_name="my_personality_badge.png",
                            mime="image/png"
                        )
                else:
                    st.warning("Could not generate a badge from the AI's response.")
            
            except Exception as e:
                st.error(f"An error occurred while generating your profile: {e}")
                st.error("This could be due to API restrictions or a problem with the response. Please try again.")