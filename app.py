import streamlit as st
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- KONFIGURASI BROWSER ---
def get_driver():
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # Menambahkan User-Agent agar tidak terlalu terlihat seperti bot
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # Di Streamlit Cloud, driver sudah terinstall di PATH jika ada packages.txt
    return webdriver.Chrome(options=options)

# --- FUNGSI SOLVER MATEMATIKA ---
def solve_math_captcha(teks_soal):
    # Mengambil semua angka dari teks menggunakan Regex
    angka = [int(s) for s in re.findall(r'\d+', teks_soal)]
    if len(angka) < 2:
        return None
    
    # Logika deteksi operator
    if any(op in teks_soal for op in ["tambah", "ditambah", "+"]):
        return angka[0] + angka[1]
    elif any(op in teks_soal for op in ["kurang", "dikurangi", "-"]):
        return angka[0] - angka[1]
    elif any(op in teks_soal for op in ["kali", "dikali", "x", "*"]):
        return angka[0] * angka[1]
    elif any(op in teks_soal for op in ["bagi", "dibagi", "/"]):
        return angka[0] // angka[1] if angka[1] != 0 else 0
    return None

# --- ANTARMUKA STREAMLIT ---
st.title("🤖 Bot Antrean Logam Mulia")
st.write("Masukkan detail login Anda. Bot akan mencoba menjawab captcha matematika secara otomatis.")

user_id = st.text_input("Email / NIK")
password = st.text_input("Password", type="password")

if st.button("Jalankan Bot"):
    if not user_id or not password:
        st.error("Mohon isi ID dan Password!")
    else:
        with st.spinner("Sedang mencoba login..."):
            driver = get_driver()
            try:
                driver.get("https://antrean.logammulia.com/login")
                wait = WebDriverWait(driver, 15)

                # 1. Input Email & Password
                email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
                email_field.send_keys(user_id)
                
                pass_field = driver.find_element(By.NAME, "password")
                pass_field.send_keys(password)

                # 2. Tangani Captcha Matematika
                try:
                    # Mencari label yang berisi teks soal matematika
                    captcha_label = driver.find_element(By.XPATH, "//label[contains(text(), 'hasil') or contains(text(), 'Berapa')]")
                    soal = captcha_label.text
                    jawaban = solve_math_captcha(soal)
                    
                    if jawaban is not None:
                        # Mencari input field untuk jawaban
                        input_jawaban = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Jawaban') or @name='jawaban_captcha']")
                        input_jawaban.send_keys(str(jawaban))
                        st.info(f"🔢 Captcha Terdeteksi: {soal} -> Bot menjawab: **{jawaban}**")
                except Exception as e:
                    st.warning("Tidak mendeteksi captcha matematika atau gagal menjawab.")

                # 3. Klik Login
                # Catatan: reCAPTCHA (I'm not a robot) mungkin tetap akan menghalangi di sini
                login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                login_btn.click()

                time.sleep(5) 
                
                # Cek Keberhasilan
                if "login" not in driver.current_url.lower():
                    st.success("✅ Berhasil Login!")
                else:
                    driver.save_screenshot("halaman_akhir.png")
                    st.error("❌ Gagal Login. Mungkin reCAPTCHA perlu diklik manual atau data salah.")
                    st.image("halaman_akhir.png", caption="Tampilan terakhir browser")

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
            finally:
                driver.quit()
