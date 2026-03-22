import streamlit as st
from openai import OpenAI
import time

st.set_page_config(
    page_title="RecipeGPT — Minecraft Edition",
    page_icon="🍛",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
:root {
    --black:#0A0A08;--coal:#1C1C1A;--smoke:#2E2E2B;--ash:#4A4A45;--dust:#7A7A72;
    --paper:#F2EDE4;--grass:#5D9E2F;--grass-top:#79C240;--gold:#FFD700;
    --diamond:#4DD9E0;--creeper:#4CAF50;--stone:#8B8B8B;--stone-dk:#5A5A5A;--chili:#B83232;
}

/* ── Force dark background everywhere ── */
html, body { background-color: #0A0A08 !important; }

.stApp {
    background-color: #0A0A08 !important;
    background-image:
        repeating-linear-gradient(0deg, transparent, transparent 31px, rgba(255,255,255,0.018) 31px, rgba(255,255,255,0.018) 32px),
        repeating-linear-gradient(90deg, transparent, transparent 31px, rgba(255,255,255,0.018) 31px, rgba(255,255,255,0.018) 32px) !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #0A0A08 !important;
    background-image:
        repeating-linear-gradient(0deg, transparent, transparent 31px, rgba(255,255,255,0.018) 31px, rgba(255,255,255,0.018) 32px),
        repeating-linear-gradient(90deg, transparent, transparent 31px, rgba(255,255,255,0.018) 31px, rgba(255,255,255,0.018) 32px),
        radial-gradient(circle at 15% 15%, rgba(77,217,224,0.05) 0%, transparent 45%),
        radial-gradient(circle at 85% 85%, rgba(93,158,47,0.05) 0%, transparent 45%) !important;
}

[data-testid="stMain"],
[data-testid="block-container"],
.main,
.main .block-container,
[data-testid="stVerticalBlock"],
[class*="css"] {
    background-color: #0A0A08 !important;
}

/* ── Font ── */
html, body, button, input, select, textarea,
[class*="css"], *, *::before, *::after {
    font-family: 'Press Start 2P', monospace !important;
    color: #F2EDE4;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: #1C1C1A !important;
    border-right: 4px solid #2E2E2B !important;
}
[data-testid="stSidebar"] * {
    color: #F2EDE4 !important;
    font-size: 7px !important;
}

/* ── Title ── */
.mc-title {
    font-family: 'Press Start 2P', monospace;
    font-size: 28px; color: #FFD700;
    text-shadow: 4px 4px 0 #000, 6px 6px 0 rgba(0,0,0,0.4);
    text-align: center; margin-bottom: 4px; line-height: 1.4;
}
.mc-sub {
    font-family: 'Press Start 2P', monospace;
    font-size: 8px; color: #4CAF50;
    text-align: center; text-shadow: 2px 2px 0 #000;
    letter-spacing: 2px; margin-bottom: 8px;
}
.mc-by {
    font-family: 'Press Start 2P', monospace;
    font-size: 7px; color: #4A4A45;
    text-align: center; margin-bottom: 24px;
}
.mc-divider {
    height: 4px;
    background: linear-gradient(90deg, transparent, #5D9E2F, #FFD700, #5D9E2F, transparent);
    margin: 16px 0 24px; border: none;
}

/* ── Music Player ── */
.music-player {
    background: #000;
    border: 4px solid #2E2E2B;
    box-shadow: inset -4px -4px 0 #000, inset 4px 4px 0 #444;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}
.music-note {
    font-size: 18px;
    animation: noteBounce 1s infinite;
    display: inline-block;
}
@keyframes noteBounce {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-5px); }
}
.music-info { flex: 1; }
.music-title {
    font-size: 7px; color: #FFD700;
    text-shadow: 1px 1px 0 #000;
    display: block; margin-bottom: 4px;
    font-family: 'Press Start 2P', monospace;
}
.music-artist {
    font-size: 6px; color: #4A4A45;
    display: block;
    font-family: 'Press Start 2P', monospace;
}
.music-bar {
    display: flex; gap: 3px; align-items: flex-end; height: 20px;
}
.music-bar span {
    width: 4px; background: #4CAF50;
    animation: barAnim 0.5s infinite alternate;
    display: inline-block;
}
.music-bar span:nth-child(1) { height: 6px;  animation-delay: 0.0s; }
.music-bar span:nth-child(2) { height: 14px; animation-delay: 0.1s; }
.music-bar span:nth-child(3) { height: 9px;  animation-delay: 0.2s; }
.music-bar span:nth-child(4) { height: 16px; animation-delay: 0.15s; }
.music-bar span:nth-child(5) { height: 6px;  animation-delay: 0.05s; }
@keyframes barAnim {
    from { transform: scaleY(0.3); opacity: 0.5; }
    to   { transform: scaleY(1.0); opacity: 1.0; }
}
.music-bar.paused span { animation-play-state: paused; opacity: 0.3; }

/* ── Inputs ── */
[data-testid="stTextInput"] input {
    font-family: 'Press Start 2P', monospace !important;
    font-size: 8px !important;
    background: #000 !important;
    border: 2px solid #2E2E2B !important;
    color: #F2EDE4 !important;
    border-radius: 0 !important;
    box-shadow: inset 2px 2px 0 #000 !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #FFD700 !important;
}
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label {
    font-family: 'Press Start 2P', monospace !important;
    font-size: 7px !important;
    color: #7A7A72 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* ── Main button ── */
[data-testid="stButton"] button {
    font-family: 'Press Start 2P', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    background: #5D9E2F !important;
    color: #fff !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 14px 28px !important;
    width: 100% !important;
    box-shadow: inset -4px -4px 0 #3D6E1A, inset 4px 4px 0 #79C240, 0 4px 0 #000 !important;
    text-shadow: 2px 2px 0 rgba(0,0,0,0.5) !important;
    transition: filter 0.1s !important;
}
[data-testid="stButton"] button:hover {
    filter: brightness(1.2) !important;
    background: #5D9E2F !important;
}
[data-testid="stButton"] button:active {
    transform: translateY(2px) !important;
    box-shadow: inset -2px -2px 0 #3D6E1A, inset 2px 2px 0 #79C240, 0 2px 0 #000 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #000 !important;
    border: 2px solid #2E2E2B !important;
    border-radius: 0 !important;
    font-family: 'Press Start 2P', monospace !important;
    font-size: 8px !important;
    color: #F2EDE4 !important;
}

/* ── Recipe output box ── */
.recipe-output {
    background: #000;
    border: 4px solid #2E2E2B;
    box-shadow: inset 4px 4px 0 #111, inset -4px -4px 0 #333;
    padding: 24px;
    font-family: 'VT323', monospace;
    font-size: 18px;
    line-height: 1.8;
    color: #F2EDE4;
    white-space: pre-wrap;
    min-height: 200px;
}

/* ── Stat pills ── */
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 10px; }
.stat-pill {
    background: #5A5A5A;
    border: 2px solid #4A4A45;
    box-shadow: inset -2px -2px 0 #000, inset 2px 2px 0 #777;
    padding: 4px 10px;
    font-size: 7px;
    color: #FFD700;
    font-family: 'Press Start 2P', monospace;
}

/* ── Error / warning box ── */
.secrets-box {
    background: rgba(184,50,50,0.15);
    border: 4px solid #B83232;
    box-shadow: inset -4px -4px 0 #000, inset 4px 4px 0 rgba(255,100,100,0.1);
    padding: 20px;
    margin: 20px 0;
}
.secrets-box p {
    font-size: 7px !important;
    color: #ff9999 !important;
    line-height: 2.5 !important;
    margin: 0 !important;
}
.secrets-box code {
    background: #000;
    padding: 2px 6px;
    color: #FFD700;
    font-family: 'Press Start 2P', monospace;
    font-size: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Minecraft Music Player (Web Audio API — no YouTube, no iframes) ───────────
st.markdown("""
<div class="music-player">
    <span class="music-note" id="noteIcon">🎵</span>
    <div class="music-info">
        <span class="music-title" id="songTitle">C418 — Sweden</span>
        <span class="music-artist">MINECRAFT SOUNDTRACK · DICYPR</span>
    </div>
    <div class="music-bar" id="musicBar">
        <span></span><span></span><span></span><span></span><span></span>
    </div>
    <button onclick="toggleMusic()" id="playBtn"
        style="font-family:'Press Start 2P',monospace;font-size:8px;
               background:#1C1C1A;border:2px solid #4A4A45;color:#FFD700;
               padding:6px 12px;cursor:pointer;letter-spacing:1px;
               box-shadow:inset -2px -2px 0 #000,inset 2px 2px 0 #666">
        ▶ PLAY
    </button>
</div>

<script>
var audioCtx     = null;
var isPlaying    = false;
var noteTimeout  = null;
var noteIndex    = 0;

// C418 "Sweden" melody — [frequency Hz, duration seconds]
var melody = [
    [329.63,0.4],[369.99,0.4],[392.00,0.4],[440.00,0.8],
    [392.00,0.4],[369.99,0.4],[329.63,0.8],[261.63,0.4],
    [293.66,0.4],[329.63,0.4],[369.99,0.8],[329.63,0.4],
    [293.66,0.4],[261.63,0.8],[220.00,0.4],[246.94,0.4],
    [261.63,0.4],[293.66,0.8],[329.63,0.4],[369.99,0.4],
    [392.00,0.8],[440.00,0.4],[392.00,0.4],[369.99,0.8],
    [329.63,0.4],[293.66,0.4],[261.63,0.8],[220.00,0.4],
    [246.94,0.4],[261.63,0.4],[293.66,1.2],[0,0.4],
];

function playNote(freq, dur) {
    if (!audioCtx || freq === 0) return;
    var osc  = audioCtx.createOscillator();
    var gain = audioCtx.createGain();
    var rev  = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.0, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.12, audioCtx.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur * 0.9);
    osc.start(audioCtx.currentTime);
    osc.stop(audioCtx.currentTime + dur);
}

function scheduleNext() {
    if (!isPlaying) return;
    var note = melody[noteIndex % melody.length];
    playNote(note[0], note[1]);
    noteIndex++;
    noteTimeout = setTimeout(scheduleNext, note[1] * 1000 + 60);
}

function toggleMusic() {
    var btn  = document.getElementById('playBtn');
    var bar  = document.getElementById('musicBar');
    var icon = document.getElementById('noteIcon');

    if (!isPlaying) {
        try {
            audioCtx  = new (window.AudioContext || window.webkitAudioContext)();
            isPlaying = true;
            noteIndex = 0;
            scheduleNext();
            btn.textContent = '⏸ PAUSE';
            bar.classList.remove('paused');
            icon.style.animationPlayState = 'running';
        } catch(e) {
            btn.textContent = '✗ NO AUDIO';
        }
    } else {
        isPlaying = false;
        if (noteTimeout) clearTimeout(noteTimeout);
        if (audioCtx)    { audioCtx.close(); audioCtx = null; }
        btn.textContent = '▶ PLAY';
        bar.classList.add('paused');
        icon.style.animationPlayState = 'paused';
    }
}
</script>
""", unsafe_allow_html=True)


# ── Get API key ────────────────────────────────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["NVIDIA_API_KEY"]
    except Exception:
        pass
    import os
    return os.environ.get("NVIDIA_API_KEY", "")

api_key = get_api_key()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="mc-title">⚒ RECIPEGPT</div>', unsafe_allow_html=True)
st.markdown('<div class="mc-sub">MINECRAFT EDITION</div>', unsafe_allow_html=True)
st.markdown('<div class="mc-by">BY DICYPR · AI RECIPE ENGINE</div>', unsafe_allow_html=True)
st.markdown('<hr class="mc-divider">', unsafe_allow_html=True)

# ── No API key warning ─────────────────────────────────────────────────────────
if not api_key:
    st.markdown("""
    <div class="secrets-box">
    <p>⚠ NO API KEY FOUND<br><br>
    GO TO MANAGE APP → EDIT SECRETS<br>
    AND ADD THIS LINE:<br><br>
    <code>NVIDIA_API_KEY = "nvapi-..."</code>
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧪 CRAFTING TABLE")
    st.markdown("---")
    dish = st.text_input(
        "DISH NAME",
        value="Butter Chicken",
        placeholder="Type any Indian dish..."
    )
    st.markdown("**QUICK PICKS**")
    col1, col2 = st.columns(2)
    picks = [
        ("🍗 Butter Chkn", "Butter Chicken"),
        ("🫘 Dal Makhani",  "Dal Makhani"),
        ("🍚 Biryani",      "Hyderabadi Biryani"),
        ("🥬 Palak Paneer", "Palak Paneer"),
        ("🍮 Gulab Jamun",  "Gulab Jamun"),
        ("🫛 Chole",        "Chole Masala"),
        ("🥩 Rogan Josh",   "Rogan Josh"),
        ("🍶 Kheer",        "Kheer"),
    ]
    for i, (label, val) in enumerate(picks):
        c = col1 if i % 2 == 0 else col2
        if c.button(label, key=f"p{i}", use_container_width=True):
            st.session_state['dish'] = val
    st.markdown("---")
    serves = st.slider("SERVES", 1, 10, 4)
    spice  = st.selectbox("SPICE LEVEL", [
        "🟢 Mild (Easy)",
        "🟡 Medium (Normal)",
        "🔴 Hot (Hard)",
        "💀 Hardcore"
    ])
    diet = st.selectbox("GAME MODE", [
        "🎮 Any",
        "🌿 Vegetarian",
        "☘️ Vegan"
    ])
    detail = st.selectbox("DETAIL", [
        "⚡ Quick",
        "📖 Full Recipe",
        "👨‍🍳 Chef's Edition"
    ])
    st.markdown("---")
    st.markdown("DICYPR AI v2.0")
    st.markdown("NVIDIA NIM ENGINE")

if 'dish' in st.session_state:
    dish = st.session_state['dish']

# ── Dish display ───────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
c1.markdown(
    f'<div style="font-size:7px;color:#7A7A72;letter-spacing:2px;margin-bottom:6px">DISH</div>'
    f'<div style="font-size:14px;color:#FFD700;text-shadow:2px 2px 0 #000;font-family:\'Press Start 2P\',monospace">{dish}</div>',
    unsafe_allow_html=True
)
c2.markdown(
    f'<div style="font-size:7px;color:#7A7A72;letter-spacing:2px;margin-bottom:6px">SERVES</div>'
    f'<div style="font-size:14px;color:#4DD9E0;text-shadow:2px 2px 0 #000;font-family:\'Press Start 2P\',monospace">{serves} PLAYERS</div>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)
generate = st.button("⚒  CRAFT RECIPE", use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

out_ph   = st.empty()
stats_ph = st.empty()

# ── Placeholder ────────────────────────────────────────────────────────────────
if not generate:
    out_ph.markdown("""
    <div class="recipe-output" style="display:flex;align-items:center;justify-content:center;
         flex-direction:column;gap:20px;min-height:320px">
        <div style="font-size:48px">🍳</div>
        <div style="font-size:9px;color:#2E2E2B;text-align:center;line-height:3;
                    font-family:'Press Start 2P',monospace">
            NO RECIPE CRAFTED YET<br>
            SELECT A DISH AND<br>
            PRESS [ CRAFT RECIPE ]
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Generate ───────────────────────────────────────────────────────────────────
if generate:
    spice_map = {
        "🟢 Mild (Easy)":     "mild",
        "🟡 Medium (Normal)": "medium",
        "🔴 Hot (Hard)":      "hot",
        "💀 Hardcore":        "extremely hot and fiery"
    }
    diet_map = {
        "🎮 Any":        "any",
        "🌿 Vegetarian": "strictly vegetarian, no meat or seafood",
        "☘️ Vegan":      "strictly vegan, no dairy, eggs, or meat"
    }
    detail_map = {
        "⚡ Quick":           "Brief recipe — key ingredients and short method only.",
        "📖 Full Recipe":     "Complete recipe with exact quantities and full numbered method and tips.",
        "👨‍🍳 Chef's Edition": "Professional chef level — exact quantities, detailed technique notes, why each step matters, common mistakes to avoid, plating suggestions, and cultural context about the dish."
    }

    system_prompt = """You are RecipeGPT, a world-class expert in authentic Indian cuisine with deep knowledge of every regional tradition from Kashmir to Kerala.
Generate accurate, detailed and inspiring Indian recipes in EXACTLY this structure — do not deviate:

[RECIPE]
NAME: <dish name>
CATEGORY: <cuisine region and type>
SERVES: <number>
PREP TIME: <time>
COOK TIME: <time>

INGREDIENTS:
- <exact quantity> <ingredient>
(list every single ingredient with precise measurements)

METHOD:
1. <detailed step>
2. <detailed step>
(number every step, be specific about technique and timing)

CHEF'S TIPS:
<2-3 professional tips that make a real difference to the final dish>
[/RECIPE]

Be precise with measurements. Use authentic Indian cooking techniques and terminology. Make every recipe inspiring, achievable and delicious."""

    user_prompt = f"""Generate a complete recipe for: {dish}
Serves: {serves} people
Spice level: {spice_map.get(spice, 'medium')}
Dietary requirement: {diet_map.get(diet, 'any')}
{detail_map.get(detail, '')}"""

    # Furnace loading state
    out_ph.markdown("""
    <div class="recipe-output" style="display:flex;align-items:center;justify-content:center;
         flex-direction:column;gap:20px;min-height:320px">
        <div style="font-size:40px;animation:spin 1s linear infinite;display:inline-block">🔥</div>
        <div style="font-size:9px;color:#FFD700;text-align:center;letter-spacing:2px;
                    font-family:'Press Start 2P',monospace;text-shadow:2px 2px 0 #000">
            SMELTING IN FURNACE...
        </div>
    </div>
    <style>@keyframes spin{0%,100%{transform:scale(1)}50%{transform:scale(1.3)}}</style>
    """, unsafe_allow_html=True)

    start     = time.time()
    full_text = ""

    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )

        with client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1200,
            stream=True
        ) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta is not None:
                    full_text += delta
                    elapsed    = time.time() - start
                    out_ph.markdown(
                        f'<div class="recipe-output">{full_text}▌</div>',
                        unsafe_allow_html=True
                    )
                    stats_ph.markdown(
                        f'<div class="stat-row">'
                        f'<span class="stat-pill">⏱ {elapsed:.1f}S</span>'
                        f'<span class="stat-pill">📝 {len(full_text)} CHARS</span>'
                        f'<span class="stat-pill">🔥 STREAMING</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        # Final render
        elapsed = time.time() - start
        out_ph.markdown(
            f'<div class="recipe-output">{full_text}</div>',
            unsafe_allow_html=True
        )
        stats_ph.markdown(
            f'<div class="stat-row">'
            f'<span class="stat-pill">⏱ {elapsed:.1f}S</span>'
            f'<span class="stat-pill">📝 {len(full_text)} CHARS</span>'
            f'<span class="stat-pill" style="color:#79C240">✔ CRAFTED</span>'
            f'<span class="stat-pill">DICYPR ENGINE</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Copy button
        st.code(full_text, language=None)

    except Exception as e:
        out_ph.markdown(
            f'<div class="secrets-box"><p>⚠ ERROR<br><br>{str(e)}</p></div>',
            unsafe_allow_html=True
        )
