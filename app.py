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
    # Penyamaran agar tidak terdeteksi bot
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # PERBAIKAN: Langsung panggil webdriver.Chrome tanpa Service(ChromeDriverManager)
    return webdriver.Chrome(options=options)

def solve_math_captcha(teks_soal):
    angka = [int(s) for s in re.findall(r'\d+', teks_soal)]
    if len(angka) < 2: return None
    
    if any(op in teks_soal for op in ["tambah", "ditambah", "+"]): return angka[0] + angka[1]
    if any(op in teks_soal for op in ["kurang", "dikurangi", "-"]): return angka[0] - angka[1]
    if any(op in teks_soal for op in ["kali", "dikali", "x"]): return angka[0] * angka[1]
    if any(op in teks_soal for op in ["bagi", "dibagi", "/"]): return angka[0] // angka[1]
    return None

st.title("🤖 Bot Antrean Logam Mulia")

user_id = st.text_input("Email / NIK")
password = st.text_input("Password", type="password")

if st.button("Jalankan Bot"):
    if not user_id or not password:
        st.error("Isi data dulu!")
    else:
        with st.spinner("Proses Login..."):
            driver = get_driver()
            try:
                driver.get("https://antrean.logammulia.com/login")
                wait = WebDriverWait(driver, 15)

                # Input Login
                wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(user_id)
                driver.find_element(By.NAME, "password").send_keys(password)

                # Solver Matematika
                try:
                    label = driver.find_element(By.XPATH, "//label[contains(text(), 'hasil') or contains(text(), 'Berapa')]")
                    jawaban = solve_math_captcha(label.text)
                    if jawaban is not None:
                        driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Jawaban')]").send_keys(str(jawaban))
                        st.info(f"🔢 Captcha: {label.text} = {jawaban}")
                except:
                    st.warning("Captcha matematika tidak ditemukan.")

                # Klik Login
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(5)
                
                if "login" not in driver.current_url.lower():
                    st.success("✅ Berhasil!")
                else:
                    st.error("❌ Gagal. Cek screenshot di bawah.")
                    driver.save_screenshot("debug.png")
                    st.image("debug.png")

            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                driver.quit()
