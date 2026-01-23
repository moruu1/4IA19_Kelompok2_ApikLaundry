import pandas as pd
import os
import json
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# 1. Load Environment Variables (Handled by config.py)
URL = SUPABASE_URL
KEY = SUPABASE_KEY

# Inisialisasi Client Supabase
supabase: Client = create_client(URL, KEY)

class InventoryPredictor:
    def get_prediction(self):
        print("📦 Memulai Prediksi Stok Inventaris (Moving Average)...")
        
        try:
            # --- TAHAP 1: AMBIL DATA TRANSAKSI ---
            # Mengambil 100 transaksi terakhir untuk analisis beban kerja
            trx_res = supabase.table('transactions') \
                .select('tanggal_masuk, service_id, jumlah_unit') \
                .order('tanggal_masuk', desc=True) \
                .limit(100) \
                .execute()
                
            if not trx_res.data:
                return {"error": "Data transaksi kosong. Belum bisa prediksi."}

            # Buat DataFrame Pandas
            df_trx = pd.DataFrame(trx_res.data)
            df_trx['tanggal_masuk'] = pd.to_datetime(df_trx['tanggal_masuk'])
            
            # --- TAHAP 2: HITUNG BEBAN KERJA (MOVING AVERAGE) ---
            # a. Kelompokkan per Hari dan per Layanan (Total Qty hari itu)
            df_daily = df_trx.groupby([df_trx['tanggal_masuk'].dt.date, 'service_id'])['jumlah_unit'].sum().reset_index()
            
            # b. Hitung Rata-rata Harian (Moving Average) untuk setiap Service ID
            # Contoh: Service ID 1 (Cuci Kiloan) rata-rata order 50kg/hari
            avg_load_per_service = df_daily.groupby('service_id')['jumlah_unit'].mean().reset_index()
            avg_load_per_service.columns = ['service_id', 'avg_daily_qty']
            
            print(f"✅ Analisis beban kerja harian selesai. Service terdeteksi: {len(avg_load_per_service)}")

            # --- TAHAP 3: AMBIL DATA BOM & INVENTORY ---
            # Join Tabel: service_bom -> inventory_items
            # Kita ambil resep untuk tahu Service A butuh Bahan B berapa banyak
            bom_res = supabase.table('service_bom') \
                .select('service_id, jumlah_dipakai_per_unit, inventory_items(id_inventory_item, nama_barang, stok_sisa, unit)') \
                .execute()
            
            bom_data = bom_res.data
            
            # --- TAHAP 4: KALKULASI PENGGUNAAN BAHAN ---
            inventory_report = {} 

            for item in bom_data:
                srv_id = item['service_id']
                usage_rate = item['jumlah_dipakai_per_unit'] # Resep (misal: 0.067 Liter/kg)
                
                # Ambil data nested dari inventory_items
                inv_data = item['inventory_items']
                if not inv_data: continue # Skip jika relasi putus/kosong

                inv_id = inv_data['id_inventory_item']
                inv_name = inv_data['nama_barang']
                current_stock = float(inv_data['stok_sisa']) # Pastikan float
                unit = inv_data['unit'] # Liter, Kg, Tabung
                
                # Cek apakah ada transaksi untuk service ini?
                service_load = avg_load_per_service[avg_load_per_service['service_id'] == srv_id]
                
                if not service_load.empty:
                    # Ambil rata-rata order harian untuk service ini
                    daily_qty = service_load.iloc[0]['avg_daily_qty']
                    
                    # RUMUS SAKTI: Rata2 Order x Resep Pemakaian
                    # Contoh: 50kg cucian x 0.067 Liter = 3.35 Liter/hari
                    daily_material_usage = daily_qty * usage_rate
                    
                    # Masukkan ke report dictionary (Akumulasi)
                    # Karena 1 bahan (misal Plastik) bisa dipakai di Service 1, 2, dan 3.
                    if inv_name not in inventory_report:
                        inventory_report[inv_name] = {
                            "stok": current_stock,
                            "daily_usage": 0,
                            "unit": unit
                        }
                    inventory_report[inv_name]["daily_usage"] += daily_material_usage

            # --- TAHAP 5: FORMAT HASIL & STATUS WARNING ---
            final_results = []
            
            for name, data in inventory_report.items():
                usage = data['daily_usage']
                stok = data['stok']
                unit = data['unit']
                
                # Hitung Estimasi Hari (Days of Supply)
                # Hindari pembagian nol
                if usage > 0.0001:
                    days_left = stok / usage
                else:
                    days_left = 999 # Awet selamanya kalau gak dipake
                
                # Tentukan Batas Minimum (Safety Stock) Dinamis
                # CATATAN: Logika ini disesuaikan dengan frontend (stok <= 10 = warning)
                if unit == 'Tabung':
                    min_stock = 3  # Gas warning kalau sisa <= 3 tabung
                    critical_stock = 1  # Kritis kalau tinggal 1
                elif unit == 'Liter' or unit == 'Kg':
                    min_stock = 5  # Chemical/Plastik warning kalau <= 5
                    critical_stock = 2  # Kritis kalau tinggal <= 2
                else:
                    min_stock = 10
                    critical_stock = 5
                
                # Tentukan Status Logika (prioritas: days_left > stok absolut)
                status = "Aman ✅"
                
                # 1. Cek dulu estimasi hari (prioritas tertinggi)
                if days_left < 3:
                    status = "KRITIS 🚨"
                elif days_left < 7:
                    status = "Warning (< 7 hari) ⚠️"
                # 2. Baru cek stok absolut jika days_left >= 7
                elif stok <= critical_stock:
                    status = "KRITIS 🚨"
                elif stok <= min_stock:
                    status = "Warning (stok menipis) ⚠️"
                
                # Rapikan data untuk JSON
                final_results.append({
                    "nama_barang": name,
                    "stok_sekarang": round(stok, 2),
                    "pemakaian_harian_rata2": round(usage, 4), # 4 desimal biar gas/plastik kelihatan detail
                    "satuan": unit,
                    "estimasi_habis": f"{int(days_left)} hari lagi",
                    "status": status
                })
            
            print("✅ Prediksi selesai.")
            return final_results

        except Exception as e:
            print(f"❌ Error Inventory: {e}")
            return {"error": str(e)}

# --- BLOCK TEST MANUAL (Bisa dijalankan langsung di terminal) ---
if __name__ == "__main__":
    predictor = InventoryPredictor()
    result = predictor.get_prediction()
    print(json.dumps(result, indent=2))