# --- Import necessary libraries ---
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv  # Used only for local development
import time

# --- Load environment variables locally (if .env file exists) ---
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="SGU Story Weaver",
    page_icon="📖",
    layout="centered"
)

# --- Constants ---
FREE_GEMINI_MODEL = "models/gemini-2.5-flash"

# --- Securely Get API Key ---
@st.cache_resource
def get_api_key():
    """Safely retrieve API key, prioritizing Streamlit secrets."""
    try:
        # Use st.secrets if available (deployment)
        if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
            st.sidebar.info("🔑 Using API Key from Streamlit secrets.")
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        # Silently pass if secrets aren't available (running locally)
        pass

    # Fallback to environment variable (local development)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.sidebar.info("🔑 Using API Key from local environment variable.")
        return api_key

    # If no key found, display error and stop
    st.error("""
    🔐 **Gemini API Key Not Found!**

    Please set your Gemini API key using one of the following methods:

    **1. Streamlit Cloud:**
       Add the following in your app's Secrets:
       ```toml
       GEMINI_API_KEY="YOUR_API_KEY"
       ```

    **2. Local Development:**
       Create a `.env` file and add:
       ```
       GEMINI_API_KEY=YOUR_API_KEY
       ```
    Get your key from [Google AI Studio](https://aistudio.google.com/).
    """)
    st.stop()


# --- Configure Gemini ---
@st.cache_resource
def configure_gemini():
    """Configure Gemini API with error handling and model validation."""
    api_key = get_api_key()
    if not api_key:
        return None # Should have stopped already

    try:
        genai.configure(api_key=api_key)
        # Check available models that support generateContent
        available_models = [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]

        # Use the primary free model if available
        if FREE_GEMINI_MODEL in available_models:
            st.sidebar.success(f"✅ Using model: `{FREE_GEMINI_MODEL}`")
            return genai.GenerativeModel(FREE_GEMINI_MODEL)

        # Try a common fallback if the primary isn't listed
        fallback_model = "models/gemini-pro"
        if fallback_model in available_models:
            st.sidebar.warning(
                f"⚠️ `{FREE_GEMINI_MODEL}` not found. Falling back to `{fallback_model}`."
            )
            return genai.GenerativeModel(fallback_model)

        # If neither is found, show error
        st.error("❌ No valid Gemini models found for content generation.")
        st.info("Available models supporting 'generateContent':")
        st.json(available_models)
        st.stop()

    except Exception as e:
        st.error(f"😥 Failed to configure Gemini: {e}")
        st.stop()


# --- Initialize Model ---
model = configure_gemini()

# --- SGU Campus Context (Shortened for brevity in code block) ---
SGU_CONTEXT = """
## SGU Campus Context 

**Sanjay Ghodawat University (SGU)** is a large, modern State Private University spread over **165 acres** on the **Kolhapur-Sangli Highway, Atigre, Kolhapur**. It's part of the diverse Sanjay Ghodawat Group, bringing a strong industrial connection.

**Key Academic Areas & Schools (likely in distinct buildings/blocks):**
* School of Engineering & Technology (housing departments like Aeronautical, Civil, Computer Science & Engineering (CSE), AI & Machine Learning (AI&ML), Electronics & Communication (E&C))
* School of Computer Applications (BCA, MCA)
* School of Commerce & Management (B.Com, BBA, MBA - including specializations like Business Analytics, Disaster Management)
* School of Physical and Chemical Sciences (Physics - including Space Science/Nano Science, Chemistry)
* School of Life Sciences (Medical Lab Technology, Food Science & Technology, Biotechnology)
* School of Pharmaceutical Science (D.Pharm, B.Pharm, M.Pharm)
* School of Design (B.Des covering Fashion, Product, Interior, Communication, Animation, Game Design)
* School of Media (Journalism & Mass Communication)
* School of Social Science (History, Geography, Political Science, English)
* School of Legal Studies (Law) (BA LLB, BBA LLB, LLB)

**Specific Campus Facilities & Landmarks:**
* **Central Library:** A key hub for studying and resources. 
* **Hostels:** Separate residential facilities for students.
* **Sports Facilities:** Includes a **Stadium**, **Playgrounds**, courts, and a **Swimming Pool**. 
* **Advanced Laboratories:** Sophisticated labs for various science and tech fields.
* **Specialized Centers:** High-End Simulation & Robotic Lab, Industry 4.0 C4i4 Lab, Center for Space and Atmospheric Science (CSAS), TATA Technologies Centre, BOSCH Mechatronics Lab.
* **Auditorium:** For major events, gatherings, and maybe celebrity visits.
* **Food Court / Canteen:** Social spots for meals and breaks.
* **SGU Music Academy:** A dedicated place for musical activities.
* **Star Local Mart:** An on-campus convenience store.
* **Well-Equipped Classrooms & Sophisticated Computer Labs.**
* **Green Spaces:** Gardens and pathways. 
* **Parking Areas.**

**Campus Vibe:** Focuses on **Project & Design Based Learning**, strong **Industry Connections** (internships, placements with recruiters like TCS, Infosys, Capgemini, etc.), and aims for overall student development and character building. Has global partnerships (Study Abroad programs with universities in USA, UK, Australia) and hosts events like convocations and potentially fests or celebrity interactions.
""" # Keep the full context in your actual file!


# --- Story Generation Function ---
def generate_sgu_story(user_prompt, _model):
    """Generate a story based on user prompt and SGU context."""
    if not _model:
        st.error("Model not initialized.")
        return None, None # Return None for story, None for feedback

    # Construct the detailed prompt for the AI
    full_prompt = f"""
You are a creative storyteller. Write a short, engaging story (around 250–400 words)
that takes place entirely on the campus of Sanjay Ghodawat University (SGU), Kolhapur.
You should explain whole story in simple english so that any age group can read the story easily.

**SGU Campus Details:**
{SGU_CONTEXT}

**User's Story Idea:**
{user_prompt}

**Instructions:**
1. Make the story feel authentic to the SGU campus experience.
2. Mention at least 2-3 specific SGU locations (e.g., Central Library, Food Court, School of Technology building, Stadium, Star Local Mart, Robotic Lab).
3. Ensure the story is appropriate for all audiences and positive in tone.
4. Generate *only* the story text, using clear paragraphs. Do not add a title.
5. Please make sure that story is easy to read by any age group.

**Story:**
"""

    try:
        # Generation settings
        generation_config = genai.types.GenerationConfig(
            temperature=0.75, # Controls randomness (creativity)
            top_p=0.85,       # Nucleus sampling
            top_k=40,         # Top-k sampling
            max_output_tokens=2048 # INCREASED THIS VALUE
        )

        # Safety filters
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        # Call the Gemini API
        response = _model.generate_content(
            full_prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # --- Safer way to get text ---
        story_text = None
        feedback = getattr(response, 'prompt_feedback', None) # Get feedback if it exists

        # Check if response has 'parts' first
        if hasattr(response, 'parts') and response.parts:
            # Join text from all parts (usually just one for text models)
            story_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
        # If no parts, maybe the .text attribute exists (less common now but safer to check)
        elif hasattr(response, 'text') and response.text:
             story_text = response.text

        return story_text, feedback # Return text (or None) and feedback

    except Exception as e:
        # Handle errors during the API call itself
        st.error(f"❌ API Error during generation: {e}")
        st.info("Check network, API key, or prompt complexity.")
        return None, None # Return None for both story and feedback


# --- Main Streamlit Interface Function ---
def main():
    # Display SGU Logo
    st.image("images/SGU_Logo.jpg", width=550)
    # App Title
    st.title("📖 SGU Story Weaver ✨")
    st.markdown("Weave a tale set right here on the **Sanjay Ghodawat University** campus!")

    # Expander with example prompts
    with st.expander("💡 Need inspiration? Click for story ideas!"):
        st.markdown("""
        * A student makes an unexpected friend while studying late in the **Central Library**.
        * Two rivals from the **School of Technology** become partners during a project in the **Robotic Lab**.
        * A shy musician finds courage to perform at the **SGU Music Academy**.
        * A group discussion over snacks at the **Food Court** sparks a brilliant idea.
        * Finding something unusual near the **Stadium** during an evening walk.
        * A chance encounter at the **Star Local Mart**.
        """)

    # Text area for user input
    user_prompt = st.text_area(
        "**What should your SGU story be about?** (Be descriptive!)",
        placeholder="e.g., A first-year student feeling nervous on their way to the School of Engineering & Technology...",
        height=120,
        max_chars=500, # Limit input size
        key="user_story_prompt" # Add a key for state persistence
    )

    # Centered generate button
    col1_btn, col2_btn, col3_btn = st.columns([1, 1.5, 1]) # Adjust centering
    with col2_btn:
        clicked = st.button(
            "✨ Weave My Story!",
            type="primary", # Style the button
            use_container_width=True,
            disabled=not user_prompt.strip(), # Disable if input is empty
            key="generate_button" # Add a key
        )

    # Logic to run when button is clicked
    if clicked and user_prompt.strip():
        # Show a spinner while waiting
        with st.spinner("✍️ Gemini is crafting your SGU story... Please wait."):
            story_text, feedback = generate_sgu_story(user_prompt.strip(), model) # Call generation function

        # Display results or errors
        if story_text:
            st.markdown("---")
            st.subheader("📜 Your SGU Story:")
            # Use a container for better formatting
            with st.container(border=True):
                st.markdown(story_text) # Display the story

            # Add a download button
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            st.download_button(
                label="📥 Download Story (.txt)",
                data=story_text,
                file_name=f"sgu_story_{timestamp}.txt",
                mime="text/plain",
                use_container_width=True,
                key=f"download_{timestamp}" # Use dynamic key for download button
            )

        # Handle cases where the story wasn't generated (blocked or empty)
        elif feedback and hasattr(feedback, 'block_reason'):
            st.error("🚫 Story generation was blocked due to safety settings.")
            st.info(f"Reason: `{feedback.block_reason.name}`")
            st.warning("Please try rephrasing your prompt to be clearer and avoid sensitive topics.")
        elif not story_text and not feedback:
            # This case covers errors caught within generate_sgu_story
             pass # Error already displayed
        else: # Catch-all for other non-generation cases
            st.warning("⚠️ No story was generated. This might be due to the prompt or API issues. Please try again or rephrase.")


# --- Footer Function ---
def display_footer():
    st.markdown("---")
    # Centered footer with links
    footer_html = """
        <div style='text-align: center; font-size: 0.85em; color: #777;'>
            <p>Powered by Google Gemini | Built with Streamlit</p>
            <p>
               <a href="https://github.com/GauravPatil04/StoryMaker" target="_blank" style="color: black;">View on GitHub</a> </p>
        </div>
        """
    st.markdown(footer_html, unsafe_allow_html=True)


# --- Run the Main App ---
if __name__ == "__main__":
    # Ensure the model was initialized before running the main UI
    if model:
        main()
        display_footer()
    else:
        # If model is None, configuration failed, error already shown.
        st.warning("❌ Cannot start app — AI model failed to initialize.")