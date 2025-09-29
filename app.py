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
        .model-info {
            background: #374151;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #8b5cf6;
        }
    </style>
""", unsafe_allow_html=True)

def test_huggingface_token(token):
    """Test if the Hugging Face token is valid"""
    try:
        # Test with a simple model info request
        test_url = "https://huggingface.co/api/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "✅ Token is valid!"
        elif response.status_code == 401:
            return False, "❌ Invalid token - Unauthorized"
        elif response.status_code == 403:
            return False, "❌ Token doesn't have inference access"
        else:
            return False, f"❌ Token test failed with status {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def generate_image_huggingface(prompt, token, model_choice):
    """Generate image using Hugging Face Inference API"""
    try:
        # Use models that work with free tokens
        models = {
            "CompVis/stable-diffusion-v1-4": "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
            "runwayml/stable-diffusion-v1-5": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            "prompthero/openjourney": "https://api-inference.huggingface.co/models/prompthero/openjourney",
            "wavymulder/Analog-Diffusion": "https://api-inference.huggingface.co/models/wavymulder/Analog-Diffusion"
        }
        
        API_URL = models.get(model_choice, models["prompthero/openjourney"])
        headers = {"Authorization": f"Bearer {token}"}
        
        # Payload for the API request
        payload = {
            "inputs": prompt,
            "options": {
                "wait_for_model": True,
                "use_cache": True
            }
        }
        
        # Make the API request with longer timeout
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        
        # Check response status
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)), "success"
        
        elif response.status_code == 503:
            # Model is loading
            error_data = response.json()
            estimated_time = error_data.get('estimated_time', 45)
            return None, f"🔄 Model is loading. Please wait {int(estimated_time)} seconds and try again."
            
        elif response.status_code == 403:
            return None, f"🔐 Access denied for {model_choice}. The model may require payment or special access."
            
        elif response.status_code == 429:
            return None, "⏳ Rate limit exceeded. Please wait a few minutes before trying again."
            
        else:
            error_text = response.text[:200]  # Limit error text length
            return None, f"❌ API Error {response.status_code}: {error_text}"
            
    except requests.exceptions.Timeout:
        return None, "⏰ Request timeout. The model is taking too long to respond. Try a different model."
    except requests.exceptions.ConnectionError:
        return None, "🌐 Connection error. Please check your internet connection."
    except Exception as e:
        return None, f"⚠️ Unexpected error: {str(e)}"

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
    
    # Token Verification Section
    st.subheader("🔐 Token Verification")
    
    # Get token from secrets
    current_token = os.getenv('HF_TOKEN', '')
    
    if current_token:
        st.write("Current token found in secrets. Testing...")
        is_valid, message = test_huggingface_token(current_token)
        
        if is_valid:
            st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">❌ No HF_TOKEN found in secrets</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Image Generation Section
    st.subheader("🎨 Create Your Image")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="A majestic dragon flying over misty mountains at sunset, fantasy art style",
            height=120,
            key="prompt"
        )
        
        # Model selection
        st.markdown("### 🎯 Model Selection")
        model_choice = st.selectbox(
            "Choose AI Model:",
            [
                "prompthero/openjourney",
                "wavymulder/Analog-Diffusion", 
                "CompVis/stable-diffusion-v1-4",
                "runwayml/stable-diffusion-v1-5"
            ],
            help="Some models may require payment. OpenJourney and Analog Diffusion work best with free tokens."
        )
        
        # Show model info
        model_info = {
            "prompthero/openjourney": "🎨 Best for artistic and fantasy images",
            "wavymulder/Analog-Diffusion": "📸 Film photography style",
            "CompVis/stable-diffusion-v1-4": "🖼️ Original Stable Diffusion",
            "runwayml/stable-diffusion-v1-5": "🌟 Improved version (may require payment)"
        }
        
        st.markdown(f'<div class="model-info">💡 {model_info[model_choice]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💡 Prompt Tips")
        st.markdown("""
        **Be specific about:**
        - Style (fantasy, realistic, anime)
        - Lighting (sunset, dramatic, soft)
        - Composition (close-up, landscape)
        - Mood (epic, serene, mysterious)
        
        **Better:**
        "Epic dragon flying over misty mountains at golden hour, fantasy art, highly detailed"
        
        **Avoid:**
        "A dragon" (too vague)
        """)
    
    # Generate button
    if st.button("🚀 Generate Image", use_container_width=True):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        elif not current_token:
            st.error("No Hugging Face token configured. Please add HF_TOKEN to Streamlit secrets.")
        else:
            with st.spinner(f"🔄 Generating your image using {model_choice}... This may take 30-60 seconds."):
                generated_image, message = generate_image_huggingface(prompt, current_token, model_choice)
                
                if generated_image:
                    st.markdown('<div class="success-box">✅ Image generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Display image
                    st.image(generated_image, use_container_width=True, caption=f"Generated with: {model_choice}")
                    
                    # Download button
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG")
                    st.download_button(
                        label="📥 Download Image",
                        data=buf.getvalue(),
                        file_name=f"ai_generated_{hash(prompt) % 10000}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                else:
                    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
                    
                    # Show troubleshooting tips
                    with st.expander("🔧 Troubleshooting Tips"):
                        st.markdown("""
                        **If you see access errors:**
                        1. Try **OpenJourney** or **Analog Diffusion** models (they work better with free tokens)
                        2. Some models require payment - check Hugging Face for pricing
                        3. Wait a few minutes if you hit rate limits
                        4. Try a simpler prompt
                        
                        **Best free models to try:**
                        - `prompthero/openjourney` - Great for fantasy and artistic images
                        - `wavymulder/Analog-Diffusion` - Film photography style
                        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Hugging Face AI Models | Professional Image Generation</p>
    </div>
""", unsafe_allow_html=True)
