import pandas as pd
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Load Konfigurasi Environment
load_dotenv()
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(URL, KEY)

class LaundryChatbot:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.df = None
        self.tfidf_matrix = None
        # Muat data saat bot pertama kali dinyalakan
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Mengambil data dari tabel 'faq' di Supabase"""
        print("🤖 Sedang memuat data otak chatbot...")
        try:
            # Sesuaikan nama tabel di sini: 'faq'
            response = supabase.table('faq').select('*').execute()
            data = response.data
            
            if data:
                self.df = pd.DataFrame(data)
                
                # Preprocessing: Bersihkan kolom 'pertanyaan'
                # Kita buat kolom baru 'clean_question' untuk perhitungan matematikanya
                self.df['clean_question'] = self.df['pertanyaan'].apply(self.preprocess)
                
                # TRAINING: Ubah teks pertanyaan jadi Vektor Angka (TF-IDF)
                self.tfidf_matrix = self.vectorizer.fit_transform(self.df['clean_question'])
                
                print(f"✅ Berhasil memuat {len(data)} data FAQ.")
            else:
                print("⚠️ Tabel 'faq' kosong! Bot tidak punya otak.")
                
        except Exception as e:
            print(f"❌ Error saat load data: {e}")

    def preprocess(self, text):
        """Membersihkan teks (huruf kecil, hapus tanda baca)"""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text) # Hapus simbol aneh
        return text

    def reload_data(self):
        """Reload FAQ data from Supabase"""
        print("🔄 Reloading FAQ data...")
        self.load_knowledge_base()
        return len(self.df) if self.df is not None else 0

    def get_response(self, user_input):
        """Mencari jawaban terbaik berdasarkan kemiripan"""
        if self.df is None or self.df.empty:
            return "Maaf, sistem sedang offline."

        # 1. Bersihkan input user
        clean_input = self.preprocess(user_input)
        
        # 2. Ubah input user jadi Vektor (pakai rumus yang sama dengan database)
        input_vector = self.vectorizer.transform([clean_input])
        
        # 3. Hitung Jarak Kemiripan (Cosine Similarity)
        similarity_scores = cosine_similarity(input_vector, self.tfidf_matrix)
        
        # Ambil skor tertinggi
        best_score_index = similarity_scores.argmax()
        best_score = similarity_scores[0, best_score_index]
        
        # Debugging: Lihat di terminal bot nebak apa
        print(f"Input: '{user_input}' | Mirip dgn: '{self.df.iloc[best_score_index]['pertanyaan']}' | Skor: {best_score:.2f}")

        # 4. Logika Threshold (Batas Minimal Kemiripan)
        # Jika kemiripan di bawah 0.55 (55%), bot nyerah
        if best_score < 0.55:
            return "Maaf, saya tidak mengerti pertanyaan Anda. 🙏\n\nJika ada yang ingin ditanyakan lebih lanjut, silakan hubungi Admin via WhatsApp:\n👉 0816-1709-8435"
        
        # 5. Jika paham, kembalikan isi kolom 'jawaban'
        return self.df.iloc[best_score_index]['jawaban']

# --- Blok Test Manual (Bisa dijalankan langsung untuk ngetes) ---
if __name__ == "__main__":
    bot = LaundryChatbot()
    
    # Contoh tes
    print("\n--- Test Chat ---")
    print("User: harganya brp?")
    print("Bot :", bot.get_response("harganya brp?"))
    
    print("\nUser: lokasi dimana?")
    print("Bot :", bot.get_response("lokasi dimana?"))
    
    print("\nUser: resep nasi goreng")
    print("Bot :", bot.get_response("resep nasi goreng"))