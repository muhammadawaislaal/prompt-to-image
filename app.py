import streamlit as st
import requests
from PIL import Image
import io
import os
import time
import base64

# Page configuration
st.set_page_config(
    page_title="Professional AI Image Generator",
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
    </style>
""", unsafe_allow_html=True)

def generate_with_huggingface_free(prompt, model_name):
    """Generate image using Hugging Face FREE inference API"""
    try:
        # FREE models that actually work without payment
        free_models = {
            "black-forest-labs/FLUX.1-schnell": {
                "url": "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
                "requires_token": False
            },
            "dataautogpt3/OpenDalleV1.1": {
                "url": "https://api-inference.huggingface.co/models/dataautogpt3/OpenDalleV1.1", 
                "requires_token": False
            },
            "stabilityai/stable-diffusion-xl-base-1.0": {
                "url": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                "requires_token": False
            }
        }
        
        model_info = free_models.get(model_name)
        if not model_info:
            return None, f"Model {model_name} not found"
        
        API_URL = model_info["url"]
        
        # Use token if available, but these models work without token
        headers = {}
        token = os.getenv('HF_TOKEN', '')
        if token and model_info["requires_token"]:
            headers = {"Authorization": f"Bearer {token}"}
        
        # Optimized payload for better quality
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512
            },
            "options": {
                "wait_for_model": True,
                "use_cache": True
            }
        }
        
        # Make request with timeout
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image, f"Success with {model_name}"
        
        elif response.status_code == 503:
            # Model is loading
            try:
                error_data = response.json()
                estimated_time = error_data.get('estimated_time', 30)
                return None, f"Model is loading. Wait {int(estimated_time)} seconds."
            except:
                return None, "Model loading. Please wait."
        
        else:
            return None, f"API Error {response.status_code}. Try another model."
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def enhance_prompt(base_prompt, style):
    """Enhance the prompt for better results"""
    style_enhancements = {
        "realistic": "photorealistic, highly detailed, professional photography, sharp focus, 8K resolution",
        "fantasy": "fantasy art, magical, epic, concept art, digital painting, trending on artstation",
        "anime": "anime style, Japanese animation, vibrant colors, detailed, masterpiece",
        "digital_art": "digital artwork, illustrative, vivid colors, detailed, trending on artstation",
        "cinematic": "cinematic, dramatic lighting, film still, movie quality, depth of field"
    }
    
    enhancement = style_enhancements.get(style, "high quality, detailed, professional")
    return f"{base_prompt}, {enhancement}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>🎨 Professional AI Image Generator</h1>
        <p>High-Quality Images Using Free Hugging Face Models</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>🚀 High-Quality Free Models</h3>
        <p>These models produce <strong>realistic, high-quality images</strong> and are completely free to use!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="A realistic photo of a majestic dragon flying over misty mountains at sunset, highly detailed, 8K resolution",
            height=100,
            key="prompt"
        )
        
        # Model selection
        st.markdown("### 🎯 Select AI Model")
        model_choice = st.selectbox(
            "Choose model:",
            [
                "black-forest-labs/FLUX.1-schnell",
                "dataautogpt3/OpenDalleV1.1", 
                "stabilityai/stable-diffusion-xl-base-1.0"
            ],
            help="FLUX.1-schnell: Fast & high quality, OpenDalle: Good for creative images, SDXL: Balanced quality"
        )
        
        # Style enhancement
        st.markdown("### 🎨 Image Style")
        style_choice = st.selectbox(
            "Enhance with style:",
            ["realistic", "fantasy", "cinematic", "digital_art", "anime"],
            help="This will enhance your prompt for better results"
        )
        
        # Show model info
        model_info = {
            "black-forest-labs/FLUX.1-schnell": "🌟 **Best Choice** - Fast generation, high quality, realistic images",
            "dataautogpt3/OpenDalleV1.1": "🎨 Creative images, good for fantasy and artistic styles", 
            "stabilityai/stable-diffusion-xl-base-1.0": "🖼️ Balanced quality, reliable results"
        }
        
        st.markdown(f'<div class="model-card">{model_info[model_choice]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💡 Pro Tips")
        st.markdown("""
        **For REALISTIC images:**
        • Start with "A realistic photo of..."
        • Add "highly detailed, 8K resolution"
        • Specify lighting: "dramatic lighting, golden hour"
        • Mention camera: "professional photography"
        
        **Example:**
        "A realistic photo of a dragon flying over mountains at sunset, highly detailed, 8K resolution, professional photography, dramatic lighting"
        """)
        
        st.markdown("### ⚡ Quick Presets")
        if st.button("🏔️ Realistic Landscape"):
            st.session_state.prompt = "A realistic photo of majestic mountains at sunrise, misty valleys, dramatic lighting, professional landscape photography, 8K resolution"
        
        if st.button("🐉 Fantasy Dragon"):
            st.session_state.prompt = "A realistic photo of a majestic dragon flying over misty mountains at golden hour, highly detailed scales, dramatic lighting, fantasy art, 8K resolution"
        
        if st.button("🌃 Cyberpunk City"):
            st.session_state.prompt = "A realistic photo of a cyberpunk city at night, neon lights, flying cars, futuristic architecture, cinematic lighting, 8K resolution"
    
    # Generate button
    if st.button("🚀 Generate High-Quality Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        else:
            # Enhance the prompt
            enhanced_prompt = enhance_prompt(prompt, style_choice)
            
            with st.spinner(f"🔄 Generating high-quality image with {model_choice}... (30-60 seconds)"):
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(5):
                    progress_bar.progress((i + 1) * 20)
                    if i == 0:
                        status_text.text("📝 Enhancing your prompt...")
                    elif i == 1:
                        status_text.text("🔧 Initializing AI model...")
                    elif i == 2:
                        status_text.text("🎨 Generating image...")
                    elif i == 3:
                        status_text.text("✨ Adding final details...")
                    time.sleep(1)
                
                # Generate image
                generated_image, message = generate_with_huggingface_free(enhanced_prompt, model_choice)
                
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                if generated_image:
                    st.markdown(f'<div class="success-box">🎉 High-quality image generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Show original vs enhanced prompt
                    with st.expander("📝 See enhanced prompt"):
                        st.write(f"**Original:** {prompt}")
                        st.write(f"**Enhanced:** {enhanced_prompt}")
                    
                    # Display image
                    st.image(generated_image, use_container_width=True, caption=f"'{prompt}' - Generated with {model_choice.split('/')[-1]}")
                    
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
                    
                    # Success tips
                    st.info("""
                    **✅ Success! Tips for even better results:**
                    - Try different models for varied styles
                    - Use the 'realistic' style for photorealistic images  
                    - Be very specific in your descriptions
                    - Mention lighting and camera details
                    """)
                
                else:
                    st.error(f"❌ {message}")
                    
                    # Troubleshooting guide
                    with st.expander("🔧 Troubleshooting Guide"):
                        st.markdown("""
                        **If generation fails:**
                        1. **Wait 1 minute** - models might be loading
                        2. **Try a different model** - FLUX.1-schnell is most reliable
                        3. **Simplify your prompt** - remove very specific details
                        4. **Check internet connection**
                        5. **Try again in 2 minutes** - free tier might have rate limits
                        
                        **Best model order:**
                        1. FLUX.1-schnell (fastest & highest quality)
                        2. OpenDalleV1.1 (good for creative)
                        3. SDXL (reliable backup)
                        """)
    
    # Model information section
    st.markdown("---")
    st.markdown("### 🏆 Recommended Models")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.markdown("""
        **🌟 FLUX.1-schnell**
        - Highest quality free model
        - Fast generation (15-30s)
        - Great for realistic images
        - Minimal loading time
        """)
    
    with col4:
        st.markdown("""
        **🎨 OpenDalleV1.1** 
        - Excellent for creative art
        - Good fantasy & anime
        - Reliable free access
        - Fast responses
        """)
    
    with col5:
        st.markdown("""
        **🖼️ Stable Diffusion XL**
        - Most stable model
        - Consistent results
        - Good all-rounder
        - Rarely busy
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Hugging Face Free Inference API | Professional Quality Images</p>
    </div>
""", unsafe_allow_html=True)
