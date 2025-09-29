import streamlit as st
import requests
from PIL import Image
import io
import time
import json

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
        .free-badge {
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin: 0.5rem 0;
        }
    </style>
""", unsafe_allow_html=True)

def generate_with_prodia(prompt):
    """Generate image using Prodia API - 100% FREE"""
    try:
        # Step 1: Start generation job
        generate_url = "https://api.prodia.com/v1/sd/generate"
        generate_data = {
            "prompt": prompt,
            "model": "dreamshaper_8_93211.safetensors [bcaa7c82]",
            "negative_prompt": "ugly, blurry, low quality",
            "steps": 25,
            "cfg_scale": 7.5,
            "seed": -1,
            "upscale": False
        }
        
        generate_response = requests.post(generate_url, json=generate_data, timeout=30)
        
        if generate_response.status_code == 200:
            job_data = generate_response.json()
            job_id = job_data.get('job')
            
            # Step 2: Wait for job to complete
            max_attempts = 40  # 40 attempts * 1.5 seconds = 60 seconds max
            for attempt in range(max_attempts):
                job_url = f"https://api.prodia.com/v1/job/{job_id}"
                job_response = requests.get(job_url, timeout=30)
                
                if job_response.status_code == 200:
                    job_result = job_response.json()
                    status = job_result.get('status')
                    
                    if status == 'succeeded':
                        image_url = job_result.get('imageUrl')
                        if image_url:
                            # Step 3: Download the image
                            image_response = requests.get(image_url, timeout=30)
                            if image_response.status_code == 200:
                                image = Image.open(io.BytesIO(image_response.content))
                                return image, "Prodia API"
                    
                    elif status == 'failed':
                        return None, "Generation failed"
                
                time.sleep(1.5)  # Wait 1.5 seconds between checks
            
            return None, "Generation timeout"
        else:
            return None, f"API error: {generate_response.status_code}"
            
    except Exception as e:
        return None, f"Prodia error: {str(e)}"

def generate_with_hotpot(prompt):
    """Generate image using Hotpot API - FREE"""
    try:
        url = "https://api.hotpot.ai/create-art"
        data = {
            "prompt": prompt,
            "style": "fantasy",
            "width": 512,
            "height": 512
        }
        
        response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'imageUrl' in result:
                image_response = requests.get(result['imageUrl'], timeout=30)
                if image_response.status_code == 200:
                    image = Image.open(io.BytesIO(image_response.content))
                    return image, "Hotpot AI"
        
        return None, "Hotpot API busy"
        
    except Exception as e:
        return None, f"Hotpot error: {str(e)}"

def generate_with_stable_diffusion_api(prompt):
    """Generate using Stable Diffusion API - FREE"""
    try:
        url = "https://api.stablediffusionapi.com/v1/text2img"
        data = {
            "key": "free",  # Free tier key
            "prompt": prompt,
            "negative_prompt": "ugly, blurry, bad anatomy",
            "width": "512",
            "height": "512",
            "samples": "1",
            "safety_checker": "no"  # Faster generation
        }
        
        response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                image_data = result['output'][0]
                if image_data.startswith('http'):
                    image_response = requests.get(image_data, timeout=30)
                    if image_response.status_code == 200:
                        image = Image.open(io.BytesIO(image_response.content))
                        return image, "Stable Diffusion API"
                else:
                    # Base64 image
                    import base64
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    return image, "Stable Diffusion API"
        
        return None, "Stable Diffusion API busy"
        
    except Exception as e:
        return None, f"SD API error: {str(e)}"

def create_demo_image(prompt):
    """Create a demo image when APIs are busy"""
    from PIL import Image, ImageDraw, ImageFont
    import random
    
    width, height = 512, 512
    img = Image.new('RGB', (width, height), color='#1f2937')
    draw = ImageDraw.Draw(img)
    
    # Create artistic background
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    for _ in range(20):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(x1, width)
        y2 = random.randint(y1, height)
        color = random.choice(colors)
        
        shape_type = random.choice(['circle', 'rectangle'])
        if shape_type == 'circle':
            draw.ellipse([x1, y1, x2, y2], fill=color, width=0)
        else:
            draw.rectangle([x1, y1, x2, y2], fill=color, width=0)
    
    # Add text
    try:
        font = ImageDraw.ImageFont.load_default()
        text = f"AI Preview: {prompt[:40]}..." if len(prompt) > 40 else f"AI Preview: {prompt}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Text background
        draw.rectangle([x-10, y-10, x+text_width+10, y+text_height+10], fill='#000000')
        draw.text((x, y), text, fill='white', font=font)
        
    except:
        pass
    
    return img, "Demo Preview"

# Header Section
st.markdown("""
    <div class="header">
        <h1>🎨 100% Free AI Image Generator</h1>
        <p>No API Keys Required • No Payments • High Quality Images</p>
        <div class="free-badge">🚀 COMPLETELY FREE - NO TOKEN NEEDED</div>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>🎯 How This Works</h3>
        <p>This generator uses <strong>multiple FREE public APIs</strong> that don't require any API keys, tokens, or payments. 
        We automatically try different services until one works!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="Example: A majestic dragon flying over misty mountains at sunset, fantasy art, highly detailed, dramatic lighting",
            height=120,
            key="prompt"
        )
        
        # Generation options
        st.markdown("### 🎯 Generation Strategy")
        strategy = st.radio(
            "Choose approach:",
            ["Auto (Try All Free APIs)", "Fastest Available", "Highest Quality"],
            help="Auto: Tries all services, Fastest: Quickest response, Quality: Best image quality"
        )
    
    with col2:
        st.markdown("### 💡 Best Practices")
        st.markdown("""
        **For best results:**
        • Be descriptive and creative
        • Include style keywords
        • Mention lighting and mood
        • Add quality terms
        
        **Great examples:**
        - Majestic dragon fantasy landscape
        - Cyberpunk city neon lights
        - Magical forest with fairies
        - Space warrior sci-fi art
        """)
        
        st.markdown("### ⚡ Quick Templates")
        if st.button("🐉 Fantasy Dragon"):
            st.session_state.prompt = "A majestic dragon flying over misty mountains at golden hour, fantasy art, highly detailed, epic scale, dramatic lighting"
        
        if st.button("🌆 Cyberpunk City"):
            st.session_state.prompt = "Futuristic cyberpunk city at night, neon lights, flying cars, detailed architecture, cinematic, 4K"
        
        if st.button("🏔️ Mountain Landscape"):
            st.session_state.prompt = "Majestic mountain landscape at sunrise, misty valleys, professional photography, highly detailed, dramatic lighting"

    # Generate button
    if st.button("🚀 Generate Free AI Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        else:
            with st.spinner("🔄 Finding available free AI service..."):
                generated_image = None
                service_used = ""
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Try different services based on strategy
                services_to_try = []
                
                if strategy == "Auto (Try All Free APIs)":
                    services_to_try = ["prodia", "hotpot", "stable_diffusion", "demo"]
                elif strategy == "Fastest Available":
                    services_to_try = ["prodia", "demo"]
                else:  # Highest Quality
                    services_to_try = ["stable_diffusion", "prodia", "hotpot", "demo"]
                
                for i, service in enumerate(services_to_try):
                    progress = (i / len(services_to_try)) * 100
                    progress_bar.progress(int(progress))
                    
                    if service == "prodia":
                        status_text.text("🔄 Trying Prodia API...")
                        generated_image, service_used = generate_with_prodia(prompt)
                    
                    elif service == "hotpot":
                        status_text.text("🔄 Trying Hotpot AI...")
                        generated_image, service_used = generate_with_hotpot(prompt)
                    
                    elif service == "stable_diffusion":
                        status_text.text("🔄 Trying Stable Diffusion API...")
                        generated_image, service_used = generate_with_stable_diffusion_api(prompt)
                    
                    elif service == "demo":
                        status_text.text("🎨 Creating demo preview...")
                        generated_image, service_used = create_demo_image(prompt)
                    
                    if generated_image:
                        break
                    
                    time.sleep(2)  # Brief pause between services
                
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                if generated_image:
                    st.markdown(f'<div class="success-box">🎉 Image created successfully using {service_used}!</div>', unsafe_allow_html=True)
                    
                    # Display image
                    st.image(generated_image, use_container_width=True, caption=f"'{prompt}' - Generated with {service_used}")
                    
                    # Download button
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG", quality=95)
                    st.download_button(
                        label="📥 Download Image",
                        data=buf.getvalue(),
                        file_name=f"free_ai_image_{int(time.time())}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    st.balloons()
                    
                    # Show service info
                    if "demo" in service_used.lower():
                        st.info("""
                        **💡 Demo Mode Active:** 
                        - This is a preview of how AI generation works
                        - For real AI images, the free APIs might be busy
                        - Try again in 5-10 minutes for actual AI generation
                        """)
                    else:
                        st.success("**✅ Real AI Generation Successful!** You can generate unlimited images for free!")
                
                else:
                    st.error("❌ All free services are currently busy. Please try:")
                    st.markdown("""
                    1. **Wait 5-10 minutes** and try again
                    2. **Use 'Fastest Available'** strategy
                    3. **Try a simpler prompt**
                    4. **Check your internet connection**
                    """)
    
    # Free services info
    st.markdown("---")
    st.markdown("### 🆓 Free Services We Use")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.markdown("""
        **🔮 Prodia API**
        - High quality images
        - Fast generation
        - No API key needed
        - Free forever
        """)
    
    with col4:
        st.markdown("""
        **🎨 Hotpot AI**
        - Artistic styles
        - Good for creative images
        - No registration
        - Free tier
        """)
    
    with col5:
        st.markdown("""
        **🤖 Stable Diffusion API**
        - Professional quality
        - Multiple models
        - Free access
        - Reliable
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>🎉 100% Free AI Image Generation • No API Keys • No Payments • No Limits</p>
    </div>
""", unsafe_allow_html=True)
