/**
 * RecipeGPT — Backend API Server
 * By Dicypr
 *
 * This server proxies requests from the frontend (site/index.html)
 * to the AI API, keeping your API key secret on the server side.
 *
 * Deploy on: Railway, Render, Fly.io, Vercel, or any Node host.
 *
 * Usage:
 *   npm install
 *   ANTHROPIC_API_KEY=your_key node server.js
 */

const express = require('express');
const cors    = require('cors');
const https   = require('https');

const app  = express();
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.ANTHROPIC_API_KEY;

if (!API_KEY) {
  console.error('ERROR: ANTHROPIC_API_KEY environment variable not set.');
  console.error('Set it with: export ANTHROPIC_API_KEY=your_key_here');
  process.exit(1);
}

app.use(cors({
  origin: '*', // Restrict to your GitHub Pages domain in production
  methods: ['POST'],
}));
app.use(express.json({ limit: '1mb' }));

// Health check
app.get('/', (req, res) => {
  res.json({ status: 'ok', service: 'RecipeGPT by Dicypr' });
});

// Proxy endpoint — streams AI response back to browser
app.post('/generate', (req, res) => {
  const body = JSON.stringify({
    ...req.body,
    stream: true,
  });

  const options = {
    hostname: 'api.anthropic.com',
    path: '/v1/messages',
    method: 'POST',
    headers: {
      'Content-Type':      'application/json',
      'Content-Length':    Buffer.byteLength(body),
      'x-api-key':         API_KEY,
      'anthropic-version': '2023-06-01',
    },
  };

  res.setHeader('Content-Type',  'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection',    'keep-alive');

  const apiReq = https.request(options, (apiRes) => {
    apiRes.pipe(res);
    apiRes.on('end', () => res.end());
  });

  apiReq.on('error', (err) => {
    console.error('API error:', err.message);
    if (!res.headersSent) {
      res.status(500).json({ error: err.message });
    }
  });

  apiReq.write(body);
  apiReq.end();
});

app.listen(PORT, () => {
  console.log(`RecipeGPT backend running on port ${PORT}`);
  console.log(`API key: ${API_KEY.slice(0, 8)}...`);
});
