import streamlit as st
import tempfile
import os
import time
import json

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

# Sidebar
with st.sidebar:
    st.markdown("### 🔑 API Key")
    api_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIza...")
    st.markdown("""<div style='background:rgba(109,40,217,0.1);border:1px solid rgba(109,40,217,0.3);
    border-radius:8px;padding:0.7rem;font-size:0.75rem;color:#a78bfa;'>
    🆓 FREE Key:<br><a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#67e8f9;'>
    aistudio.google.com/app/apikey</a></div>""", unsafe_allow_html=True)
    st.markdown("---")
    num_scenes = st.slider("Max Scenes", 3, 20, 10)
    lang = st.radio("Language:", ["🇬🇧 English", "🇵🇰 Urdu (Roman)", "🇮🇳 Hindi (Roman)"])

# Header
st.markdown('<div class="hero">🎬 Video2Prompts AI Pro</div>', unsafe_allow_html=True)
st.markdown("**Har scene ka Image + Animation + Audio + Video Prompt**")
st.markdown("---")

uploaded = st.file_uploader("📁 Video Upload Karo (2 min se kam)", type=["mp4","mov","avi","mkv","webm"])
if uploaded:
    st.video(uploaded)

st.markdown("<br>", unsafe_allow_html=True)
btn = st.button("🚀 Scenes Detect Karo & Prompts Generate Karo", use_container_width=True)

if btn:
    if not api_key:
        st.error("❌ API Key daalo sidebar mein!")
    elif not uploaded:
        st.error("❌ Video upload karo pehle!")
    else:
        try:
            # Import here to avoid module error at startup
            import importlib
            genai = importlib.import_module("google.generativeai")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            with st.spinner("📤 Video upload ho rahi hai Gemini ko..."):
                ext = uploaded.name.split('.')[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name

                vf = genai.upload_file(path=tmp_path, mime_type=uploaded.type)
                bar = st.progress(0, text="Processing...")
                i = 0
                while vf.state.name == "PROCESSING":
                    time.sleep(2)
                    vf = genai.get_file(vf.name)
                    i = min(i+8, 85)
                    bar.progress(i, text="Video process ho rahi hai...")
                bar.progress(100, text="✅ Ready!")

                if vf.state.name == "FAILED":
                    st.error("❌ Video fail. Dobara try karo.")
                    st.stop()

            if "Urdu" in lang:
                li = "Sab text Roman Urdu mein likho (Urdu ko English huroof mein). Jaise: 'Ek aadmi paani ke paas baitha hai...'"
                ll = "Roman Urdu"
            elif "Hindi" in lang:
                li = "Sab text Roman Hindi mein likho (Hindi ko English huroof mein). Jaise: 'Ek aadmi paani ke paas baitha hai...'"
                ll = "Roman Hindi"
            else:
                li = "Write all text in English."
                ll = "English"

            prompt = f"""Watch this video and detect every scene carefully (even 3-5 second scenes).
{li}
Return ONLY valid JSON (no markdown fences, no extra text):
{{
  "video_title": "title",
  "video_summary": "2 sentence description",
  "aspect_ratio": "e.g. 9:16",
  "scenes": [
    {{
      "scene_number": 1,
      "start_time": "0:00",
      "end_time": "0:06",
      "duration_seconds": 6,
      "scene_description": "what happens visually",
      "image_prompt": "detailed prompt for Midjourney/DALL-E/Stable Diffusion/Firefly/Leonardo/Flux",
      "animation_prompt": "detailed motion prompt for Runway/Kling/Pika/Luma/Haiper with camera movements",
      "audio_prompt": "music/sound prompt for Suno/Udio/ElevenLabs - genre, BPM, instruments, mood",
      "video_prompt": "cinematic video prompt for Sora/Runway/Kling/Pika/Luma/Veo"
    }}
  ]
}}
Detect up to {num_scenes} scenes. JSON only."""

            with st.spinner("🧠 AI scenes analyze kar raha hai..."):
                resp = model.generate_content(
                    [vf, prompt],
                    generation_config={"temperature": 0.3, "max_output_tokens": 8192}
                )

            raw = resp.text.strip()
            # Clean markdown fences if any
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            data = json.loads(raw)
            scenes = data.get("scenes", [])

            st.markdown(f"""<div class='ok-banner'>
            ✅ <b>{data.get('video_title','Done')}!</b> — {len(scenes)} scenes detect hue | 🌐 {ll}<br>
            <span style='color:#94a3b8;font-size:0.85rem;'>{data.get('video_summary','')}</span>
            </div>""", unsafe_allow_html=True)

            # Stats
            c1,c2,c3,c4 = st.columns(4)
            for col, val, lbl in zip(
                [c1,c2,c3,c4],
                [len(scenes), data.get('aspect_ratio','N/A'), len(scenes), len(scenes)],
                ["SCENES","RATIO","IMG PROMPTS","VIDEO PROMPTS"]
            ):
                with col:
                    st.metric(lbl, val)

            st.markdown("---")

            # Scene cards
            for s in scenes:
                st.markdown(f"""<div class='scene-box'>
                <b>🎬 Scene {s.get('scene_number','?')}</b> &nbsp;
                <code>{s.get('start_time','')} → {s.get('end_time','')} ({s.get('duration_seconds','')} sec)</code><br>
                <span style='color:#94a3b8;font-size:0.9rem;'>{s.get('scene_description','')}</span>
                </div>""", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🖼️ IMAGE PROMPT**")
                    st.markdown("`Midjourney · DALL-E · SD · Firefly · Leonardo · Flux`")
                    st.code(s.get("image_prompt",""), language=None)
                    st.markdown("**🔊 AUDIO PROMPT**")
                    st.markdown("`Suno · Udio · ElevenLabs · Musicgen`")
                    st.code(s.get("audio_prompt",""), language=None)
                with col2:
                    st.markdown("**🎬 ANIMATION PROMPT**")
                    st.markdown("`Runway · Kling · Pika · Luma · Haiper`")
                    st.code(s.get("animation_prompt",""), language=None)
                    st.markdown("**📹 VIDEO PROMPT**")
                    st.markdown("`Sora · Runway · Kling · Pika · Luma · Veo`")
                    st.code(s.get("video_prompt",""), language=None)
                st.markdown("---")

            # Download
            out = f"VIDEO2PROMPTS REPORT\n{'='*60}\nTitle: {data.get('video_title','')}\nSummary: {data.get('video_summary','')}\nRatio: {data.get('aspect_ratio','')} | Scenes: {len(scenes)} | Language: {ll}\n{'='*60}\n\n"
            for s in scenes:
                out += f"SCENE {s['scene_number']} [{s.get('start_time','')} -> {s.get('end_time','')}] {s.get('duration_seconds','')} sec\n"
                out += f"Description: {s.get('scene_description','')}\n\n"
                out += f"IMAGE PROMPT:\n{s.get('image_prompt','')}\n\nANIMATION PROMPT:\n{s.get('animation_prompt','')}\n\nAUDIO PROMPT:\n{s.get('audio_prompt','')}\n\nVIDEO PROMPT:\n{s.get('video_prompt','')}\n\n{'-'*60}\n\n"

            d1,d2 = st.columns(2)
            with d1:
                st.download_button("📥 TXT Download", data=out, file_name="prompts.txt", mime="text/plain", use_container_width=True)
            with d2:
                st.download_button("📋 JSON Download", data=json.dumps(data, indent=2, ensure_ascii=False), file_name="prompts.json", mime="application/json", use_container_width=True)

            os.unlink(tmp_path)
            try:
                genai.delete_file(vf.name)
            except:
                pass

        except json.JSONDecodeError as e:
            st.error("❌ JSON parse error. Dobara try karo.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif not uploaded:
    st.markdown("""
    <div style='text-align:center;padding:3rem;background:#10101c;border:2px dashed #252540;border-radius:16px;margin-top:1rem;'>
    <div style='font-size:3rem;'>🎬</div>
    <div style='font-size:1.2rem;font-weight:800;margin:0.8rem 0;'>Video Upload Karo — Sab Automatic Hoga</div>
    <div style='font-size:0.85rem;color:#64748b;line-height:2;'>
    ✅ Har scene detect hoga (3 sec se bhi kam)<br>
    🖼️ Image · 🎬 Animation · 🔊 Audio · 📹 Video Prompts<br>
    MP4 · MOV · AVI · MKV · WebM | 2 min se kam
    </div>
    </div>""", unsafe_allow_html=True)
