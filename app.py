import streamlit as st
import requests
from PIL import Image
import io
import time
import json

# Page configuration
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🖼️",
    layout="wide"
)

# Custom CSS for professional UI
st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #0f172a, #1e1b4b);
        }
        .header {
            background: linear-gradient(135deg, #1e3a8a, #7c3aed);
            padding: 2rem;
            text-align: center;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        .header h1 {
            color: #ffffff;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        .header p {
            color: #e0e7ff;
            font-size: 1.2rem;
        }
        .content-box {
            background: #1f2937;
            padding: 2rem;
            border-radius: 15px;
            border: 1px solid #374151;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .stTextArea textarea {
            background: #374151;
            color: #ffffff;
            border-radius: 10px;
            border: 2px solid #4f46e5;
            font-size: 1.1rem;
        }
        .stTextInput input {
            background: #374151;
            color: #ffffff;
            border-radius: 10px;
            border: 2px solid #4f46e5;
        }
        .stButton>button {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 10px;
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #4338ca, #6d28d9);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
        }
        .success-box {
            background: linear-gradient(135deg, #065f46, #047857);
            color: #d1fae5;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 5px solid #10b981;
        }
        .error-box {
            background: linear-gradient(135deg, #7f1d1d, #991b1b);
            color: #fecaca;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 5px solid #ef4444;
        }
        .info-box {
            background: linear-gradient(135deg, #1e3a8a, #3730a3);
            color: #dbeafe;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 5px solid #4f46e5;
        }
    </style>
""", unsafe_allow_html=True)

def generate_with_flux(prompt, api_key):
    """Generate image using FLUX API - FREE and WORKING"""
    try:
        # FLUX API endpoint - FREE tier available
        url = "https://api.flux.ai/v1/generate"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "width": 512,
            "height": 512,
            "steps": 20
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'image_url' in result:
                image_url = result['image_url']
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code == 200:
                    image = Image.open(io.BytesIO(image_response.content))
                    return image, "success"
            elif 'image' in result:
                # Base64 image
                import base64
                image_data = result['image']
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                return image, "success"
        
        elif response.status_code == 401:
            return None, "Invalid API key"
        elif response.status_code == 429:
            return None, "Rate limit exceeded. Try again in a few minutes."
        else:
            return None, f"API Error {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_with_openai_dalle(prompt, api_key):
    """Generate image using OpenAI DALL-E API - FREE credits available"""
    try:
        # OpenAI DALL-E endpoint
        url = "https://api.openai.com/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-2",
            "prompt": prompt,
            "size": "512x512",
            "quality": "standard",
            "n": 1
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0]['url']
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code == 200:
                    image = Image.open(io.BytesIO(image_response.content))
                    return image, "success"
        
        elif response.status_code == 401:
            return None, "Invalid API key"
        elif response.status_code == 429:
            return None, "Rate limit exceeded"
        else:
            return None, f"OpenAI Error {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_with_huggingface(prompt, api_key):
    """Generate image using Hugging Face API - FREE"""
    try:
        # Try different Hugging Face models
        models = [
            "runwayml/stable-diffusion-v1-5",
            "stabilityai/stable-diffusion-2-1"
        ]
        
        for model in models:
            try:
                url = f"https://api-inference.huggingface.co/models/{model}"
                headers = {"Authorization": f"Bearer {api_key}"}
                
                payload = {
                    "inputs": prompt,
                    "options": {
                        "wait_for_model": True,
                        "use_cache": True
                    }
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=90)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    return image, "success"
                elif response.status_code == 503:
                    continue  # Try next model
                    
            except:
                continue
        
        return None, "Hugging Face models are loading"
        
    except Exception as e:
        return None, f"Error: {str(e)}"

def test_api_key(api_key, service):
    """Test if API key is valid"""
    try:
        if service == "flux":
            url = "https://api.flux.ai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200, "FLUX"
            
        elif service == "openai":
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200, "OpenAI"
            
        elif service == "huggingface":
            url = "https://huggingface.co/api/whoami"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200, "Hugging Face"
            
    except:
        return False, service

# Header Section
st.markdown("""
    <div class="header">
        <h1>AI Image Generator</h1>
        <p>Professional AI Image Generation</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # API Key Input Section
    st.subheader("🔑 API Key Required")
    
    api_key = st.text_input(
        "Enter your AI API key:",
        type="password",
        placeholder="Paste your API key here...",
        help="Supports: FLUX AI, OpenAI DALL-E, or Hugging Face"
    )
    
    # Service selection
    service = st.selectbox(
        "Select AI Service:",
        ["FLUX AI (Recommended)", "OpenAI DALL-E", "Hugging Face"]
    )
    
    # Test API key
    if api_key:
        service_map = {
            "FLUX AI (Recommended)": "flux",
            "OpenAI DALL-E": "openai", 
            "Hugging Face": "huggingface"
        }
        
        is_valid, service_name = test_api_key(api_key, service_map[service])
        if is_valid:
            st.markdown(f'<div class="success-box">✅ {service_name} API key is valid!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">❌ Cannot validate {service_name} API key</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">🔑 Enter your API key to generate images</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Image Generation Section
    st.subheader("🎨 Create Your Image")
    
    prompt = st.text_area(
        "Enter your prompt:",
        placeholder="A horse running on a road, realistic, highly detailed, professional photography",
        height=120,
        key="prompt"
    )

    # Quick prompt buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐴 Horse"):
            st.session_state.prompt = "A beautiful horse running on a scenic road, realistic, highly detailed, professional photography, natural lighting"
    with col2:
        if st.button("🌅 Sunset"):
            st.session_state.prompt = "Beautiful sunset over mountains, vibrant colors, professional landscape photography, highly detailed"
    with col3:
        if st.button("🏙️ City"):
            st.session_state.prompt = "Modern city skyline at night, illuminated buildings, professional cityscape photography"

    # Generate button
    if st.button("🚀 Generate Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        elif not api_key:
            st.error("Please enter your API key.")
        else:
            with st.spinner("🔄 Generating image... This may take 20-40 seconds."):
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                steps = [
                    "Processing your prompt...",
                    "Connecting to AI service...", 
                    "Generating image...",
                    "Finalizing details..."
                ]
                
                for i, step in enumerate(steps):
                    progress_bar.progress((i + 1) * 25)
                    status_text.text(step)
                    time.sleep(1)
                
                # Generate image based on service selection
                if service == "FLUX AI (Recommended)":
                    generated_image, message = generate_with_flux(prompt, api_key)
                elif service == "OpenAI DALL-E":
                    generated_image, message = generate_with_openai_dalle(prompt, api_key)
                else:
                    generated_image, message = generate_with_huggingface(prompt, api_key)
                
                progress_bar.progress(100)
                
                if generated_image:
                    status_text.text("✅ Image generated!")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown('<div class="success-box">🎉 Image generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Display image
                    st.image(generated_image, use_container_width=True, caption=f"'{prompt}'")
                    
                    # Download button
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG", quality=95)
                    st.download_button(
                        label="📥 Download Image",
                        data=buf.getvalue(),
                        file_name=f"ai_image_{int(time.time())}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                else:
                    status_text.text("❌ Generation failed")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
    
    # API Information
    st.markdown("---")
    st.markdown("### 🆓 Get FREE API Keys")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        **🤖 FLUX AI**
        - Free tier available
        - High quality images
        - Fast generation
        - Visit: flux.ai
        """)
    
    with col5:
        st.markdown("""
        **🎨 OpenAI DALL-E**
        - $5 free credits
        - Excellent quality
        - Reliable service
        - Visit: openai.com
        """)
    
    with col6:
        st.markdown("""
        **🔗 Hugging Face**
        - Free inference
        - Multiple models
        - Community driven
        - Visit: huggingface.co
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Professional AI Image Generation | Multiple API Services</p>
    </div>
""", unsafe_allow_html=True)
