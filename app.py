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
        test_url = "https://huggingface.co/api/models"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "✅ Token is valid and working!"
        elif response.status_code == 401:
            return False, "❌ Invalid token - Unauthorized access"
        elif response.status_code == 403:
            return False, "❌ Token rejected - Check permissions"
        else:
            return False, f"❌ Token error: Status {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Connection failed: {str(e)}"

def generate_image_huggingface(prompt, token):
    """Generate image using Hugging Face Inference API"""
    try:
        # Use a model that works with free inference
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Simple payload - no complex parameters that might cause issues
        payload = {
            "inputs": prompt,
            "options": {
                "wait_for_model": True,
                "use_cache": False  # Set to False to avoid cache issues
            }
        }
        
        # Make the API request with timeout
        with st.spinner("🔄 Sending request to Hugging Face..."):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        
        # Check response status
        if response.status_code == 200:
            try:
                image = Image.open(io.BytesIO(response.content))
                return image, "success"
            except Exception as img_error:
                return None, f"Image processing error: {str(img_error)}"
        
        elif response.status_code == 503:
            # Model is loading
            try:
                error_data = response.json()
                estimated_time = error_data.get('estimated_time', 60)
                return None, f"🔄 Model is loading. Estimated wait: {int(estimated_time)} seconds. Please try again later."
            except:
                return None, "🔄 Model is currently loading. Please try again in 1-2 minutes."
            
        elif response.status_code == 401:
            return None, "🔐 Invalid token. Please check your Hugging Face token in secrets."
            
        elif response.status_code == 403:
            return None, "🚫 Access forbidden. This model requires payment or special access. Please use a different model or upgrade your account."
            
        elif response.status_code == 429:
            return None, "⏳ Rate limit exceeded. Please wait 1-2 minutes before trying again."
            
        else:
            error_msg = response.text[:150] if response.text else "No error details"
            return None, f"❌ API Error {response.status_code}: {error_msg}"
            
    except requests.exceptions.Timeout:
        return None, "⏰ Request timeout. Server is taking too long to respond. Try again later."
    except requests.exceptions.ConnectionError:
        return None, "🌐 Connection error. Check your internet connection."
    except Exception as e:
        return None, f"⚠️ Unexpected error: {str(e)}"

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
    
    # Token Status Section
    st.subheader("🔐 API Status")
    
    # Get token from secrets
    current_token = os.getenv('HF_TOKEN', '')
    
    if current_token:
        # Test the token
        is_valid, message = test_huggingface_token(current_token)
        
        if is_valid:
            st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
            st.stop()  # Stop execution if token is invalid
    else:
        st.markdown('<div class="error-box">❌ No HF_TOKEN found in Streamlit secrets</div>', unsafe_allow_html=True)
        st.info("Please add your Hugging Face token to Streamlit secrets as HF_TOKEN")
        st.stop()
    
    st.markdown("---")
    
    # Image Generation Section
    st.subheader("🎨 Create Your Image")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="Example: A majestic dragon flying over misty mountains at sunset, fantasy art style, highly detailed",
            height=120,
            key="prompt"
        )
        
        # Model information
        st.markdown("### 🛠 Model Information")
        st.markdown("""
        **Current Model:** `runwayml/stable-diffusion-v1-5`
        
        **Status:** ✅ Ready for inference
        
        **Note:** First request may take longer as the model loads
        """)
    
    with col2:
        st.markdown("### 💡 Prompt Guide")
        st.markdown("""
        **For best results:**
        
        • Be descriptive and specific
        • Include style keywords
        • Mention lighting and mood
        • Add quality terms
        
        **Good example:**
        "Epic dragon soaring over misty peaks at golden hour, fantasy artwork, highly detailed, dramatic lighting"
        """)
    
    # Generate button
    if st.button("🚀 Generate Image Now", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        else:
            # Show generation progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(3):
                progress_bar.progress((i + 1) * 25)
                if i == 0:
                    status_text.text("📝 Processing your prompt...")
                elif i == 1:
                    status_text.text("🔄 Connecting to AI model...")
                elif i == 2:
                    status_text.text("🎨 Generating your image...")
                time.sleep(1)
            
            # Generate image
            generated_image, message = generate_image_huggingface(prompt, current_token)
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            if generated_image:
                st.markdown('<div class="success-box">🎉 Image generated successfully!</div>', unsafe_allow_html=True)
                
                # Display image
                st.image(generated_image, use_container_width=True, caption=f"Generated: '{prompt}'")
                
                # Download button
                buf = io.BytesIO()
                generated_image.save(buf, format="PNG")
                st.download_button(
                    label="📥 Download Image",
                    data=buf.getvalue(),
                    file_name=f"ai_image_{int(time.time())}.png",
                    mime="image/png",
                    use_container_width=True
                )
                
                st.balloons()
            else:
                st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
                
                # Show specific solutions based on error
                if "loading" in message.lower():
                    st.markdown("""
                    **🔄 Model Loading Solution:**
                    - Wait 1-2 minutes and try again
                    - The model needs to load on Hugging Face servers
                    - This is normal for first-time use
                    """)
                elif "payment" in message.lower() or "forbidden" in message.lower():
                    st.markdown("""
                    **🚫 Access Solution:**
                    - This model may require payment
                    - Check your Hugging Face account billing
                    - Consider using free-tier models
                    """)
                elif "token" in message.lower():
                    st.markdown("""
                    **🔐 Token Solution:**
                    - Verify your token in Streamlit secrets
                    - Ensure token has 'read' permissions
                    - Generate a new token if needed
                    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Hugging Face Inference API | Stable Diffusion v1.5</p>
    </div>
""", unsafe_allow_html=True)
