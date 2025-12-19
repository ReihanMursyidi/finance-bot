# 🤖 AI Financial Tracker Bot (Telegram)

**Bot Pencatat Keuangan Cerdas** yang mengubah percakapan natural menjadi data keuangan terstruktur menggunakan **Artificial Intelligence (Llama 3)** dan menyimpannya ke database **PostgreSQL**.

Bot ini dibangun dengan arsitektur modern menggunakan **FastAPI** dan **Uvicorn** agar kompatibel dengan platform deployment berbasis container seperti Hugging Face Spaces atau Docker.

## 🚀 Fitur Utama

* **🗣️ Natural Language Processing:** Cukup ketik _"Habis beli nasi padang 25rb dan es teh 5000"_, bot akan otomatis memisahkan item, harga, dan kategori.
* **🧠 AI-Powered (Groq):** Menggunakan model Llama-3-8b via Groq API untuk ekstraksi data yang super cepat dan akurat.
* **🗄️ Database Terintegrasi:** Semua transaksi disimpan secara aman di PostgreSQL (Supabase).
* **🔒 Multi-Tenant / Multi-User:** Data antar pengguna terisolasi (User A tidak bisa melihat data User B).
* **📊 Laporan Keuangan:** Fitur `/report` untuk melihat total pemasukan, pengeluaran, dan sisa saldo secara realtime.

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **AI Model:** Llama 3 (via Groq API)
* **Backend Framework:** FastAPI & Uvicorn (untuk manajemen webhook/polling & health check)
* **Database:** Supabase (PostgreSQL)
* **Interface:** Python-Telegram-Bot

## 📂 Struktur Project

