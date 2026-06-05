import streamlit as st
import json
import requests

st.set_page_config(page_title="B-Roll Director AI", page_icon="🎬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*{font-family:'Inter',sans-serif;}
html,body,[class*="css"]{background:#0f0f0f !important;color:#f0f0f0;}
.stApp{background:#0f0f0f !important;}
[data-testid="stSidebar"]{background:#1a1a1a !important;border-right:1px solid #2a2a2a;}
.stButton>button{background:#2563eb !important;color:white !important;border:none !important;border-radius:8px !important;font-weight:600 !important;width:100% !important;}
.stButton>button:hover{background:#1d4ed8 !important;}
.scene-card{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:1.2rem;margin-bottom:1rem;}
.scene-title{font-size:0.9rem;font-weight:600;color:#60a5fa;margin-bottom:0.5rem;}
.prompt-box{background:#0f0f0f;border:1px solid #2a2a2a;border-radius:8px;padding:0.8rem;font-size:0.82rem;color:#d0d0d0;line-height:1.6;margin-bottom:0.6rem;}
.prompt-label{font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;}
.label-img{color:#a78bfa;}
.label-anim{color:#34d399;}
.label-audio{color:#f59e0b;}
.label-video{color:#60a5fa;}
.top-header{display:flex;align-items:center;gap:10px;padding:1rem 0;border-bottom:1px solid #2a2a2a;margin-bottom:1.5rem;}
.header-badge{background:#1e3a5f;color:#60a5fa;font-size:0.72rem;padding:3px 10px;border-radius:20px;font-weight:600;}
.option-box{background:#1a1a1a;border:2px solid #333;border-radius:12px;padding:1rem;margin-bottom:0.8rem;cursor:pointer;}
.option-box.active{border-color:#2563eb;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='top-header'>
<span style='font-size:1.5rem;'>🎬</span>
<span style='font-size:1.3rem;font-weight:700;'>B-Roll Director AI</span>
<span class='header-badge'>Powered by Gemini</span>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1.5])

with left:
    st.markdown("#### VIDEO INPUT")

    # Video input method
    method = st.radio("", ["📁 File Upload", "🔗 YouTube Link", "☁️ Google Drive Link"],
        label_visibility="collapsed")

    video_url = None
    uploaded = None

    if method == "📁 File Upload":
        st.markdown("<div style='color:#f59e0b;font-size:0.8rem;'>⚠️ 20MB se kam video use karo — fast hoga!</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["mp4","mov","avi","mkv","webm"], label_visibility="collapsed")
        if uploaded:
            st.video(uploaded)
            mb = uploaded.size/1024/1024
            if mb > 20:
                st.error(f"❌ File {mb:.1f}MB hai — 20MB se kam rakho!")
                uploaded = None
            else:
                st.success(f"✅ {uploaded.name} — {mb:.1f}MB")

    elif method == "🔗 YouTube Link":
        st.markdown("<div style='color:#aaa;font-size:0.8rem;'>YouTube video ka link paste karo</div>", unsafe_allow_html=True)
        video_url = st.text_input("", placeholder="https://youtube.com/watch?v=...", label_visibility="collapsed")
        if video_url:
            st.markdown(f"<div style='color:#34d399;font-size:0.8rem;'>✅ Link ready!</div>", unsafe_allow_html=True)

    elif method == "☁️ Google Drive Link":
        st.markdown("<div style='color:#aaa;font-size:0.8rem;'>Google Drive video ka shareable link paste karo</div>", unsafe_allow_html=True)
        video_url = st.text_input("", placeholder="https://drive.google.com/file/d/...", label_visibility="collapsed")
        if video_url:
            st.markdown(f"<div style='color:#34d399;font-size:0.8rem;'>✅ Link ready!</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📐 Aspect Ratio**")
    ratio = st.radio("", ["1:1","16:9","9:16","4:3","3:4"], horizontal=True, index=2, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🎨 Visual Style**")
    style = st.selectbox("", ["🎬 Cinematic","🏛️ Ancient Cinematic","📸 Photorealistic","🎨 Artistic","🌆 Modern Urban","🌿 Nature & Landscape"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🌐 Language**")
    lang = st.radio("", ["🇬🇧 English","🇵🇰 Urdu (Roman)","🇮🇳 Hindi (Roman)"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🔑 API Provider**")
    api_provider = st.radio("", ["🔵 Gemini (Google)", "🟠 OpenRouter"], label_visibility="collapsed")

    if "Gemini" in api_provider:
        api_key = st.text_input("", type="password", placeholder="AIza...", label_visibility="collapsed")
        st.markdown("<a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#60a5fa;font-size:0.75rem;'>🆓 Free Gemini key yahan se lo</a>", unsafe_allow_html=True)
    else:
        api_key = st.text_input("", type="password", placeholder="sk-or-v1-...", label_visibility="collapsed")
        st.markdown("<a href='https://openrouter.ai/keys' target='_blank' style='color:#60a5fa;font-size:0.75rem;'>🔑 OpenRouter key yahan se lo</a>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("✨ Analyze Video", use_container_width=True)
    # Store provider for use in right column
    st.session_state["provider"] = api_provider

with right:
    st.markdown("#### SCENE BREAKDOWN")

    if analyze_btn:
        if not api_key:
            st.error("❌ API Key daalo!")
        elif not uploaded and not video_url:
            st.error("❌ Video upload karo ya link daalo!")
        else:
            if "Urdu" in lang:
                li = "Roman Urdu mein likho (Urdu English huroof mein). Jaise: 'Ek aadmi paani ke paas...'"
                ll = "Roman Urdu"
            elif "Hindi" in lang:
                li = "Roman Hindi mein likho"
                ll = "Roman Hindi"
            else:
                li = "Write in English"
                ll = "English"

            style_clean = style.split(" ",1)[1] if " " in style else style

            prompt = f"""Watch this video and detect every scene carefully (even 3-5 second scenes).
Style: {style_clean} | Ratio: {ratio} | {li}

Return ONLY valid JSON (no markdown, no extra text):
{{
  "video_title": "title",
  "scenes": [
    {{
      "scene_number": 1,
      "timestamp": "0:00 - 0:06",
      "duration": "6s",
      "description": "what happens visually",
      "image_prompt": "ultra detailed for Midjourney/DALL-E/SD/Firefly/Leonardo/Flux, {style_clean}, {ratio}",
      "animation_prompt": "for Runway/Kling/Pika/Luma/Haiper, camera movements, {ratio}",
      "audio_prompt": "for Suno/Udio/ElevenLabs/Musicgen, genre BPM mood instruments",
      "video_prompt": "for Sora/Runway/Kling/Pika/Luma/Veo, {ratio}, {style_clean}"
    }}
  ]
}}"""

            try:
                provider = st.session_state.get("provider","🔵 Gemini (Google)")

                if uploaded:
                    import base64
                    progress = st.progress(0, text="📤 Upload ho rahi hai...")
                    video_bytes = uploaded.getvalue()
                    video_b64 = base64.b64encode(video_bytes).decode("utf-8")
                    progress.progress(50, text="🧠 Analyzing...")

                    if "OpenRouter" in provider:
                        # OpenRouter with base64 image support
                        url = "https://openrouter.ai/api/v1/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        }
                        body = {
                            "model": "google/gemini-2.0-flash-exp:free",
                            "messages": [{"role": "user", "content": [
                                {"type": "image_url", "image_url": {"url": f"data:video/mp4;base64,{video_b64}"}},
                                {"type": "text", "text": prompt}
                            ]}],
                            "max_tokens": 8192
                        }
                    else:
                        # Gemini direct
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                        body = {
                            "contents": [{"parts": [
                                {"inline_data": {"mime_type": "video/mp4", "data": video_b64}},
                                {"text": prompt}
                            ]}],
                            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8192}
                        }
                        headers = {"Content-Type": "application/json"}

                    r = requests.post(url, json=body, headers=headers, timeout=180)
                    r.raise_for_status()

                    if "OpenRouter" in provider:
                        raw = r.json()["choices"][0]["message"]["content"]
                    else:
                        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]

                    progress.progress(100, text="✅ Done!")

                else:
                    # URL method
                    with st.spinner("🧠 Analyzing video from link..."):
                        if "OpenRouter" in provider:
                            url = "https://openrouter.ai/api/v1/chat/completions"
                            headers = {
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            }
                            body = {
                                "model": "google/gemini-2.0-flash-exp:free",
                                "messages": [{"role": "user", "content": [
                                    {"type": "text", "text": f"Video URL: {video_url}\n\n{prompt}"}
                                ]}],
                                "max_tokens": 8192
                            }
                            r = requests.post(url, json=body, headers=headers, timeout=120)
                            r.raise_for_status()
                            raw = r.json()["choices"][0]["message"]["content"]
                        else:
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                            body = {
                                "contents": [{"parts": [
                                    {"text": f"Video URL: {video_url}\n\n{prompt}"}
                                ]}],
                                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8192}
                            }
                            r = requests.post(url, json=body, timeout=120)
                            r.raise_for_status()
                            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]

                # Parse JSON
                raw = raw.strip()
                if "```" in raw:
                    parts = raw.split("```")
                    for p in parts:
                        p = p.strip()
                        if p.startswith("json"): p = p[4:].strip()
                        if p.startswith("{"): raw = p; break

                data = json.loads(raw.strip())
                scenes = data.get("scenes", [])
                st.session_state["scenes"] = scenes
                st.session_state["title"] = data.get("video_title","")
                st.session_state["ll"] = ll

            except requests.exceptions.HTTPError as e:
                code = e.response.status_code if hasattr(e,'response') else '?'
                if code == 429:
                    st.error("❌ Too Many Requests — 5 min wait karo ya nayi API key banao!")
                elif code == 403:
                    st.error("❌ API Key galat hai!")
                else:
                    try: msg = e.response.json().get("error",{}).get("message","")
                    except: msg = str(e)
                    st.error(f"❌ Error {code}: {msg}")
            except json.JSONDecodeError:
                st.error("❌ Response parse nahi hua. Dobara try karo.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Show results
    if "scenes" in st.session_state:
        scenes = st.session_state["scenes"]
        title = st.session_state.get("title","")
        ll = st.session_state.get("ll","English")

        st.markdown(f"""<div style='background:#1a1a2e;border:1px solid #2563eb;border-radius:10px;
        padding:0.8rem 1rem;margin-bottom:1rem;'>
        ✅ <b>{title}</b> — {len(scenes)} scenes | 🌐 {ll}</div>""", unsafe_allow_html=True)

        for s in scenes:
            st.markdown(f"""<div class='scene-card'>
            <div class='scene-title'>📍 Scene {s.get('scene_number','?')} | ⏱️ {s.get('timestamp','')} ({s.get('duration','')})</div>
            <div style='color:#aaa;font-size:0.85rem;margin-bottom:0.8rem;'>{s.get('description','')}</div>
            <div class='prompt-label label-img'>🖼️ Image Prompt</div>
            <div class='prompt-box'>{s.get('image_prompt','')}</div>
            <div class='prompt-label label-anim'>🎬 Animation Prompt</div>
            <div class='prompt-box'>{s.get('animation_prompt','')}</div>
            <div class='prompt-label label-audio'>🔊 Audio Prompt</div>
            <div class='prompt-box'>{s.get('audio_prompt','')}</div>
            <div class='prompt-label label-video'>📹 Video Prompt</div>
            <div class='prompt-box'>{s.get('video_prompt','')}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        out = f"B-ROLL DIRECTOR AI\n{'='*60}\nTitle: {title} | Language: {ll}\n{'='*60}\n\n"
        for s in scenes:
            out += f"SCENE {s['scene_number']} | {s.get('timestamp','')} ({s.get('duration','')})\nDesc: {s.get('description','')}\n\nIMAGE:\n{s.get('image_prompt','')}\n\nANIMATION:\n{s.get('animation_prompt','')}\n\nAUDIO:\n{s.get('audio_prompt','')}\n\nVIDEO:\n{s.get('video_prompt','')}\n\n{'-'*60}\n\n"

        d1,d2 = st.columns(2)
        with d1:
            st.download_button("📥 TXT Download", data=out, file_name="broll.txt", mime="text/plain", use_container_width=True)
        with d2:
            st.download_button("📋 JSON Download", data=json.dumps(scenes, indent=2, ensure_ascii=False), file_name="broll.json", mime="application/json", use_container_width=True)
    else:
        st.markdown("""<div style='background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;
        padding:3rem;text-align:center;color:#444;'>
        <div style='font-size:2rem;margin-bottom:1rem;'>🎬</div>
        <b style='color:#666;'>3 Options:</b><br><br>
        <span style='color:#555;'>📁 File Upload (20MB se kam)</span><br>
        <span style='color:#555;'>🔗 YouTube Link (fastest!)</span><br>
        <span style='color:#555;'>☁️ Google Drive Link</span>
        </div>""", unsafe_allow_html=True)
