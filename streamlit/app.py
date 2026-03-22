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
html,body{background:#0A0A08!important;margin:0;padding:0;}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="block-container"],.main,.main .block-container,
[data-testid="stVerticalBlock"],[class*="css"]{
    background:transparent!important;color:#F2EDE4!important;
}
*,*::before,*::after{font-family:'Press Start 2P',monospace!important;color:#F2EDE4;}
#MainMenu,footer,header{visibility:hidden;}
#mc-bg-canvas{position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;image-rendering:pixelated;}
[data-testid="stSidebar"],section[data-testid="stSidebar"],
section[data-testid="stSidebar"]>div{background:#1C1C1A!important;border-right:4px solid #2E2E2B!important;}
[data-testid="stSidebar"] *{color:#F2EDE4!important;font-size:7px!important;}
.mc-title{font-size:clamp(18px,3vw,28px);color:#FFD700;
    text-shadow:4px 4px 0 #000,6px 6px 0 rgba(0,0,0,0.5);
    text-align:center;margin-bottom:4px;line-height:1.4;display:block;}
.mc-sub{font-size:8px;color:#4CAF50;text-align:center;text-shadow:2px 2px 0 #000;
    letter-spacing:2px;margin-bottom:8px;display:block;}
.mc-by{font-size:7px;color:#4A4A45;text-align:center;margin-bottom:20px;display:block;}
.mc-divider{height:4px;border:none;margin:12px 0 20px;
    background:linear-gradient(90deg,transparent,#5D9E2F,#FFD700,#5D9E2F,transparent);}
.mc-music{background:rgba(0,0,0,0.88);border:4px solid #2E2E2B;
    box-shadow:inset -4px -4px 0 #000,inset 4px 4px 0 #444;
    padding:12px 16px;display:flex;align-items:center;gap:12px;margin-bottom:16px;}
.mc-music-info{flex:1;}
.mc-music-title{font-size:7px;color:#FFD700;display:block;margin-bottom:3px;}
.mc-music-sub{font-size:6px;color:#4A4A45;display:block;}
.eq-bar{display:flex;gap:3px;align-items:flex-end;height:18px;}
.eq-bar span{width:4px;background:#4CAF50;display:inline-block;}
.mc-music-btn{font-family:'Press Start 2P',monospace;font-size:8px;letter-spacing:1px;
    background:#1C1C1A;border:2px solid #4A4A45;color:#FFD700;
    padding:6px 12px;cursor:pointer;box-shadow:inset -2px -2px 0 #000,inset 2px 2px 0 #666;}
.mc-music-btn:hover{background:#2E2E2B;}
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
.recipe-output{background:rgba(0,0,0,0.92);border:4px solid #2E2E2B;
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

# ── Canvas Background + Music Player ─────────────────────────────────────────
st.markdown("""
<canvas id="mc-bg-canvas"></canvas>

<div class="mc-music">
    <span style="font-size:18px" id="mNote">🎵</span>
    <div class="mc-music-info">
        <span class="mc-music-title">C418 — Sweden</span>
        <span class="mc-music-sub">MINECRAFT OST · DICYPR</span>
    </div>
    <div class="eq-bar" id="eqBar">
        <span id="b1" style="height:6px"></span>
        <span id="b2" style="height:12px"></span>
        <span id="b3" style="height:8px"></span>
        <span id="b4" style="height:15px"></span>
        <span id="b5" style="height:5px"></span>
    </div>
    <button class="mc-music-btn" id="mBtn" onclick="toggleMusic()">▶ PLAY</button>
</div>

<script>
// ── CANVAS WORLD ─────────────────────────────────────────────────────────────
(function drawWorld(){
    var cv  = document.getElementById('mc-bg-canvas');
    if(!cv) return;
    var cx  = cv.getContext('2d');
    var B   = 32;
    var seed = 42.7;

    function rnd(arr){ return arr[Math.floor(Math.random()*arr.length)]; }
    function noise(x){
        return Math.sin(x*0.38+seed)*0.5+Math.sin(x*0.81+seed*1.7)*0.3+Math.sin(x*0.19+seed*0.4)*0.2;
    }
    function shade(color, amt){
        var num=parseInt(color.slice(1),16);
        var r=Math.max(0,Math.min(255,(num>>16)+amt));
        var g=Math.max(0,Math.min(255,((num>>8)&0xFF)+amt));
        var b=Math.max(0,Math.min(255,(num&0xFF)+amt));
        return '#'+(r<<16|g<<8|b).toString(16).padStart(6,'0');
    }

    var BLOCKS={
        grass:['#5D9E2F','#63A832','#579429'],
        dirt: ['#866043','#7A5538','#8C6850'],
        stone:['#5A5A5A','#626262','#545454'],
        coal: ['#3A3A3A','#444444','#333333'],
        iron: ['#8C7E6A','#96886F','#857561'],
        gold: ['#C8A42A','#D4B030','#BC9824'],
        diamond:['#2AA8B8','#30B4C0','#26A0B0'],
        wood: ['#7A5518','#6B4A14','#83601C'],
        leaves:['#3D6E1A','#447820','#4A8224'],
        water:['#1A4A8C','#1E5098','#184480'],
        sand: ['#C8B464','#D0BC6C','#C0AC5C'],
    };

    function drawBlock(x,y,type){
        var c=rnd(BLOCKS[type]||BLOCKS.stone);
        cx.fillStyle=c; cx.fillRect(x,y,B,B);
        cx.fillStyle='rgba(0,0,0,0.22)'; cx.fillRect(x+B-3,y,3,B); cx.fillRect(x,y+B-3,B,3);
        cx.fillStyle='rgba(255,255,255,0.09)'; cx.fillRect(x,y,B,3); cx.fillRect(x,y,3,B);
    }

    function drawTree(tx,ty){
        for(var i=0;i<4;i++){
            cx.fillStyle=rnd(BLOCKS.wood);cx.fillRect(tx+B*0.375,ty-i*B,B*0.25,B);
        }
        var lp=[[-1,-4],[0,-4],[1,-4],[-2,-3],[-1,-3],[0,-3],[1,-3],[2,-3],
                [-2,-2],[-1,-2],[0,-2],[1,-2],[2,-2],[-1,-1],[0,-1],[1,-1]];
        lp.forEach(function(p){
            cx.fillStyle=rnd(BLOCKS.leaves);
            cx.fillRect(tx+p[0]*B*0.5,ty+p[1]*B*0.5,B*0.5,B*0.5);
        });
    }

    function drawCreeper(cx2,x,baseY){
        var p=6;
        cx2.fillStyle='#4CAF50'; cx2.fillRect(x-p*3,baseY-p*14,p*6,p*6);
        cx2.fillStyle='#000'; cx2.fillRect(x-p*2,baseY-p*13,p,p); cx2.fillRect(x+p,baseY-p*13,p,p);
        cx2.fillRect(x-p*2,baseY-p*10,p,p); cx2.fillRect(x+p,baseY-p*10,p,p);
        cx2.fillRect(x-p,baseY-p*9,p*2,p);
        cx2.fillStyle='#3D8C3D'; cx2.fillRect(x-p*3,baseY,p*6,p*8);
        cx2.fillStyle='#2E7D32'; cx2.fillRect(x-p*3,baseY,p*2,p*3); cx2.fillRect(x+p,baseY,p*2,p*3);
    }

    function drawTorch(tx,ty){
        cx.fillStyle='#C8A42A'; cx.fillRect(tx-2,ty-10,4,10);
        cx.fillStyle='#FF6600'; cx.fillRect(tx-3,ty-16,6,6);
        cx.fillStyle='#FFCC00'; cx.fillRect(tx-2,ty-18,4,4);
        var g=cx.createRadialGradient(tx,ty-14,2,tx,ty-14,22);
        g.addColorStop(0,'rgba(255,140,0,0.3)'); g.addColorStop(1,'rgba(255,140,0,0)');
        cx.fillStyle=g; cx.fillRect(tx-22,ty-36,44,44);
    }

    function render(){
        var W=cv.width=window.innerWidth;
        var H=cv.height=window.innerHeight;
        var cols=Math.ceil(W/B)+2;
        var rows=Math.ceil(H/B)+2;

        // Night sky gradient
        var sky=cx.createLinearGradient(0,0,0,H*0.65);
        sky.addColorStop(0,'#050D1E'); sky.addColorStop(0.5,'#0D1A35'); sky.addColorStop(1,'#1A2E52');
        cx.fillStyle=sky; cx.fillRect(0,0,W,H);

        // Stars
        for(var s=0;s<220;s++){
            cx.fillStyle='rgba(255,255,255,'+(0.4+Math.random()*0.6)+')';
            cx.fillRect(Math.random()*W,Math.random()*H*0.58,Math.random()<0.3?2:1,Math.random()<0.3?2:1);
        }

        // Moon
        cx.fillStyle='#E8E4CC'; cx.beginPath(); cx.arc(W*0.83,H*0.1,30,0,Math.PI*2); cx.fill();
        cx.fillStyle='#0D1A35'; cx.beginPath(); cx.arc(W*0.83+14,H*0.1-9,24,0,Math.PI*2); cx.fill();

        // Ground heights
        var gy=[];
        for(var c=0;c<cols;c++) gy[c]=Math.floor(rows*0.6+noise(c)*3.5);

        // Terrain blocks
        for(var c=0;c<cols;c++){
            var top=gy[c];
            for(var r=top;r<rows;r++){
                var x2=(c-1)*B, y2=r*B, type;
                if(r===top) type='grass';
                else if(r<=top+2) type='dirt';
                else {
                    var rv=Math.random();
                    type=rv<0.07?'coal':rv<0.04?'iron':rv<0.015?'gold':rv<0.004?'diamond':'stone';
                }
                drawBlock(x2,y2,type);
            }
            // Grass top highlight
            cx.fillStyle='#79C240'; cx.fillRect((c-1)*B,top*B,B,5);
            // Trees
            if(c>2&&c<cols-2&&c%7===3&&Math.random()<0.75)
                drawTree((c-1)*B,top*B);
        }

        // Water
        for(var w=0;w<4;w++){
            var wc=Math.floor(cols*0.1+w*cols*0.25);
            var wy=gy[Math.min(wc,cols-1)]+1;
            for(var wd=0;wd<3;wd++){
                cx.fillStyle=rnd(BLOCKS.water); cx.fillRect((wc+wd-1)*B,wy*B,B,B);
                cx.fillStyle='rgba(80,160,255,0.25)'; cx.fillRect((wc+wd-1)*B,wy*B,B,4);
            }
        }

        // Sand patches
        for(var sp=0;sp<3;sp++){
            var sc=Math.floor(cols*0.2+sp*cols*0.3);
            var sg=gy[Math.min(sc,cols-1)];
            for(var sd=-1;sd<=1;sd++) drawBlock((sc+sd-1)*B,sg*B,'sand');
        }

        // Torches
        for(var t=0;t<6;t++){
            var tc=Math.floor(cols*0.08+t*(cols/6));
            drawTorch((tc-1)*B+B/2,(gy[Math.min(tc,cols-1)]-1)*B);
        }

        // Creepers
        drawCreeper(cx,W*0.2,gy[Math.floor(W*0.2/B)]*B);
        drawCreeper(cx,W*0.65,gy[Math.floor(W*0.65/B)]*B);
        drawCreeper(cx,W*0.88,gy[Math.floor(W*0.88/B)]*B);

        // Overlay to darken and improve readability
        cx.fillStyle='rgba(5,10,20,0.35)'; cx.fillRect(0,0,W,H);
    }

    render();
    window.addEventListener('resize',function(){ setTimeout(render,100); });
})();

// ── MUSIC — Web Audio API ────────────────────────────────────────────────────
var _ac=null,_on=false,_ti=null,_ni=0,_af=null;

var NOTES=[
    [329.63,0.4],[0,0.08],[369.99,0.4],[0,0.08],[392.00,0.4],[0,0.08],
    [440.00,0.85],[0,0.12],[392.00,0.4],[0,0.08],[369.99,0.4],[0,0.08],
    [329.63,0.85],[0,0.12],[261.63,0.4],[0,0.08],[293.66,0.4],[0,0.08],
    [329.63,0.4],[0,0.08],[369.99,0.85],[0,0.12],[329.63,0.4],[0,0.08],
    [293.66,0.4],[0,0.08],[261.63,0.85],[0,0.18],[220.00,0.4],[0,0.08],
    [246.94,0.4],[0,0.08],[261.63,0.4],[0,0.08],[293.66,0.85],[0,0.12],
    [329.63,0.4],[0,0.08],[369.99,0.4],[0,0.08],[392.00,0.85],[0,0.12],
    [440.00,0.4],[0,0.08],[392.00,0.4],[0,0.08],[369.99,0.85],[0,0.18],
    [329.63,0.4],[0,0.08],[293.66,0.4],[0,0.08],[261.63,0.85],[0,0.18],
    [220.00,0.4],[0,0.08],[246.94,0.4],[0,0.08],[261.63,0.4],[0,0.08],
    [293.66,1.3],[0,0.5]
];

function _tone(f,d){
    if(!_ac||f===0)return;
    var o=_ac.createOscillator(),g=_ac.createGain(),n=_ac.currentTime;
    o.connect(g);g.connect(_ac.destination);
    o.type='sine';o.frequency.setValueAtTime(f,n);
    g.gain.setValueAtTime(0,n);
    g.gain.linearRampToValueAtTime(0.14,n+0.025);
    g.gain.exponentialRampToValueAtTime(0.001,n+d*0.88);
    o.start(n);o.stop(n+d);
}

function _eqAnim(){
    if(!_on)return;
    ['b1','b2','b3','b4','b5'].forEach(function(id){
        var el=document.getElementById(id);
        if(el)el.style.height=(3+Math.random()*14)+'px';
    });
    setTimeout(_eqAnim,110);
}

function _stopEQ(){
    [6,12,8,15,5].forEach(function(h,i){
        var el=document.getElementById('b'+(i+1));
        if(el)el.style.height=h+'px';
    });
}

function _next(){
    if(!_on)return;
    var n=NOTES[_ni%NOTES.length];
    _tone(n[0],n[1]);_ni++;
    _ti=setTimeout(_next,n[1]*1000+45);
}

function toggleMusic(){
    var btn=document.getElementById('mBtn');
    var note=document.getElementById('mNote');
    if(!_on){
        try{
            _ac=new(window.AudioContext||window.webkitAudioContext)();
            // iOS unlock
            var b=_ac.createBuffer(1,1,22050),s=_ac.createBufferSource();
            s.buffer=b;s.connect(_ac.destination);s.start(0);
        }catch(e){btn.textContent='✗ NO AUDIO';return;}
        _on=true;_ni=0;_next();_eqAnim();
        btn.textContent='⏸ PAUSE';note.textContent='🎶';
    }else{
        _on=false;
        if(_ti)clearTimeout(_ti);
        if(_ac){_ac.close();_ac=null;}
        _stopEQ();
        btn.textContent='▶ PLAY';note.textContent='🎵';
    }
}
</script>
""", unsafe_allow_html=True)


# ── API Key ────────────────────────────────────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["NVIDIA_API_KEY"]
    except Exception:
        pass
    import os
    return os.environ.get("NVIDIA_API_KEY", "")

api_key = get_api_key()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<span class="mc-title">⚒ RECIPEGPT</span>', unsafe_allow_html=True)
st.markdown('<span class="mc-sub">MINECRAFT EDITION</span>', unsafe_allow_html=True)
st.markdown('<span class="mc-by">BY DICYPR · AI RECIPE ENGINE</span>', unsafe_allow_html=True)
st.markdown('<hr class="mc-divider">', unsafe_allow_html=True)

if not api_key:
    st.markdown("""
    <div class="secrets-box">
    <p>⚠ NO API KEY FOUND<br><br>
    MANAGE APP → EDIT SECRETS<br>
    ADD THIS LINE:<br><br>
    <code>NVIDIA_API_KEY = "nvapi-..."</code>
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧪 CRAFTING TABLE")
    st.markdown("---")
    dish = st.text_input("DISH NAME", value="Butter Chicken", placeholder="Type any Indian dish...")
    st.markdown("**QUICK PICKS**")
    c1,c2 = st.columns(2)
    picks=[
        ("🍗 Butter Chkn","Butter Chicken"),("🫘 Dal Makhani","Dal Makhani"),
        ("🍚 Biryani","Hyderabadi Biryani"),("🥬 Palak Paneer","Palak Paneer"),
        ("🍮 Gulab Jamun","Gulab Jamun"),("🫛 Chole","Chole Masala"),
        ("🥩 Rogan Josh","Rogan Josh"),("🍶 Kheer","Kheer"),
    ]
    for i,(lb,vl) in enumerate(picks):
        cc=c1 if i%2==0 else c2
        if cc.button(lb,key=f"p{i}",use_container_width=True):
            st.session_state['dish']=vl
    st.markdown("---")
    serves=st.slider("SERVES",1,10,4)
    spice=st.selectbox("SPICE LEVEL",["🟢 Mild (Easy)","🟡 Medium (Normal)","🔴 Hot (Hard)","💀 Hardcore"])
    diet=st.selectbox("GAME MODE",["🎮 Any","🌿 Vegetarian","☘️ Vegan"])
    detail=st.selectbox("DETAIL",["⚡ Quick","📖 Full Recipe","👨‍🍳 Chef's Edition"])
    st.markdown("---")
    st.markdown("DICYPR AI v3.0")
    st.markdown("NVIDIA NIM ENGINE")

if 'dish' in st.session_state:
    dish=st.session_state['dish']

dc1,dc2=st.columns(2)
dc1.markdown(f'<div style="font-size:7px;color:#7A7A72;letter-spacing:2px;margin-bottom:6px">DISH</div><div style="font-size:13px;color:#FFD700;text-shadow:2px 2px 0 #000">{dish}</div>',unsafe_allow_html=True)
dc2.markdown(f'<div style="font-size:7px;color:#7A7A72;letter-spacing:2px;margin-bottom:6px">SERVES</div><div style="font-size:13px;color:#4DD9E0;text-shadow:2px 2px 0 #000">{serves} PLAYERS</div>',unsafe_allow_html=True)
st.markdown("<br>",unsafe_allow_html=True)
generate=st.button("⚒  CRAFT RECIPE",use_container_width=True)
st.markdown("<br>",unsafe_allow_html=True)

out_ph=st.empty()
stats_ph=st.empty()

if not generate:
    out_ph.markdown("""
    <div class="recipe-output" style="display:flex;align-items:center;justify-content:center;
    flex-direction:column;gap:20px;min-height:300px">
        <div style="font-size:44px">🍳</div>
        <div style="font-size:9px;color:#2E2E2B;text-align:center;line-height:3">
            NO RECIPE CRAFTED YET<br>SELECT A DISH AND PRESS<br>[ CRAFT RECIPE ]
        </div>
    </div>""",unsafe_allow_html=True)

if generate:
    sm={"🟢 Mild (Easy)":"mild","🟡 Medium (Normal)":"medium","🔴 Hot (Hard)":"hot","💀 Hardcore":"extremely hot"}
    dm={"🎮 Any":"any","🌿 Vegetarian":"strictly vegetarian","☘️ Vegan":"strictly vegan"}
    dtm={
        "⚡ Quick":"Brief recipe with key ingredients and short method only.",
        "📖 Full Recipe":"Complete recipe with exact quantities and full numbered method.",
        "👨‍🍳 Chef's Edition":"Professional chef level with technique notes, mistakes to avoid, and cultural context."
    }

    sys_p="""You are RecipeGPT, an expert in authentic Indian cuisine.
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
[/RECIPE]"""

    usr_p=f"Recipe for: {dish}\nServes: {serves}\nSpice: {sm.get(spice,'medium')}\nDiet: {dm.get(diet,'any')}\n{dtm.get(detail,'')}"

    out_ph.markdown("""
    <div class="recipe-output" style="display:flex;align-items:center;justify-content:center;
    flex-direction:column;gap:20px;min-height:300px">
        <div style="font-size:40px">🔥</div>
        <div style="font-size:9px;color:#FFD700;text-align:center;letter-spacing:2px">
            SMELTING IN FURNACE...
        </div>
    </div>""",unsafe_allow_html=True)

    start=time.time()
    full=""

    try:
        client=OpenAI(base_url="https://integrate.api.nvidia.com/v1",api_key=api_key)
        with client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[{"role":"system","content":sys_p},{"role":"user","content":usr_p}],
            temperature=0.7,top_p=0.9,max_tokens=1200,stream=True
        ) as stream:
            for chunk in stream:
                d=chunk.choices[0].delta.content
                if d:
                    full+=d
                    el=time.time()-start
                    out_ph.markdown(f'<div class="recipe-output">{full}▌</div>',unsafe_allow_html=True)
                    stats_ph.markdown(f'<div class="stat-row"><span class="stat-pill">⏱ {el:.1f}S</span><span class="stat-pill">📝 {len(full)} CHARS</span><span class="stat-pill">🔥 STREAMING</span></div>',unsafe_allow_html=True)

        el=time.time()-start
        out_ph.markdown(f'<div class="recipe-output">{full}</div>',unsafe_allow_html=True)
        stats_ph.markdown(f'<div class="stat-row"><span class="stat-pill">⏱ {el:.1f}S</span><span class="stat-pill">📝 {len(full)} CHARS</span><span class="stat-pill" style="color:#79C240">✔ CRAFTED</span><span class="stat-pill">DICYPR ENGINE</span></div>',unsafe_allow_html=True)
        st.code(full,language=None)

    except Exception as e:
        out_ph.markdown(f'<div class="secrets-box"><p>⚠ ERROR<br><br>{str(e)}</p></div>',unsafe_allow_html=True)
