# ⚡ Quick Setup Guide

## 5-Minute Deploy (GitHub Pages only)

```bash
# 1. Fork this repo on GitHub
# 2. Go to Settings → Pages
# 3. Source: Deploy from branch → main → /site
# 4. Done! Site is live at https://YOUR_USERNAME.github.io/recipegpt
```

The site loads instantly. The Generate button needs a backend to work (see below).

---

## Full Deploy (Train + Streamlit)

### 1. Train in Colab (10 min)
```
Open: notebooks/nanoGPT_Indian_Recipes_v2.ipynb
Set: Runtime → T4 GPU
Run: All cells
Download: recipe_gpt_v2.pt
```

### 2. Deploy Streamlit
```bash
git clone https://github.com/YOUR_USERNAME/recipegpt
cd recipegpt
pip install -r streamlit/requirements.txt
cp ~/Downloads/recipe_gpt_v2.pt streamlit/recipe_gpt.pt
streamlit run streamlit/app.py
```

For Streamlit Cloud:
1. Push `recipe_gpt.pt` to the repo (under 100MB is fine)
2. Deploy at streamlit.io/cloud → point to `streamlit/app.py`

---

## Backend Server (for live Generate button)

```bash
cd backend
npm install
export ANTHROPIC_API_KEY=your_key_here
node server.js
```

Then in `site/index.html`, update:
```js
const BACKEND_URL = 'http://localhost:3000/generate';
```

For production deployment on Railway:
1. Push backend/ to GitHub
2. Create new Railway project → Deploy from GitHub
3. Add env variable: `ANTHROPIC_API_KEY=your_key`
4. Copy your Railway URL
5. Update `BACKEND_URL` in `site/index.html`

---

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Backend server / Railway | Your AI API key |
| `BACKEND_URL` | `site/index.html` line 1 | Your backend URL |

**Never commit API keys to GitHub.**
