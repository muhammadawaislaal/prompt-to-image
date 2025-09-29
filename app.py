import streamlit as st
from huggingface_hub import InferenceClient
import requests
from PIL import Image
import io
import os
import time
import base64

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

            # Try Hugging Face Inference API with a supported model
            for attempt in range(retries):
                try:
                    # Use a free model that works without specific providers
                    client = InferenceClient(
                        token=os.getenv('HF_TOKEN', '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')
                    )
                    image = client.text_to_image(
                        prompt=prompt,
                        model="runwayml/stable-diffusion-v1-5",  # Use a more widely supported model
                        negative_prompt="low quality, blurry, distorted",
                        guidance_scale=7.5,
                        num_inference_steps=20  # Reduced for faster generation
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

            # Fallback to alternative APIs if Hugging Face fails
            if not success:
                st.warning("Hugging Face API failed, trying alternative APIs...")
                
                # Option 1: Try Prodia API (free alternative)
                try:
                    st.info("Trying Prodia API...")
                    prodia_url = "https://api.prodia.com/v1/sd/generate"
                    prodia_headers = {
                        "Content-Type": "application/json"
                    }
                    prodia_data = {
                        "prompt": prompt,
                        "model": "sd_xl_base_1.0.safetensors [be9edd61]",
                        "steps": 20,
                        "cfg_scale": 7.5,
                        "negative_prompt": "low quality, blurry"
                    }
                    
                    response = requests.post(prodia_url, json=prodia_data, headers=prodia_headers)
                    
                    if response.status_code == 200:
                        job_data = response.json()
                        job_id = job_data.get('job')
                        
                        # Wait for generation to complete
                        max_attempts = 30
                        for i in range(max_attempts):
                            job_response = requests.get(f"https://api.prodia.com/v1/job/{job_id}")
                            if job_response.status_code == 200:
                                job_result = job_response.json()
                                if job_result.get('status') == 'succeeded':
                                    image_url = job_result.get('imageUrl')
                                    if image_url:
                                        image_response = requests.get(image_url)
                                        image = Image.open(io.BytesIO(image_response.content))
                                        
                                        # Display image
                                        st.image(image, caption="Generated Image (Prodia)", use_container_width=True)
                                        
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
                            time.sleep(1)
                        
                        if not success:
                            st.error("Prodia API: Image generation timed out")
                    
                    else:
                        st.error(f"Prodia API error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Prodia API error: {str(e)}")
                
                # Final fallback: Use a simple local simulation
                if not success:
                    st.warning("All APIs failed. Showing placeholder simulation.")
                    # Create a simple placeholder image
                    width, height = 512, 512
                    placeholder = Image.new('RGB', (width, height), color='#1f2937')
                    
                    # Add some text to the placeholder
                    from PIL import ImageDraw, ImageFont
                    draw = ImageDraw.Draw(placeholder)
                    try:
                        font = ImageFont.load_default()
                        text = f"Prompt: {prompt[:50]}..."
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        x = (width - text_width) // 2
                        y = (height - text_height) // 2
                        draw.text((x, y), text, fill='white', font=font)
                    except:
                        pass
                    
                    st.image(placeholder, caption="Placeholder (API Services Unavailable)", use_container_width=True)
                    st.info("This is a placeholder. In a working setup, this would be your generated image.")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <p>Developed by Muhammad Awais Laal | 2025</p>
    </div>
""", unsafe_allow_html=True)
