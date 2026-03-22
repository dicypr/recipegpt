import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import time
import os
import base64

st.set_page_config(
    page_title="RecipeGPT — Minecraft Edition",
    page_icon="🍛",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
:root{--black:#0A0A08;--coal:#1C1C1A;--smoke:#2E2E2B;--ash:#4A4A45;
--paper:#F2EDE4;--grass:#5D9E2F;--grass-top:#79C240;--gold:#FFD700;
--diamond:#4DD9E0;--creeper:#4CAF50;--stone-dk:#5A5A5A;--chili:#B83232;}
html,body{background:#0A0A08!important;}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="block-container"],.main,.main .block-container,
[data-testid="stVerticalBlock"],[class*="css"]{background:#0A0A08!important;color:#F2EDE4!important;}
*,*::before,*::after{font-family:'Press Start 2P',monospace!important;color:#F2EDE4;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebar"],section[data-testid="stSidebar"],
section[data-testid="stSidebar"]>div{background:#1C1C1A!important;border-right:4px solid #2E2E2B!important;}
[data-testid="stSidebar"] *{color:#F2EDE4!important;font-size:7px!important;}
.mc-title{font-size:clamp(18px,3vw,28px);color:#FFD700;
    text-shadow:4px 4px 0 #000;text-align:center;margin-bottom:4px;line-height:1.4;display:block;}
.mc-sub{font-size:8px;color:#4CAF50;text-align:center;text-shadow:2px 2px 0 #000;
    letter-spacing:2px;margin-bottom:8px;display:block;}
.mc-by{font-size:7px;color:#4A4A45;text-align:center;margin-bottom:20px;display:block;}
.mc-divider{height:4px;border:none;margin:12px 0 20px;
    background:linear-gradient(90deg,transparent,#5D9E2F,#FFD700,#5D9E2F,transparent);}
.mc-music-wrap{background:#000;border:4px solid #2E2E2B;
    box-shadow:inset -4px -4px 0 #000,inset 4px 4px 0 #444;
    padding:12px 16px;margin-bottom:16px;}
.mc-music-label{font-size:7px;color:#FFD700;letter-spacing:2px;
    display:block;margin-bottom:8px;text-shadow:2px 2px 0 #000;}
.mc-music-sub{font-size:6px;color:#4A4A45;display:block;margin-bottom:10px;}
[data-testid="stAudio"] audio{width:100%!important;height:32px!important;
    filter:invert(1) hue-rotate(180deg) saturate(0.8);border-radius:0!important;}
[data-testid="stTextInput"] input{font-size:8px!important;background:#000!important;
    border:2px solid #2E2E2B!important;color:#F2EDE4!important;border-radius:0!important;}
[data-testid="stTextInput"] input:focus{border-color:#FFD700!important;}
[data-testid="stTextInput"] label,[data-testid="stSelectbox"] label,[data-testid="stSlider"] label{
    font-size:7px!important;color:#7A7A72!important;letter-spacing:1px!important;text-transform:uppercase!important;}
[data-testid="stButton"] button{font-size:11px!important;letter-spacing:2px!important;
    background:#5D9E2F!important;color:#fff!important;border:none!important;border-radius:0!important;
    padding:14px!important;width:100%!important;
    box-shadow:inset -4px -4px 0 #3D6E1A,inset 4px 4px 0 #79C240,0 4px 0 #000!important;
    text-shadow:2px 2px 0 rgba(0,0,0,0.5)!important;}
[data-testid="stButton"] button:hover{filter:brightness(1.2)!important;}
[data-testid="stButton"] button:active{transform:translateY(2px)!important;}
[data-testid="stSelectbox"]>div>div{background:#000!important;border:2px solid #2E2E2B!important;
    border-radius:0!important;font-size:8px!important;color:#F2EDE4!important;}
.recipe-output{background:#000;border:4px solid #2E2E2B;
    box-shadow:inset 4px 4px 0 #111,inset -4px -4px 0 #333;
    padding:24px;font-family:'VT323',monospace!important;font-size:18px;line-height:1.8;
    color:#F2EDE4;white-space:pre-wrap;min-height:200px;}
.stat-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;}
.stat-pill{background:#5A5A5A;border:2px solid #4A4A45;
    box-shadow:inset -2px -2px 0 #000,inset 2px 2px 0 #777;
    padding:4px 10px;font-size:7px;color:#FFD700;}
.secrets-box{background:rgba(184,50,50,0.2);border:4px solid #B83232;padding:20px;margin:20px 0;}
.secrets-box p{font-size:7px!important;color:#ff9999!important;line-height:2.5!important;margin:0!important;}
.secrets-box code{background:#000;padding:2px 6px;color:#FFD700;font-size:6px;}
</style>
""", unsafe_allow_html=True)

# ── Minecraft Animated Background using components.html (bypasses sandbox) ────
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background: transparent; overflow: hidden; }
  canvas { display:block; image-rendering: pixelated; }
</style>
</head>
<body>
<canvas id="cv"></canvas>
<script>
var cv = document.getElementById('cv');
var cx = cv.getContext('2d');
var B=32, seed=42.7, frame=0, stars=[], groundY=[], W=0, H=0;

function rnd(a){return a[Math.floor(Math.random()*a.length)];}
function noise(x){return Math.sin(x*0.38+seed)*0.5+Math.sin(x*0.81+seed*1.7)*0.3+Math.sin(x*0.19+seed*0.4)*0.2;}

var BK={
  grass:['#5D9E2F','#63A832'],dirt:['#866043','#7A5538'],
  stone:['#5A5A5A','#626262'],coal:['#3A3A3A','#444'],
  iron:['#8C7E6A','#96886F'],gold:['#C8A42A','#D4B030'],
  diamond:['#2AA8B8','#30B4C0'],wood:['#7A5518','#6B4A14'],
  leaves:['#3D6E1A','#447820'],water:['#1A4A8C','#1E5098']
};

function blk(x,y,t){
  cx.fillStyle=rnd(BK[t]||BK.stone); cx.fillRect(x,y,B,B);
  cx.fillStyle='rgba(0,0,0,0.22)'; cx.fillRect(x+B-3,y,3,B); cx.fillRect(x,y+B-3,B,3);
  cx.fillStyle='rgba(255,255,255,0.09)'; cx.fillRect(x,y,B,3); cx.fillRect(x,y,3,B);
}

function tree(tx,ty){
  for(var i=0;i<4;i++){cx.fillStyle=rnd(BK.wood);cx.fillRect(tx+B*0.375,ty-i*B,B*0.25,B);}
  [[-1,-4],[0,-4],[1,-4],[-2,-3],[-1,-3],[0,-3],[1,-3],[2,-3],
   [-2,-2],[-1,-2],[0,-2],[1,-2],[2,-2],[-1,-1],[0,-1],[1,-1]].forEach(function(p){
    cx.fillStyle=rnd(BK.leaves);cx.fillRect(tx+p[0]*B*0.5,ty+p[1]*B*0.5,B*0.5,B*0.5);});
}

function creeper(x,y){
  var p=7;
  cx.fillStyle='#5DBF5D'; cx.fillRect(x-p*3,y-p*14,p*6,p*6);
  cx.fillStyle='#000';
  cx.fillRect(x-p*2,y-p*13,p,p); cx.fillRect(x+p,y-p*13,p,p);
  cx.fillRect(x-p*2,y-p*10,p,p); cx.fillRect(x+p,y-p*10,p,p);
  cx.fillRect(x-p,y-p*9,p*2,p);
  cx.fillStyle='#4CAF50'; cx.fillRect(x-p*3,y-p*8,p*6,p*8);
  cx.fillStyle='#3D8C3D'; cx.fillRect(x-p*3,y,p*2,p*3); cx.fillRect(x+p,y,p*2,p*3);
}

function torch(tx,ty){
  cx.fillStyle='#C8A42A'; cx.fillRect(tx-2,ty-10,4,10);
  cx.fillStyle='#FF6600'; cx.fillRect(tx-3,ty-16,6,6);
  cx.fillStyle='#FFDD00'; cx.fillRect(tx-2,ty-18,4,4);
  var g=cx.createRadialGradient(tx,ty-14,2,tx,ty-14,26);
  g.addColorStop(0,'rgba(255,140,0,0.4)'); g.addColorStop(1,'rgba(255,140,0,0)');
  cx.fillStyle=g; cx.fillRect(tx-26,ty-40,52,52);
}

function setup(){
  W=cv.width=window.parent.innerWidth;
  H=cv.height=window.parent.innerHeight;
  var cols=Math.ceil(W/B)+2, rows=Math.ceil(H/B)+2;
  groundY=[];
  for(var c=0;c<cols;c++) groundY[c]=Math.floor(rows*0.62+noise(c)*3.5);
  stars=[];
  for(var s=0;s<260;s++) stars.push({
    x:Math.random()*W, y:Math.random()*H*0.52,
    sz:Math.random()<0.3?2:1, ph:Math.random()*10, sp:0.015+Math.random()*0.025
  });
}

function draw(){
  requestAnimationFrame(draw);
  frame++;
  var pw=window.parent.innerWidth, ph=window.parent.innerHeight;
  if(cv.width!==pw||cv.height!==ph) setup();
  if(!W) setup();
  var cols=Math.ceil(W/B)+2, rows=Math.ceil(H/B)+2;

  // Sky
  var sky=cx.createLinearGradient(0,0,0,H*0.65);
  sky.addColorStop(0,'#050D1E'); sky.addColorStop(0.5,'#0D1A35'); sky.addColorStop(1,'#1A2E52');
  cx.fillStyle=sky; cx.fillRect(0,0,W,H);

  // Stars twinkling
  stars.forEach(function(s){
    cx.fillStyle='rgba(255,255,255,'+(0.25+0.75*Math.abs(Math.sin(frame*s.sp+s.ph)))+')';
    cx.fillRect(s.x,s.y,s.sz,s.sz);
  });

  // Moon
  cx.fillStyle='#E8E4CC'; cx.beginPath(); cx.arc(W*0.83,H*0.1,32,0,Math.PI*2); cx.fill();
  cx.fillStyle='#0D1A35'; cx.beginPath(); cx.arc(W*0.83+15,H*0.1-10,26,0,Math.PI*2); cx.fill();
  cx.fillStyle='rgba(0,0,0,0.1)';
  cx.beginPath(); cx.arc(W*0.83-7,H*0.1+5,5,0,Math.PI*2); cx.fill();
  cx.beginPath(); cx.arc(W*0.83+3,H*0.1-3,3,0,Math.PI*2); cx.fill();

  // Terrain
  for(var c=0;c<cols;c++){
    var top=groundY[c]||Math.floor(rows*0.62);
    for(var r=top;r<rows;r++){
      var x2=(c-1)*B, y2=r*B, t;
      if(r===top) t='grass';
      else if(r<=top+2) t='dirt';
      else{var rv=Math.random(); t=rv<0.07?'coal':rv<0.04?'iron':rv<0.015?'gold':rv<0.004?'diamond':'stone';}
      blk(x2,y2,t);
    }
    cx.fillStyle='#79C240'; cx.fillRect((c-1)*B,top*B,B,5);
    if(c>2&&c<cols-2&&c%7===3) tree((c-1)*B,top*B);
  }

  // Water animated
  for(var ww=0;ww<4;ww++){
    var wc=Math.floor(cols*0.1+ww*cols*0.25);
    var wy=(groundY[Math.min(wc,cols-1)]||0)+1;
    for(var wd=0;wd<3;wd++){
      cx.fillStyle='#1A4A8C'; cx.fillRect((wc+wd-1)*B,wy*B,B,B);
      cx.fillStyle='rgba(80,160,255,'+(0.45+0.3*Math.sin(frame*0.06+wd))+')';
      cx.fillRect((wc+wd-1)*B,wy*B,B,4);
    }
  }

  // Torches
  for(var t=0;t<8;t++){
    var tc=Math.floor(cols*0.06+t*(cols/8));
    torch((tc-1)*B+B/2,(groundY[Math.min(tc,cols-1)]||0)*B-B);
  }

  // Creepers
  creeper(W*0.15,(groundY[Math.floor(W*0.15/B)]||0)*B);
  creeper(W*0.55,(groundY[Math.floor(W*0.55/B)]||0)*B);
  creeper(W*0.88,(groundY[Math.floor(W*0.88/B)]||0)*B);

  // Fireflies
  for(var ff=0;ff<10;ff++){
    var ffa=0.25+0.75*Math.abs(Math.sin(frame*0.07+ff*1.8));
    cx.fillStyle='rgba(180,255,120,'+ffa+')';
    cx.fillRect(W*0.04+ff*(W/10.5), H*0.44+Math.sin(frame*0.035+ff*1.3)*25, 3, 3);
  }

  // Dark overlay for readability
  cx.fillStyle='rgba(3,8,18,0.38)'; cx.fillRect(0,0,W,H);
}

setup();
draw();
</script>
</body>
</html>
""", height=0, scrolling=False)

# ── Music ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="mc-music-wrap">
    <span class="mc-music-label">🎵 C418 — SWEDEN</span>
    <span class="mc-music-sub">MINECRAFT SOUNDTRACK · DICYPR</span>
</div>
""", unsafe_allow_html=True)

audio_path = os.path.join(os.path.dirname(__file__), "sweden.mp3")
if os.path.exists(audio_path):
    with open(audio_path, "rb") as f:
        st.audio(f.read(), format="audio/mpeg")
else:
    st.markdown('<div style="font-size:6px;color:#4A4A45;margin-bottom:12px">[ UPLOAD sweden.mp3 TO streamlit/ FOLDER ]</div>', unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["NVIDIA_API_KEY"]
    except Exception:
        pass
    return os.environ.get("NVIDIA_API_KEY", "")

api_key = get_api_key()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<span class="mc-title">⚒ RECIPEGPT</span>', unsafe_allow_html=True)
st.markdown('<span class="mc-sub">MINECRAFT EDITION</span>', unsafe_allow_html=True)
st.markdown('<span class="mc-by">BY DICYPR · AI RECIPE ENGINE</span>', unsafe_allow_html=True)
st.markdown('<hr class="mc-divider">', unsafe_allow_html=True)

if not api_key:
    st.markdown("""
    <div class="secrets-box">
    <p>⚠ NO API KEY FOUND<br><br>
    MANAGE APP → EDIT SECRETS<br>
    ADD:<br><br>
    <code>NVIDIA_API_KEY = "nvapi-..."</code>
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧪 CRAFTING TABLE")
    st.markdown("---")
    dish = st.text_input("DISH NAME", value="Butter Chicken", placeholder="Type any Indian dish...")
    st.markdown("**QUICK PICKS**")
    c1, c2 = st.columns(2)
    picks = [
        ("🍗 Butter Chkn","Butter Chicken"),("🫘 Dal Makhani","Dal Makhani"),
        ("🍚 Biryani","Hyderabadi Biryani"),("🥬 Palak Paneer","Palak Paneer"),
        ("🍮 Gulab Jamun","Gulab Jamun"),("🫛 Chole","Chole Masala"),
        ("🥩 Rogan Josh","Rogan Josh"),("🍶 Kheer","Kheer"),
    ]
    for i,(lb,vl) in enumerate(picks):
        cc = c1 if i%2==0 else c2
        if cc.button(lb, key=f"p{i}", use_container_width=True):
            st.session_state['dish'] = vl
    st.markdown("---")
    serves = st.slider("SERVES", 1, 10, 4)
    spice  = st.selectbox("SPICE LEVEL",["🟢 Mild (Easy)","🟡 Medium (Normal)","🔴 Hot (Hard)","💀 Hardcore"])
    diet   = st.selectbox("GAME MODE",["🎮 Any","🌿 Vegetarian","☘️ Vegan"])
    detail = st.selectbox("DETAIL",["⚡ Quick","📖 Full Recipe","👨‍🍳 Chef's Edition"])
    st.markdown("---")
    st.markdown("DICYPR AI v3.0")
    st.markdown("NVIDIA NIM ENGINE")

if 'dish' in st.session_state:
    dish = st.session_state['dish']

dc1,dc2 = st.columns(2)
dc1.markdown(f'<div style="font-size:7px;color:#7A7A72;letter-spacing:2px;margin-bottom:6px">DISH</div><div style="font-size:13px;color:#FFD700;text-shadow:2px 2px 0 #000">{dish}</div>',unsafe_allow_html=True)
dc2.markdown(f'<div style="font-size:7px;color:#7A7A72;letter-spacing:2px;margin-bottom:6px">SERVES</div><div style="font-size:13px;color:#4DD9E0;text-shadow:2px 2px 0 #000">{serves} PLAYERS</div>',unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
generate = st.button("⚒  CRAFT RECIPE", use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

out_ph   = st.empty()
stats_ph = st.empty()

if not generate:
    out_ph.markdown("""
    <div class="recipe-output" style="display:flex;align-items:center;justify-content:center;
    flex-direction:column;gap:20px;min-height:300px">
        <div style="font-size:44px">🍳</div>
        <div style="font-size:9px;color:#2E2E2B;text-align:center;line-height:3">
            NO RECIPE CRAFTED YET<br>SELECT A DISH AND PRESS<br>[ CRAFT RECIPE ]
        </div>
    </div>""", unsafe_allow_html=True)

if generate:
    sm  = {"🟢 Mild (Easy)":"mild","🟡 Medium (Normal)":"medium","🔴 Hot (Hard)":"hot","💀 Hardcore":"extremely hot"}
    dm  = {"🎮 Any":"any","🌿 Vegetarian":"strictly vegetarian","☘️ Vegan":"strictly vegan"}
    dtm = {"⚡ Quick":"Brief recipe with key ingredients and short method only.",
           "📖 Full Recipe":"Complete recipe with exact quantities and full numbered method.",
           "👨‍🍳 Chef's Edition":"Professional chef level with technique notes, mistakes to avoid, and cultural context."}

    sys_p = """You are RecipeGPT, an expert in authentic Indian cuisine.
Generate recipes in EXACTLY this structure:

[RECIPE]
NAME: <dish name>
CATEGORY: <cuisine type>
SERVES: <number>
PREP TIME: <time>
COOK TIME: <time>

INGREDIENTS:
- <exact quantity> <ingredient>

METHOD:
1. <step>
2. <step>

CHEF'S TIPS:
<2-3 tips>
[/RECIPE]
Be precise. Use authentic Indian techniques."""

    usr_p = f"Recipe for: {dish}\nServes: {serves}\nSpice: {sm.get(spice,'medium')}\nDiet: {dm.get(diet,'any')}\n{dtm.get(detail,'')}"

    out_ph.markdown("""
    <div class="recipe-output" style="display:flex;align-items:center;justify-content:center;
    flex-direction:column;gap:20px;min-height:300px">
        <div style="font-size:40px">🔥</div>
        <div style="font-size:9px;color:#FFD700;text-align:center;letter-spacing:2px">
            SMELTING IN FURNACE...
        </div>
    </div>""", unsafe_allow_html=True)

    start = time.time()
    full  = ""

    try:
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
        with client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[{"role":"system","content":sys_p},{"role":"user","content":usr_p}],
            temperature=0.7, top_p=0.9, max_tokens=1200, stream=True
        ) as stream:
            for chunk in stream:
                d = chunk.choices[0].delta.content
                if d:
                    full += d
                    el = time.time()-start
                    out_ph.markdown(f'<div class="recipe-output">{full}▌</div>',unsafe_allow_html=True)
                    stats_ph.markdown(
                        f'<div class="stat-row">'
                        f'<span class="stat-pill">⏱ {el:.1f}S</span>'
                        f'<span class="stat-pill">📝 {len(full)} CHARS</span>'
                        f'<span class="stat-pill">🔥 STREAMING</span>'
                        f'</div>',unsafe_allow_html=True)

        el = time.time()-start
        out_ph.markdown(f'<div class="recipe-output">{full}</div>',unsafe_allow_html=True)
        stats_ph.markdown(
            f'<div class="stat-row">'
            f'<span class="stat-pill">⏱ {el:.1f}S</span>'
            f'<span class="stat-pill">📝 {len(full)} CHARS</span>'
            f'<span class="stat-pill" style="color:#79C240">✔ CRAFTED</span>'
            f'<span class="stat-pill">DICYPR ENGINE</span>'
            f'</div>',unsafe_allow_html=True)
        st.code(full, language=None)

    except Exception as e:
        out_ph.markdown(f'<div class="secrets-box"><p>⚠ ERROR<br><br>{str(e)}</p></div>',unsafe_allow_html=True)
