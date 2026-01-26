# 🚀 PANDUAN DEPLOYMENT FINAL (Vercel)

Anda akan men-deploy 2 Project terpisah dari 1 Repository yang sama:
1. **Frontend (Web App)**: Vue.js
2. **Backend (API)**: Python Flask

---

## 🛑 PERSIAPAN

Pastikan 3 hal ini sudah siap di notepad Anda:
1. **URL Supabase**: `https://....supabase.co`
2. **Anon Key Supabase**: `eyJ...` (Untuk Frontend)
3. **Service Role Key Supabase**: `eyJ...` (Untuk Backend - Cari di Settings > API)
4. **Groq API Key**: `gsk_...`

---

## 1️⃣ LANGKAH 1: DEPLOY FRONTEND

**Tujuan**: Agar website bisa dibuka.

1. Buka [Vercel Dashboard](https://vercel.com/dashboard).
2. Klik **Add New...** -> **Project**.
3. Import Repository: `GirvanAzharXD/4IA19_Kelompok2_ApikLaundry`.
4. **Konfigurasi Project**:
   - **Framework Preset**: `Vite` (Biarkan auto-detect).
   - **Root Directory**: `.` (Biarkan default).
5. **Environment Variables** (Tambahkan ini):
   - `VITE_SUPABASE_URL`: (Isi URL Supabase)
   - `VITE_SUPABASE_KEY`: (Isi Anon Key)
   - `VITE_ML_API_URL`: `https://google.com` (Isi dummy dulu agar tidak error build, nanti diupdate).
6. Klik **Deploy**.
   - *Tunggu sampai status "Ready" (Hijau).*
   - *Copy URL Frontend Anda (misal: `apik-laundry.vercel.app`).*

> **Kenapa sebelumnya Error?** 
> Karena Vercel mencoba build API Python di dalam Frontend. Sekarang sudah aman karena ada file `.vercelignore`.

---

## 2️⃣ LANGKAH 2: DEPLOY BACKEND (API)

**Tujuan**: Agar Chatbot & Prediksi ML jalan.

1. Kembali ke Dashboard Vercel.
2. Klik **Add New...** -> **Project** (Lagi).
3. Import Repository yang **SAMA PERSIS**: `GirvanAzharXD/4IA19_Kelompok2_ApikLaundry`.
4. **Konfigurasi Project** (⚠️ PENTING):
   - **Project Name**: Ubah nama, misal `apik-laundry-api`.
   - **Root Directory**: Klik **Edit** -> Pilih folder **`api`**.
   - **Framework Preset**: Pilih **Other**.
5. **Environment Variables**:
   - `SUPABASE_URL`: (Isi URL Supabase)
   - `SUPABASE_KEY`: (Isi **Service Role Key**) ⚠️ Beda dengan frontend!
   - `GROQ_API_KEY`: (Isi API Key Groq)
6. Klik **Deploy**.
   - *Tunggu proses build Python (agak lama, ~2 menit).*
   - *Copy URL Backend Anda (misal: `apik-laundry-api.vercel.app`).*

---

## 3️⃣ LANGKAH 3: SAMBUNGKAN KEDUANYA

**Tujuan**: Agar Frontend bisa memanggil Backend.

1. Buka Project **Frontend** di Vercel tadi.
2. Masuk ke **Settings** -> **Environment Variables**.
3. Edit variable `VITE_ML_API_URL`:
   - Hapus link dummy google tadi.
   - Isi dengan URL Backend dari Langkah 2 (misal: `https://apik-laundry-api.vercel.app`).
4. Klik **Save**.
5. Pergi ke tab **Deployments**.
6. Klik titik tiga (⋮) di deployment paling atas -> **Redeploy**.
   - *Ini wajib agar frontend "tahu" alamat backend yang baru.*

---

## ✅ SELESAI! CARA CEK:

1. Buka Website Frontend.
2. Coba fitur **Chatbot**. Jika membalas = Sukses.
3. Coba fitur **Prediksi**. Jika grafik muncul = Sukses.
