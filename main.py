import os
import json
import logging
from dotenv import load_dotenv
import psycopg2

# Library Telegram
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Library AI (Groq)
from groq import Groq

# Import Database buatan sendiri (PostgreSQL)
import database

# 1. KONFIGURASI ENV & LOGGING
load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Inisialisasi Client Groq
client = Groq(api_key=GROQ_API_KEY)

# 2. SYSTEM PROMPT (Instruksi Otak AI)
SYSTEM_PROMPT = """
Kamu adalah asisten pencatat keuangan pintar. 
Tugasmu adalah membaca pesan user dan MENGUBAHNYA menjadi format JSON.

Aturan Penting:
1. JANGAN banyak bicara. HANYA keluarkan output JSON valid.
2. Format JSON harus list of objects: [{"item": "...", "category": "...", "amount": 0, "type": "expense"}]
3. Kategori umum: Makanan, Transport, Belanja, Tagihan, Hiburan, Kesehatan, Pemasukan (jika income).
4. Jika user mencatat pemasukan (misal: gajian, dapat bonus), set "type": "income". Default adalah "expense".
5. Jika tidak ada transaksi keuangan di pesan user, kembalikan JSON kosong: []

Contoh User: "Beli bakso 15rb sama bayar parkir 2000"
Contoh Output:
[
  {"item": "Bakso", "category": "Makanan", "amount": 15000, "type": "expense"},
  {"item": "Parkir", "category": "Transport", "amount": 2000, "type": "expense"}
]
"""

# 3. FUNGSI HANDLER BOT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respon saat user ketik /start"""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Halo {user_name}! 👋\n\n"
        "Saya siap mencatat keuanganmu ke Cloud Database (PostgreSQL).\n"
        "Cukup ceritakan pengeluaranmu, misal:\n\n"
        "👉 *'Habis makan siang 25rb dan beli bensin 30rb'*\n"
        "👉 *'Gajian bulan ini 5.000.000'*\n\n"
        "Ketik /report untuk melihat total pengeluaran.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Otak utama: Terima Teks -> AI Extract -> Simpan DB"""
    user_text = update.message.text
    
    user_id = update.effective_user.id

    # 1. Kirim status 'Typing...' biar terlihat natural
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        # 2. Panggil AI (Groq)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-8b-instant", # Model cepat & hemat
            temperature=0, # 0 agar jawaban konsisten/fakta
        )
        
        ai_response = chat_completion.choices[0].message.content.strip()
        
        # 3. Bersihkan format JSON (kadang AI kasih ```json ... ```)
        if "```json" in ai_response:
            ai_response = ai_response.replace("```json", "").replace("```", "")
        
        # 4. Parsing string JSON ke Python List
        transactions = json.loads(ai_response)

        # Jika AI bilang tidak ada transaksi (list kosong)
        if not transactions:
            await update.message.reply_text("🤔 Saya tidak menemukan nominal uang atau nama barang di pesanmu.")
            return

        # 5. Simpan ke Database PostgreSQL
        response_msg = "✅ **Transaksi Berhasil Disimpan:**\n\n"
        
        for trx in transactions:
            # Panggil fungsi dari database.py
            database.save_transaction(
                user_id=user_id,
                item=trx['item'], 
                category=trx['category'], 
                amount=trx['amount'], 
                type=trx.get('type', 'expense')
            )
            
            # Format pesan balasan (Rp format)
            formatted_price = f"Rp {trx['amount']:,}".replace(",", ".")
            icon = "🔴" if trx.get('type') == 'expense' else "🟢"
            response_msg += f"{icon} **{trx['item']}**\n└ 📂 {trx['category']} : {formatted_price}\n"

        await update.message.reply_text(response_msg, parse_mode="Markdown")

    except json.JSONDecodeError:
        # Jaga-jaga kalau AI error generate JSON
        await update.message.reply_text("Maaf, saya bingung memproses datanya. Coba gunakan kalimat yang lebih jelas.")
        print(f"JSON Error: {ai_response}") # Print log error untuk debug
    
    except Exception as e:
        await update.message.reply_text("Terjadi kesalahan sistem.")
        print(f"System Error: {e}")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cek total Pemasukan, Pengeluaran, dan Sisa Saldo"""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    user_id = update.effective_user.id

    try:
        # Ambil data dari database (dictionary)
        data = database.get_summary(user_id)
        
        income = data['income']
        expense = data['expense']
        balance = income - expense # Rumus Saldo
        
        # Format angka jadi Rupiah (titik pemisah ribuan)
        str_income = f"Rp {income:,}".replace(",", ".")
        str_expense = f"Rp {expense:,}".replace(",", ".")
        str_balance = f"Rp {balance:,}".replace(",", ".")
        
        # Tentukan emoji saldo (Untung/Rugi)
        status_icon = "📈" if balance >= 0 else "📉"
        
        await update.message.reply_text(
            f"📊 **LAPORAN KEUANGAN**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **Pemasukan:** {str_income}\n"
            f"🔴 **Pengeluaran:** {str_expense}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{status_icon} **Sisa Saldo:** {str_balance}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text("Gagal mengambil data report.")
        print(f"Report Error: {e}")

# 4. RUNNER
def main():
    print("🤖 Bot Telegram Keuangan SIAP! (Connected to PostgreSQL)")
    
    if not TELEGRAM_TOKEN:
        print("❌ Error: TELEGRAM_TOKEN belum diisi di .env")
        return

    # Buat Aplikasi
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Daftarkan Handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Jalankan
    app.run_polling()

if __name__ == "__main__":
    main()