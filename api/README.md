# 🧺 Apik Laundry - Backend API Documentation

Sistem backend berbasis Machine Learning untuk prediksi revenue dan manajemen inventaris laundry.

## 📋 Table of Contents
- [API Endpoints](#-api-endpoints)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Local Development](#-local-development)
- [Deployment to Vercel](#-deployment-to-vercel)
- [Environment Variables](#-environment-variables)
- [Model Information](#-model-information)
- [API Response Format](#-api-response-format)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 API Endpoints

Base URL (Local): `http://127.0.0.1:5000`  
Base URL (Production): `https://your-project.vercel.app`

### Revenue Prediction
```http
GET /api/predict?days=30
```
Prediksi revenue untuk N hari ke depan menggunakan Linear Regression.

**Query Parameters:**
- `days` (optional): Jumlah hari prediksi (default: 30, max: 365)

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "date": "2026-01-17",
      "predicted_revenue": 350000,
      "upper_bound": 492698,
      "lower_bound": 207302
    }
  ],
  "summary": {
    "total_predicted": 10500000,
    "average_daily": 350000,
    "days": 30
  },
  "model_info": {
    "algorithm": "Linear Regression (sklearn)",
    "mae": 142698,
    "rmse": 206191,
    "r2": 0.0484,
    "mape": 46.49
  }
}
```

---

### Historical Data
```http
GET /api/historical
```
Mendapatkan data revenue historis dari database.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-01-01",
      "revenue": 450000
    }
  ],
  "summary": {
    "total_days": 289,
    "total_revenue": 105271888,
    "average_daily": 364263,
    "date_range": {
      "start": "2025-01-01",
      "end": "2026-01-16"
    }
  }
}
```

---

### Inventory Prediction
```http
GET /api/inventory-prediction
```
Prediksi depletion stok inventaris menggunakan Moving Average.

**Response:**
```json
{
  "success": true,
  "services": [
    {
      "service_name": "Cuci Setrika",
      "current_stock": 50,
      "daily_usage": 12.5,
      "days_until_empty": 4,
      "reorder_date": "2026-01-20",
      "status": "warning"
    }
  ],
  "summary": {
    "total_services": 3,
    "critical_count": 1,
    "warning_count": 1,
    "normal_count": 1
  }
}
```

---

### Chatbot
```http
POST /api/chatbot
Content-Type: application/json

{
  "message": "Berapa harga cuci setrika?"
}
```
AI Chatbot untuk menjawab pertanyaan customer tentang layanan laundry.

**Response:**
```json
{
  "success": true,
  "response": "Harga cuci setrika mulai dari Rp 8.000/kg...",
  "confidence": 0.95
}
```

---

### Health Check
```http
GET /api/health
```
Endpoint untuk monitoring server health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-26T04:30:00Z",
  "services": {
    "database": "connected",
    "ml_model": "loaded",
    "chatbot": "ready"
  }
}
```

---

## 🛠️ Tech Stack

### Backend Framework
- **Flask 3.0.0** - Python web framework
- **Flask-CORS 4.0.0** - Cross-Origin Resource Sharing

### Machine Learning
- **scikit-learn 1.3.2** - Linear Regression model
- **numpy 1.26.2** - Numerical computing
- **pandas 2.1.4** - Data manipulation

### Database & Services
- **Supabase 2.9.0** - PostgreSQL database & authentication
- **Groq** - AI chatbot (LLaMA model)

### Deployment
- **Vercel** - Serverless deployment platform
- **Python Runtime** - 3.9+

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Clone Repository
```bash
git clone https://github.com/moruu1/4IA19_Kelompok2_ApikLaundry.git
cd 4IA19_Kelompok2_ApikLaundry/api
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
Create `.env` file in `api/` directory:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
GROQ_API_KEY=your-groq-api-key
```

---

## 💻 Local Development

### Start Development Server
```bash
python index.py
```

Server will start on `http://127.0.0.1:5000`

### Test Endpoints
```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Get predictions
curl http://127.0.0.1:5000/api/predict?days=7

# Get historical data
curl http://127.0.0.1:5000/api/historical

# Chatbot
curl -X POST http://127.0.0.1:5000/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "Halo"}'
```

### Debug Mode
Flask debug mode sudah enabled by default di `index.py`. Server akan auto-reload saat ada perubahan code.

---

## 🚀 Deployment to Vercel

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy
```bash
cd api
vercel --prod
```

### Step 4: Configure Environment Variables
**Option A - During Deployment:**
Vercel akan prompt untuk input environment variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `GROQ_API_KEY`

**Option B - Via CLI:**
```bash
vercel env add SUPABASE_URL production
vercel env add SUPABASE_KEY production
vercel env add GROQ_API_KEY production
```

**Option C - Via Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings → Environment Variables
4. Add variables

### Step 5: Verify Deployment
```bash
# Test production endpoint
curl https://your-project.vercel.app/api/health
```

---

## 🔐 Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Supabase project URL | ✅ Yes | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon/service key | ✅ Yes | `eyJhbGci...` |
| `GROQ_API_KEY` | Groq API key untuk chatbot | ✅ Yes | `gsk_...` |

### How to Get Keys:

**Supabase:**
1. Go to https://supabase.com/dashboard
2. Select project → Settings → API
3. Copy `URL` and `anon public` key

**Groq:**
1. Go to https://console.groq.com
2. API Keys → Create API Key
3. Copy the key

---

## 📊 Model Information

### Linear Regression Model

**Algorithm:** sklearn LinearRegression  
**Training Method:** Train-Test Split (80/20)

**Features (4):**
1. `day_of_week` - Hari dalam seminggu (0-6)
2. `day_of_month` - Tanggal dalam bulan (1-31)
3. `month` - Bulan dalam tahun (1-12)
4. `day_number` - Sequential day number dari start date

**Performance Metrics:**
- **MAPE:** ~46% (Mean Absolute Percentage Error)
- **MAE:** ~Rp 142,698 (Mean Absolute Error)
- **RMSE:** ~Rp 206,191 (Root Mean Squared Error)
- **R²:** ~0.048 (Coefficient of Determination)

**Why Simple Model?**
- Data laundry sangat volatile/unpredictable
- Complex models cenderung overfit
- Simple = faster inference & deployment
- Proven performance di production

**Training Data:**
- Source: Supabase `financials` table
- Filter: `tipe = 'Pemasukan'`
- Aggregation: Daily sum
- Size: ~289 hari historical data

---

## 📐 API Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "summary": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message description",
  "details": "Additional error details (optional)"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

---

## 🧪 Testing

### Manual Testing
```bash
# Revenue prediction
curl "http://127.0.0.1:5000/api/predict?days=7" | json_pp

# Historical data
curl "http://127.0.0.1:5000/api/historical" | json_pp

# Inventory prediction
curl "http://127.0.0.1:5000/api/inventory-prediction" | json_pp

# Chatbot
curl -X POST "http://127.0.0.1:5000/api/chatbot" \
  -H "Content-Type: application/json" \
  -d '{"message": "Berapa harga cuci kiloan?"}' | json_pp
```

### Expected Response Time
- **Health:** < 100ms
- **Historical:** < 500ms
- **Predict:** < 2s (training + prediction)
- **Inventory:** < 1s
- **Chatbot:** < 3s (AI inference)

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'sklearn'`
**Solution:**
```bash
pip install scikit-learn==1.3.2
```

### Issue: `Supabase connection error`
**Solution:**
1. Check `.env` file exists dan berisi correct credentials
2. Verify `SUPABASE_URL` dan `SUPABASE_KEY`
3. Check internet connection
4. Test connection:
   ```python
   from config import SUPABASE_URL, SUPABASE_KEY
   print(f"URL: {SUPABASE_URL}")
   print(f"Key: {SUPABASE_KEY[:10]}...")
   ```

### Issue: `MAPE very high (>50%)`
**Possible causes:**
- Insufficient training data (< 30 days)
- Extreme outliers in data
- Business model changed significantly

**Solution:**
- Clean data: remove extreme outliers
- Ensure at least 60 days of consistent data
- Consider seasonal patterns

### Issue: Vercel deployment timeout
**Possible causes:**
- scikit-learn bundle too large
- Cold start timeout

**Solution:**
- Increase timeout in `vercel.json`:
  ```json
  {
    "functions": {
      "api/*.py": {
        "maxDuration": 60
      }
    }
  }
  ```

### Issue: CORS error in frontend
**Solution:**
Already handled by Flask-CORS. If still occurs:
1. Check frontend URL in allowed origins
2. Add explicit CORS config in `index.py`

---

## 📝 Changelog

### v2.0.0 (2026-01-26)
- ✅ Replaced Seasonal Model with Linear Regression
- ✅ Cleaned up unused files for deployment
- ✅ Added Vercel configuration
- ✅ Updated documentation
- ✅ Fixed prediction start date (from last_date + 1)
- ✅ Added comprehensive error handling

### v1.0.0 (Initial Release)
- Revenue prediction using Seasonal Median model
- Historical data endpoint
- Inventory prediction
- AI Chatbot integration

---

## 📄 License

Project ini dibuat untuk keperluan akademik Universitas Gunadarma.  
**Copyright © 2026 Kelompok 2 - 4IA19**

## 🆘 Support

For issues and questions:
- Create an issue: https://github.com/moruu1/4IA19_Kelompok2_ApikLaundry/issues

---

**Repository:** https://github.com/moruu1/4IA19_Kelompok2_ApikLaundry  
**Last Updated:** 2026-01-26  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
