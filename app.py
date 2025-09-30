import streamlit as st
import requests
from PIL import Image
import io
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
            return False, "❌ Invalid token"
        else:
            return False, f"❌ Error {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Connection error"

def generate_with_huggingface(prompt, token):
    """Generate image using Hugging Face Inference API with token"""
    try:
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {token}"}
        
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
            try:
                error_data = response.json()
                estimated_time = error_data.get('estimated_time', 30)
                return None, f"Model loading. Wait {estimated_time:.0f} seconds"
            except:
                return None, "Model loading. Please wait"
        
        elif response.status_code in [401, 403]:
            return None, "Token doesn't have inference access"
        
        else:
            return None, f"API Error {response.status_code}"
            
    except requests.exceptions.Timeout:
        return None, "Request timeout"
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_with_free_inference(prompt):
    """Generate image using free public inference as fallback"""
    try:
        free_models = [
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
            "https://api-inference.huggingface.co/models/prompthero/openjourney-v4"
        ]
        
        for model_url in free_models:
            try:
                payload = {
                    "inputs": prompt,
                    "options": {
                        "wait_for_model": True,
                        "use_cache": False
                    }
                }
                
                response = requests.post(model_url, json=payload, timeout=90)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    model_name = model_url.split('/')[-1]
                    return image, f"Free model: {model_name}"
                
                elif response.status_code == 503:
                    continue
                    
            except Exception:
                continue
        
        return None, "All models are busy. Please try again later."
        
    except Exception as e:
        return None, f"Generation error: {str(e)}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>AI Image Generator</h1>
        <p>Powered by Hugging Face AI</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # Hugging Face Token Input
    st.subheader("🔑 Hugging Face Token")
    
    hf_token = st.text_input(
        "Enter your Hugging Face token:",
        type="password",
        placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxx",
        help="Get your free token from https://huggingface.co/settings/tokens"
    )
    
    # Test token if provided
    if hf_token:
        is_valid, token_message = test_huggingface_token(hf_token)
        if is_valid:
            st.markdown(f'<div class="success-box">{token_message}</div>', unsafe_allow_html=True)
            use_token = True
        else:
            st.markdown(f'<div class="error-box">{token_message}</div>', unsafe_allow_html=True)
            st.markdown('<div class="warning-box">⚠️ Will use free public inference instead</div>', unsafe_allow_html=True)
            use_token = False
    else:
        st.markdown('<div class="info-box">💡 Enter your Hugging Face token for better performance, or use free public inference</div>', unsafe_allow_html=True)
        use_token = False
    
    st.markdown("---")
    
    # Image Generation Section
    st.subheader("🎨 Create Your Image")
    
    prompt = st.text_area(
        "Enter your prompt:",
        placeholder="A majestic dragon flying over misty mountains at sunset, fantasy art, highly detailed, dramatic lighting",
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
                
                # Generate image based on token availability
                if use_token:
                    generated_image, message = generate_with_huggingface(prompt, hf_token)
                else:
                    generated_image, message = generate_with_free_inference(prompt)
                
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
                        label="Download Image",
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
                    
                    # Retry suggestion
                    if "loading" in message.lower() or "busy" in message.lower():
                        st.info("💡 **Tip:** Wait 1-2 minutes and try again. AI models can take time to load.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>AI Image Generation | Hugging Face Models</p>
    </div>
""", unsafe_allow_html=True)
