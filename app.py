import streamlit as st
import requests
from PIL import Image
import io
import os
import time
import base64
import json

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
        .success-box {
            background: #065f46;
            color: #d1fae5;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

def generate_with_huggingface(prompt):
    """Generate image using Hugging Face Inference API"""
    try:
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN', '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')}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 7.5
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        elif response.status_code == 503:
            # Model is loading, get estimated time
            est_time = response.json().get('estimated_time', 30)
            st.info(f"Model is loading. Please wait about {int(est_time)} seconds and try again.")
            return None
        else:
            st.error(f"Hugging Face API error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Hugging Face API error: {str(e)}")
        return None

def generate_with_fal_ai(prompt):
    """Generate image using Fal AI (free tier available)"""
    try:
        # Fal AI offers free credits
        API_URL = "https://queue.fal.run/fal-ai/fast-sdxl/generate"
        headers = {
            "Authorization": f"Key {os.getenv('FAL_KEY', '')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "image_size": "square_hd"
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            image_url = result.get('images', [{}])[0].get('url')
            if image_url:
                image_response = requests.get(image_url)
                return Image.open(io.BytesIO(image_response.content))
        return None
        
    except Exception as e:
        st.error(f"Fal AI API error: {str(e)}")
        return None

def generate_with_black_forest(prompt):
    """Generate image using Black Forest Labs API"""
    try:
        API_URL = "https://api.blackforestlabs.ai/v1/image/generation"
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "model": "flux-schnell",
            "width": 512,
            "height": 512,
            "steps": 20
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            image_data = result.get('data', [{}])[0].get('url')
            if image_data:
                image_response = requests.get(image_data)
                return Image.open(io.BytesIO(image_response.content))
        return None
        
    except Exception as e:
        return None

def create_placeholder_image(prompt):
    """Create a placeholder image when APIs fail"""
    width, height = 512, 512
    placeholder = Image.new('RGB', (width, height), color='#1f2937')
    
    # Add some text to the placeholder
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(placeholder)
    
    try:
        # Try to use a larger font
        font = ImageFont.load_default()
        text = f"Prompt: {prompt[:40]}..." if len(prompt) > 40 else f"Prompt: {prompt}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font)
        draw.text((x, y + text_height + 10), "API Services Currently Unavailable", fill='#a5b4fc', font=font)
        
    except Exception:
        # Fallback if font loading fails
        pass
    
    return placeholder

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
            <h3 style="color: #a5b4fc;">API Status</h3>
            <p style="color: #d1d5db; font-size: 0.9rem;">
                Using free AI APIs that may have rate limits.
            </p>
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

# Add image style selection
col1, col2 = st.columns(2)
with col1:
    style = st.selectbox(
        "Image Style",
        ["Realistic", "Fantasy", "Anime", "Cyberpunk", "Oil Painting", "Watercolor"]
    )
with col2:
    quality = st.selectbox(
        "Quality",
        ["Standard", "High Quality", "Fast"]
    )

# Button to generate image
if st.button("Generate Image", key="generate"):
    if not prompt.strip():
        st.error("Please enter a prompt!")
    else:
        with st.spinner("Generating image... This may take 10-30 seconds."):
            generated_image = None
            api_used = ""
            
            # Add style to prompt
            enhanced_prompt = f"{prompt}, {style.lower()} style, high quality"
            
            # Try different APIs in sequence
            st.info("Trying Hugging Face API...")
            generated_image = generate_with_huggingface(enhanced_prompt)
            
            if generated_image:
                api_used = "Hugging Face"
            else:
                st.info("Trying alternative APIs...")
                generated_image = generate_with_fal_ai(enhanced_prompt)
                if generated_image:
                    api_used = "Fal AI"
                else:
                    generated_image = generate_with_black_forest(enhanced_prompt)
                    if generated_image:
                        api_used = "Black Forest Labs"
            
            # Display result
            if generated_image:
                st.markdown(f'<div class="success-box">✅ Image generated successfully using {api_used} API!</div>', unsafe_allow_html=True)
                st.image(generated_image, caption=f"Generated Image - '{prompt}'", use_container_width=True)
                
                # Download button
                img_buffer = io.BytesIO()
                generated_image.save(img_buffer, format="PNG")
                st.download_button(
                    label="📥 Download Image",
                    data=img_buffer.getvalue(),
                    file_name=f"generated_image_{hash(prompt) % 10000}.png",
                    mime="image/png",
                    key="download"
                )
            else:
                st.warning("All AI APIs are currently unavailable. Showing placeholder.")
                placeholder = create_placeholder_image(prompt)
                st.image(placeholder, caption="Placeholder - AI Services Currently Unavailable", use_container_width=True)
                
                st.info("""
                **Troubleshooting Tips:**
                - Check your internet connection
                - The free APIs might be experiencing high load
                - Try again in a few minutes
                - For consistent results, consider using a paid API service
                """)

# Add some usage tips
with st.expander("💡 Usage Tips"):
    st.markdown("""
    **For best results:**
    - Be descriptive in your prompts
    - Include style keywords (photorealistic, anime, oil painting, etc.)
    - Specify lighting and mood (sunset, dramatic lighting, etc.)
    - Mention important details (colors, composition, etc.)
    
    **Example prompts:**
    - "A majestic dragon flying over misty mountains at sunset, fantasy art style"
    - "Cyberpunk cityscape with neon lights and flying cars, detailed"
    - "Portrait of a warrior with armor, photorealistic, dramatic lighting"
    """)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <p>Developed by Muhammad Awais Laal | 2025 | AI Image Generation Demo</p>
    </div>
""", unsafe_allow_html=True)
