import streamlit as st
import json
import base64
import requests

st.set_page_config(page_title="B-Roll Director AI", page_icon="🎬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*{font-family:'Inter',sans-serif;}
html,body,[class*="css"]{background:#0f0f0f !important;color:#f0f0f0;}
.stApp{background:#0f0f0f !important;}

/* Sidebar */
[data-testid="stSidebar"]{background:#1a1a1a !important;border-right:1px solid #2a2a2a;}

/* Upload box */
[data-testid="stFileUploader"]{
    background:#1a1a1a !important;
    border:2px dashed #333 !important;
    border-radius:12px !important;
    padding:1rem !important;
}

/* Buttons */
.stButton>button{
    background:#2563eb !important;
    color:white !important;
    border:none !important;
    border-radius:8px !important;
    font-weight:600 !important;
    font-size:0.95rem !important;
    width:100% !important;
    padding:0.6rem !important;
}
.stButton>button:hover{background:#1d4ed8 !important;}

/* Ratio buttons */
.ratio-btn{
    display:inline-block;
    background:#1a1a1a;
    border:2px solid #333;
    border-radius:8px;
    padding:6px 16px;
    font-size:0.85rem;
    color:#aaa;
    cursor:pointer;
    margin-right:8px;
}
.ratio-btn.active{
    background:#2563eb;
    border-color:#2563eb;
    color:white;
}

/* Style buttons */
.style-card{
    background:#1a1a1a;
    border:2px solid #333;
    border-radius:10px;
    padding:0.8rem;
    text-align:center;
    cursor:pointer;
    margin-bottom:0.5rem;
    font-size:0.85rem;
    color:#aaa;
}
.style-card.active{
    border-color:#2563eb;
    color:#60a5fa;
}

/* Scene card */
.scene-card{
    background:#1a1a1a;
    border:1px solid #2a2a2a;
    border-radius:12px;
    padding:1.2rem;
    margin-bottom:1rem;
}
.scene-title{
    font-size:0.9rem;
    font-weight:600;
    color:#60a5fa;
    margin-bottom:0.5rem;
    font-family:monospace;
}
.prompt-box{
    background:#0f0f0f;
    border:1px solid #2a2a2a;
    border-radius:8px;
    padding:0.8rem;
    font-size:0.82rem;
    color:#d0d0d0;
    line-height:1.6;
    margin-bottom:0.6rem;
}
.prompt-label{
    font-size:0.72rem;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:1px;
    margin-bottom:0.3rem;
}
.label-img{color:#a78bfa;}
.label-anim{color:#34d399;}
.label-audio{color:#f59e0b;}
.label-video{color:#60a5fa;}

/* Top header */
.top-header{
    display:flex;
    align-items:center;
    gap:10px;
    padding:1rem 0;
    border-bottom:1px solid #2a2a2a;
    margin-bottom:1.5rem;
}
.header-title{font-size:1.3rem;font-weight:700;color:#f0f0f0;}
.header-badge{
    background:#1e3a5f;
    color:#60a5fa;
    font-size:0.72rem;
    padding:3px 10px;
    border-radius:20px;
    font-weight:600;
}
.analyzing-box{
    background:#1a1a2e;
    border:1px solid #2563eb;
    border-radius:10px;
    padding:1rem;
    text-align:center;
    color:#60a5fa;
    margin:1rem 0;
}
input[type="text"],[data-testid="stTextInput"] input{
    background:#1a1a1a !important;
    border:1px solid #333 !important;
    color:#f0f0f0 !important;
    border-radius:8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────
st.markdown("""
<div class='top-header'>
<span style='font-size:1.5rem;'>🎬</span>
<span class='header-title'>B-Roll Director AI</span>
<span class='header-badge'>Powered by Gemini</span>
</div>
""", unsafe_allow_html=True)

# ── Layout: Left Panel + Right Panel ────────────────────────
left, right = st.columns([1, 1.5])

with left:
    st.markdown("#### UPLOAD VIDEO")
    uploaded = st.file_uploader("", type=["mp4","mov","avi","mkv","webm"],
        label_visibility="collapsed")
    if uploaded:
        st.video(uploaded)
        st.markdown(f"<div style='color:#666;font-size:0.8rem;'>{uploaded.name} — {uploaded.size/1024/1024:.1f} MB</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#1a1a1a;border:2px dashed #333;border-radius:12px;
        padding:2rem;text-align:center;color:#555;font-size:0.85rem;'>
        🎬 Upload a video to reverse-engineer<br>its visual scenes
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Aspect Ratio
    st.markdown("**📐 Aspect Ratio**")
    ratio = st.radio("", ["1:1", "16:9", "9:16", "4:3", "3:4"],
        horizontal=True, index=2, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual Style
    st.markdown("**🎨 Visual Style**")
    style = st.selectbox("", [
        "🎬 Cinematic",
        "🏛️ Ancient Cinematic",
        "📸 Photorealistic",
        "🎨 Artistic",
        "🌆 Modern Urban",
        "🌿 Nature & Landscape"
    ], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    # Language
    st.markdown("**🌐 Language**")
    lang = st.radio("", ["🇬🇧 English", "🇵🇰 Urdu (Roman)", "🇮🇳 Hindi (Roman)"],
        label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    # API Key
    st.markdown("**🔑 API Key**")
    api_key = st.text_input("", type="password", placeholder="AIza... (aistudio.google.com)",
        label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    analyze_btn = st.button("✨ Analyzing...", use_container_width=True)

with right:
    st.markdown("#### SCENE BREAKDOWN")

    if analyze_btn:
        if not api_key:
            st.error("❌ API Key daalo!")
        elif not uploaded:
            st.error("❌ Video upload karo!")
        else:
            # Language
            if "Urdu" in lang:
                li = "Roman Urdu mein likho (Urdu English huroof mein)"
                ll = "Roman Urdu"
            elif "Hindi" in lang:
                li = "Roman Hindi mein likho (Hindi English huroof mein)"
                ll = "Roman Hindi"
            else:
                li = "Write in English"
                ll = "English"

            style_clean = style.split(" ", 1)[1] if " " in style else style

            prompt = f"""Analyze this video. Detect every scene carefully (even 3-5 second scenes).
Style: {style_clean} | Aspect Ratio: {ratio} | {li}

Return ONLY valid JSON:
{{
  "video_title": "title",
  "total_scenes": 0,
  "scenes": [
    {{
      "scene_number": 1,
      "timestamp": "0:00 - 0:06",
      "duration": "6s",
      "description": "what happens visually",
      "image_prompt": "detailed for Midjourney/DALL-E/SD/Firefly/Leonardo/Flux, {style_clean} style, {ratio} ratio",
      "animation_prompt": "motion for Runway/Kling/Pika/Luma/Haiper, camera movements, {ratio}",
      "audio_prompt": "music/sound for Suno/Udio/ElevenLabs, genre BPM mood instruments",
      "video_prompt": "cinematic for Sora/Runway/Kling/Pika/Luma/Veo, {ratio} ratio, {style_clean}"
    }}
  ]
}}"""

            with st.spinner("🧠 Analyzing video scenes..."):
                try:
                    video_b64 = base64.b64encode(uploaded.read()).decode("utf-8")
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                    body = {
                        "contents": [{"parts": [
                            {"inline_data": {"mime_type": uploaded.type, "data": video_b64}},
                            {"text": prompt}
                        ]}],
                        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8192}
                    }
                    r = requests.post(url, json=body, timeout=180)
                    r.raise_for_status()
                    raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    raw = raw.strip()
                    if "```" in raw:
                        parts = raw.split("```")
                        for p in parts:
                            p = p.strip()
                            if p.startswith("json"): p = p[4:].strip()
                            if p.startswith("{"): raw = p; break
                    data = json.loads(raw.strip())
                    scenes = data.get("scenes", [])

                    # Store in session
                    st.session_state["scenes"] = scenes
                    st.session_state["title"] = data.get("video_title", "")
                    st.session_state["ll"] = ll

                except requests.exceptions.HTTPError as e:
                    code = e.response.status_code
                    if code == 429:
                        st.error("❌ Too Many Requests — 5 min wait karo!")
                    elif code == 403:
                        st.error("❌ API Key galat hai!")
                    else:
                        st.error(f"❌ API Error {code}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Display scenes
    if "scenes" in st.session_state:
        scenes = st.session_state["scenes"]
        title = st.session_state.get("title", "")
        ll = st.session_state.get("ll", "English")

        st.markdown(f"""
        <div style='background:#1a1a2e;border:1px solid #2563eb;border-radius:10px;
        padding:0.8rem 1rem;margin-bottom:1rem;'>
        ✅ <b>{title}</b> — {len(scenes)} scenes detected | 🌐 {ll}
        </div>""", unsafe_allow_html=True)

        for s in scenes:
            st.markdown(f"""
            <div class='scene-card'>
            <div class='scene-title'>
            📍 Scene {s.get('scene_number','?')} &nbsp;|&nbsp;
            ⏱️ {s.get('timestamp','')} ({s.get('duration','')})
            </div>
            <div style='color:#aaa;font-size:0.85rem;margin-bottom:0.8rem;'>
            {s.get('description','')}
            </div>

            <div class='prompt-label label-img'>🖼️ Image Prompt</div>
            <div class='prompt-box'>{s.get('image_prompt','')}</div>

            <div class='prompt-label label-anim'>🎬 Animation Prompt</div>
            <div class='prompt-box'>{s.get('animation_prompt','')}</div>

            <div class='prompt-label label-audio'>🔊 Audio Prompt</div>
            <div class='prompt-box'>{s.get('audio_prompt','')}</div>

            <div class='prompt-label label-video'>📹 Video Prompt</div>
            <div class='prompt-box'>{s.get('video_prompt','')}</div>
            </div>
            """, unsafe_allow_html=True)

        # Download
        st.markdown("---")
        out = f"B-ROLL DIRECTOR AI — SCENE BREAKDOWN\n{'='*60}\nTitle: {title} | Language: {ll}\n{'='*60}\n\n"
        for s in scenes:
            out += f"SCENE {s['scene_number']} | {s.get('timestamp','')} ({s.get('duration','')})\n"
            out += f"Description: {s.get('description','')}\n\n"
            out += f"IMAGE:\n{s.get('image_prompt','')}\n\nANIMATION:\n{s.get('animation_prompt','')}\n\nAUDIO:\n{s.get('audio_prompt','')}\n\nVIDEO:\n{s.get('video_prompt','')}\n\n{'-'*60}\n\n"

        d1, d2 = st.columns(2)
        with d1:
            st.download_button("📥 Download TXT", data=out, file_name="broll_scenes.txt", mime="text/plain", use_container_width=True)
        with d2:
            st.download_button("📋 Download JSON", data=json.dumps(st.session_state.get("scenes",[]), indent=2, ensure_ascii=False), file_name="broll_scenes.json", mime="application/json", use_container_width=True)

    else:
        st.markdown("""
        <div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;
        padding:3rem;text-align:center;color:#444;'>
        <div style='font-size:2rem;margin-bottom:1rem;'>🎬</div>
        Upload a video and click Analyze<br>to see scene breakdown here
        </div>""", unsafe_allow_html=True)
