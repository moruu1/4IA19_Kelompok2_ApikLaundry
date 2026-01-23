import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv
from groq import Groq

# 1. Load Konfigurasi Environment
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class LaundryChatbot:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.groq_client = Groq(api_key=GROQ_API_KEY)
        self.context = ""
        # Muat pengetahuan saat inisialisasi
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Mengambil data dari tabel 'faq' di Supabase dan format jadi string konteks"""
        print("🤖 Sedang memuat data otak chatbot (Groq Context)...")
        try:
            response = self.supabase.table('faq').select('*').execute()
            data = response.data
            
            if data:
                # Format data menjadi string konteks yang mudah dibaca LLM
                context_lines = ["Berikut adalah informasi resmi tentang APIK Laundry:"]
                for item in data:
                    q = item.get('pertanyaan', '')
                    a = item.get('jawaban', '')
                    context_lines.append(f"- Q: {q}\n  A: {a}")
                
                self.context = "\n".join(context_lines)
                print(f"✅ Berhasil memuat {len(data)} item FAQ ke konteks Groq.")
            else:
                self.context = "Maaf, data FAQ kosong saat ini."
                print("⚠️ Tabel 'faq' kosong!")
                
        except Exception as e:
            print(f"❌ Error saat load data: {e}")
            self.context = "Terjadi kesalahan saat memuat data laundry."

    def get_response(self, user_input):
        """Mengirim pertanyaan ke Groq Llama 3"""
        if not GROQ_API_KEY:
            return "Maaf, API Key Groq belum dikonfigurasi."

        try:
            # System prompt untuk mengarahkan gaya bicara bot
            system_prompt = (
                "Anda adalah asisten CS 'APIK Laundry' yang ramah dan membantu. "
                "Gunakan Bahasa Indonesia yang sopan. "
                "Jawab pertanyaan pelanggan HANYA berdasarkan informasi berikut ini. "
                "Jika informasi tidak ada di konteks, arahkan ke Admin WhatsApp 0816-1709-8435. "
                "Jangan mengarang harga atau layanan yang tidak tertulis.\n\n"
                f"{self.context}"
            )

            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.5,
                max_tokens=300,
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            print(f"Error Groq: {e}")
            return "Maaf, sedang ada gangguan pada sistem AI kami. Silakan hubungi via WhatsApp."

# --- Blok Test Manual ---
if __name__ == "__main__":
    bot = LaundryChatbot()
    
    print("\n--- Test Chat Groq ---")
    print("User: harganya brp?")
    print("Bot :", bot.get_response("harganya brp?"))
    
    print("\nUser: lokasi dimana?")
    print("Bot :", bot.get_response("lokasi dimana?"))
