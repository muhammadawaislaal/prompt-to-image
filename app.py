import streamlit as st
import requests
from PIL import Image
import io
import time
import base64

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
    </style>
""", unsafe_allow_html=True)

def test_stable_diffusion_api(api_key):
    """Test if Stable Diffusion API key is valid"""
    try:
        # Try multiple API endpoints
        endpoints = [
            "https://stablediffusionapi.com/api/v4/account_status",
            "https://stablediffusionapi.com/api/v3/account_status",
            "https://stablediffusionapi.com/api/v5/account_status"
        ]
        
        for endpoint in endpoints:
            try:
                payload = {"key": api_key}
                response = requests.post(endpoint, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    return True, "✅ API key is valid and ready to use!"
            except:
                continue
        
        return False, "❌ Cannot connect to API service"
            
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def generate_with_stable_diffusion(prompt, api_key):
    """Generate image using Stable Diffusion API"""
    try:
        # Try multiple API endpoints
        endpoints = [
            "https://stablediffusionapi.com/api/v4/text2img",
            "https://stablediffusionapi.com/api/v3/text2img", 
            "https://stablediffusionapi.com/api/v5/text2img"
        ]
        
        for endpoint in endpoints:
            try:
                payload = {
                    "key": api_key,
                    "prompt": prompt,
                    "negative_prompt": "ugly, blurry, bad anatomy, poorly drawn, deformed",
                    "width": "512",
                    "height": "512",
                    "samples": "1",
                    "num_inference_steps": "25",
                    "guidance_scale": 7.5,
                    "safety_checker": "no",
                    "enhance_prompt": "yes",
                    "seed": None
                }
                
                headers = {'Content-Type': 'application/json'}
                
                response = requests.post(endpoint, json=payload, headers=headers, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('status') == 'success':
                        if 'output' in result and result['output']:
                            image_url = result['output'][0]
                            image_response = requests.get(image_url, timeout=30)
                            if image_response.status_code == 200:
                                image = Image.open(io.BytesIO(image_response.content))
                                return image, "success"
                        
                        elif 'fetch_result' in result:
                            job_id = result['id']
                            time.sleep(3)
                            
                            # Try multiple fetch endpoints
                            fetch_endpoints = [
                                f"https://stablediffusionapi.com/api/v4/fetch/{job_id}",
                                f"https://stablediffusionapi.com/api/v3/fetch/{job_id}",
                                f"https://stablediffusionapi.com/api/v5/fetch/{job_id}"
                            ]
                            
                            for fetch_endpoint in fetch_endpoints:
                                try:
                                    fetch_payload = {"key": api_key}
                                    fetch_response = requests.post(fetch_endpoint, json=fetch_payload, timeout=60)
                                    if fetch_response.status_code == 200:
                                        fetch_result = fetch_response.json()
                                        if fetch_result.get('status') == 'success' and 'output' in fetch_result:
                                            image_url = fetch_result['output'][0]
                                            image_response = requests.get(image_url, timeout=30)
                                            if image_response.status_code == 200:
                                                image = Image.open(io.BytesIO(image_response.content))
                                                return image, "success"
                                except:
                                    continue
                    
                    elif result.get('status') == 'processing':
                        return None, "Image is processing. Please wait 10-20 seconds..."
                    elif 'message' in result:
                        return None, f"API: {result['message']}"
                
                elif response.status_code == 402:
                    return None, "Daily credits exhausted. Free credits reset every 24 hours."
                
            except requests.exceptions.Timeout:
                continue
            except:
                continue
        
        return None, "All API endpoints failed. Please try again later."
            
    except Exception as e:
        return None, f"Error: {str(e)}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>AI Image Generator</h1>
        <p>Powered by Stable Diffusion API</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # API Key Input Section
    st.subheader("🔑 API Key Required")
    
    api_key = st.text_input(
        "Enter your Stable Diffusion API key:",
        type="password",
        placeholder="Paste your API key here...",
        help="Get free API key from https://stablediffusionapi.com"
    )
    
    # Test API key
    if api_key:
        is_valid, key_message = test_stable_diffusion_api(api_key)
        if is_valid:
            st.markdown(f'<div class="success-box">{key_message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">{key_message}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">🔑 Please enter your Stable Diffusion API key to generate images</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Image Generation Section
    st.subheader("🎨 Create Your Image")
    
    prompt = st.text_area(
        "Enter your prompt:",
        placeholder="A majestic dragon flying over misty mountains at sunset, fantasy art, highly detailed, dramatic lighting",
        height=120,
        key="prompt"
    )

    # Quick prompt buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐉 Fantasy Dragon"):
            st.session_state.prompt = "A majestic dragon flying over misty mountains at golden hour, fantasy art, highly detailed, epic scale, dramatic lighting"
    with col2:
        if st.button("🌆 Cyberpunk City"):
            st.session_state.prompt = "Futuristic cyberpunk city at night, neon lights, flying cars, detailed architecture, cinematic, highly detailed"
    with col3:
        if st.button("🏔️ Landscape"):
            st.session_state.prompt = "Majestic mountain landscape at sunrise, misty valleys, professional photography, highly detailed, dramatic lighting"

    # Generate button
    if st.button("🚀 Generate Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        elif not api_key:
            st.error("Please enter your Stable Diffusion API key.")
        else:
            with st.spinner("🔄 Generating image... This may take 20-40 seconds."):
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                steps = [
                    "Processing your prompt...",
                    "Connecting to Stable Diffusion API...", 
                    "Generating image...",
                    "Finalizing details..."
                ]
                
                for i, step in enumerate(steps):
                    progress_bar.progress((i + 1) * 25)
                    status_text.text(step)
                    time.sleep(1)
                
                # Generate image
                generated_image, message = generate_with_stable_diffusion(prompt, api_key)
                
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
                        label="📥 Download Image",
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
                    
                    # Helpful suggestions
                    if "credits" in message.lower():
                        st.info("💡 **Tip:** Free credits reset every 24 hours. Check your dashboard for credit status.")
                    elif any(word in message.lower() for word in ['loading', 'processing', 'wait']):
                        st.info("💡 **Tip:** Wait 30 seconds and try again. The AI model needs time to load.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Stable Diffusion API | Professional AI Image Generation</p>
    </div>
""", unsafe_allow_html=True)
