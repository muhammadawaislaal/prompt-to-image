import streamlit as st
import requests
from PIL import Image
import io
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
    </style>
""", unsafe_allow_html=True)

def generate_ai_image(prompt):
    """Generate image using free Hugging Face inference"""
    try:
        # List of free models that work without authentication
        free_models = [
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1", 
            "https://api-inference.huggingface.co/models/prompthero/openjourney-v4",
            "https://api-inference.huggingface.co/models/wavymulder/Analog-Diffusion"
        ]
        
        for model_url in free_models:
            try:
                payload = {
                    "inputs": prompt,
                    "options": {
                        "wait_for_model": True,
                        "use_cache": False
                    }
                }
                
                response = requests.post(model_url, json=payload, timeout=90)
                
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    model_name = model_url.split('/')[-1]
                    return image, f"Generated with {model_name}"
                
                elif response.status_code == 503:
                    # Model is loading, try next one
                    continue
                    
            except Exception:
                # Try next model if this one fails
                continue
        
        return None, "All AI models are currently busy. Please wait 1-2 minutes and try again."
        
    except Exception as e:
        return None, f"Generation error: {str(e)}"

# Header Section
st.markdown("""
    <div class="header">
        <h1>AI Image Generator</h1>
        <p>Create stunning images with AI - Completely Free</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>🚀 Ready to Generate</h3>
        <p>Enter your prompt below to create AI-generated images using free public models.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Create Your Image")
    
    prompt = st.text_area(
        "Enter your prompt:",
        placeholder="A majestic dragon flying over misty mountains at sunset, fantasy art, highly detailed, dramatic lighting",
        height=120,
        key="prompt"
    )

    # Generate button
    if st.button("Generate Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.error("Please enter a prompt to generate an image.")
        else:
            with st.spinner("🔄 Generating your image... This may take 30-60 seconds."):
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Progress steps
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
                
                # Generate image
                generated_image, message = generate_ai_image(prompt)
                
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
                        label="Download Image",
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
                    
                    # Retry suggestion
                    if "busy" in message.lower():
                        st.info("💡 **Tip:** Wait 1-2 minutes and try again. Free AI services can get busy during peak times.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 3rem; padding: 1rem;">
        <p>Powered by Hugging Face AI Models • Free Image Generation</p>
    </div>
""", unsafe_allow_html=True)
