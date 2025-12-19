import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load env agar bisa baca DATABASE_URL
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Membuka koneksi ke PostgreSQL Supabase"""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"❌ Gagal konek ke DB: {e}")
        return None

def init_db():
    """Membuat tabel jika belum ada"""
    conn = get_connection()
    if conn:
        c = conn.cursor()
        # Perhatikan: Kita pakai SERIAL untuk id otomatis
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                date TIMESTAMP,
                item TEXT,
                category TEXT,
                amount INTEGER,
                type TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Database PostgreSQL siap/terhubung!")

def save_transaction(user_id, item, category, amount, type="expense"):
    """Menyimpan transaksi baru"""
    conn = get_connection()
    if conn:
        c = conn.cursor()
        date_now = datetime.now()
        
        # PERHATIKAN: Gunakan %s untuk PostgreSQL, bukan ?
        c.execute('''
            INSERT INTO transactions (user_id, date, item, category, amount, type)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, date_now, item, category, amount, type))
        
        conn.commit()
        conn.close()
        print(f"💾 Disimpan {user_id}: {item}")

def get_summary(user_id):
    """Mengambil total pengeluaran"""
    conn = get_connection()
    summary = {"income": 0, "expense": 0}

    if conn:
        c = conn.cursor()
        
        # Filter WHERE user_id = ...
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='expense' AND user_id=%s", (user_id,))
        row_exp = c.fetchone()
        if row_exp and row_exp[0]:
            summary['expense'] = row_exp[0]

        c.execute("SELECT SUM(amount) FROM transactions WHERE type='income' AND user_id=%s", (user_id,))
        row_inc = c.fetchone()
        if row_inc and row_inc[0]:
            summary['income'] = row_inc[0]
            
        conn.close()

    return summary


# Inisialisasi tabel saat file dijalankan
if __name__ == "__main__":
    init_db()