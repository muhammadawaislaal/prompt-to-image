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
        .token-test {
            background: #374151;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #4b5563;
            margin: 1rem 0;
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

def generate_image_huggingface(prompt, token):
    """Generate image using Hugging Face Inference API"""
    try:
        # API endpoint for Stable Diffusion
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {token}"}
        
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
            return Image.open(io.BytesIO(response.content)), "success"
        
        elif response.status_code == 503:
            # Model is loading
            error_data = response.json()
            estimated_time = error_data.get('estimated_time', 30)
            return None, f"Model is loading. Please wait {int(estimated_time)} seconds and try again."
            
        elif response.status_code == 403:
            return None, "Access denied. Please check your Hugging Face token."
            
        elif response.status_code == 429:
            return None, "Rate limit exceeded. Please wait a few minutes before trying again."
            
        else:
            return None, f"API Error {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return None, "Request timeout. The model is taking too long to respond."
    except requests.exceptions.ConnectionError:
        return None, "Connection error. Please check your internet connection."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

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
            st.error("Please add a new valid Hugging Face token to Streamlit secrets.")
    else:
        st.markdown('<div class="error-box">❌ No HF_TOKEN found in secrets</div>', unsafe_allow_html=True)
    
    # Manual token input for testing (optional)
    with st.expander("🔧 Manual Token Test (Optional)"):
        manual_token = st.text_input("Enter a token to test:", type="password")
        if manual_token:
            is_valid, message = test_huggingface_token(manual_token)
            if is_valid:
                st.success(message)
                st.info("If this token works, add it to your Streamlit secrets!")
            else:
                st.error(message)
    
    st.markdown("---")
    
    # Image Generation Section
    st.subheader("🎨 Create Your Image")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="Describe the image you want to generate...",
            height=120,
            key="prompt"
        )
    
    with col2:
        st.markdown("""
        **Tips for best results:**
        - Be specific and descriptive
        - Include style references
        - Mention composition details
        - Specify lighting and mood
        
        **Example:**
        "A majestic dragon flying over misty mountains at sunset, fantasy art style"
        """)
    
    # Generate button
    if st.button("🚀 Generate Image", use_container_width=True):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        elif not current_token:
            st.error("No Hugging Face token configured. Please add HF_TOKEN to Streamlit secrets.")
        else:
            with st.spinner("🔄 Generating your image... This may take 20-30 seconds."):
                generated_image, message = generate_image_huggingface(prompt, current_token)
                
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
                    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Hugging Face AI Models | Professional Image Generation</p>
    </div>
""", unsafe_allow_html=True)
