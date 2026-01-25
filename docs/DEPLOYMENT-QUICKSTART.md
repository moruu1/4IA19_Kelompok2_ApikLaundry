# ⚡ Quick Deployment Checklist

## Frontend Deployment

### 1. Import Project
- [ ] Login ke https://vercel.com
- [ ] Add New → Project
- [ ] Import: `moruu1/4IA19_Kelompok2_ApikLaundry`
- [ ] Root: `./`
- [ ] Framework: Vite (auto-detected)

### 2. Environment Variables
```
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_KEY=eyJhbGci...
VITE_ML_API_URL=(kosongkan dulu)
```

### 3. Deploy
- [ ] Click Deploy
- [ ] Wait 2-3 minutes
- [ ] Copy URL: `https://your-app.vercel.app`

---

## Backend Deployment

### 1. Import as New Project
- [ ] Add New → Project
- [ ] Same repo: `moruu1/4IA19_Kelompok2_ApikLaundry`
- [ ] **Root Directory:** `api` ✅ IMPORTANT!
- [ ] Framework: Other

### 2. Environment Variables
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGci... (service key!)
GROQ_API_KEY=gsk_...
```

### 3. Deploy
- [ ] Click Deploy
- [ ] Wait 3-5 minutes
- [ ] Copy URL: `https://your-api.vercel.app`

---

## Final Step: Link Frontend & Backend

### Update Frontend
1. Go to frontend project → Settings → Environment Variables
2. Edit `VITE_ML_API_URL`
3. Value: `https://your-api.vercel.app`
4. Save
5. Deployments tab → Redeploy latest

---

## ✅ Test URLs

**Frontend:** `https://your-app.vercel.app`  
**Backend Health:** `https://your-api.vercel.app/api/health`  
**Prediction:** `https://your-api.vercel.app/api/predict?days=7`

---

## 🔑 Where to Get Keys

**Supabase:**
- Dashboard → Settings → API
- URL: Project URL
- Anon Key: For frontend
- Service Key: For backend

**Groq:**
- https://console.groq.com
- API Keys → Create API Key

---

## 🐛 Common Issues

**Build Failed?**
- Check `package.json` or `requirements.txt`
- Verify root directory setting

**CORS Error?**
- Update `VITE_ML_API_URL`
- Redeploy frontend

**504 Timeout?**
- Normal for cold start
- Wait 15s, refresh

---

**Total Time:** ~15 minutes  
**Cost:** FREE (Vercel hobby plan)
