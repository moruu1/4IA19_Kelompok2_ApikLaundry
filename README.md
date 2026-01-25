# 🧺 Apik Laundry - Sistem Manajemen Laundry

![Project Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Frontend](https://img.shields.io/badge/Frontend-Vue.js%203-4FC08D)
![Backend](https://img.shields.io/badge/Backend-Supabase-3ECF8E)
![ML](https://img.shields.io/badge/ML-Python%20Flask-3776AB)

## 📋 Overview

**Apik Laundry** adalah sistem manajemen laundry berbasis web dengan fitur Machine Learning untuk prediksi pendapatan & inventory, dilengkapi AI chatbot untuk customer service otomatis.

### ✨ Key Features

- 🔐 **Multi-Role System**: Customer, Admin, Owner dengan akses berbeda
- 📊 **Real-time Dashboard**: Statistik dan analytics live
- 🤖 **AI Chatbot**: TF-IDF + Cosine Similarity untuk FAQ otomatis
- 📈 **ML Predictions**: Revenue forecasting (Linear Regression) & Inventory (Moving Average)
- 📱 **Mobile Responsive**: Optimized untuk semua device
- 💰 **Financial Reports**: Tracking pemasukan/pengeluaran dengan filtering

## 🚀 Tech Stack

### Frontend
- **Vue.js 3** - Progressive framework
- **Pinia** - State management
- **Vue Router** - Navigation dengan guards
- **TailwindCSS** - Styling
- **Chart.js** - Data visualization
- **Vite** - Build tool

### Backend
- **Supabase** - PostgreSQL database + Auth
- **Python Flask** - ML API server
- **scikit-learn** - Machine learning models
- **Pandas/NumPy** - Data processing

## 📁 Project Structure

```
Project Laundry/
├── backend-ml/              # Python Flask ML API
│   ├── app.py              # API endpoints
│   ├── model.py            # Revenue prediction
│   ├── inventory.py        # Inventory forecasting
│   ├── chatbot.py          # AI Chatbot engine
│   └── requirements.txt
├── src/
│   ├── components/          # Reusable Vue components
│   ├── stores/             # Pinia stores (7 stores)
│   ├── views/              # Page components
│   │   ├── admin/          # Admin pages (CRUD operations)
│   │   ├── owner/          # Owner pages (Analytics & Predictions)
│   │   └── customer/       # Customer pages (Orders & Tracking)
│   └── router/             # Vue Router config
└── README.md
```

## 🛠️ Installation

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase Account (free tier)

### Quick Start

**1. Clone Repository**
```bash
git clone https://github.com/moruu1/4IA19_Kelompok2_ApikLaundry.git
cd "4IA19_Kelompok2_ApikLaundry"
```

**2. Frontend Setup**
```bash
npm install
cp .env.example .env
# Edit .env dengan Supabase credentials

npm run dev
# App running at http://localhost:5173
```

**3. Backend ML Setup**
```bash
cd backend-ml
pip install -r requirements.txt
cp .env.example .env
# Edit .env dengan Supabase credentials

python app.py
# API running at http://localhost:5000
```

**4. Database Setup**
- Login ke [Supabase Dashboard](https://supabase.com)
- Create new project
- Buka **SQL Editor** → New Query
- Buat tables sesuai schema (lihat section Database Schema di bawah)
- Disable RLS untuk development (Table Editor → Settings → RLS: OFF)
- Copy Project URL & Anon Key ke kedua `.env` files

## 👥 User Roles

### Customer (`/customer/*`)
- View order history & status tracking
- Browse services catalog
- AI chatbot untuk FAQ
- Profile management

### Admin (`/admin/*`)
- Dashboard dengan statistik real-time
- CRUD: Orders, Customers, Services, Inventory
- Financial reports dengan filtering
- Low stock alerts

### Owner (`/owner/*`)
- Business analytics dashboard
- Revenue & inventory predictions (ML)
- Comprehensive reports
- Monitoring semua operasi

## 🤖 Machine Learning Features

### 1. Revenue Prediction
- **Algorithm**: Linear Regression
- **Input**: 256 hari historical transactions
- **Output**: 30 hari forecast dengan confidence interval (±MAE/MAPE)
- **Visualization**: Interactive line chart

### 2. Inventory Forecasting
- **Algorithm**: Moving Average (7-day window)
- **Output**: Estimasi hari hingga stok habis
- **Alerts**: Warning (<7 hari), Urgent (<3 hari)

### 3. AI Chatbot (Tanya Apik)
- **Method**: TF-IDF + Cosine Similarity
- **Threshold**: 0.55 untuk relevancy check
- **Data**: FAQ database dari Supabase (real-time sync)

## 🗄️ Database Schema

**8 Main Tables:**

1. **users** - User profiles dengan roles (admin/owner/customer)
2. **customers** - Database pelanggan laundry  
3. **services** - Layanan laundry dengan pricing
4. **transactions** - Order/transaksi dengan relasi ke customers & services
5. **financials** - Tracking pemasukan/pengeluaran
6. **inventory_items** - Manajemen stok barang
7. **service_bom** - Bill of Materials (relasi service → inventory)
8. **faq** - Knowledge base untuk AI chatbot

**Catatan**: Schema SQL detail tersedia di Supabase Dashboard → SQL Editor atau hubungi developer team.

## 📊 Key Features Detail

### Admin Dashboard
- **4 KPI Cards**: Total Customers, Orders Today, Revenue Today, Low Stock Items
- **Revenue Chart**: Monthly bar chart
- **Recent Transactions**: Last 5 orders
- **Low Stock Alerts**: Items with stock ≤ 10

### Owner Prediction Page
- **Revenue Forecast**: 30-day prediction dengan accuracy metrics (MAE, RMSE, R², MAPE)
- **Inventory Predictions**: Auto-calculate restock dates
- **Interactive Charts**: Hover untuk detail data
- **Confidence Intervals**: Visual range untuk uncertainty

### Mobile Optimization
- Bottom navigation (70px fixed)
- Touch-friendly buttons (48px min height)
- Horizontal scroll tables
- No horizontal overflow
- Font sizes optimized (16px inputs - anti zoom)

## 📝 API Endpoints (Flask)

```
GET  /api/health                - Health check
GET  /api/train                 - Train ML model
GET  /api/predict               - Revenue forecast
GET  /api/historical            - Get historical data
GET  /api/inventory-prediction  - Inventory forecast
POST /api/chatbot               - Chat conversation
GET  /api/chatbot/reload        - Reload FAQ
```

## 👨‍💻 Development Team

**Kelompok 2 - 4IA19**
- Project: PPPL
- Repository: [GitHub](https://github.com/moruu1/4IA19_Kelompok2_ApikLaundry)

## 📄 License

Private - Academic Project

## 📞 Support

Untuk pertanyaan atau issue, silakan buka GitHub Issues.

---

**Last Updated**: Januari 22, 2026
