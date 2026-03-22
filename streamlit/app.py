import streamlit as st
import torch
import torch.nn as nn
from torch.nn import functional as F
import time
import os
import requests

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RecipeGPT 🍛",
    page_icon="🍛",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --saffron:   #F4A820;
    --turmeric:  #E8840A;
    --chili:     #C0392B;
    --cardamom:  #2C5F2E;
    --cream:     #FDF6EC;
    --ink:       #1A0E00;
    --smoke:     #6B5B45;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream);
    color: var(--ink);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Hero title */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.1;
    margin-bottom: 0;
}
.hero-sub {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.15rem;
    color: var(--smoke);
    margin-top: 0.3rem;
    margin-bottom: 2rem;
}
.accent { color: var(--saffron); }

/* Divider */
.spice-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.5rem 0;
    color: var(--turmeric);
    font-size: 1.2rem;
    letter-spacing: 6px;
}
.spice-divider::before, .spice-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--saffron), transparent);
}

/* Generate button */
.stButton > button {
    background: linear-gradient(135deg, var(--saffron), var(--turmeric)) !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s ease !important;
    letter-spacing: 0.5px !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Recipe output box */
.recipe-box {
    background: #fff;
    border-left: 4px solid var(--saffron);
    border-radius: 0 12px 12px 0;
    padding: 1.5rem 1.8rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.88rem;
    line-height: 1.75;
    color: var(--ink);
    white-space: pre-wrap;
    box-shadow: 4px 4px 24px rgba(244,168,32,0.08);
    min-height: 120px;
}

/* Slider label */
.slider-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--smoke);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.2rem;
}

/* Stats bar */
.stat-pill {
    display: inline-block;
    background: rgba(244,168,32,0.12);
    border: 1px solid rgba(244,168,32,0.3);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    color: var(--turmeric);
    font-family: 'DM Mono', monospace;
    margin-right: 6px;
}

/* Tip box */
.tip-box {
    background: rgba(44,95,46,0.07);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.82rem;
    color: var(--cardamom);
    border-left: 3px solid var(--cardamom);
}

/* Model status */
.status-ok  { color: var(--cardamom); font-size:0.82rem; }
.status-err { color: var(--chili);    font-size:0.82rem; }

/* Input styling */
.stTextInput > div > div > input {
    border-radius: 8px !important;
    border: 1.5px solid rgba(244,168,32,0.4) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.95rem !important;
    background: #fff !important;
    color: var(--ink) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--saffron) !important;
    box-shadow: 0 0 0 2px rgba(244,168,32,0.15) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Model definition (must match training notebook exactly) ────────────────────
class Head(nn.Module):
    def __init__(self, n_embd, head_size, block_size, dropout):
        super().__init__()
        self.key   = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, C = x.shape
        k, q = self.key(x), self.query(x)
        wei = q @ k.transpose(-2, -1) * k.shape[-1]**-0.5
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = self.dropout(F.softmax(wei, dim=-1))
        return wei @ self.value(x)


class MultiHeadAttention(nn.Module):
    def __init__(self, n_embd, num_heads, head_size, dropout):
        super().__init__()
        self.heads   = nn.ModuleList([Head(n_embd, head_size, 256, dropout) for _ in range(num_heads)])
        self.proj    = nn.Linear(head_size * num_heads, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.dropout(self.proj(torch.cat([h(x) for h in self.heads], dim=-1)))


class FeedForward(nn.Module):
    def __init__(self, n_embd, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    def __init__(self, n_embd, n_head, dropout):
        super().__init__()
        head_size = n_embd // n_head
        self.sa  = MultiHeadAttention(n_embd, n_head, head_size, dropout)
        self.ffn = FeedForward(n_embd, dropout)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x


class RecipeGPT(nn.Module):
    def __init__(self, vocab_size, n_embd=384, n_head=6, n_layer=6, block_size=256, dropout=0.2):
        super().__init__()
        self.block_size = block_size
        self.tok_emb = nn.Embedding(vocab_size, n_embd)
        self.pos_emb = nn.Embedding(block_size, n_embd)
        self.blocks  = nn.Sequential(*[Block(n_embd, n_head, dropout) for _ in range(n_layer)])
        self.ln_f    = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)
        self.tok_emb.weight = self.lm_head.weight

    def forward(self, idx):
        B, T = idx.shape
        x = self.tok_emb(idx) + self.pos_emb(torch.arange(T, device=idx.device))
        return self.lm_head(self.ln_f(self.blocks(x)))

    @torch.no_grad()
    def generate_token(self, idx, temperature=1.0, top_k=None):
        logits = self.forward(idx[:, -self.block_size:])[:, -1, :] / temperature
        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = float('-inf')
        return torch.multinomial(F.softmax(logits, dim=-1), num_samples=1)


# ── Load model ─────────────────────────────────────────────────────────────────
MODEL_PATH = "recipe_gpt.pt"

@st.cache_resource(show_spinner=False)
def load_model():
    """Load model from local file or Google Drive."""
    if not os.path.exists(MODEL_PATH):
        # ── If you host on Google Drive, paste the direct download URL below ──
        # GDRIVE_URL = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"
        # r = requests.get(GDRIVE_URL); open(MODEL_PATH,'wb').write(r.content)
        return None, None, None, "Model file not found. Train in Colab first, then place recipe_gpt.pt here."

    try:
        ckpt = torch.load(MODEL_PATH, map_location='cpu')
        hp   = ckpt.get('hyperparams', dict(n_embd=384, n_head=6, n_layer=6, block_size=256))
        stoi = ckpt['stoi']
        itos = ckpt['itos']
        model = RecipeGPT(
            vocab_size  = ckpt['vocab_size'],
            n_embd      = hp['n_embd'],
            n_head      = hp['n_head'],
            n_layer     = hp['n_layer'],
            block_size  = hp['block_size'],
        )
        model.load_state_dict(ckpt['model_state_dict'])
        model.eval()
        params = sum(p.numel() for p in model.parameters())
        return model, stoi, itos, f"✓ Model loaded — {params/1e6:.1f}M parameters"
    except Exception as e:
        return None, None, None, f"Error loading model: {e}"


# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">Recipe<span class="accent">GPT</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">A tiny transformer that dreams up Indian recipes</p>', unsafe_allow_html=True)
st.markdown('<div class="spice-divider">✦ ✦ ✦</div>', unsafe_allow_html=True)

# Load model
with st.spinner("Loading model..."):
    model, stoi, itos, model_msg = load_model()

if model is not None:
    st.markdown(f'<p class="status-ok">{model_msg}</p>', unsafe_allow_html=True)
else:
    st.markdown(f'<p class="status-err">{model_msg}</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="tip-box">
    <b>How to get the model:</b><br>
    1. Run the training notebook in Google Colab (GPU runtime)<br>
    2. Download <code>recipe_gpt.pt</code> from Colab's file panel<br>
    3. Place it in the same folder as <code>app.py</code><br>
    4. Restart this app
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("###")

# ── Controls ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_input(
        "Prompt",
        value="BUTTER CHICKEN",
        placeholder="e.g. PANEER, DAL, SAMOSA...",
        label_visibility="collapsed",
    )
    st.caption("Type a recipe name, ingredient, or leave blank for surprise generation")

with col2:
    max_tokens = st.number_input("Max tokens", min_value=50, max_value=1000, value=400, step=50)

col3, col4 = st.columns(2)
with col3:
    st.markdown('<p class="slider-label">Temperature</p>', unsafe_allow_html=True)
    temperature = st.slider("temperature", 0.3, 1.5, 0.8, 0.05, label_visibility="collapsed")
    temp_desc = "🧊 Focused" if temperature < 0.6 else ("⚖️ Balanced" if temperature < 1.1 else "🔥 Creative")
    st.caption(f"{temp_desc}  —  {temperature}")

with col4:
    st.markdown('<p class="slider-label">Top-K Sampling</p>', unsafe_allow_html=True)
    top_k = st.slider("top_k", 5, 100, 40, 5, label_visibility="collapsed")
    st.caption(f"Sampling from top {top_k} tokens")

st.markdown("###")
generate_btn = st.button("✦ Generate Recipe", use_container_width=True)
st.markdown("###")

# ── Generation ─────────────────────────────────────────────────────────────────
if generate_btn:
    output_box = st.empty()
    generated  = ""
    start_time = time.time()

    try:
        if prompt.strip():
            # Encode only chars that exist in vocab
            safe_prompt = "".join(c for c in prompt if c in stoi)
            if not safe_prompt:
                safe_prompt = list(stoi.keys())[0]
            ctx = torch.tensor([[ stoi[c] for c in safe_prompt ]], dtype=torch.long)
            generated = safe_prompt
        else:
            ctx = torch.zeros((1, 1), dtype=torch.long)

        for i in range(max_tokens):
            next_tok = model.generate_token(ctx, temperature=temperature, top_k=top_k)
            char = itos[next_tok.item()]
            generated += char
            ctx = torch.cat((ctx, next_tok), dim=1)

            # Update display every 8 chars for smooth streaming feel
            if i % 8 == 0 or i == max_tokens - 1:
                output_box.markdown(
                    f'<div class="recipe-box">{generated}▌</div>',
                    unsafe_allow_html=True
                )

        elapsed = time.time() - start_time
        tok_per_sec = max_tokens / elapsed

        # Final output without cursor
        output_box.markdown(f'<div class="recipe-box">{generated}</div>', unsafe_allow_html=True)

        # Stats
        st.markdown(
            f'<div style="margin-top:0.8rem">'
            f'<span class="stat-pill">⏱ {elapsed:.1f}s</span>'
            f'<span class="stat-pill">⚡ {tok_per_sec:.0f} tok/s</span>'
            f'<span class="stat-pill">📝 {len(generated)} chars</span>'
            f'<span class="stat-pill">🌡 temp={temperature}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Generation error: {e}")

# ── Footer tips ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="tip-box">
<b>Tips:</b> &nbsp;
Try prompts like <code>BIRYANI</code>, <code>KHEER</code>, <code>TANDOORI</code>, <code>GULAB JAMUN</code>. &nbsp;
Lower temperature → more recipe-like. &nbsp;
Higher temperature → more experimental (and occasionally chaotic 🌶️).
</div>
""", unsafe_allow_html=True)
