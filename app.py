import streamlit as st
import requests
from PIL import Image
import io
import os
import time

# Page configuration
st.set_page_config(
    page_title="AI Image Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for ultra-professional UI
st.markdown("""
    <style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
        padding: 3rem 2rem;
        text-align: center;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .header-title {
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .header-subtitle {
        color: #e0e7ff;
        font-size: 1.4rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    /* Content boxes */
    .content-box {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        margin-bottom: 2rem;
    }
    
    /* Text areas */
    .stTextArea textarea {
        background: rgba(55, 65, 81, 0.8);
        color: #ffffff;
        border-radius: 12px;
        border: 2px solid #4f46e5;
        font-size: 1.1rem;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
    }
    
    /* Buttons */
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
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4);
    }
    
    /* Status boxes */
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
    
    .info-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        color: #dbeafe;
        border-left-color: #4f46e5;
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(55, 65, 81, 0.6);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

def check_api_status():
    """Check if Hugging Face API is available"""
    try:
        HF_TOKEN = os.getenv('HF_TOKEN', '')
        if not HF_TOKEN:
            return False, "No API token configured"
        
        # Test the token
        test_url = "https://huggingface.co/api/whoami"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "API Connected Successfully"
        else:
            return False, "API Connection Failed"
            
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def generate_image(prompt):
    """Generate image using Hugging Face API"""
    try:
        HF_TOKEN = os.getenv('HF_TOKEN', '')
        if not HF_TOKEN:
            return None, "API token not configured"
        
        # Use a reliable model
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512
            },
            "options": {
                "wait_for_model": True,
                "use_cache": True
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image, "success"
        
        elif response.status_code == 503:
            return None, "AI Model is Loading - Please wait 30 seconds"
        
        else:
            return None, f"Generation Failed - Error {response.status_code}"
            
    except Exception as e:
        return None, f"Generation Error: {str(e)}"

# Header Section
st.markdown("""
    <div class="header-container">
        <div class="header-title">AI Image Studio</div>
        <div class="header-subtitle">Transform Ideas into Stunning Visual Art with AI</div>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # API Status Check
    st.subheader("🔧 System Status")
    api_working, api_message = check_api_status()
    
    if api_working:
        st.markdown(f'<div class="status-box success-box">✅ {api_message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-box error-box">❌ {api_message}</div>', unsafe_allow_html=True)
        st.stop()
    
    st.markdown("---")
    
    # Creative Section
    st.subheader("🎨 Create Your Masterpiece")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Describe Your Vision:",
            placeholder="A majestic dragon soaring over misty mountain peaks at golden hour, fantasy art style, highly detailed, dramatic lighting, epic scale...",
            height=150,
            key="prompt"
        )
        
        # Style enhancement
        st.markdown("#### 🎯 Enhance Your Creation")
        style = st.selectbox(
            "Art Style:",
            ["Realistic Photography", "Fantasy Art", "Digital Painting", "Cinematic", "Anime", "Oil Painting"]
        )
        
        # Add style to prompt
        if prompt and style:
            enhanced_prompt = f"{prompt}, {style.lower()}, masterpiece, 4K resolution, professional"
        else:
            enhanced_prompt = prompt

    with col2:
        st.markdown("#### 💫 Quick Templates")
        
        template_col1, template_col2 = st.columns(2)
        
        with template_col1:
            if st.button("🐉 Epic Dragon", use_container_width=True):
                st.session_state.prompt = "A majestic dragon flying over misty mountains at golden hour, fantasy art, highly detailed, epic scale, dramatic lighting"
            if st.button("🌅 Serene Landscape", use_container_width=True):
                st.session_state.prompt = "Tranquil mountain landscape at sunrise, misty valleys, professional photography, highly detailed, peaceful atmosphere"
        
        with template_col2:
            if st.button("🏙️ Urban Future", use_container_width=True):
                st.session_state.prompt = "Futuristic cyberpunk city at night, neon lights, flying vehicles, detailed architecture, cinematic, highly detailed"
            if st.button("🧙 Fantasy Realm", use_container_width=True):
                st.session_state.prompt = "Enchanted forest with magical creatures, glowing mushrooms, fantasy realm, detailed, mystical atmosphere"

    # Generate Section
    st.markdown("---")
    
    if st.button("🚀 Generate Masterpiece", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("✨ Please describe your vision to create a masterpiece")
        else:
            with st.spinner("🎨 Creating your masterpiece... This may take 20-40 seconds"):
                # Enhanced progress animation
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                creative_steps = [
                    "🌟 Igniting creative sparks...",
                    "🎨 Preparing digital canvas...", 
                    "🖌️ Painting with AI magic...",
                    "✨ Adding final touches..."
                ]
                
                for i, step in enumerate(creative_steps):
                    progress_bar.progress((i + 1) * 25)
                    status_text.markdown(f"<div style='text-align: center; font-size: 1.2rem; color: #e0e7ff;'>{step}</div>", unsafe_allow_html=True)
                    time.sleep(2)
                
                # Generate the image
                final_prompt = enhanced_prompt if enhanced_prompt else prompt
                generated_image, message = generate_image(final_prompt)
                
                progress_bar.progress(100)
                
                if generated_image:
                    status_text.markdown("<div style='text-align: center; font-size: 1.2rem; color: #10b981;'>✅ Masterpiece Complete!</div>", unsafe_allow_html=True)
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Success display
                    st.markdown('<div class="status-box success-box">🎉 Your AI Masterpiece is Ready!</div>', unsafe_allow_html=True)
                    
                    # Image display with enhanced styling
                    col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
                    with col_img2:
                        st.image(generated_image, use_container_width=True, caption=f"\"{prompt}\"")
                    
                    # Download section
                    st.markdown("---")
                    st.subheader("📥 Download Your Creation")
                    
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG", quality=100)
                    
                    col_dl1, col_dl2, col_dl3 = st.columns(3)
                    with col_dl2:
                        st.download_button(
                            label="💾 Download HD Image",
                            data=buf.getvalue(),
                            file_name=f"masterpiece_{int(time.time())}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    # Celebration
                    st.balloons()
                    
                else:
                    status_text.markdown(f"<div style='text-align: center; font-size: 1.2rem; color: #ef4444;'>❌ {message}</div>", unsafe_allow_html=True)
                    time.sleep(2)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown(f'<div class="status-box error-box">❌ {message}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Features Section
st.markdown("---")
st.subheader("✨ Why Choose AI Image Studio?")

feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎨</div>
        <h3>Infinite Creativity</h3>
        <p>Transform any idea into stunning visual art with advanced AI technology</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3>Lightning Fast</h3>
        <p>Generate high-quality images in seconds with our optimized AI models</p>
    </div>
    """, unsafe_allow_html=True)

with feature_col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔒</div>
        <h3>Professional Grade</h3>
        <p>Enterprise-level AI technology for clients who demand the best quality</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 4rem; padding: 2rem;">
        <p style="font-size: 0.9rem;">AI Image Studio • Professional AI-Powered Image Generation • Powered by Hugging Face</p>
    </div>
""", unsafe_allow_html=True)
