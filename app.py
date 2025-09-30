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
        .warning-box {
            background: linear-gradient(135deg, #78350f, #92400e);
            color: #fef3c7;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 5px solid #f59e0b;
        }
    </style>
""", unsafe_allow_html=True)

def test_huggingface_token(token):
    """Test if Hugging Face token is valid"""
    try:
        test_url = "https://huggingface.co/api/whoami"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            return True, f"✅ Token valid - Welcome {user_info.get('name', 'User')}"
        elif response.status_code == 401:
            return False, "❌ Invalid token - Please check your token"
        else:
            return False, f"❌ Error {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Connection error"

def generate_with_huggingface_free(prompt):
    """Generate image using Hugging Face FREE inference without token"""
    try:
        # Use models that work without authentication
        models = [
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
            "https://api-inference.huggingface.co/models/prompthero/openjourney-v4"
        ]
        
        for model_url in models:
            try:
                headers = {}
                payload = {
                    "inputs": prompt,
                    "options": {
                        "wait_for_model": True,
                        "use_cache": True
                    }
                }
                
                response = requests.post(model_url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    return image, f"Success with {model_url.split('/')[-1]}"
                
                elif response.status_code == 503:
                    continue  # Try next model
                    
            except:
                continue  # Try next model
        
        return None, "All models are currently loading or busy"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_with_huggingface_token(prompt, token):
    """Generate image using Hugging Face with token"""
    try:
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "inputs": prompt,
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
            return None, "Model is loading. Please wait 30-60 seconds and try again."
        
        elif response.status_code in [401, 403]:
            return None, "Token doesn't have inference access"
        
        else:
            return None, f"API Error {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>AI Image Generator</h1>
        <p>Powered by Hugging Face AI Models</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # Get Hugging Face token from secrets
    HF_TOKEN = os.getenv('HF_TOKEN', '')
    
    # Check token status
    if HF_TOKEN:
        is_valid, token_message = test_huggingface_token(HF_TOKEN)
        if is_valid:
            st.markdown(f'<div class="success-box">{token_message}</div>', unsafe_allow_html=True)
            use_token = True
        else:
            st.markdown(f'<div class="error-box">{token_message}</div>', unsafe_allow_html=True)
            st.markdown('<div class="warning-box">⚠️ Using free public inference instead</div>', unsafe_allow_html=True)
            use_token = False
    else:
        st.markdown('<div class="warning-box">⚠️ No token found - Using free public inference</div>', unsafe_allow_html=True)
        use_token = False
    
    st.subheader("Create Your Image")
    
    prompt = st.text_area(
        "Enter your prompt:",
        placeholder="A majestic dragon flying over misty mountains at sunset, fantasy art, highly detailed",
        height=120,
        key="prompt"
    )

    # Generate button
    if st.button("Generate Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        else:
            with st.spinner("Generating image... This may take 30-60 seconds."):
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(4):
                    progress_bar.progress((i + 1) * 25)
                    if i == 0:
                        status_text.text("Processing your prompt...")
                    elif i == 1:
                        status_text.text("Connecting to AI service...")
                    elif i == 2:
                        status_text.text("Generating image...")
                    time.sleep(1)
                
                # Generate image
                if use_token:
                    generated_image, message = generate_with_huggingface_token(prompt, HF_TOKEN)
                else:
                    generated_image, message = generate_with_huggingface_free(prompt)
                
                progress_bar.progress(100)
                
                if generated_image:
                    status_text.text("✅ Image generated!")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown('<div class="success-box">Image generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Display image
                    st.image(generated_image, use_container_width=True, caption=f"'{prompt}'")
                    
                    # Download button
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG", quality=95)
                    st.download_button(
                        label="Download Image",
                        data=buf.getvalue(),
                        file_name=f"ai_image_{int(time.time())}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                else:
                    status_text.text("❌ Failed")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
                    
                    # Show retry suggestion
                    if "loading" in message.lower():
                        st.info("💡 **Tip:** Wait 30-60 seconds and try again. The AI model needs time to load.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>AI Image Generation | Hugging Face Models</p>
    </div>
""", unsafe_allow_html=True)
