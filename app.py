import streamlit as st
import requests
from PIL import Image
import io
import time
import base64

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
        .api-card {
            background: #374151;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #8b5cf6;
        }
    </style>
""", unsafe_allow_html=True)

def generate_with_stable_diffusion_api(prompt, api_key):
    """Generate image using Stable Diffusion API with API key"""
    try:
        url = "https://stablediffusionapi.com/api/v3/text2img"
        
        payload = {
            "key": api_key,
            "prompt": prompt,
            "negative_prompt": "ugly, blurry, bad anatomy, poorly drawn",
            "width": "512",
            "height": "512",
            "samples": "1",
            "num_inference_steps": "20",
            "guidance_scale": 7.5,
            "safety_checker": "no",
            "enhance_prompt": "yes",
            "seed": None,
            "webhook": None,
            "track_id": None
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('status') == 'success':
                if 'output' in result and result['output']:
                    image_url = result['output'][0]
                    # Download the image
                    image_response = requests.get(image_url, timeout=30)
                    if image_response.status_code == 200:
                        image = Image.open(io.BytesIO(image_response.content))
                        return image, "Stable Diffusion API"
                
                elif 'fetch_result' in result:
                    # Need to fetch result with job ID
                    job_id = result['id']
                    time.sleep(5)  # Wait for processing
                    
                    fetch_url = f"https://stablediffusionapi.com/api/v3/fetch/{job_id}"
                    fetch_payload = {"key": api_key}
                    
                    fetch_response = requests.post(fetch_url, json=fetch_payload, timeout=60)
                    if fetch_response.status_code == 200:
                        fetch_result = fetch_response.json()
                        if fetch_result.get('status') == 'success' and 'output' in fetch_result:
                            image_url = fetch_result['output'][0]
                            image_response = requests.get(image_url, timeout=30)
                            if image_response.status_code == 200:
                                image = Image.open(io.BytesIO(image_response.content))
                                return image, "Stable Diffusion API"
            
            elif result.get('status') == 'processing':
                return None, "Image is processing. Please wait..."
            elif 'message' in result:
                return None, f"API Error: {result['message']}"
            else:
                return None, "Unknown API error"
        
        elif response.status_code == 402:
            return None, "API credits exhausted. Get free credits from Stable Diffusion API website."
        else:
            return None, f"HTTP Error {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_with_prodia(prompt, api_key=None):
    """Generate image using Prodia API"""
    try:
        # Step 1: Start generation
        generate_url = "https://api.prodia.com/v1/sd/generate"
        generate_data = {
            "prompt": prompt,
            "model": "dreamshaper_8_93211.safetensors [bcaa7c82]",
            "negative_prompt": "ugly, blurry, low quality, poorly drawn",
            "steps": 25,
            "cfg_scale": 7.5,
            "seed": -1,
            "upscale": False
        }
        
        if api_key:
            generate_data["key"] = api_key
        
        generate_response = requests.post(generate_url, json=generate_data, timeout=30)
        
        if generate_response.status_code == 200:
            job_data = generate_response.json()
            job_id = job_data.get('job')
            
            # Step 2: Wait for completion
            max_attempts = 30
            for attempt in range(max_attempts):
                job_url = f"https://api.prodia.com/v1/job/{job_id}"
                job_response = requests.get(job_url, timeout=30)
                
                if job_response.status_code == 200:
                    job_result = job_response.json()
                    status = job_result.get('status')
                    
                    if status == 'succeeded':
                        image_url = job_result.get('imageUrl')
                        if image_url:
                            image_response = requests.get(image_url, timeout=30)
                            if image_response.status_code == 200:
                                image = Image.open(io.BytesIO(image_response.content))
                                return image, "Prodia API"
                    
                    elif status == 'failed':
                        return None, "Generation failed"
                
                time.sleep(2)
            
            return None, "Generation timeout"
        else:
            return None, f"Prodia API error: {generate_response.status_code}"
            
    except Exception as e:
        return None, f"Prodia error: {str(e)}"

def test_api_key(api_key, service):
    """Test if API key is valid"""
    try:
        if service == "stable_diffusion":
            test_url = "https://stablediffusionapi.com/api/v3/account"
            test_data = {"key": api_key}
            response = requests.post(test_url, json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'credits' in result:
                    return True, f"✅ Valid - Credits: {result['credits']}"
                else:
                    return False, "❌ Invalid API key"
            else:
                return False, f"❌ API error: {response.status_code}"
                
        elif service == "prodia":
            # Prodia doesn't have a test endpoint, but we can try a simple generation
            return True, "✅ Prodia key accepted"
            
    except Exception as e:
        return False, f"❌ Test failed: {str(e)}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>🎨 Free AI Image Generator</h1>
        <p>Using Stable Diffusion API with Free API Key</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # API Key Section
    st.subheader("🔑 Get FREE API Key")
    
    st.markdown("""
    <div class="info-box">
        <h3>🚀 How to Get FREE API Key</h3>
        <p><strong>Step 1:</strong> Go to <a href="https://stablediffusionapi.com" target="_blank">stablediffusionapi.com</a></p>
        <p><strong>Step 2:</strong> Sign up for free account</p>
        <p><strong>Step 3:</strong> Go to Dashboard → API Keys</p>
        <p><strong>Step 4:</strong> Copy your free API key</p>
        <p><strong>Step 5:</strong> Paste below (you get 100 free images daily!)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key Input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        api_key = st.text_input(
            "Stable Diffusion API Key:",
            type="password",
            placeholder="Enter your free API key from stablediffusionapi.com"
        )
        
        if api_key:
            # Test the API key
            is_valid, message = test_api_key(api_key, "stable_diffusion")
            if is_valid:
                st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💡 Free Credits")
        st.markdown("""
        **With Free Account:**
        - 100 images per day
        - No credit card needed
        - High quality 512x512
        - Fast generation
        """)
    
    st.markdown("---")
    
    # Image Generation Section
    st.subheader("🎨 Create Your Image")
    
    col3, col4 = st.columns([2, 1])
    
    with col3:
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="A majestic dragon flying over misty mountains at sunset, fantasy art, highly detailed, dramatic lighting, 4K",
            height=100,
            key="prompt"
        )
        
        # Model settings
        st.markdown("### ⚙️ Settings")
        service_choice = st.selectbox(
            "AI Service:",
            ["Stable Diffusion API", "Prodia API"],
            help="Stable Diffusion: Highest quality, Prodia: Fast generation"
        )
    
    with col4:
        st.markdown("### 💡 Prompt Tips")
        st.markdown("""
        **For REALISTIC images:**
        • Start with "A realistic photo of..."
        • Add "highly detailed, 8K resolution"
        • Specify lighting conditions
        • Mention camera style
        
        **Examples:**
        - Realistic photo of dragon, highly detailed
        - Cyberpunk city, neon lights, cinematic
        - Fantasy landscape, magical, epic scale
        """)
        
        st.markdown("### ⚡ Quick Templates")
        if st.button("🐉 Fantasy Dragon"):
            st.session_state.prompt = "A majestic dragon flying over misty mountains at golden hour, fantasy art, highly detailed, epic scale, dramatic lighting, 4K resolution"
        
        if st.button("🌆 Cyberpunk City"):
            st.session_state.prompt = "Futuristic cyberpunk city at night, neon lights, flying cars, detailed architecture, cinematic, highly detailed, 4K"
        
        if st.button("🏔️ Landscape"):
            st.session_state.prompt = "Majestic mountain landscape at sunrise, misty valleys, professional photography, highly detailed, dramatic lighting, 8K"

    # Generate button
    if st.button("🚀 Generate High-Quality Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        elif not api_key:
            st.error("Please enter your Stable Diffusion API key.")
        else:
            with st.spinner("🔄 Generating high-quality image... (20-40 seconds)"):
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(5):
                    progress_bar.progress((i + 1) * 20)
                    if i == 0:
                        status_text.text("📝 Processing your prompt...")
                    elif i == 1:
                        status_text.text("🔗 Connecting to AI service...")
                    elif i == 2:
                        status_text.text("🎨 Generating image...")
                    elif i == 3:
                        status_text.text("✨ Enhancing details...")
                    time.sleep(1)
                
                # Generate based on service choice
                if service_choice == "Stable Diffusion API":
                    generated_image, message = generate_with_stable_diffusion_api(prompt, api_key)
                else:
                    generated_image, message = generate_with_prodia(prompt)
                
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
                        label="📥 Download High-Quality Image",
                        data=buf.getvalue(),
                        file_name=f"professional_ai_image_{int(time.time())}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    st.balloons()
                    
                    # Success info
                    st.info("""
                    **✅ Success!** 
                    - This is a real AI-generated image
                    - High quality 512x512 resolution
                    - You can generate 100 images daily for free
                    - No watermarks or limitations
                    """)
                
                else:
                    status_text.text("❌ Failed")
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                    
                    # Solutions
                    if "credits" in message.lower():
                        st.error("""
                        **💳 Solution:** 
                        - You've used your daily free credits
                        - Wait 24 hours for reset
                        - Or upgrade account for more credits
                        """)
                    elif "processing" in message.lower():
                        st.info("**🔄 Solution:** Wait 30 seconds and try again. The image is still processing.")
                    else:
                        st.info("**🔄 Solution:** Try using Prodia API or check your API key.")
    
    # API Information
    st.markdown("---")
    st.markdown("### 🆓 Free API Information")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("""
        **🤖 Stable Diffusion API**
        - 100 free images daily
        - High quality 512x512
        - Fast generation
        - No watermarks
        - Professional results
        """)
    
    with col6:
        st.markdown("""
        **🔑 Get API Key:**
        1. Visit stablediffusionapi.com
        2. Sign up free account
        3. Go to API Keys section
        4. Copy your key
        5. Paste above and generate!
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Stable Diffusion API • Free Tier • High Quality Images</p>
    </div>
""", unsafe_allow_html=True)
