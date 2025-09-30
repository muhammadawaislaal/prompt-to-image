import streamlit as st
import requests
from PIL import Image
import io
import os
import time

# Page configuration
st.set_page_config(
    page_title="AI Image Studio Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for ultra-professional UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }
    
    .header-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
        padding: 3rem 2rem;
        text-align: center;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
    }
    
    .header-title {
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #e0e7ff;
        font-size: 1.4rem;
        font-weight: 300;
    }
    
    .content-box {
        background: rgba(30, 41, 59, 0.9);
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    
    .stTextArea textarea {
        background: rgba(55, 65, 81, 0.8);
        color: #ffffff;
        border-radius: 12px;
        border: 2px solid #4f46e5;
        font-size: 1.1rem;
        padding: 1rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 12px;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        transform: translateY(-2px);
    }
    
    .status-box {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid;
        font-weight: 600;
    }
    
    .success-box {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        color: #d1fae5;
        border-left-color: #10b981;
    }
    
    .error-box {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        color: #fecaca;
        border-left-color: #ef4444;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
        color: #fef3c7;
        border-left-color: #f59e0b;
    }
    
    .feature-card {
        background: rgba(55, 65, 81, 0.6);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def test_huggingface_token():
    """Test Hugging Face token with multiple methods"""
    try:
        HF_TOKEN = os.getenv('HF_TOKEN', '')
        if not HF_TOKEN:
            return False, "No token found in secrets"
        
        # Test 1: Basic API call
        test_url = "https://huggingface.co/api/whoami"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            return True, f"✅ Connected as {user_info.get('name', 'User')}"
        else:
            return False, f"❌ Token test failed: {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def generate_image_huggingface(prompt):
    """Generate image using Hugging Face API with multiple model fallbacks"""
    try:
        HF_TOKEN = os.getenv('HF_TOKEN', '')
        if not HF_TOKEN:
            return None, "Token not configured"
        
        # List of models that work with free inference
        models = [
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
            "https://api-inference.huggingface.co/models/prompthero/openjourney-v4",
            "https://api-inference.huggingface.co/models/wavymulder/Analog-Diffusion"
        ]
        
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        for model_url in models:
            try:
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "num_inference_steps": 20,
                        "guidance_scale": 7.5,
                        "width": 512,
                        "height": 512
                    },
                    "options": {
                        "wait_for_model": True,
                        "use_cache": False
                    }
                }
                
                response = requests.post(model_url, headers=headers, json=payload, timeout=90)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    model_name = model_url.split('/')[-1]
                    return image, f"Generated with {model_name}"
                
                elif response.status_code == 503:
                    # Model is loading, try next one
                    continue
                    
                elif response.status_code == 401:
                    # Token issue, stop trying
                    return None, "Token doesn't have inference access"
                    
            except requests.exceptions.Timeout:
                continue
            except Exception:
                continue
        
        return None, "All models are currently loading. Please wait 1-2 minutes and try again."
        
    except Exception as e:
        return None, f"Generation error: {str(e)}"

def generate_with_public_api(prompt):
    """Fallback: Generate using public APIs without token"""
    try:
        # Try multiple public endpoints
        endpoints = [
            "https://image.pollinations.ai/prompt/" + prompt.replace(" ", "%20"),
            f"https://image.pollinations.ai/prompt/{prompt}",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=60)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    return image, "Public API"
            except:
                continue
        
        return None, "Public services busy"
        
    except Exception as e:
        return None, f"Public API error: {str(e)}"

# Header Section
st.markdown("""
    <div class="header-container">
        <div class="header-title">AI Image Studio Pro</div>
        <div class="header-subtitle">Professional AI-Powered Image Generation</div>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # System Status
    st.subheader("🔧 System Status")
    
    # Test the token
    token_valid, token_message = test_huggingface_token()
    
    if token_valid:
        st.markdown(f'<div class="status-box success-box">{token_message}</div>', unsafe_allow_html=True)
        use_huggingface = True
    else:
        st.markdown(f'<div class="status-box warning-box">{token_message}</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-box info-box">🔄 Using alternative generation method</div>', unsafe_allow_html=True)
        use_huggingface = False
    
    st.markdown("---")
    
    # Creative Section
    st.subheader("🎨 Create Your Vision")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Describe your image:",
            placeholder="A majestic dragon flying over misty mountains at sunset, fantasy art, highly detailed, dramatic lighting...",
            height=120,
            key="prompt"
        )
        
        # Style selection
        style = st.selectbox(
            "Art Style:",
            ["Realistic", "Fantasy", "Digital Art", "Cinematic", "Anime", "Painting"]
        )

    with col2:
        st.markdown("#### 🚀 Quick Start")
        
        if st.button("🐉 Fantasy Dragon", use_container_width=True):
            st.session_state.prompt = "A majestic dragon flying over misty mountains at golden hour, fantasy art, highly detailed, epic scale"
        
        if st.button("🌆 Cyberpunk City", use_container_width=True):
            st.session_state.prompt = "Futuristic cyberpunk city at night, neon lights, flying cars, detailed architecture, cinematic"
        
        if st.button("🏔️ Mountain Landscape", use_container_width=True):
            st.session_state.prompt = "Majestic mountain landscape at sunrise, misty valleys, professional photography, highly detailed"
        
        if st.button("🎨 Abstract Art", use_container_width=True):
            st.session_state.prompt = "Colorful abstract art, vibrant colors, modern art, creative, unique patterns"

    # Generate Button
    st.markdown("---")
    
    if st.button("🚀 Generate Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a description for your image")
        else:
            with st.spinner("🔄 Creating your image... This may take 30-60 seconds"):
                # Progress animation
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                steps = [
                    "Processing your vision...",
                    "Connecting to AI services...", 
                    "Generating artwork...",
                    "Finalizing image..."
                ]
                
                for i, step in enumerate(steps):
                    progress_bar.progress((i + 1) * 25)
                    status_text.text(step)
                    time.sleep(2)
                
                # Generate image
                enhanced_prompt = f"{prompt}, {style.lower()} style, high quality, detailed"
                
                if use_huggingface:
                    generated_image, message = generate_image_huggingface(enhanced_prompt)
                else:
                    generated_image, message = generate_with_public_api(enhanced_prompt)
                
                progress_bar.progress(100)
                
                if generated_image:
                    status_text.text("✅ Image created!")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown('<div class="status-box success-box">🎉 Your image has been generated successfully!</div>', unsafe_allow_html=True)
                    
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
                    
                    st.balloons()
                    
                else:
                    status_text.text("❌ Generation failed")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown(f'<div class="status-box error-box">{message}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Features Section
st.markdown("---")
st.subheader("✨ Professional Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎨</div>
        <h3>AI-Powered</h3>
        <p>Advanced AI models for stunning image generation</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚡</div>
        <h3>High Quality</h3>
        <p>Professional 512x512 resolution images</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔒</div>
        <h3>Always Works</h3>
        <p>Multiple fallback methods ensure reliability</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 2rem;">
        <p>AI Image Studio Pro • Professional Image Generation</p>
    </div>
""", unsafe_allow_html=True)
