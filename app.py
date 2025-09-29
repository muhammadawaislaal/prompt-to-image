import streamlit as st
import requests
from PIL import Image
import io
import os
import time

# Page configuration
st.set_page_config(
    page_title="Free AI Image Generator",
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
        .model-card {
            background: #374151;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #8b5cf6;
        }
        .token-status {
            padding: 0.5rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

def test_huggingface_token(token):
    """Test if Hugging Face token is valid"""
    try:
        # Test with a simple API call
        test_url = "https://huggingface.co/api/whoami"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            return True, f"✅ Token valid - Welcome {user_info.get('name', 'User')}!"
        elif response.status_code == 401:
            return False, "❌ Invalid token"
        else:
            return False, f"❌ Error {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def generate_with_huggingface_api(prompt, token, model_name):
    """Generate image using Hugging Face API with token"""
    try:
        # Models that work with free API tokens
        models = {
            "runwayml/stable-diffusion-v1-5": {
                "url": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            },
            "stabilityai/stable-diffusion-2-1": {
                "url": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
            },
            "prompthero/openjourney": {
                "url": "https://api-inference.huggingface.co/models/prompthero/openjourney"
            }
        }
        
        if model_name not in models:
            return None, "Model not found"
        
        API_URL = models[model_name]["url"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Enhanced payload for better quality
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
        
        # Make the API request
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image, "success"
        
        elif response.status_code == 503:
            # Model is loading
            try:
                error_data = response.json()
                estimated_time = error_data.get('estimated_time', 30)
                return None, f"Model loading... Wait {estimated_time:.0f}s"
            except:
                return None, "Model loading. Please wait..."
        
        elif response.status_code == 401:
            return None, "Invalid token"
        
        elif response.status_code == 402:
            return None, "Payment required - upgrade account"
        
        else:
            return None, f"API Error {response.status_code}"
            
    except requests.exceptions.Timeout:
        return None, "Timeout - Try again"
    except Exception as e:
        return None, f"Error: {str(e)}"

def enhance_prompt_for_model(prompt, model_name):
    """Enhance prompt based on model type"""
    enhancements = {
        "runwayml/stable-diffusion-v1-5": "high quality, detailed, professional",
        "stabilityai/stable-diffusion-2-1": "high quality, sharp focus, detailed",
        "prompthero/openjourney": "mdjrny-v4 style, vibrant, detailed"
    }
    
    enhancement = enhancements.get(model_name, "high quality, detailed")
    return f"{prompt}, {enhancement}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>🎨 Free AI Image Generator</h1>
        <p>Using Hugging Face API Key - High Quality Images</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # API Key Section
    st.subheader("🔑 Hugging Face API Key")
    
    # Get token from secrets or input
    token_from_secrets = os.getenv('HF_TOKEN', '')
    
    if token_from_secrets:
        st.success("✅ API Key found in Streamlit secrets!")
        hf_token = token_from_secrets
        is_valid, token_message = test_huggingface_token(hf_token)
        
        if is_valid:
            st.markdown(f'<div class="success-box">{token_message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">{token_message}</div>', unsafe_allow_html=True)
            st.stop()
    else:
        st.warning("No API key in secrets. Enter your Hugging Face token:")
        manual_token = st.text_input("Hugging Face Token:", type="password")
        
        if manual_token:
            hf_token = manual_token
            is_valid, token_message = test_huggingface_token(hf_token)
            
            if is_valid:
                st.markdown(f'<div class="success-box">{token_message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">{token_message}</div>', unsafe_allow_html=True)
                st.stop()
        else:
            st.info("💡 Get free token from: https://huggingface.co/settings/tokens")
            st.stop()
    
    st.markdown("---")
    
    # Image Generation Section
    st.subheader("🎨 Create Your Image")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="A majestic dragon flying over misty mountains at sunset, fantasy art, highly detailed",
            height=100,
            key="prompt"
        )
        
        # Model selection
        st.markdown("### 🤖 Select Model")
        model_choice = st.selectbox(
            "Choose AI model:",
            [
                "runwayml/stable-diffusion-v1-5",
                "stabilityai/stable-diffusion-2-1", 
                "prompthero/openjourney"
            ],
            help="SD 1.5: Good all-rounder, SD 2.1: Better quality, OpenJourney: Artistic style"
        )
        
        # Show model info
        model_info = {
            "runwayml/stable-diffusion-v1-5": "🔄 **Most Reliable** - Good for all image types",
            "stabilityai/stable-diffusion-2-1": "🌟 **Higher Quality** - Better details and resolution", 
            "prompthero/openjourney": "🎨 **Artistic Style** - Great for fantasy and creative images"
        }
        
        st.markdown(f'<div class="model-card">{model_info[model_choice]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💡 Pro Tips")
        st.markdown("""
        **For BEST results:**
        • Be descriptive and specific
        • Include style keywords
        • Mention lighting and mood
        • Add quality terms
        
        **Great prompts:**
        - Majestic dragon flying over misty mountains, fantasy art, highly detailed, dramatic lighting
        - Cyberpunk city at night, neon lights, futuristic, cinematic
        - Beautiful landscape sunset, professional photography, 8K
        """)
        
        st.markdown("### ⚡ Quick Templates")
        if st.button("🐉 Fantasy Dragon"):
            st.session_state.prompt = "A majestic dragon flying over misty mountains at golden hour, fantasy art, highly detailed, epic scale"
        
        if st.button("🌅 Landscape"):
            st.session_state.prompt = "Beautiful mountain landscape at sunrise, misty valleys, professional photography, highly detailed"
        
        if st.button("🤖 Sci-Fi"):
            st.session_state.prompt = "Futuristic cyberpunk city at night, neon lights, flying cars, detailed architecture, cinematic"
    
    # Generate button
    if st.button("🚀 Generate Image with API", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        else:
            # Enhance prompt
            enhanced_prompt = enhance_prompt_for_model(prompt, model_choice)
            
            with st.spinner(f"🔄 Generating image with {model_choice}..."):
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(4):
                    progress_bar.progress((i + 1) * 25)
                    if i == 0:
                        status_text.text("📝 Processing prompt...")
                    elif i == 1:
                        status_text.text("🔗 Connecting to API...")
                    elif i == 2:
                        status_text.text("🎨 Generating image...")
                    time.sleep(1)
                
                # Generate image
                generated_image, message = generate_with_huggingface_api(enhanced_prompt, hf_token, model_choice)
                
                progress_bar.progress(100)
                
                if generated_image:
                    status_text.text("✅ Image generated!")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown('<div class="success-box">🎉 High-quality image created successfully!</div>', unsafe_allow_html=True)
                    
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
                    status_text.text("❌ Failed")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                    
                    # Solutions based on error
                    if "loading" in message.lower():
                        st.info("🔄 **Solution:** Wait 30-60 seconds and try again. The model is loading.")
                    elif "payment" in message.lower():
                        st.error("💳 **Solution:** This model requires payment. Try 'runwayml/stable-diffusion-v1-5' instead.")
                    elif "token" in message.lower():
                        st.error("🔑 **Solution:** Check your API token is correct and has inference permissions.")
                    else:
                        st.info("🔄 **Solution:** Try a different model or wait a few minutes.")
    
    # Free API Information
    st.markdown("---")
    st.markdown("### 🆓 Free Hugging Face API")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        **✅ What's FREE:**
        - Unlimited image generation
        - No credit card required
        - Multiple AI models
        - High quality 512x512 images
        - No watermarks
        """)
    
    with col4:
        st.markdown("""
        **🔑 Get API Token:**
        1. Go to huggingface.co
        2. Create free account
        3. Settings → Access Tokens
        4. Create new token (read permission)
        5. Add to Streamlit secrets as HF_TOKEN
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Hugging Face Inference API | Free & High Quality</p>
    </div>
""", unsafe_allow_html=True)
