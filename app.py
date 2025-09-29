import streamlit as st
import requests
from PIL import Image
import io
import os
import time

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

def generate_image_huggingface(prompt):
    """
    Generate image using Hugging Face Inference API
    Returns PIL Image if successful, None otherwise
    """
    try:
        # Your Hugging Face token from Streamlit secrets
        HF_TOKEN = os.getenv('HF_TOKEN', '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')
        
        # API endpoint for Stable Diffusion
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        # Payload for the API request
        payload = {
            "inputs": prompt,
            "options": {
                "wait_for_model": True,
                "use_cache": True
            },
            "parameters": {
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512
            }
        }
        
        # Make the API request with timeout
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        # Check response status
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        
        elif response.status_code == 503:
            # Model is loading
            error_data = response.json()
            estimated_time = error_data.get('estimated_time', 30)
            st.error(f"🔄 Model is loading. Please wait {int(estimated_time)} seconds and try again.")
            return None
            
        elif response.status_code == 403:
            st.error("🔐 Access denied. Please check your Hugging Face token.")
            return None
            
        elif response.status_code == 429:
            st.error("⏳ Rate limit exceeded. Please wait a few minutes before trying again.")
            return None
            
        else:
            st.error(f"❌ API Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏰ Request timeout. The model is taking too long to respond.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🌐 Connection error. Please check your internet connection.")
        return None
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
        return None

def create_placeholder(prompt):
    """Create a professional placeholder image"""
    width, height = 512, 512
    img = Image.new('RGB', (width, height), color='#1f2937')
    return img

# Header Section
st.markdown("""
    <div class="header">
        <h1>AI Image Generator</h1>
        <p>Transform your ideas into stunning visual art</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Create Your Image")
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="Describe the image you want to generate...",
            height=120,
            key="prompt"
        )
        
        # Advanced options
        with st.expander("Advanced Settings"):
            model_choice = st.selectbox(
                "Model",
                ["runwayml/stable-diffusion-v1-5", "stabilityai/stable-diffusion-2-1"],
                help="Choose the AI model for image generation"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                steps = st.slider("Inference Steps", 10, 50, 25)
            with col_b:
                guidance = st.slider("Guidance Scale", 5.0, 15.0, 7.5)
    
    with col2:
        st.subheader("Guide")
        st.markdown("""
        **Tips for best results:**
        - Be specific and descriptive
        - Include style references
        - Mention composition details
        - Specify lighting and mood
        """)
        
        st.markdown("""
        **Example prompts:**
        - Photorealistic portrait of a wise old wizard
        - Cyberpunk cityscape at night with neon lights
        - Serene mountain landscape at sunrise
        """)
    
    # Generate button
    if st.button("🚀 Generate Image", use_container_width=True):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        else:
            with st.spinner("🔄 Generating your image... This may take 20-30 seconds."):
                # Update payload with advanced settings
                generated_image = generate_image_huggingface(prompt)
                
                if generated_image:
                    st.markdown('<div class="success-box">✅ Image generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Display image
                    st.image(generated_image, use_container_width=True)
                    
                    # Download button
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG")
                    st.download_button(
                        label="📥 Download Image",
                        data=buf.getvalue(),
                        file_name=f"ai_generated_{prompt[:20]}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                else:
                    st.markdown('<div class="error-box">❌ Failed to generate image. Please try again.</div>', unsafe_allow_html=True)
                    
                    # Show placeholder
                    placeholder = create_placeholder(prompt)
                    st.image(placeholder, use_container_width=True)
                    
                    # Troubleshooting guide
                    with st.expander("Troubleshooting Guide"):
                        st.markdown("""
                        **Common solutions:**
                        1. Check your Hugging Face token is valid
                        2. Ensure you have internet connection
                        3. Try a different prompt
                        4. Wait a few minutes if rate limited
                        5. Contact support if issue persists
                        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Hugging Face AI Models | Professional Image Generation</p>
    </div>
""", unsafe_allow_html=True)
