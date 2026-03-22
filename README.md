# 🍛 RecipeGPT — Minecraft Edition

> *An AI-powered Indian recipe generator built from scratch — nanoGPT architecture, Minecraft-themed UI, deployable on Streamlit or GitHub Pages.*
> 
> **By [Dicypr](https://github.com/dicypr)**

![RecipeGPT Banner](https://img.shields.io/badge/RecipeGPT-Minecraft%20Edition-5D9E2F?style=for-the-badge&logo=data:image/png;base64,)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.3+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📁 Repository Structure

```
recipegpt/
├── 📓 notebooks/
│   ├── nanoGPT_Indian_Recipes_v2.ipynb   ← Train the model (run in Colab)
│   └── RecipeGPT_TestSuite.ipynb         ← Evaluate output quality
│
├── 🌐 site/
│   └── index.html                         ← Minecraft-themed frontend (GitHub Pages)
│
├── 🚀 streamlit/
│   ├── app.py                             ← Streamlit web app
│   └── requirements.txt                  ← Python dependencies
│
├── 🔧 .github/
│   └── workflows/
│       └── deploy.yml                    ← Auto-deploy to GitHub Pages
│
├── .gitignore
└── README.md
```

---

## 🎮 Live Demo

| Platform | URL |
|---|---|
| GitHub Pages | `https://YOUR_USERNAME.github.io/recipegpt` |
| Streamlit Cloud | `https://YOUR_USERNAME-recipegpt.streamlit.app` |

---

## 🧠 What Is This?

RecipeGPT is a **decoder-only GPT Transformer** trained from scratch on Indian recipe text — the same architecture as GPT-2, just much smaller (~30M params). Inspired by Andrej Karpathy's *"Let's Build GPT from Scratch"* lecture.

### Architecture

| Component | Spec |
|---|---|
| Model type | Decoder-only GPT (nanoGPT) |
| Parameters | ~30M |
| Layers | 8 |
| Attention heads | 8 |
| Embedding dim | 512 |
| Context window | 384 tokens |
| Tokenizer | Character-level |
| Training data | ~250K chars Indian recipes |
| Training time | ~10 min on Colab T4 GPU |

### Upgrades over vanilla nanoGPT
- ✅ Fused QKV attention (GPT-2 style)
- ✅ GELU activation
- ✅ Weight tying (token emb ↔ lm_head)
- ✅ Cosine LR with linear warmup
- ✅ Gradient accumulation (effective batch 128)
- ✅ Top-K + Top-P (nucleus) sampling
- ✅ Structured `[RECIPE]` training format

---

## 🚀 Quick Start

### Option 1 — GitHub Pages (Frontend Only, No Training)

The `site/index.html` works as a standalone frontend. It calls an AI backend at runtime.

1. Fork this repo
2. Go to **Settings → Pages → Source: Deploy from branch → main / site**
3. Your site is live at `https://YOUR_USERNAME.github.io/recipegpt`

> ⚠️ The Generate button needs a backend with an API key. See backend setup below.

---

### Option 2 — Train + Deploy on Streamlit

#### Step 1: Train the model in Google Colab

```
1. Open notebooks/nanoGPT_Indian_Recipes_v2.ipynb in Colab
2. Runtime → Change runtime type → T4 GPU
3. Run all cells (~10 minutes)
4. Download recipe_gpt_v2.pt from the Colab file panel
```

#### Step 2: Run Streamlit locally

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/recipegpt.git
cd recipegpt

# Install dependencies
pip install -r streamlit/requirements.txt

# Place your trained model
cp ~/Downloads/recipe_gpt_v2.pt streamlit/recipe_gpt.pt

# Run
streamlit run streamlit/app.py
```

Open http://localhost:8501

#### Step 3: Deploy to Streamlit Cloud (Free)

```bash
# Add model to repo (it's ~40MB, fine for GitHub)
cp ~/Downloads/recipe_gpt_v2.pt streamlit/recipe_gpt.pt
git add streamlit/recipe_gpt.pt
git commit -m "add trained model weights"
git push
```

Then:
1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click **New app**
3. Connect your GitHub repo
4. Main file: `streamlit/app.py`
5. Click **Deploy** ✅

---

### Option 3 — Backend API Server (for GitHub Pages frontend)

To make the Generate button on the HTML site work, you need a simple backend that injects the API key server-side.

#### Using Node.js (Vercel/Railway/Render)

```bash
npm init -y
npm install express cors node-fetch
```

Create `server.js`:

```js
const express = require('express');
const cors    = require('cors');
const fetch   = require('node-fetch');
const app     = express();

app.use(cors());
app.use(express.json());

app.post('/generate', async (req, res) => {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': process.env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify(req.body)
  });
  response.body.pipe(res);
});

app.listen(3000);
```

Set env variable `ANTHROPIC_API_KEY` in your hosting provider dashboard.

Then update the fetch URL in `site/index.html`:
```js
// Change this line:
const res = await fetch('https://api.anthropic.com/v1/messages', {
// To your deployed backend:
const res = await fetch('https://your-backend.railway.app/generate', {
```

---

## 📓 Notebooks

### `nanoGPT_Indian_Recipes_v2.ipynb`
Full training notebook. Run top-to-bottom in Colab.

| Cell | What it does |
|---|---|
| 1 | Builds 250K char recipe corpus |
| 2-3 | Tokenizer + train/val split |
| 4-5 | Hyperparameters + data loader |
| 6 | Model definition (RecipeGPTv2) |
| 7 | Training loop with grad accumulation |
| 8 | Loss curve plots |
| 9-10 | Generation with temperature/top-k/top-p |
| 11 | Save model to `recipe_gpt_v2.pt` |

### `RecipeGPT_TestSuite.ipynb`
Run after training to evaluate quality.

| Test | What it checks |
|---|---|
| Test 1 | Raw output for 5 dish types |
| Test 2 | Quality score (structure, quantities, spice names) |
| Test 3 | Temperature comparison (0.6 / 0.9 / 1.3) |
| Test 4 | Perplexity — confirms model learned recipes |

---

## 🎨 Frontend (Minecraft Theme)

`site/index.html` is a fully self-contained single-file Minecraft-themed site.

**Features:**
- Press Start 2P pixel font
- Procedural Minecraft landscape (canvas)
- Block-break particle effects on button click
- Furnace output panel with fire animation
- Hotbar navigation
- XP bar on load
- Chest inventory showcase cards
- Enchanting Table "How it works" section
- Token-by-token streaming output
- Copy to clipboard

**No build step. No npm. No dependencies.** Just open in a browser or host on GitHub Pages.

---

## 🔧 Streamlit App Features

| Feature | Details |
|---|---|
| Model loading | Cached with `@st.cache_resource` |
| Generation | Token-by-token streaming |
| Temperature | Slider 0.3–1.5 |
| Top-K | Slider 5–100 |
| Quick picks | 8 preset dishes |
| Stats | Chars generated, time elapsed, tok/s |
| Save/load | Downloads `recipe_gpt.pt` from Colab |

---

## 📊 Expected Training Results

| Metric | Value |
|---|---|
| Final train loss | ~0.8–1.2 |
| Final val loss | ~1.0–1.4 |
| Perplexity (recipes) | < 5.0 |
| Quality score | ~80%+ |
| Training time (T4) | ~10 min |

---

## 🌶️ Sample Output

```
[RECIPE]
NAME: Palak Paneer
CATEGORY: North Indian, Vegetarian
SERVES: 4
PREP TIME: 15 minutes
COOK TIME: 25 minutes

INGREDIENTS:
- 300g fresh paneer, cubed
- 500g spinach leaves
- 2 medium tomatoes
- 1 onion, chopped
- 1 tsp cumin seeds
- 1 tsp garam masala
- 2 tbsp cream
...

METHOD:
1. Blanch spinach in boiling water 2 minutes, transfer to ice bath.
2. Blend spinach with green chilies until smooth.
3. Fry paneer until golden, soak in warm water...
```

---

## 🏗️ Credits

- **Architecture**: Inspired by [Andrej Karpathy's nanoGPT](https://github.com/karpathy/nanoGPT)
- **Built by**: [Dicypr](https://github.com/dicypr)
- **Theme**: Minecraft (Mojang Studios trademark, fan project)
- **Training**: Google Colab T4 GPU

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

> *Minecraft is a trademark of Mojang Studios. This is an independent fan project not affiliated with Mojang or Microsoft.*
