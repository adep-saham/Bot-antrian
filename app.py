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
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # FIX: Di Streamlit Cloud, kita tidak perlu ChromeDriverManager.
    # Selenium akan otomatis mencari 'chromedriver' yang diinstal via packages.txt
    return webdriver.Chrome(options=options)

# --- FUNGSI SOLVER MATEMATIKA ---
def solve_math_captcha(teks_soal):
    # Mengambil angka menggunakan regex
    angka = [int(s) for s in re.findall(r'\d+', teks_soal)]
    if len(angka) < 2:
        return None
    
    # Deteksi operasi matematika sederhana
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
st.write("Bot ini akan mencoba login dan menjawab captcha matematika.")

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
                    # Mencari teks soal matematika (biasanya di dalam label)
                    captcha_label = driver.find_element(By.XPATH, "//label[contains(text(), 'hasil') or contains(text(), 'Berapa')]")
                    soal = captcha_label.text
                    jawaban = solve_math_captcha(soal)
                    
                    if jawaban is not None:
                        # Mencari kotak input jawaban
                        input_jawaban = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Jawaban') or @name='jawaban_captcha']")
                        input_jawaban.send_keys(str(jawaban))
                        st.info(f"🔢 Captcha: {soal} -> Jawaban: **{jawaban}**")
                except:
                    st.warning("Captcha matematika tidak ditemukan/gagal dijawab.")

                # 3. Klik Login
                login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                login_btn.click()

                time.sleep(5) 
                
                # Cek Hasil
                if "login" not in driver.current_url.lower():
                    st.success("✅ Berhasil Login!")
                else:
                    driver.save_screenshot("debug_login.png")
                    st.error("❌ Gagal Login. Mungkin reCAPTCHA Google menghalangi atau data salah.")
                    st.image("debug_login.png", caption="Tampilan terakhir browser")

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
            finally:
                driver.quit()
