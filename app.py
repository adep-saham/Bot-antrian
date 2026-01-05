import streamlit as st
import time  # <--- Tambahkan ini
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
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
    
    # Langsung return di sini
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options
    )

# --- ANTARMUKA STREAMLIT ---
st.title("🤖 Bot Antrean Logam Mulia")
st.write("Masukkan detail login Anda untuk memulai pengecekan.")

user_id = st.text_input("Email / NIK")
password = st.text_input("Password", type="password")

if st.button("Jalankan Bot"):
    if not user_id or not password:
        st.error("Mohon isi ID dan Password!")
    else:
        with st.spinner("Sedang mencoba login ke antrean.logammulia.com..."):
            driver = get_driver()
            try:
                driver.get("https://antrean.logammulia.com/login")
                wait = WebDriverWait(driver, 15)

                # Proses Login
                email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
                email_field.send_keys(user_id)
                
                pass_field = driver.find_element(By.NAME, "password")
                pass_field.send_keys(password)
                
                login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                login_btn.click()

                # Cek Keberhasilan
                time.sleep(5) 
                
                if "login" not in driver.current_url.lower():
                    st.success("✅ Berhasil Login!")
                    st.info(f"Halaman saat ini: {driver.title}")
                else:
                    # Ambil screenshot jika gagal untuk melihat apakah ada CAPTCHA
                    driver.save_screenshot("error_login.png")
                    st.error("❌ Gagal Login. Mungkin ada CAPTCHA atau data salah.")
                    st.image("error_login.png", caption="Tampilan saat gagal login")

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
            finally:
                driver.quit()
