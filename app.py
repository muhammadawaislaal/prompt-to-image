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
    </style>
""", unsafe_allow_html=True)

def generate_with_stable_diffusion_api(prompt, api_key):
    """Generate image using Stable Diffusion API"""
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
            "seed": None
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
                    time.sleep(5)
                    
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
                                return image, "success"
            
            elif result.get('status') == 'processing':
                return None, "Image processing. Please wait..."
            elif 'message' in result:
                return None, f"API: {result['message']}"
        
        elif response.status_code == 402:
            return None, "API credits exhausted"
        else:
            return None, f"API error: {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_with_prodia(prompt):
    """Generate image using Prodia API"""
    try:
        generate_url = "https://api.prodia.com/v1/sd/generate"
        generate_data = {
            "prompt": prompt,
            "model": "dreamshaper_8_93211.safetensors [bcaa7c82]",
            "negative_prompt": "ugly, blurry, low quality",
            "steps": 25,
            "cfg_scale": 7.5,
            "seed": -1
        }
        
        generate_response = requests.post(generate_url, json=generate_data, timeout=30)
        
        if generate_response.status_code == 200:
            job_data = generate_response.json()
            job_id = job_data.get('job')
            
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
                                return image, "success"
                    
                    elif status == 'failed':
                        return None, "Generation failed"
                
                time.sleep(2)
            
            return None, "Generation timeout"
        else:
            return None, f"Prodia error: {generate_response.status_code}"
            
    except Exception as e:
        return None, f"Prodia error: {str(e)}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>AI Image Generator</h1>
        <p>Transform your ideas into visual art</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    # Get API keys from secrets
    SD_API_KEY = os.getenv('SD_API_KEY', '')
    PRODIA_API_KEY = os.getenv('PRODIA_API_KEY', '')
    
    # Check if any API key is available
    if not SD_API_KEY and not PRODIA_API_KEY:
        st.markdown('<div class="error-box">No API keys configured in Streamlit secrets</div>', unsafe_allow_html=True)
        st.stop()
    
    st.subheader("Create Your Image")
    
    prompt = st.text_area(
        "Enter your prompt:",
        placeholder="Describe the image you want to generate...",
        height=120,
        key="prompt"
    )
    
    # Service selection
    service = st.selectbox(
        "AI Service:",
        ["Stable Diffusion API", "Prodia API"]
    )

    # Generate button
    if st.button("Generate Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        else:
            with st.spinner("Generating image... This may take 20-40 seconds."):
                
                generated_image = None
                error_message = ""
                
                if service == "Stable Diffusion API" and SD_API_KEY:
                    generated_image, error_message = generate_with_stable_diffusion_api(prompt, SD_API_KEY)
                elif service == "Prodia API":
                    generated_image, error_message = generate_with_prodia(prompt)
                else:
                    error_message = "Selected service not available"
                
                if generated_image:
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
                    st.markdown(f'<div class="error-box">{error_message}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>AI Image Generation</p>
    </div>
""", unsafe_allow_html=True)
