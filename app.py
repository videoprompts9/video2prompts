import streamlit as st
import tempfile
import os
import time
import json

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Video2Prompts AI Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; background-color: #080810; color: #e2e8f0; }
.stApp { background: #080810; }
.hero-title { font-size:2.8rem; font-weight:800; background:linear-gradient(135deg,#7c3aed,#06b6d4,#10b981); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero-sub { color:#64748b; font-size:1rem; font-family:'Space Mono',monospace; }
.scene-header { background:linear-gradient(90deg,rgba(109,40,217,0.2),transparent); border-left:4px solid #7c3aed; border-radius:0 10px 10px 0; padding:0.8rem 1.2rem; margin-bottom:1rem; }
.stat-box { background:#10101c; border:1px solid #252540; border-radius:10px; padding:1rem; text-align:center; }
.stat-number { font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#7c3aed,#06b6d4); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.stat-label { font-size:0.75rem; color:#64748b; font-family:'Space Mono',monospace; }
.success-banner { background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:10px; padding:1rem 1.5rem; margin-bottom:1.5rem; }
.stButton > button { background:linear-gradient(135deg,#6d28d9,#0891b2); color:white; border:none; border-radius:8px; font-weight:700; font-size:1rem; width:100%; }
[data-testid="stSidebar"] { background:#10101c; border-right:1px solid #252540; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 API Key")
    api_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIza...")
    st.markdown("""
    <div style='background:rgba(109,40,217,0.1);border:1px solid rgba(109,40,217,0.3);
    border-radius:8px;padding:0.7rem;font-size:0.75rem;font-family:monospace;color:#a78bfa;'>
    🆓 FREE Key yahan se lo:<br>
    <a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#67e8f9;'>
    aistudio.google.com/app/apikey</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    num_scenes = st.slider("Max Scenes", 3, 20, 10)
    prompt_lang = st.radio("Prompts Language:", ["🇬🇧 English", "🇵🇰 Urdu (Roman)", "🇮🇳 Hindi (Roman)"])

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🎬 Video2Prompts AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">// Har scene ka Image + Animation + Audio + Video Prompt</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📁 Video Upload Karo (2 min se kam)", type=["mp4","mov","avi","mkv","webm"])

if uploaded_file:
    st.video(uploaded_file)

st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("🚀 Scenes Detect Karo & Prompts Generate Karo", use_container_width=True)

# ─── Generate ──────────────────────────────────────────────────────────────────
if generate_btn:
    if not api_key:
        st.error("❌ Sidebar mein API Key enter karo!")
    elif not uploaded_file:
        st.error("❌ Pehle video upload karo!")
    else:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            with st.spinner("📤 Video upload ho rahi hai..."):
                suffix = uploaded_file.name.split('.')[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                video_file = genai.upload_file(path=tmp_path, mime_type=uploaded_file.type)
                bar = st.progress(0, text="Processing...")
                step = 0
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                    step = min(step+10, 90)
                    bar.progress(step, text="Video process ho rahi hai...")
                bar.progress(100, text="✅ Ready!")

                if video_file.state.name == "FAILED":
                    st.error("❌ Video fail ho gayi.")
                    st.stop()

            if "Urdu" in prompt_lang:
                lang_instr = "Write ALL text in Roman Urdu (Urdu using English letters). Example: 'Ek aadmi samundar ke kinare khara hai...'"
                lang_label = "🇵🇰 Roman Urdu"
            elif "Hindi" in prompt_lang:
                lang_instr = "Write ALL text in Roman Hindi (Hindi using English letters). Example: 'Ek aadmi samudra ke kinare khada hai...'"
                lang_label = "🇮🇳 Roman Hindi"
            else:
                lang_instr = "Write ALL text in clear English."
                lang_label = "🇬🇧 English"

            prompt = f"""
You are an expert AI prompt engineer. Watch this video carefully and detect every scene (even 3-5 second scenes).

{lang_instr}

Return ONLY valid JSON (no markdown, no extra text):
{{
  "video_title": "title",
  "video_summary": "2 sentence summary",
  "total_scenes": 0,
  "aspect_ratio": "9:16 or 16:9 etc",
  "scenes": [
    {{
      "scene_number": 1,
      "start_time": "0:00",
      "end_time": "0:05",
      "duration_seconds": 5,
      "scene_description": "what happens",
      "image_prompt": "detailed prompt for Midjourney/DALL-E/SD/Firefly/Leonardo/Ideogram/Flux",
      "animation_prompt": "detailed prompt for Runway/Kling/Pika/Luma/Haiper with camera movements",
      "audio_prompt": "music/sound prompt for Suno/Udio/ElevenLabs/Musicgen with genre, BPM, instruments",
      "video_prompt": "full cinematic prompt for Sora/Runway/Kling/Pika/Luma/Veo"
    }}
  ]
}}

Detect up to {num_scenes} scenes. Be thorough.
"""

            with st.spinner("🧠 Gemini scenes analyze kar raha hai..."):
                response = model.generate_content(
                    [video_file, prompt],
                    generation_config={"temperature": 0.3, "max_output_tokens": 8192}
                )

            raw = response.text.strip().replace("```json","").replace("```","").strip()
            data = json.loads(raw)
            scenes = data.get("scenes", [])
            ratio = data.get("aspect_ratio", "N/A")

            st.markdown(f"""
            <div class='success-banner'>
            ✅ <strong>{data.get('video_title','Done')}!</strong><br>
            <span style='font-family:monospace;font-size:0.85rem;color:#94a3b8;'>
            {data.get('video_summary','')} | Language: {lang_label}
            </span>
            </div>""", unsafe_allow_html=True)

            cols = st.columns(5)
            for col, (val, lbl) in zip(cols, [
                (len(scenes),"SCENES"), (ratio,"RATIO"),
                (len(scenes),"IMG"), (len(scenes),"ANIM"), (len(scenes),"AUDIO")
            ]):
                with col:
                    st.markdown(f"<div class='stat-box'><div class='stat-number'>{val}</div><div class='stat-label'>{lbl}</div></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            for scene in scenes:
                sn  = scene.get("scene_number","?")
                st_ = scene.get("start_time","")
                et  = scene.get("end_time","")
                dur = scene.get("duration_seconds","")
                desc= scene.get("scene_description","")

                st.markdown(f"""
                <div class='scene-header'>
                <b style='font-size:1.1rem;'>🎬 Scene {sn}</b><br>
                <span style='font-family:monospace;font-size:0.75rem;color:#a78bfa;'>⏱️ {st_} → {et} | {dur} seconds</span><br>
                <span style='font-size:0.9rem;color:#94a3b8;'>{desc}</span>
                </div>""", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**🖼️ IMAGE PROMPT** `Midjourney · DALL-E · SD · Firefly · Leonardo`")
                    st.code(scene.get("image_prompt",""), language=None)
                    st.markdown("**🔊 AUDIO PROMPT** `Suno · Udio · ElevenLabs · Musicgen`")
                    st.code(scene.get("audio_prompt",""), language=None)
                with c2:
                    st.markdown("**🎬 ANIMATION PROMPT** `Runway · Kling · Pika · Luma · Haiper`")
                    st.code(scene.get("animation_prompt",""), language=None)
                    st.markdown("**📹 VIDEO PROMPT** `Sora · Runway · Kling · Pika · Luma · Veo`")
                    st.code(scene.get("video_prompt",""), language=None)

                st.markdown("---")

            # Download
            out = f"VIDEO2PROMPTS AI PRO\n{'='*60}\n"
            out += f"Title: {data.get('video_title','')}\nSummary: {data.get('video_summary','')}\nRatio: {ratio} | Scenes: {len(scenes)} | Lang: {lang_label}\n{'='*60}\n\n"
            for s in scenes:
                out += f"SCENE {s['scene_number']} [{s.get('start_time','')} -> {s.get('end_time','')}] ({s.get('duration_seconds','')} sec)\n"
                out += f"Description: {s.get('scene_description','')}\n\n"
                out += f"IMAGE PROMPT:\n{s.get('image_prompt','')}\n\nANIMATION PROMPT:\n{s.get('animation_prompt','')}\n\nAUDIO PROMPT:\n{s.get('audio_prompt','')}\n\nVIDEO PROMPT:\n{s.get('video_prompt','')}\n\n{'-'*60}\n\n"

            d1, d2 = st.columns(2)
            with d1:
                st.download_button("📥 TXT Download", data=out, file_name="prompts.txt", mime="text/plain", use_container_width=True)
            with d2:
                st.download_button("📋 JSON Download", data=json.dumps(data, indent=2, ensure_ascii=False), file_name="prompts.json", mime="application/json", use_container_width=True)

            os.unlink(tmp_path)
            try: genai.delete_file(video_file.name)
            except: pass

        except json.JSONDecodeError:
            st.error("❌ Response parse nahi hua. Dobara try karo.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif not uploaded_file:
    st.markdown("""
    <div style='text-align:center;padding:3rem;background:#10101c;border:2px dashed #252540;border-radius:16px;'>
    <div style='font-size:3rem;'>🎬</div>
    <div style='font-size:1.2rem;font-weight:800;margin:1rem 0;'>Video Upload Karo</div>
    <div style='font-family:monospace;font-size:0.82rem;color:#64748b;line-height:2;'>
    ✅ Har scene detect hoga (3 sec se bhi)<br>
    🖼️ Image · 🎬 Animation · 🔊 Audio · 📹 Video Prompts<br>
    MP4 · MOV · AVI · MKV | 2 min se kam
    </div>
    </div>""", unsafe_allow_html=True)
