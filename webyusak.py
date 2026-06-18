import streamlit as st
import json
import re
import smtplib
from email.mime.text import MIMEText
import time
import os
import pandas as pd
import random
import google.generativeai as genai

# --- KONFIGURASI AI ---
genai.configure(api_key="MASUKKAN_API_KEY_GEMINI_DISINI")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CLASS & FUNGSI DATABASE (Sama seperti sebelumnya) ---
class Mahasiswa:
    def __init__(self, nim, nama, email, jurusan, ipk):
        self.__nim = nim
        self.nama = nama
        self.email = email
        self.jurusan = jurusan
        self.ipk = float(ipk)
    def get_nim(self): return self.__nim
    def to_dict(self): return {"nim": self.__nim, "nama": self.nama, "email": self.email, "jurusan": self.jurusan, "ipk": self.ipk}

DATA_FILE = "data_mahasiswa.json"
def load_data():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        return [Mahasiswa(d['nim'], d['nama'], d['email'], d['jurusan'], d['ipk']) for d in data]

def save_data(mahasiswa_list):
    with open(DATA_FILE, "w") as f:
        json.dump([m.to_dict() for m in mahasiswa_list], f, indent=4)

# --- CSS AESTHETIC ---
def inject_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0b1120; color: #f1f5f9; }
        .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); }
        h1, h2 { color: #22d3ee; }
    </style>
    """, unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="Mahasiswa Academy", layout="wide")
    inject_css()
    
    if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
    if 'data' not in st.session_state: st.session_state['data'] = ...

    if not st.session_state['logged_in']:
        st.title("🎓 Login Mahasiswa Academy")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pwd == "12345":
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("Salah!")
        return

    st.sidebar.title("🧭 Navigasi")
    menu = st.sidebar.radio("Menu", ["📊 Dashboard", "🤖 Asisten AI", "➕ Tambah Data", "⚙️ Kelola", "🗃️ Data"])
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    data_mhs = st.session_state['data']

    if menu == "📊 Dashboard":
        st.title("📊 Ringkasan Data")
        if data_mhs:
            df = pd.DataFrame([m.to_dict() for m in data_mhs])
            st.metric("Total Mahasiswa", len(data_mhs))
            st.bar_chart(df.groupby('jurusan')['ipk'].mean())

    elif menu == "🤖 Asisten AI":
        st.title("🤖 Asisten Akademik AI")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        query = st.text_input("Tanya AI tentang kampus:")
        if st.button("Tanya"):
            response = model.generate_content(f"Kamu asisten akademik. Jawab singkat: {query}")
            st.info(response.text)
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ Tambah Data":
        with st.form("tambah"):
            nim = st.text_input("NIM")
            nama = st.text_input("Nama")
            jurusan = st.selectbox("Jurusan", ["Informatika", "Sistem Informasi"])
            ipk = st.slider("IPK", 0.0, 4.0, 3.0)
            if st.form_submit_button("Simpan"):
                data_mhs.append(Mahasiswa(nim, nama, "email@test.com", jurusan, ipk))
                save_data(data_mhs)
                st.success("Data Tersimpan!")

    elif menu == "⚙️ Kelola":
        st.title("⚙️ Kelola Data")
        for m in data_mhs:
            if st.button(f"Hapus {m.nama}"):
                st.session_state['data'].remove(m)
                save_data(st.session_state['data'])
                st.rerun()

    elif menu == "🗃️ Data":
        st.title("🗃️ Semua Data")
        st.table([m.to_dict() for m in data_mhs])

if __name__ == "__main__":
    main()