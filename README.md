# 🧺 Apik Laundry - Sistem Manajemen Laundry Berbasis Web

**Tugas Kelompok 2 - Kelas 4IA19**  
**Universitas Gunadarma**  
**Mata Kuliah: RPL 2 dan PPPL**
**Tahun Akademik: 2025/2026**

---

## 👥 Anggota Kelompok 2

| No | NPM | Nama | Role | GitHub |
|----|-----|------|------|--------|
| 1  | 51422153 | Muhammad Ryan Firmansyah | Project Manager | @muhammadryanfirmansyah28-gif(https://github.com/muhammadryanfirmansyah28-gif) |
| 2  | 50422887 | Mochamad Girvan Azhar | Full Stack Developer | @girvanazharXD(https://github.com/girvanazharXD) |
| 3  | 50422380 | Daniel Alvin Trianto | QA | @Fortunatoo(https://github.com/Fortunatoo) |
| 4  | 50422919 | Moryska Kusuma Dewi | Technical Writer | @moruu1(https://github.com/moruu1) |
| 5  | 51422669 | Zahra Putri Fajrina | UI/UX Designer | @zahrafajrina02(https://github.com/zahrafajrina02) |

---

## 📖 Tentang Project

Apik Laundry adalah sistem manajemen laundry berbasis web yang dilengkapi dengan:
- ✨ Machine Learning untuk prediksi revenue
- 🤖 AI Chatbot untuk customer service
- 📊 Dashboard analytics real-time
- 📦 Inventory management system
- 💰 Financial tracking & reporting

Project ini dibuat dengan fokus pada implementasi teknologi modern seperti Vue.js, Flask, Machine Learning, dan cloud services.

---

## � Tujuan Project

1. **Pembelajaran Fullstack Development**
   - Frontend: Vue.js 3 + Vite
   - Backend: Python Flask + RESTful API
   - Database: Supabase (PostgreSQL)

2. **Implementasi Machine Learning**
   - Predictive analytics untuk revenue forecasting
   - Time series analysis
   - scikit-learn integration

3. **Cloud Integration**
   - Deployment ke Vercel/Netlify
   - Database cloud dengan Supabase
   - API integration

---

## 🏗️ Struktur Project

```
4IA19_Kelompok2_ApikLaundry/
├── api/                    # Backend API (Flask + ML)
│   ├── README.md          # API Documentation
│   ├── model.py           # Linear Regression model
│   ├── predict.py         # Prediction endpoint
│   ├── chatbot.py         # AI Chatbot
│   ├── requirements.txt   # Python dependencies
│   └── vercel.json        # Vercel deployment config
│
├── backend-ml/            # Alternative Backend
│   ├── app.py            # Main Flask app
│   └── model.py          # ML model
│
├── src/                   # Frontend (Vue.js)
│   ├── components/       # Reusable Vue components
│   ├── views/           # Page views (Owner/Kasir)
│   │   ├── owner/       # Owner dashboard
│   │   └── kasir/       # Cashier interface
│   ├── router/          # Vue Router configuration
│   └── assets/          # Static assets & CSS
│
├── public/               # Public static files
├── .env                  # Environment variables (not in repo)
├── package.json         # Node.js dependencies
└── README.md           # This file
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.9+
- **Git**
- Code editor (VS Code recommended)

### 1. Clone Repository
```bash
git clone https://github.com/moruu1/4IA19_Kelompok2_ApikLaundry.git
cd 4IA19_Kelompok2_ApikLaundry
```

### 2. Setup Frontend
```bash
# Install dependencies
npm install

# Run development server
npm run dev
```
Frontend akan berjalan di `http://localhost:5173`

### 3. Setup Backend API
```bash
# Navigate to api folder
cd api

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
# Edit .env dengan credentials Anda

# Run API server
python index.py
```
API akan berjalan di `http://127.0.0.1:5000`

---

## 📦 Tech Stack

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router** - Official routing library
- **Vite** - Next generation build tool
- **Chart.js** - Data visualization library
- **Axios** - HTTP client untuk API calls

### Backend
- **Flask 3.0** - Micro web framework (Python)
- **scikit-learn 1.3.2** - Machine Learning library
- **NumPy & Pandas** - Data processing
- **Flask-CORS** - Cross-Origin Resource Sharing

### Database & Services
- **Supabase** - Backend as a Service (PostgreSQL)
- **Groq AI** - LLaMA model untuk chatbot
- **Vercel** - Deployment platform

### Machine Learning
- **Algorithm:** Linear Regression
- **Library:** scikit-learn
- **Features:** 4 time-based features
- **Performance:** MAPE ~46%

---

## � Fitur Utama

### 1. Dashboard Owner 👨‍💼
- Revenue analytics & predictions
- Inventory management
- Financial reports
- User management
- Machine Learning insights

### 2. Dashboard Kasir 💼
- Transaction processing
- Customer management
- Quick access tools
- Daily reports

### 3. Revenue Prediction 📈
- ML-based revenue forecasting
- 7-365 days prediction range
- Accuracy metrics (MAPE, MAE, R²)
- Visual chart representation

### 4. Inventory Management 📦
- Real-time stock tracking
- Auto-depletion prediction
- Reorder alerts
- Usage analytics

### 5. AI Chatbot 🤖
- 24/7 customer support
- Natural language processing
- FAQ integration
- Groq LLaMA powered

### 6. Financial Tracking 💰
- Income & expense monitoring
- Daily/monthly reports
- Category breakdown
- Export to PDF/Excel

---

## � Environment Variables

### Root `.env` (Frontend)
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your-supabase-anon-key
VITE_ML_API_URL=http://127.0.0.1:5000
```

### `api/.env` (Backend)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-key
GROQ_API_KEY=your-groq-api-key
```

Lihat file `.env.example` untuk template lengkap.

---

## 🌐 Deployment

### Frontend (Vercel)
```bash
npm run build
vercel --prod
```

### Backend API (Vercel)
```bash
cd api
vercel --prod
```

Dokumentasi lengkap deployment: [api/README.md](api/README.md)

---

## 📚 Dokumentasi Lengkap

- **API Documentation:** [api/README.md](api/README.md)
- **Model Documentation:** [api/model.py](api/model.py)
- **Frontend Components:** [src/components/](src/components/)

---

## 🧪 Testing

### Frontend
```bash
# Run development server
npm run dev

# Build for production
npm run build
```

### Backend
```bash
cd api

# Test model
python model.py

# Run API server
python index.py
```

### Manual API Testing
```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Prediction
curl "http://127.0.0.1:5000/api/predict?days=7"

# Historical data
curl http://127.0.0.1:5000/api/historical
```

---

## 📸 Screenshots

> **Note:** Tambahkan screenshots aplikasi di sini (Dashboard, Prediction, Chatbot, dll)

## 🐛 Known Issues & Future Improvements

### Current Issues
- [ ] Prediction accuracy bisa ditingkatkan dengan more features
- [ ] Chatbot masih perlu training lebih lanjut

### Future Enhancements
- [ ] Mobile app (React Native / Flutter)
- [ ] WhatsApp integration untuk notifications
- [ ] Advanced ML models (LSTM, Prophet)
- [ ] Multi-branch support
- [ ] Accounting integration

---

## 📞 Contact & Support

**Kelompok 2 - 4IA19**

Untuk pertanyaan atau issues terkait project: Silahkan Create GitHub Issue

---

## � License

Project ini dibuat untuk keperluan akademik Universitas Gunadarma.

**Copyright © 2026 Kelompok 2 - 4IA19**  
All rights reserved.

---

## � Acknowledgments

- **Open Source Community** - Vue.js, Flask, scikit-learn
- **Supabase & Groq** - Free tier services

---

## 📊 Project Statistics

- **Total Commits:** [Auto-update]
- **Contributors:** 5 students
- **Lines of Code:** ~10,000+
- **Technologies Used:** 15+

---

**Repository:** https://github.com/moruu1/4IA19_Kelompok2_ApikLaundry  
**Last Updated:** 2026-01-26  
**Status:** ✅ Ready for Submission

---

> *"Built with ❤️ by Kelompok 2 - 4IA19 Universitas Gunadarma"*
