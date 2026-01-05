import streamlit as st
import time
import re
from selenium import webdriver
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
    
    # PERBAIKAN: Streamlit Cloud akan otomatis mendeteksi driver dari packages.txt
    return webdriver.Chrome(options=options)

# --- SOLVER CAPTCHA MATEMATIKA ---
def solve_math(text):
    angka = [int(s) for s in re.findall(r'\d+', text)]
    if len(angka) < 2: return None
    
    if any(op in text for op in ["tambah", "ditambah", "+"]): return angka[0] + angka[1]
    if any(op in text for op in ["kurang", "dikurangi", "-"]): return angka[0] - angka[1]
    if any(op in text for op in ["kali", "dikali", "x"]): return angka[0] * angka[1]
    if any(op in text for op in ["bagi", "dibagi", "/"]): return angka[0] // angka[1] if angka[1] != 0 else 0
    return None

st.title("🤖 Bot Antrean Logam Mulia")

user_id = st.text_input("Email / NIK")
password = st.text_input("Password", type="password")

if st.button("Jalankan Bot"):
    if not user_id or not password:
        st.error("Isi data login terlebih dahulu!")
    else:
        with st.spinner("Sedang memproses..."):
            driver = get_driver()
            try:
                driver.get("https://antrean.logammulia.com/login")
                wait = WebDriverWait(driver, 15)

                # Input Login
                wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(user_id)
                driver.find_element(By.NAME, "password").send_keys(password)

                # Selesaikan Captcha Matematika
                try:
                    label = driver.find_element(By.XPATH, "//label[contains(text(), 'hasil') or contains(text(), 'Berapa')]")
                    jawaban = solve_math(label.text)
                    if jawaban is not None:
                        input_captcha = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Jawaban')]")
                        input_captcha.send_keys(str(jawaban))
                        st.info(f"🔢 Menjawab Captcha: {label.text} = {jawaban}")
                except:
                    st.warning("Captcha matematika tidak ditemukan atau gagal dibaca.")

                # Klik Login
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(5)
                
                if "login" not in driver.current_url.lower():
                    st.success("✅ Berhasil Login!")
                else:
                    st.error("❌ Gagal Login. Cek screenshot di bawah.")
                    driver.save_screenshot("debug.png")
                    st.image("debug.png")

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
            finally:
                driver.quit()
