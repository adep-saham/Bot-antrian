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
    # Argumen wajib untuk lingkungan Cloud/Docker
    options.add_argument("--headless=new") # Gunakan mode headless terbaru
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    # SANGAT PENTING: Jangan masukkan path apapun di sini. 
    # Selenium akan otomatis mencari chromium-driver dari packages.txt
    return webdriver.Chrome(options=options)

# --- SOLVER CAPTCHA MATEMATIKA ---
def solve_math(text):
    try:
        # Mencari angka-angka dalam teks
        nums = [int(s) for s in re.findall(r'\d+', text)]
        if len(nums) < 2: return None
        
        # Deteksi operasi
        if any(x in text for x in ["tambah", "ditambah", "+"]): return nums[0] + nums[1]
        if any(x in text for x in ["kurang", "dikurangi", "-"]): return nums[0] - nums[1]
        if any(x in text for x in ["kali", "dikali", "x", "*"]): return nums[0] * nums[1]
        if any(x in text for x in ["bagi", "dibagi", "/"]): return nums[0] // nums[1] if nums[1] != 0 else 0
    except:
        return None
    return None

st.title("🤖 Bot Antrean Logam Mulia")

user_id = st.text_input("Email / NIK")
password = st.text_input("Password", type="password")

if st.button("Jalankan Bot"):
    if not user_id or not password:
        st.error("Isi Email dan Password dulu!")
    else:
        with st.spinner("Membuka browser..."):
            driver = get_driver()
            try:
                driver.get("https://antrean.logammulia.com/login")
                wait = WebDriverWait(driver, 15)

                # 1. Login Form
                wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(user_id)
                driver.find_element(By.NAME, "password").send_keys(password)

                # 2. Captcha Matematika
                try:
                    label = driver.find_element(By.XPATH, "//label[contains(text(), 'hasil') or contains(text(), 'Berapa')]")
                    jawaban = solve_math(label.text)
                    if jawaban is not None:
                        # Masukkan jawaban ke input field
                        input_ans = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Jawaban')]")
                        input_ans.send_keys(str(jawaban))
                        st.info(f"🔢 Menjawab Matematika: {label.text} = {jawaban}")
                except:
                    st.warning("Captcha matematika tidak ditemukan.")

                # 3. Klik Submit
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(5)
                
                # Cek Dashboard
                if "login" not in driver.current_url.lower():
                    st.success("✅ Berhasil Login!")
                else:
                    st.error("❌ Gagal Login. Cek screenshot di bawah.")
                    driver.save_screenshot("debug.png")
                    st.image("debug.png")

            except Exception as e:
                st.error(f"Error Detil: {e}")
            finally:
                driver.quit()
