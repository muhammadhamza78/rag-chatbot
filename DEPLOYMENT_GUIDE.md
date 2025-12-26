# Deployment Guide - RAG Chatbot

This guide covers deploying the complete RAG chatbot system to production.

---

## Architecture Overview

The system has two main components:

1. **Frontend (Docusaurus)** → Deploy to **Vercel**
2. **Backend (FastAPI)** → Deploy to **Render** or **Railway**

---

## Part 1: Deploy Backend to Render

### Step 1: Prepare Backend for Deployment

The backend is already configured in the `backend/` directory.

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `muhammadhamza78/rag-chatbot`
3. Configure:
   - **Name:** `rag-chatbot-backend`
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && pip install -r ../rag-pipeline/requirements-agent.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn api_server:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** Free (or paid for better performance)

### Step 4: Add Environment Variables

In Render dashboard, add these environment variables:

```
OPENAI_API_KEY=your-openai-key
COHERE_API_KEY=your-cohere-key
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key
QDRANT_COLLECTION_NAME=physical_ai_book
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Note your backend URL: `https://rag-chatbot-backend.onrender.com`

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### Step 2: Deploy via Vercel Website

1. Go to https://vercel.com
2. Click **"Add New Project"**
3. Import `muhammadhamza78/rag-chatbot` from GitHub
4. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `physical-ai-book`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
   - **Install Command:** `npm install`

### Step 3: Add Environment Variable

In Vercel dashboard → Settings → Environment Variables:

```
REACT_APP_API_URL=https://rag-chatbot-backend.onrender.com
```

**Important:** Replace with your actual Render backend URL from Part 1.

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait for build (3-5 minutes)
3. Your frontend will be live at: `https://rag-chatbot-xxx.vercel.app`

### Step 5: Update Backend CORS

After deployment, update `backend/api_server.py` to allow your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://rag-chatbot-xxx.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push this change - Render will auto-deploy.

---

## Alternative: Deploy via Vercel CLI

```bash
# Navigate to project
cd physical-ai-hackathon

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? **rag-chatbot**
- Directory? **./physical-ai-book**
- Override settings? **N**

---

## Part 3: Verify Deployment

### Test Backend

```bash
# Health check
curl https://rag-chatbot-backend.onrender.com/api/health

# Test query
curl -X POST https://rag-chatbot-backend.onrender.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is physical AI?"}'
```

### Test Frontend

1. Visit your Vercel URL: `https://rag-chatbot-xxx.vercel.app`
2. Navigate to `/ask-ai`
3. Send a test query
4. Verify response appears

---

## Part 4: Custom Domain (Optional)

### For Frontend (Vercel)

1. Go to Vercel dashboard → Settings → Domains
2. Add your custom domain (e.g., `chat.yourdomain.com`)
3. Update DNS settings as instructed
4. SSL certificate is automatic

### For Backend (Render)

1. Go to Render dashboard → Settings → Custom Domains
2. Add your custom domain (e.g., `api.yourdomain.com`)
3. Update DNS settings
4. SSL certificate is automatic

---

## Troubleshooting

### Frontend Can't Connect to Backend

**Issue:** CORS errors in browser console

**Fix:**
1. Check backend CORS allows frontend URL
2. Ensure `REACT_APP_API_URL` points to correct backend
3. Verify backend is running: visit `/api/health`

### Backend Deployment Fails

**Issue:** Build errors on Render

**Fix:**
1. Check build logs for specific error
2. Verify all environment variables are set
3. Ensure `requirements.txt` includes all dependencies

### Slow Cold Starts (Render Free Tier)

**Issue:** First request takes 30+ seconds

**Why:** Free tier spins down after inactivity

**Solutions:**
- Upgrade to paid tier ($7/month)
- Use a cron job to ping every 14 minutes
- Accept the trade-off for free hosting

### Environment Variables Not Working

**Issue:** API keys not loading

**Fix:**
1. Verify variables are set in Render/Vercel dashboard
2. Restart the service after adding variables
3. Check variable names match exactly (case-sensitive)

---

## Production Checklist

### Backend
- [ ] All environment variables configured
- [ ] CORS updated with production URLs
- [ ] Health check endpoint working
- [ ] API endpoints tested
- [ ] Logs monitoring set up

### Frontend
- [ ] Backend API URL configured
- [ ] Build successful
- [ ] Chat interface working
- [ ] All pages accessible
- [ ] Mobile responsive verified

### Security
- [ ] API keys in environment variables (not code)
- [ ] CORS restricted to specific domains
- [ ] HTTPS enabled (automatic on Vercel/Render)
- [ ] Rate limiting considered (future)

---

## Cost Estimation

### Free Tier
- **Vercel:** Free (hobby plan)
- **Render:** Free (with limitations)
- **OpenAI:** Pay per use (~$0.001-0.003 per query)
- **Cohere:** Free tier available
- **Qdrant:** Free tier available

**Total:** ~$0-5/month (depending on usage)

### Paid Tier (Recommended for Production)
- **Vercel:** $20/month (Pro)
- **Render:** $7/month (Starter)
- **OpenAI:** Pay per use (~$10-50/month)
- **Cohere:** $0 (free tier sufficient)
- **Qdrant:** $0 (free tier sufficient)

**Total:** ~$40-80/month

---

## Monitoring

### Vercel Analytics
- Visit Vercel dashboard → Analytics
- Track page views, unique visitors
- Monitor build times

### Render Logs
- Visit Render dashboard → Logs
- Monitor API requests
- Track errors and warnings

### OpenAI Usage
- Visit OpenAI dashboard → Usage
- Track token consumption
- Monitor costs

---

## Continuous Deployment

Both Vercel and Render support automatic deployment:

1. **Push to GitHub main branch**
2. **Vercel auto-builds** frontend
3. **Render auto-deploys** backend
4. **Changes live in 5-10 minutes**

**Enable:**
- Already enabled by default when connecting GitHub
- Every push to `main` triggers deployment
- Preview deployments for pull requests

---

## Rollback

### Vercel
1. Go to Deployments tab
2. Click previous successful deployment
3. Click "Promote to Production"

### Render
1. Go to Events tab
2. Find previous successful deploy
3. Click "Redeploy"

---

## Support Resources

- **Vercel Docs:** https://vercel.com/docs
- **Render Docs:** https://render.com/docs
- **Docusaurus Deploy:** https://docusaurus.io/docs/deployment
- **FastAPI Deploy:** https://fastapi.tiangolo.com/deployment/

---

## Quick Deploy Commands

```bash
# Update backend CORS with production URL
# Edit backend/api_server.py

# Commit and push
git add .
git commit -m "Update CORS for production deployment"
git push origin main

# Both services will auto-deploy
# Frontend: 3-5 minutes
# Backend: 5-10 minutes
```

---

**Deployment Status:** Ready for production
**Estimated Setup Time:** 30-45 minutes
**Difficulty:** Medium

🚀 **Your RAG chatbot will be live and accessible worldwide!**
