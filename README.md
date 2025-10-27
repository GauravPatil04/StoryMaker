# SGU Story Weaver 📖✨

A simple web application that uses Google's Gemini AI to generate short stories set entirely on the campus of **Sanjay Ghodawat University (SGU), Kolhapur**.

The app takes a user's story idea and combines it with known details about the SGU campus (like the Central Library, School of Technology, Food Court, Stadium, etc.) to prompt the Gemini AI to write a unique, relevant story.



---

## Features

* Takes a user prompt for a story idea.
* Uses the **free tier** of the Google Gemini API (`models/gemini-2.5-flash`) via the `google-generativeai` library.
* Generates stories **specifically set on the SGU campus**, incorporating known locations and features.
* Instructions ensure stories are written in **simple English**.
* Built with **Streamlit** for an easy-to-use web interface.
* Includes **error handling** for API key issues and content generation blocks.
* Provides a button to **download** the generated story as a `.txt` file.
---

## Setup & Run Locally 💻

1.  **Get API Key:** Obtain a free API key for the Gemini API from [Google AI Studio](https://aistudio.google.com/).
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/GauravPatil04/StoryMaker # <-- Replace with your repo URL!
    cd StoryMaker
    ```
3.  **Create Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    # Activate it:
    # Linux/macOS:
    source .venv/bin/activate
    # Windows (cmd):
    # .venv\Scripts\activate.bat
    # Windows (PowerShell):
    # .venv\Scripts\Activate.ps1
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Set API Key Locally:**
    * Create a file named `.env` in the project root.
    * Add your API key to it like this:
        ```
        GEMINI_API_KEY=YOUR_ACTUAL_API_KEY_HERE
        ```
    * **Ensure `.env` is listed in your `.gitignore` file!**
6.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
    The app should open in your web browser.

---

## Deployment (Streamlit Community Cloud) ☁️

1.  **Push to GitHub:** Make sure your `app.py`, `requirements.txt`, and `.gitignore` files are committed and pushed to your GitHub repository. **Do NOT push the `.env` file.**
2.  **Connect to Streamlit Cloud:** Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
3.  **Deploy New App:**
    * Click "New app".
    * Select your repository, branch (usually `main` or `master`), and ensure `app.py` is the main file path.
4.  **Add Secrets:**
    * Click on "Advanced settings...".
    * Go to the "Secrets" section.
    * Paste your API key in the following format:
        ```toml
        GEMINI_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
        ```
5.  **Deploy!** Click the "Deploy!" button. Your app will be built and hosted for free.

---

## Technologies Used 🛠️

* **Language:** Python 3.9+
* **Web Framework:** Streamlit
* **AI Model:** Google Gemini API (`models/gemini-2.5-flash` via `google-generativeai` SDK)
* **Version Control:** Git / GitHub
* **Hosting:** Streamlit Community Cloud

---