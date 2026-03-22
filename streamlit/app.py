import streamlit as st
import anthropic
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
    --paper:#F2EDE4;--grass:#5D9E2F;--grass-top:#79C240;--saffron:#E8971A;
    --gold:#FFD700;--diamond:#4DD9E0;--creeper:#4CAF50;--stone:#8B8B8B;
    --stone-dk:#5A5A5A;--chili:#B83232;
}
html,body,[class*="css"],[data-testid="stAppViewContainer"]{
    font-family:'Press Start 2P',monospace!important;
    background-color:var(--black)!important;color:var(--paper)!important;
}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stAppViewContainer"]{
    background:var(--black);
    background-image:radial-gradient(circle at 20% 20%,rgba(77,217,224,0.03) 0%,transparent 50%),
    radial-gradient(circle at 80% 80%,rgba(93,158,47,0.04) 0%,transparent 50%);
}
.mc-title{font-family:'Press Start 2P',monospace;font-size:28px;color:var(--gold);
    text-shadow:4px 4px 0 #000,6px 6px 0 rgba(0,0,0,0.3);text-align:center;
    margin-bottom:4px;line-height:1.4;}
.mc-sub{font-family:'Press Start 2P',monospace;font-size:8px;color:var(--creeper);
    text-align:center;text-shadow:2px 2px 0 #000;letter-spacing:2px;margin-bottom:8px;}
.mc-by{font-family:'Press Start 2P',monospace;font-size:7px;color:var(--ash);
    text-align:center;margin-bottom:32px;}
.mc-divider{height:4px;background:linear-gradient(90deg,transparent,var(--grass),
    var(--gold),var(--grass),transparent);margin:16px 0 24px;border:none;}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"] select{
    font-family:'Press Start 2P',monospace!important;font-size:8px!important;
    background:#000!important;border:2px solid var(--smoke)!important;
    color:var(--paper)!important;border-radius:0!important;}
[data-testid="stTextInput"] label,[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label{
    font-family:'Press Start 2P',monospace!important;font-size:7px!important;
    color:var(--dust)!important;letter-spacing:1px!important;text-transform:uppercase!important;}
[data-testid="stButton"] button{
    font-family:'Press Start 2P',monospace!important;font-size:11px!important;
    letter-spacing:2px!important;background:var(--grass)!important;color:#fff!important;
    border:none!important;border-radius:0!important;padding:14px 28px!important;
    width:100%!important;
    box-shadow:inset -4px -4px 0 var(--stone-dk),inset 4px 4px 0 var(--grass-top),0 4px 0 #000!important;
    text-shadow:2px 2px 0 rgba(0,0,0,0.5)!important;}
[data-testid="stButton"] button:hover{filter:brightness(1.2)!important;}
[data-testid="stSelectbox"]>div>div{
    background:#000!important;border:2px solid var(--smoke)!important;
    border-radius:0!important;font-family:'Press Start 2P',monospace!important;
    font-size:8px!important;color:var(--paper)!important;}
.recipe-output{background:#000;border:4px solid var(--smoke);
    box-shadow:inset 2px 2px 0 #000,inset -2px -2px 0 #333;
    padding:24px;font-family:'VT323',monospace;font-size:18px;line-height:1.7;
    color:var(--paper);white-space:pre-wrap;min-height:200px;}
.stat-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;}
.stat-pill{background:var(--stone-dk);border:2px solid var(--ash);
    box-shadow:inset -2px -2px 0 #000,inset 2px 2px 0 #666;
    padding:4px 10px;font-size:7px;color:var(--gold);font-family:'Press Start 2P',monospace;}
.secrets-box{background:rgba(184,50,50,0.15);border:4px solid var(--chili);
    box-shadow:inset -4px -4px 0 #000,inset 4px 4px 0 rgba(255,100,100,0.2);
    padding:20px;margin:20px 0;}
.secrets-box p{font-size:7px!important;color:#ff9999!important;
    line-height:2.5!important;margin:0!important;}
.secrets-box code{background:#000;padding:2px 6px;color:var(--gold);
    font-family:'Press Start 2P',monospace;font-size:6px;}
[data-testid="stSidebar"]{background:var(--coal)!important;
    border-right:4px solid var(--smoke)!important;}
[data-testid="stSidebar"] *{font-family:'Press Start 2P',monospace!important;font-size:7px!important;}
</style>
""", unsafe_allow_html=True)

def get_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    import os
    return os.environ.get("ANTHROPIC_API_KEY", "")

api_key = get_api_key()

st.markdown('<div class="mc-title">⚒ RECIPEGPT</div>', unsafe_allow_html=True)
st.markdown('<div class="mc-sub">MINECRAFT EDITION</div>', unsafe_allow_html=True)
st.markdown('<div class="mc-by">BY DICYPR · AI RECIPE ENGINE</div>', unsafe_allow_html=True)
st.markdown('<hr class="mc-divider">', unsafe_allow_html=True)

if not api_key:
    st.markdown("""
    <div class="secrets-box">
    <p>⚠ NO API KEY FOUND<br><br>
    TO DEPLOY ON STREAMLIT CLOUD:<br>
    1. GO TO YOUR APP DASHBOARD<br>
    2. CLICK THE 3 DOTS MENU<br>
    3. CLICK EDIT SECRETS<br>
    4. ADD THIS LINE:<br><br>
    <code>ANTHROPIC_API_KEY = "sk-ant-..."</code><br><br>
    FOR LOCAL DEV, RUN:<br>
    <code>export ANTHROPIC_API_KEY=sk-ant-...</code>
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("### 🧪 CRAFTING TABLE")
    st.markdown("---")
    dish = st.text_input("DISH NAME", value="Butter Chicken", placeholder="Type any Indian dish...")
    st.markdown("**QUICK PICKS**")
    col1, col2 = st.columns(2)
    picks = [
        ("🍗 Butter Chkn", "Butter Chicken"),
        ("🫘 Dal Makhani", "Dal Makhani"),
        ("🍚 Biryani",     "Hyderabadi Biryani"),
        ("🥬 Palak Paneer","Palak Paneer"),
        ("🍮 Gulab Jamun", "Gulab Jamun"),
        ("🫛 Chole",       "Chole Masala"),
        ("🥩 Rogan Josh",  "Rogan Josh"),
        ("🍶 Kheer",       "Kheer"),
    ]
    for i,(label,val) in enumerate(picks):
        c = col1 if i%2==0 else col2
        if c.button(label, key=f"p{i}", use_container_width=True):
            st.session_state['dish'] = val
    st.markdown("---")
    serves = st.slider("SERVES", 1, 10, 4)
    spice  = st.selectbox("SPICE LEVEL", [
        "🟢 Mild (Easy)","🟡 Medium (Normal)","🔴 Hot (Hard)","💀 Hardcore"])
    diet   = st.selectbox("GAME MODE", ["🎮 Any","🌿 Vegetarian","☘️ Vegan"])
    detail = st.selectbox("DETAIL", ["⚡ Quick","📖 Full Recipe","👨‍🍳 Chef's Edition"])
    st.markdown("---")
    st.markdown("DICYPR AI v2.0")

if 'dish' in st.session_state:
    dish = st.session_state['dish']

c1,c2 = st.columns(2)
c1.markdown(f'<div style="font-size:7px;color:#7A7A72;letter-spacing:2px;margin-bottom:4px">DISH</div><div style="font-size:14px;color:#FFD700;text-shadow:2px 2px 0 #000">{dish}</div>', unsafe_allow_html=True)
c2.markdown(f'<div style="font-size:7px;color:#7A7A72;letter-spacing:2px;margin-bottom:4px">SERVES</div><div style="font-size:14px;color:#4DD9E0;text-shadow:2px 2px 0 #000">{serves} PLAYERS</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
generate = st.button("⚒  CRAFT RECIPE", use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

out_ph   = st.empty()
stats_ph = st.empty()

if not generate:
    out_ph.markdown('<div class="recipe-output" style="display:flex;align-items:center;justify-content:center;flex-direction:column;gap:16px;min-height:300px"><div style="font-size:40px">🍳</div><div style="font-size:10px;color:#333;text-align:center;line-height:2.5">NO RECIPE CRAFTED YET<br>SELECT A DISH AND PRESS<br>[ CRAFT RECIPE ]</div></div>', unsafe_allow_html=True)

if generate:
    spice_map  = {"🟢 Mild (Easy)":"mild","🟡 Medium (Normal)":"medium","🔴 Hot (Hard)":"hot","💀 Hardcore":"extra hot and fiery"}
    diet_map   = {"🎮 Any":"any","🌿 Vegetarian":"strictly vegetarian","☘️ Vegan":"strictly vegan, no dairy or meat"}
    detail_map = {
        "⚡ Quick":          "Brief recipe with key ingredients and short method only.",
        "📖 Full Recipe":    "Complete recipe with exact quantities and full numbered method.",
        "👨‍🍳 Chef's Edition": "Professional chef level — exact quantities, technique notes, why each step matters, mistakes to avoid, plating and cultural context."
    }

    system_prompt = """You are RecipeGPT, an expert in authentic Indian cuisine.
Generate accurate, detailed and inspiring Indian recipes in EXACTLY this structure:

[RECIPE]
NAME: <dish name>
CATEGORY: <cuisine region and type>
SERVES: <number>
PREP TIME: <time>
COOK TIME: <time>

INGREDIENTS:
- <exact quantity> <ingredient>

METHOD:
1. <detailed step>
2. <detailed step>

CHEF'S TIPS:
<2-3 professional tips>
[/RECIPE]

Be precise with measurements. Use authentic Indian cooking techniques."""

    user_prompt = f"Recipe for: {dish}\nServes: {serves}\nSpice: {spice_map.get(spice,'medium')}\nDiet: {diet_map.get(diet,'any')}\n{detail_map.get(detail,'')}"

    out_ph.markdown('<div class="recipe-output" style="display:flex;align-items:center;justify-content:center;flex-direction:column;gap:16px;min-height:300px"><div style="font-size:32px">🔥</div><div style="font-size:9px;color:#FFD700;text-align:center;letter-spacing:2px">SMELTING IN FURNACE...</div></div>', unsafe_allow_html=True)

    start     = time.time()
    full_text = ""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
            system=system_prompt,
            messages=[{"role":"user","content":user_prompt}]
        ) as stream:
            for chunk in stream.text_stream:
                full_text += chunk
                elapsed    = time.time()-start
                out_ph.markdown(f'<div class="recipe-output">{full_text}▌</div>', unsafe_allow_html=True)
                stats_ph.markdown(f'<div class="stat-row"><span class="stat-pill">⏱ {elapsed:.1f}S</span><span class="stat-pill">📝 {len(full_text)} CHARS</span><span class="stat-pill">🔥 STREAMING</span></div>', unsafe_allow_html=True)

        elapsed = time.time()-start
        out_ph.markdown(f'<div class="recipe-output">{full_text}</div>', unsafe_allow_html=True)
        stats_ph.markdown(f'<div class="stat-row"><span class="stat-pill">⏱ {elapsed:.1f}S</span><span class="stat-pill">📝 {len(full_text)} CHARS</span><span class="stat-pill" style="color:#79C240">✔ CRAFTED</span><span class="stat-pill">DICYPR ENGINE</span></div>', unsafe_allow_html=True)
        st.code(full_text, language=None)

    except anthropic.AuthenticationError:
        out_ph.markdown('<div class="secrets-box"><p>⚠ INVALID API KEY<br><br>CHECK YOUR KEY IN STREAMLIT SECRETS.</p></div>', unsafe_allow_html=True)
    except Exception as e:
        out_ph.error(f"Error: {str(e)}")
