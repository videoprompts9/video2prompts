import streamlit as st
import tempfile
import os
import time
import json
import base64
import requests

st.set_page_config(page_title="Video2Prompts AI Pro", page_icon="🎬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;800&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif;background:#080810;color:#e2e8f0;}
.stApp{background:#080810;}
.hero{font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#7c3aed,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stButton>button{background:linear-gradient(135deg,#6d28d9,#0891b2);color:white;border:none;border-radius:8px;font-weight:700;font-size:1rem;width:100%;}
[data-testid="stSidebar"]{background:#10101c;}
.scene-box{background:#10101c;border-left:4px solid #7c3aed;border-radius:0 10px 10px 0;padding:0.8rem 1.2rem;margin-bottom:1rem;}
.ok-banner{background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:1rem;margin-bottom:1rem;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔑 Gemini API Key")
    api_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIza...")
    st.markdown("""<div style='background:rgba(109,40,217,0.1);border:1px solid rgba(109,40,217,0.3);
    border-radius:8px;padding:0.7rem;font-size:0.75rem;color:#a78bfa;'>
    🆓 FREE Key yahan se lo:<br>
    <a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#67e8f9;'>
    aistudio.google.com/app/apikey</a>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    num_scenes = st.slider("Max Scenes", 3, 20, 10)
    lang = st.radio("Language:", ["🇬🇧 English", "🇵🇰 Urdu (Roman)", "🇮🇳 Hindi (Roman)"])

st.markdown('<div class="hero">🎬 Video2Prompts AI Pro</div>', unsafe_allow_html=True)
st.markdown("**Har scene ka Image + Animation + Audio + Video Prompt**")
st.markdown("---")

uploaded = st.file_uploader("📁 Video Upload Karo (2 min se kam)", type=["mp4","mov","avi","mkv","webm"])
if uploaded:
    st.video(uploaded)

st.markdown("<br>", unsafe_allow_html=True)
btn = st.button("🚀 Scenes Detect Karo & Prompts Generate Karo", use_container_width=True)

def call_gemini(api_key, video_b64, mime_type, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    body = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": mime_type, "data": video_b64}},
                {"text": prompt}
            ]
        }],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8192}
    }
    resp = requests.post(url, json=body, timeout=120)
    resp.raise_for_status()
    result = resp.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]

if btn:
    if not api_key:
        st.error("❌ API Key daalo sidebar mein!")
    elif not uploaded:
        st.error("❌ Video upload karo pehle!")
    else:
        try:
            if "Urdu" in lang:
                li = "Sab text Roman Urdu mein likho. Jaise: 'Ek aadmi paani ke paas baitha hai...'"
                ll = "Roman Urdu"
            elif "Hindi" in lang:
                li = "Sab text Roman Hindi mein likho. Jaise: 'Ek aadmi paani ke paas baitha hai...'"
                ll = "Roman Hindi"
            else:
                li = "Write all text in English."
                ll = "English"

            prompt = f"""Watch this video and detect every scene (even 3-5 second scenes).
{li}
Return ONLY valid JSON (no markdown, no extra text):
{{
  "video_title": "title",
  "video_summary": "2 sentence description",
  "aspect_ratio": "9:16 or 16:9 etc",
  "scenes": [
    {{
      "scene_number": 1,
      "start_time": "0:00",
      "end_time": "0:06",
      "duration_seconds": 6,
      "scene_description": "what happens",
      "image_prompt": "detailed prompt for Midjourney/DALL-E/SD/Firefly/Leonardo/Flux",
      "animation_prompt": "motion prompt for Runway/Kling/Pika/Luma/Haiper with camera movements",
      "audio_prompt": "music/sound for Suno/Udio/ElevenLabs - genre BPM instruments mood",
      "video_prompt": "cinematic prompt for Sora/Runway/Kling/Pika/Luma/Veo"
    }}
  ]
}}
Detect up to {num_scenes} scenes."""

            with st.spinner("📤 Video process ho rahi hai..."):
                video_bytes = uploaded.read()
                video_b64 = base64.b64encode(video_bytes).decode("utf-8")
                mime = uploaded.type

            with st.spinner("🧠 AI scenes analyze kar raha hai... (1-2 min)"):
                raw = call_gemini(api_key, video_b64, mime, prompt)

            raw = raw.strip()
            if "```" in raw:
                parts = raw.split("```")
                for p in parts:
                    if p.strip().startswith("{") or p.strip().startswith("json"):
                        raw = p.strip()
                        if raw.startswith("json"):
                            raw = raw[4:].strip()
                        break

            data = json.loads(raw)
            scenes = data.get("scenes", [])

            st.markdown(f"""<div class='ok-banner'>
            ✅ <b>{data.get('video_title','Done')}!</b> — {len(scenes)} scenes | 🌐 {ll}<br>
            <span style='color:#94a3b8;'>{data.get('video_summary','')}</span>
            </div>""", unsafe_allow_html=True)

            c1,c2,c3,c4 = st.columns(4)
            for col,val,lbl in zip([c1,c2,c3,c4],
                [len(scenes), data.get('aspect_ratio','N/A'), len(scenes), len(scenes)],
                ["SCENES","RATIO","IMG PROMPTS","VIDEO PROMPTS"]):
                with col:
                    st.metric(lbl, val)

            st.markdown("---")

            for s in scenes:
                st.markdown(f"""<div class='scene-box'>
                <b>🎬 Scene {s.get('scene_number','?')}</b> &nbsp;
                <code>{s.get('start_time','')} → {s.get('end_time','')} ({s.get('duration_seconds','')} sec)</code><br>
                <span style='color:#94a3b8;'>{s.get('scene_description','')}</span>
                </div>""", unsafe_allow_html=True)

                col1,col2 = st.columns(2)
                with col1:
                    st.markdown("**🖼️ IMAGE PROMPT** `Midjourney · DALL-E · SD · Firefly · Leonardo`")
                    st.code(s.get("image_prompt",""), language=None)
                    st.markdown("**🔊 AUDIO PROMPT** `Suno · Udio · ElevenLabs · Musicgen`")
                    st.code(s.get("audio_prompt",""), language=None)
                with col2:
                    st.markdown("**🎬 ANIMATION PROMPT** `Runway · Kling · Pika · Luma · Haiper`")
                    st.code(s.get("animation_prompt",""), language=None)
                    st.markdown("**📹 VIDEO PROMPT** `Sora · Runway · Kling · Pika · Luma · Veo`")
                    st.code(s.get("video_prompt",""), language=None)
                st.markdown("---")

            out = f"VIDEO2PROMPTS REPORT\n{'='*60}\nTitle: {data.get('video_title','')}\nSummary: {data.get('video_summary','')}\nRatio: {data.get('aspect_ratio','')} | Scenes: {len(scenes)} | Language: {ll}\n{'='*60}\n\n"
            for s in scenes:
                out += f"SCENE {s['scene_number']} [{s.get('start_time','')} -> {s.get('end_time','')}] {s.get('duration_seconds','')} sec\n"
                out += f"Description: {s.get('scene_description','')}\n\nIMAGE PROMPT:\n{s.get('image_prompt','')}\n\nANIMATION PROMPT:\n{s.get('animation_prompt','')}\n\nAUDIO PROMPT:\n{s.get('audio_prompt','')}\n\nVIDEO PROMPT:\n{s.get('video_prompt','')}\n\n{'-'*60}\n\n"

            d1,d2 = st.columns(2)
            with d1:
                st.download_button("📥 TXT Download", data=out, file_name="prompts.txt", mime="text/plain", use_container_width=True)
            with d2:
                st.download_button("📋 JSON Download", data=json.dumps(data, indent=2, ensure_ascii=False), file_name="prompts.json", mime="application/json", use_container_width=True)

        except json.JSONDecodeError:
            st.error("❌ Response parse nahi hua. Dobara try karo.")
        except requests.exceptions.HTTPError as e:
            if "400" in str(e):
                st.error("❌ API Key galat hai ya video bahut bari hai!")
            elif "403" in str(e):
                st.error("❌ API Key sahi nahi — dobara check karo!")
            else:
                st.error(f"❌ API Error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif not uploaded:
    st.markdown("""
    <div style='text-align:center;padding:3rem;background:#10101c;border:2px dashed #252540;border-radius:16px;margin-top:1rem;'>
    <div style='font-size:3rem;'>🎬</div>
    <div style='font-size:1.2rem;font-weight:800;margin:0.8rem 0;'>Video Upload Karo</div>
    <div style='font-size:0.85rem;color:#64748b;line-height:2;'>
    ✅ Har scene detect hoga (3 sec se bhi)<br>
    🖼️ Image · 🎬 Animation · 🔊 Audio · 📹 Video Prompts<br>
    MP4 · MOV · AVI · MKV | 2 min se kam
    </div>
    </div>""", unsafe_allow_html=True)
