import streamlit as st
from huggingface_hub import InferenceClient
import requests
from PIL import Image
import io
import os
import time

# Page configuration
st.set_page_config(
    page_title="Text-to-Image Generator",
    page_icon="🖼️",
    layout="wide"
)

# Custom CSS for eye-catching UI
st.markdown("""
    <style>
        .header {
            background: linear-gradient(135deg, #1e3a8a, #7c3aed);
            padding: 2rem;
            text-align: center;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .header h1 {
            color: #ffffff;
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
        }
        .header p {
            color: #e0e7ff;
            font-size: 1.3rem;
            font-style: italic;
        }
        .footer {
            background: linear-gradient(135deg, #1e3a8a, #7c3aed);
            padding: 1rem;
            text-align: center;
            border-radius: 15px;
            margin-top: 2rem;
            color: #e0e7ff;
            font-size: 1rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .sidebar .sidebar-content {
            background: #111827;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        }
        .prompt-suggestion {
            background: #1f2937;
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            color: #a5b4fc;
            cursor: pointer;
            transition: all 0.3s ease;
            border-left: 4px solid #7c3aed;
        }
        .prompt-suggestion:hover {
            background: #4b5563;
            transform: translateX(5px);
            color: #ffffff;
            border-left-color: #3b82f6;
        }
        .main-content {
            background: #1f2937;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .stTextArea textarea {
            background: #374151;
            color: #ffffff;
            border-radius: 8px;
            border: 2px solid #7c3aed;
            transition: border-color 0.3s ease;
        }
        .stTextArea textarea:focus {
            border-color: #3b82f6;
        }
        .stButton>button {
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            color: #ffffff;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #2563eb, #6d28d9);
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div class="sidebar-content">
            <h3 style="color: #a5b4fc;">Prompt Suggestions</h3>
            <div class="prompt-suggestion" onclick="document.getElementById('prompt').value='A futuristic cityscape at night with neon lights, cyberpunk style'">Futuristic cityscape, cyberpunk</div>
            <div class="prompt-suggestion" onclick="document.getElementById('prompt').value='A serene forest at dawn, photorealistic style'">Serene forest at dawn</div>
            <div class="prompt-suggestion" onclick="document.getElementById('prompt').value='A majestic dragon flying over mountains, fantasy art'">Dragon over mountains, fantasy</div>
            <hr style="border-color: #4b5563;">
            <h3 style="color: #a5b4fc;">Tips for Better Prompts</h3>
            <ul style="color: #d1d5db;">
                <li>Be specific with styles (e.g., photorealistic, anime).</li>
                <li>Include details like colors or lighting.</li>
                <li>Avoid vague terms for clearer results.</li>
            </ul>
            <hr style="border-color: #4b5563;">
            <p style="color: #e0e7ff; font-size: 0.9rem; text-align: center;">
                <strong>Muhammad Awais Laal</strong>, Gen AI Developer
            </p>
        </div>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1>Text-to-Image Generator</h1>
        <p>Transform your imagination into stunning visuals with AI-powered image generation.</p>
    </div>
""", unsafe_allow_html=True)

# Main content
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.subheader("Create Your Image")
prompt = st.text_area("Prompt", placeholder="e.g., Astronaut riding a horse, photorealistic style", height=100, key="prompt")

# Button to generate image
if st.button("Generate Image", key="generate"):
    if not prompt.strip():
        st.error("Please enter a prompt!")
    else:
        with st.spinner("Generating image..."):
            retries = 3
            delay = 5  # seconds
            success = False
            error_message = ""

            # Try Hugging Face Inference API
            for attempt in range(retries):
                try:
                    client = InferenceClient(
                        provider="nebius",
                        token=os.getenv('HF_TOKEN', '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')
                    )
                    image = client.text_to_image(
                        prompt=prompt,
                        model="stabilityai/stable-diffusion-xl-base-1.0",
                        negative_prompt="low quality, blurry",
                        guidance_scale=7.5,
                        num_inference_steps=50
                    )
                    
                    # Display image
                    st.image(image, caption="Generated Image (Hugging Face)", use_container_width=True)
                    
                    # Option to download image
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format="PNG")
                    st.download_button(
                        label="Download Image",
                        data=img_buffer.getvalue(),
                        file_name="generated_image.png",
                        mime="image/png"
                    )
                    success = True
                    break
                
                except Exception as e:
                    error_message = str(e)
                    if "503" in error_message or "model is loading" in error_message.lower():
                        st.warning(f"Model loading, retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                        time.sleep(delay)
                        continue
                    st.error(f"Hugging Face API error: {error_message}")
                    break

            # Fallback to Craiyon API if Hugging Face fails
            if not success:
                st.warning("Hugging Face API failed, trying Craiyon API...")
                try:
                    craiyon_url = "https://api.craiyon.com/v1/draw"
                    payload = {"prompt": prompt}
                    response = requests.post(craiyon_url, json=payload)
                    
                    if not response.ok:
                        st.error(f"Craiyon API error: {response.reason} (Status: {response.status_code})")
                        st.stop()

                    data = response.json()
                    if "images" not in data or not data["images"]:
                        st.error("Craiyon API returned no images")
                        st.stop()

                    # Craiyon returns base64 images; decode the first one
                    from base64 import b64decode
                    image_data = b64decode(data["images"][0]["base64"])
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Display image
                    st.image(image, caption="Generated Image (Craiyon)", use_container_width=True)
                    
                    # Option to download image
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format="PNG")
                    st.download_button(
                        label="Download Image",
                        data=img_buffer.getvalue(),
                        file_name="generated_image.png",
                        mime="image/png"
                    )
                
                except Exception as e:
                    st.error(f"Craiyon API error: {str(e)}")
                    st.stop()
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <p>Developed by Muhammad Awais Laal | 2025</p>
    </div>
""", unsafe_allow_html=True)