# Optimized: No Pandas dependency for faster Vercel cold starts
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
        """Generate inventory stock predictions based on usage patterns"""
        
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

            # --- TAHAP 2: HITUNG BEBAN KERJA (NATIVE PYTHON) ---
            # Data transaksi: list of dicts [{'tanggal_masuk': '...', 'service_id': ..., 'jumlah_unit': ...}]
            transactions = trx_res.data
            
            # Group by Date & Service ID
            # Structure: {(date, service_id): total_qty}
            daily_service_load = {}
            
            from datetime import datetime
            
            for trx in transactions:
                # Parse date string "YYYY-MM-DD..." to date object
                t_date = trx['tanggal_masuk'].split('T')[0] # Ambil tanggal saja
                svc_id = trx['service_id']
                qty = float(trx['jumlah_unit'] or 0)
                
                key = (t_date, svc_id)
                if key not in daily_service_load:
                    daily_service_load[key] = 0
                daily_service_load[key] += qty
            
            # Hitung Rata-rata Harian per Service ID
            # Structure: {service_id: {'total_qty': X, 'days_count': Y}}
            service_stats = {}
            
            for (t_date, svc_id), daily_total in daily_service_load.items():
                if svc_id not in service_stats:
                    service_stats[svc_id] = {'total_qty': 0, 'data_points': 0}
                
                service_stats[svc_id]['total_qty'] += daily_total
                service_stats[svc_id]['data_points'] += 1
            
            # Final Average Dictionary: {service_id: avg_daily_qty}
            avg_load_per_service = {}
            for svc_id, stats in service_stats.items():
                avg_load_per_service[svc_id] = stats['total_qty'] / stats['data_points'] if stats['data_points'] > 0 else 0
            
            # --- TAHAP 3: AMBIL DATA BOM & INVENTORY ---
            bom_res = supabase.table('service_bom') \
                .select('service_id, jumlah_dipakai_per_unit, inventory_items(id_inventory_item, nama_barang, stok_sisa, unit)') \
                .execute()
            
            bom_data = bom_res.data
            
            # --- TAHAP 4: KALKULASI PENGGUNAAN BAHAN ---
            inventory_report = {} 

            for item in bom_data:
                srv_id = item['service_id']
                usage_rate = float(item['jumlah_dipakai_per_unit'] or 0)
                
                # Ambil data nested dari inventory_items
                inv_data = item['inventory_items']
                if not inv_data: continue 

                inv_id = inv_data['id_inventory_item']
                inv_name = inv_data['nama_barang']
                current_stock = float(inv_data['stok_sisa'] or 0)
                unit = inv_data['unit']
                
                # Cek apakah ada transaksi untuk service ini?
                if srv_id in avg_load_per_service:
                    daily_qty = avg_load_per_service[srv_id]
                    
                    # Rata2 Order x Resep Pemakaian
                    daily_material_usage = daily_qty * usage_rate
                    
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
                if usage > 0.0001:
                    days_left = stok / usage
                else:
                    days_left = 999 
                
                # Tentukan Batas Minimum (Safety Stock)
                if unit == 'Tabung':
                    min_stock = 3  
                    critical_stock = 1  
                elif unit == 'Liter' or unit == 'Kg':
                    min_stock = 5  
                    critical_stock = 2  
                else:
                    min_stock = 10
                    critical_stock = 5
                
                # Tentukan Status Logika
                status = "Aman ✅"
                
                if days_left < 3:
                    status = "KRITIS 🚨"
                elif days_left < 7:
                    status = "Warning (< 7 hari) ⚠️"
                elif stok <= critical_stock:
                    status = "KRITIS 🚨"
                elif stok <= min_stock:
                    status = "Warning (stok menipis) ⚠️"
                
                final_results.append({
                    "nama_barang": name,
                    "stok_sekarang": round(stok, 2),
                    "pemakaian_harian_rata2": round(usage, 4),
                    "satuan": unit,
                    "estimasi_habis": f"{int(days_left)} hari lagi",
                    "status": status
                })
            
            return final_results

        except Exception as error:
            # Force fresh deploy
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Inventory Prediction Error: {error}\n{error_trace}")
            return {"error": f"Inventory prediction failed: {str(error)}"}

# --- BLOCK TEST MANUAL (Bisa dijalankan langsung di terminal) ---
if __name__ == "__main__":
    predictor = InventoryPredictor()
    result = predictor.get_prediction()
    print(json.dumps(result, indent=2))