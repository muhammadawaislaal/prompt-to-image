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
        # Updated API endpoint
        url = "https://stablediffusionapi.com/api/v5/account_status"
        payload = {"key": api_key}
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'credits' in result or 'status' in result:
                return True, "✅ API key is valid and ready to use!"
            else:
                return False, "❌ Invalid API key response"
        else:
            return False, f"❌ API error: {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def generate_with_stable_diffusion(prompt, api_key):
    """Generate image using Stable Diffusion API with updated endpoints"""
    try:
        # Updated API endpoint
        url = "https://stablediffusionapi.com/api/v5/text2img"
        
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
            "seed": None,
            "webhook": None,
            "track_id": None
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
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
                    
                    # Updated fetch endpoint
                    fetch_url = f"https://stablediffusionapi.com/api/v5/fetch/{job_id}"
                    fetch_payload = {"key": api_key}
                    
                    fetch_response = requests.post(fetch_url, json=fetch_payload, timeout=60)
                    if fetch_response.status_code == 200:
                        fetch_result = fetch_response.json()
                        if fetch_result.get('status') == 'success' and 'output' in fetch_result:
                            image_url = fetch_result['output'][0]
                            image_response = requests.get(image_url, timeout=30)
                            if image_response.status_code == 200:
                                image = Image.open(io.BytesIO(image_response.content))
                                return image, "success"
            
            elif result.get('status') == 'processing':
                return None, "Image is processing. Please wait 10-20 seconds..."
            elif 'message' in result:
                return None, f"API Message: {result['message']}"
            else:
                return None, "Unknown API response"
        
        elif response.status_code == 402:
            return None, "Daily credits exhausted. Free credits reset every 24 hours."
        elif response.status_code == 404:
            return None, "API endpoint not found. Service may be updating."
        else:
            return None, f"API Error {response.status_code}: {response.text[:100]}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_with_prodia(prompt):
    """Generate image using Prodia API (no key required) - RELIABLE"""
    try:
        generate_url = "https://api.prodia.com/v1/sd/generate"
        generate_data = {
            "prompt": prompt,
            "model": "dreamshaper_8_93211.safetensors [bcaa7c82]",
            "negative_prompt": "ugly, blurry, low quality, poorly drawn, deformed",
            "steps": 25,
            "cfg_scale": 7.5,
            "seed": -1,
            "upscale": False
        }
        
        generate_response = requests.post(generate_url, json=generate_data, timeout=30)
        
        if generate_response.status_code == 200:
            job_data = generate_response.json()
            job_id = job_data.get('job')
            
            # Wait for generation to complete
            max_attempts = 40
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
                                return image, "success"
                    
                    elif status == 'failed':
                        return None, "Generation failed - try a different prompt"
                
                time.sleep(1.5)  # Wait 1.5 seconds between checks
            
            return None, "Generation timeout - try again"
        else:
            return None, f"Prodia API error: {generate_response.status_code}"
            
    except Exception as e:
        return None, f"Prodia error: {str(e)}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>AI Image Generator</h1>
        <p>Free High-Quality Image Generation</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # API Key Input Section
    st.subheader("🔑 Free API Key")
    
    api_key = st.text_input(
        "Enter your Stable Diffusion API key:",
        type="password",
        placeholder="Paste your API key here...",
        help="Get free API key from https://stablediffusionapi.com"
    )
    
    # Service selection - Default to Prodia since it's more reliable
    service = st.selectbox(
        "Select AI Service:",
        ["Prodia API (Recommended - No key needed)", "Stable Diffusion API"],
        help="Prodia: More reliable, no API key needed. Stable Diffusion: Higher quality but may have issues."
    )
    
    # Test API key if provided and selected
    if api_key and service == "Stable Diffusion API":
        is_valid, key_message = test_stable_diffusion_api(api_key)
        if is_valid:
            st.markdown(f'<div class="success-box">{key_message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">{key_message}</div>', unsafe_allow_html=True)
    
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
        elif service == "Stable Diffusion API" and not api_key:
            st.error("Please enter your Stable Diffusion API key.")
        else:
            with st.spinner("🔄 Generating image... This may take 20-40 seconds."):
                
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
                
                # Generate image based on service selection
                if service == "Stable Diffusion API":
                    generated_image, message = generate_with_stable_diffusion(prompt, api_key)
                else:
                    generated_image, message = generate_with_prodia(prompt)
                
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
                        st.info("💡 **Tip:** Free credits reset every 24 hours. Try Prodia API for unlimited free images.")
                    elif any(word in message.lower() for word in ['loading', 'processing', 'wait']):
                        st.info("💡 **Tip:** Wait 30 seconds and try again. The AI model needs time to load.")
                    elif "404" in message:
                        st.info("💡 **Tip:** API endpoint issue. Use 'Prodia API' which is more reliable.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Free AI Image Generation | Unlimited Images with Prodia API</p>
    </div>
""", unsafe_allow_html=True)
