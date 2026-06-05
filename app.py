import streamlit as st
from google import generativeai as genai
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

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg: #080810;
    --surface: #10101c;
    --surface2: #16162a;
    --border: #252540;
    --accent: #6d28d9;
    --accent2: #0891b2;
    --accent3: #059669;
    --accent4: #d97706;
    --accent5: #dc2626;
    --text: #e2e8f0;
    --muted: #64748b;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}
.stApp { background: var(--bg); }
h1,h2,h3 { font-family:'Syne',sans-serif; font-weight:800; }

.hero-title {
    font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #06b6d4, #10b981);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.1; margin-bottom: 0.4rem;
}
.hero-sub {
    color: var(--muted); font-size: 1rem;
    font-family: 'Space Mono', monospace; margin-bottom: 1.5rem;
}
.badge {
    display:inline-block;
    background:rgba(124,58,237,0.15); border:1px solid rgba(124,58,237,0.4);
    color:#a78bfa; font-family:'Space Mono',monospace; font-size:0.7rem;
    padding:2px 10px; border-radius:20px; margin-right:6px; margin-bottom:4px;
}
.badge.cyan { background:rgba(6,182,212,0.15); border-color:rgba(6,182,212,0.4); color:#67e8f9; }
.badge.green { background:rgba(16,185,129,0.15); border-color:rgba(16,185,129,0.4); color:#6ee7b7; }
.badge.orange { background:rgba(217,119,6,0.15); border-color:rgba(217,119,6,0.4); color:#fcd34d; }

.scene-header {
    background: linear-gradient(90deg, rgba(109,40,217,0.2), transparent);
    border-left: 4px solid #7c3aed; border-radius: 0 10px 10px 0;
    padding: 0.8rem 1.2rem; margin-bottom: 1rem;
}
.scene-title { font-size: 1.1rem; font-weight: 800; color: #e2e8f0; }
.scene-time {
    font-family:'Space Mono',monospace; font-size:0.75rem;
    color:#a78bfa; margin-top:2px;
}
.scene-desc { font-size:0.9rem; color:#94a3b8; margin-top:0.4rem; }

.prompt-block {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
}
.prompt-label {
    font-family:'Space Mono',monospace; font-size:0.7rem; font-weight:700;
    letter-spacing:2px; text-transform:uppercase; margin-bottom:0.6rem;
    display:flex; align-items:center; gap:8px;
}
.label-img { color:#a78bfa; }
.label-anim { color:#67e8f9; }
.label-audio { color:#6ee7b7; }
.label-video { color:#fcd34d; }

.stat-box {
    background:var(--surface); border:1px solid var(--border);
    border-radius:10px; padding:1rem; text-align:center;
}
.stat-number {
    font-size:1.8rem; font-weight:800;
    background:linear-gradient(135deg,#7c3aed,#06b6d4);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.stat-label { font-size:0.75rem; color:var(--muted); font-family:'Space Mono',monospace; }

.success-banner {
    background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25);
    border-radius:10px; padding:1rem 1.5rem; margin-bottom:1.5rem;
}

div[data-testid="stFileUploader"] {
    background:var(--surface); border:2px dashed var(--border); border-radius:12px; padding:1rem;
}
div[data-testid="stFileUploader"]:hover { border-color:var(--accent); }

.stButton > button {
    background:linear-gradient(135deg,#6d28d9,#0891b2);
    color:white; border:none; border-radius:8px;
    font-family:'Syne',sans-serif; font-weight:700; font-size:1rem;
    padding:0.6rem 2rem; width:100%; transition:opacity 0.2s;
}
.stButton > button:hover { opacity:0.85; }

.stTextInput > div > input {
    background:var(--surface) !important; border:1px solid var(--border) !important;
    color:var(--text) !important; border-radius:8px !important;
    font-family:'Space Mono',monospace !important;
}
.stSelectbox > div > div { background:var(--surface) !important; border-color:var(--border) !important; }
[data-testid="stSidebar"] { background:var(--surface); border-right:1px solid var(--border); }
hr { border-color:var(--border); }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 API Key")
    api_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIza...", help="aistudio.google.com se free key lo")
    st.markdown("""
    <div style='background:rgba(109,40,217,0.1);border:1px solid rgba(109,40,217,0.3);
    border-radius:8px;padding:0.7rem;font-size:0.75rem;font-family:Space Mono,monospace;color:#a78bfa;'>
    🆓 FREE Key yahan se:<br>
    <a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#67e8f9;'>
    aistudio.google.com/app/apikey</a><br><br>
    1. Google se sign in karo<br>
    2. "Create API Key" dabao<br>
    3. Copy karke yahan paste karo
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    num_scenes = st.slider("Max Scenes", min_value=3, max_value=20, value=10,
        help="Video mein kitne scenes dhundne hain")

    st.markdown("#### 🌐 Prompts Language")
    prompt_lang = st.radio("Language:", ["🇬🇧 English", "🇵🇰 Urdu (Roman)", "🇮🇳 Hindi (Roman)"], index=0)

    st.markdown("---")
    st.markdown("""
    <div style='font-family:Space Mono,monospace;font-size:0.72rem;color:#64748b;'>
    ⚡ Gemini 1.5 Flash<br>
    🎯 Scene-by-Scene Detection<br>
    🖼️ Image Prompts (All AI Tools)<br>
    🎬 Animation Prompts<br>
    🔊 Audio/Music Prompts<br>
    📹 Video Prompts (All AI Tools)<br>
    ☁️ Streamlit Cloud (Free)
    </div>
    """, unsafe_allow_html=True)


# ─── Main Header ───────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🎬 Video2Prompts AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">// Video upload karo → Har scene ka Image + Animation + Audio + Video Prompt pao</div>', unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown('<div class="badge">🖼️ Image Prompts</div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="badge cyan">🎬 Animation Prompts</div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="badge green">🔊 Audio Prompts</div>', unsafe_allow_html=True)
with c4: st.markdown('<div class="badge orange">📹 Video Prompts</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Upload ────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📁 Video Upload Karo (2 minutes se kam, koi bhi ratio)",
    type=["mp4", "mov", "avi", "mkv", "webm"],
    help="MP4 · MOV · AVI · MKV · WebM | Max 200MB | 2 min se kam"
)

if uploaded_file:
    st.video(uploaded_file)
    mb = uploaded_file.size / (1024*1024)
    st.markdown(f"""
    <div style='font-family:Space Mono,monospace;font-size:0.8rem;color:#64748b;margin-top:0.4rem;'>
    📄 {uploaded_file.name} &nbsp;|&nbsp; 📦 {mb:.1f} MB
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("🚀 Scenes Detect Karo & Prompts Generate Karo", use_container_width=True)

# ─── Processing ────────────────────────────────────────────────────────────────
if generate_btn:
    if not api_key:
        st.error("❌ Sidebar mein API Key enter karo!")
    elif not uploaded_file:
        st.error("❌ Pehle video upload karo!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            with st.spinner("📤 Video Gemini ko bhej raha hoon..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                video_file = genai.upload_file(path=tmp_path, mime_type=uploaded_file.type)
                progress = st.progress(0, text="Video process ho rahi hai...")
                step = 0
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                    step = min(step + 10, 90)
                    progress.progress(step, text="Video process ho rahi hai...")
                progress.progress(100, text="✅ Video ready!")
                if video_file.state.name == "FAILED":
                    st.error("❌ Video process fail ho gayi. Dobara try karo.")
                    st.stop()

            # Language instruction
            if "Urdu" in prompt_lang:
                lang_instr = "Write ALL text fields in Roman Urdu (Urdu using English letters). Example style: 'Ek aadmi samundar ke kinare khara hai, suraj ghurub ho raha hai...'"
                lang_label = "🇵🇰 Roman Urdu"
            elif "Hindi" in prompt_lang:
                lang_instr = "Write ALL text fields in Roman Hindi (Hindi using English letters). Example style: 'Ek aadmi samudra ke kinare khada hai, suraj doob raha hai...'"
                lang_label = "🇮🇳 Roman Hindi"
            else:
                lang_instr = "Write ALL text fields in clear English."
                lang_label = "🇬🇧 English"

            big_prompt = f"""
You are a world-class AI prompt engineer and video analyst. Carefully watch this entire video and detect every distinct scene — even very short ones (3 seconds, 5 seconds, 8 seconds). Do NOT skip any scene.

For EACH scene provide 4 types of prompts that work with ALL major AI tools:

1. IMAGE_PROMPT: Works with Midjourney, DALL-E 3, Stable Diffusion, Adobe Firefly, Leonardo AI, Ideogram, Flux
2. ANIMATION_PROMPT: Works with Runway Gen-3, Kling AI, Pika Labs, Luma Dream Machine, Haiper
3. AUDIO_PROMPT: Works with Suno AI, Udio, ElevenLabs, Musicgen — describe the exact music/sound/ambience for this scene
4. VIDEO_PROMPT: Works with Sora, Runway, Kling, Pika, Luma, Veo — full cinematic video description

{lang_instr}

Return ONLY valid JSON, no extra text, no markdown fences:
{{
  "video_title": "short catchy title for this video",
  "video_summary": "overall video description in 2 sentences",
  "total_scenes": <number>,
  "aspect_ratio": "detected aspect ratio e.g. 9:16 or 16:9 or 1:1",
  "scenes": [
    {{
      "scene_number": 1,
      "start_time": "0:00",
      "end_time": "0:05",
      "duration_seconds": 5,
      "scene_description": "Exactly what happens visually in this scene",
      "image_prompt": "Ultra detailed image generation prompt. Subject, environment, lighting, mood, style, camera angle, colors, textures. Compatible with Midjourney/DALL-E/SD/Firefly/Leonardo/Ideogram/Flux.",
      "animation_prompt": "Detailed animation prompt. Starting frame, motion description, camera movement (pan/zoom/tilt), speed, transitions, visual effects. Compatible with Runway/Kling/Pika/Luma/Haiper.",
      "audio_prompt": "Detailed audio/music prompt. Genre, instruments, tempo BPM, mood, sound effects, ambience, vocals if any. Compatible with Suno/Udio/ElevenLabs/Musicgen.",
      "video_prompt": "Complete cinematic video prompt. Scene setup, action, camera work, lighting, color grade, lens type, motion, duration. Compatible with Sora/Runway/Kling/Pika/Luma/Veo."
    }}
  ]
}}

Detect up to {num_scenes} scenes. Be thorough — short scenes are important too.
"""

            with st.spinner("🧠 Gemini har scene analyze kar raha hai..."):
                response = model.generate_content(
                    [video_file, big_prompt],
                    generation_config={"temperature": 0.3, "max_output_tokens": 8192}
                )

            raw = response.text.strip().replace("```json","").replace("```","").strip()
            data = json.loads(raw)

            scenes = data.get("scenes", [])
            ratio = data.get("aspect_ratio", "N/A")

            # ─── Summary Banner ────────────────────────────────────────────
            st.markdown(f"""
            <div class='success-banner'>
            ✅ <strong>{data.get('video_title','Analysis Complete')}!</strong><br>
            <span style='font-family:Space Mono,monospace;font-size:0.85rem;color:#94a3b8;'>
            {data.get('video_summary','')}
            </span>
            </div>
            """, unsafe_allow_html=True)

            # Stats
            s1,s2,s3,s4,s5 = st.columns(5)
            stats = [
                (len(scenes), "SCENES"),
                (ratio, "RATIO"),
                (len(scenes), "IMG PROMPTS"),
                (len(scenes), "ANIM PROMPTS"),
                (len(scenes), "AUDIO PROMPTS"),
            ]
            for col, (val, lbl) in zip([s1,s2,s3,s4,s5], stats):
                with col:
                    st.markdown(f"""
                    <div class='stat-box'>
                    <div class='stat-number'>{val}</div>
                    <div class='stat-label'>{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"### 🎞️ {len(scenes)} Scenes Detected — Language: {lang_label}")
            st.markdown("---")

            # ─── Scene Cards ───────────────────────────────────────────────
            for scene in scenes:
                sn   = scene.get("scene_number", "?")
                st_  = scene.get("start_time", "")
                et   = scene.get("end_time", "")
                dur  = scene.get("duration_seconds", "")
                desc = scene.get("scene_description", "")
                ip   = scene.get("image_prompt", "")
                ap   = scene.get("animation_prompt", "")
                aup  = scene.get("audio_prompt", "")
                vp   = scene.get("video_prompt", "")

                st.markdown(f"""
                <div class='scene-header'>
                <div class='scene-title'>🎬 Scene {sn}</div>
                <div class='scene-time'>⏱️ {st_} → {et} &nbsp;|&nbsp; ⏳ {dur} seconds</div>
                <div class='scene-desc'>{desc}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    # Image Prompt
                    st.markdown("""
                    <div class='prompt-block'>
                    <div class='prompt-label label-img'>🖼️ IMAGE PROMPT
                    <span style='color:#64748b;font-size:0.65rem;'>Midjourney · DALL-E · SD · Firefly · Leonardo · Ideogram · Flux</span>
                    </div>
                    </div>""", unsafe_allow_html=True)
                    st.code(ip, language=None)

                    # Audio Prompt
                    st.markdown("""
                    <div class='prompt-block'>
                    <div class='prompt-label label-audio'>🔊 AUDIO / MUSIC PROMPT
                    <span style='color:#64748b;font-size:0.65rem;'>Suno · Udio · ElevenLabs · Musicgen</span>
                    </div>
                    </div>""", unsafe_allow_html=True)
                    st.code(aup, language=None)

                with col2:
                    # Animation Prompt
                    st.markdown("""
                    <div class='prompt-block'>
                    <div class='prompt-label label-anim'>🎬 ANIMATION PROMPT
                    <span style='color:#64748b;font-size:0.65rem;'>Runway · Kling · Pika · Luma · Haiper</span>
                    </div>
                    </div>""", unsafe_allow_html=True)
                    st.code(ap, language=None)

                    # Video Prompt
                    st.markdown("""
                    <div class='prompt-block'>
                    <div class='prompt-label label-video'>📹 VIDEO PROMPT
                    <span style='color:#64748b;font-size:0.65rem;'>Sora · Runway · Kling · Pika · Luma · Veo</span>
                    </div>
                    </div>""", unsafe_allow_html=True)
                    st.code(vp, language=None)

                st.markdown("---")

            # ─── Download ──────────────────────────────────────────────────
            st.markdown("### 💾 Sab Prompts Download Karo")
            out = f"VIDEO2PROMPTS AI PRO — FULL REPORT\n{'='*70}\n"
            out += f"Title: {data.get('video_title','')}\n"
            out += f"Summary: {data.get('video_summary','')}\n"
            out += f"Aspect Ratio: {ratio} | Total Scenes: {len(scenes)} | Language: {lang_label}\n"
            out += f"{'='*70}\n\n"

            for scene in scenes:
                out += f"SCENE {scene['scene_number']}  [{scene.get('start_time','')} → {scene.get('end_time','')}]  ({scene.get('duration_seconds','')} sec)\n"
                out += f"Description: {scene.get('scene_description','')}\n\n"
                out += f"🖼️  IMAGE PROMPT (Midjourney/DALL-E/SD/Firefly/Leonardo/Ideogram/Flux):\n{scene.get('image_prompt','')}\n\n"
                out += f"🎬  ANIMATION PROMPT (Runway/Kling/Pika/Luma/Haiper):\n{scene.get('animation_prompt','')}\n\n"
                out += f"🔊  AUDIO/MUSIC PROMPT (Suno/Udio/ElevenLabs/Musicgen):\n{scene.get('audio_prompt','')}\n\n"
                out += f"📹  VIDEO PROMPT (Sora/Runway/Kling/Pika/Luma/Veo):\n{scene.get('video_prompt','')}\n\n"
                out += f"{'-'*70}\n\n"

            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button("📥 Text File Download (.txt)", data=out,
                    file_name="video2prompts_full.txt", mime="text/plain", use_container_width=True)
            with dl2:
                st.download_button("📋 JSON Download (.json)", data=json.dumps(data, indent=2, ensure_ascii=False),
                    file_name="video2prompts_data.json", mime="application/json", use_container_width=True)

            # Cleanup
            os.unlink(tmp_path)
            try: genai.delete_file(video_file.name)
            except: pass

        except json.JSONDecodeError:
            st.error("❌ Response theek se parse nahi hua. Dobara try karo.")
            with st.expander("Raw Response dekho"):
                st.code(response.text[:1000])
        except Exception as e:
            st.error(f"❌ Error aaya: {str(e)}")
            st.info("💡 Check karo: API key sahi hai? Video 2 min se kam hai? Internet hai?")

elif not uploaded_file:
    st.markdown("""
    <div style='text-align:center;padding:3rem 2rem;background:#10101c;
    border:2px dashed #252540;border-radius:16px;margin-top:1rem;'>
    <div style='font-size:3.5rem;margin-bottom:1rem;'>🎬</div>
    <div style='font-size:1.3rem;font-weight:800;color:#e2e8f0;margin-bottom:0.8rem;'>
    Video Upload Karo — Sab Kuch Automatic Hoga
    </div>
    <div style='font-family:Space Mono,monospace;font-size:0.82rem;color:#64748b;line-height:2;'>
    ✅ Har scene detect hoga (3 sec se lekar koi bhi)<br>
    🖼️ Image Prompt → Midjourney · DALL-E · SD · Firefly · Leonardo<br>
    🎬 Animation Prompt → Runway · Kling · Pika · Luma · Haiper<br>
    🔊 Audio Prompt → Suno · Udio · ElevenLabs · Musicgen<br>
    📹 Video Prompt → Sora · Runway · Kling · Pika · Luma · Veo<br><br>
    MP4 · MOV · AVI · MKV · WebM &nbsp;|&nbsp; 2 min se kam &nbsp;|&nbsp; Koi bhi ratio
    </div>
    </div>
    """, unsafe_allow_html=True)
