import psycopg2
import sys

# --- ISI DATA INI SECARA MANUAL (COPY DARI SUPABASE) ---

# 1. Host (Ambil dari connection string bagian setelah @ sampai sebelum :6543)
# Contoh: aws-0-ap-southeast-1.pooler.supabase.com
DB_HOST = "aws-1-ap-northeast-2.pooler.supabase.com" 

# 2. Port (Wajib 6543 untuk Pooler)
DB_PORT = "6543"

# 3. Database Name (Biasanya 'postgres')
DB_NAME = "postgres"

# 4. User (INI YANG KRUSIAL!)
# Cek connection string di Supabase. 
# Username adalah teks DI ANTARA 'postgresql://' DAN tanda titik dua ':'
# Contoh: postgres.xcaifefgodwcserngsyt
DB_USER = "postgres.xcaifefgodwcserngsyt"

# 5. Password (Tulis manual di sini)
DB_PASS = "ReihanMursyidi"

# ---------------------------------------------------------

print(f"🕵️ Mencoba menghubungkan ke:")
print(f"   Host: {DB_HOST}")
print(f"   User: {DB_USER}")
print(f"   Port: {DB_PORT}")
print("   Connecting...", end=" ")

try:
    connection = psycopg2.connect(
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    print("✅ BERHASIL! Password dan User benar.")
    print("   Sekarang kamu tahu masalahnya ada di cara penulisan URL di .env")
    connection.close()

except psycopg2.OperationalError as e:
    print("\n❌ GAGAL (Operational Error)")
    print(e)
    print("\n💡 TIPS:")
    print("1. Cek User. Untuk Pooler, user HARUS format 'postgres.idproject'")
    print("2. Cek apakah ini Password DATABASE, bukan password login Supabase?")

except Exception as e:
    print(f"\n❌ ERROR LAIN: {e}")