import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL, DOWNLOAD_DIR, DOWNLOADS_DIR
from gpt_rename import generate_filename

# === Sabit Kategori Tanımı ===
KATEGORI_ADI = "Eğitim ve Öğrenci İşleri"
KATEGORI_SLUG = "egitim_ve_ogrenci_isleri"
KATEGORI_KLASORU = os.path.join(DOWNLOAD_DIR, KATEGORI_SLUG)

if not os.path.exists(KATEGORI_KLASORU):
    os.makedirs(KATEGORI_KLASORU)

# === Tarayıcı başlat ===
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": DOWNLOADS_DIR}
options.add_experimental_option("prefs", prefs)
service = Service(executable_path=os.path.join(os.getcwd(), "chromedriver"))
driver = webdriver.Chrome(service=service, options=options)
driver.get(BASE_URL)

# === KATEGORİ SEÇ ===
try:
    kategori_id = 7  # Eğitim ve Öğrenci İşleri
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "dropdownMenu3"))
    )
    dropdown_button.click()
    time.sleep(1)

    kategori_xpath = f"//button[contains(@onclick, 'filterRegulations({kategori_id},')]"
    kategori_buton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, kategori_xpath))
    )
    actions = ActionChains(driver)
    actions.move_to_element(kategori_buton).click().perform()

    print(f"'{KATEGORI_ADI}' kategorisi başarıyla seçildi.")
except Exception as e:
    print("Kategori seçilemedi:", e)
    driver.quit()
    exit()

# === SAYFA SAYFA GEZ ===
sayfa = 1
while True:
    time.sleep(2)
    print(f"Sayfa {sayfa} işleniyor...")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mevzuatBody tr"))
        )
        rows = driver.find_elements(By.CSS_SELECTOR, "#mevzuatBody tr")
    except Exception as e:
        print(f"Tablo yüklenemedi: {e}")
        break

    for row in rows:
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 4:
                continue

            belge_adi = cols[1].text.strip()
            print(f"GPT’ye gönderiliyor: {belge_adi}")
            dosya_adi = generate_filename(belge_adi)
            dosya_yolu = os.path.join(KATEGORI_KLASORU, f"{dosya_adi}.pdf")

            if os.path.exists(dosya_yolu):
                continue

            # === Butona tıkla ===
            link = row.find_element(By.CSS_SELECTOR, "a.btn-pdf")
            driver.execute_script("arguments[0].removeAttribute('target');", link)
            link.click()
            time.sleep(5)  # indirme için bekleme süresi

            # === Dosyayı taşı ===
            indirilen_dosya = max(
                [os.path.join(DOWNLOADS_DIR, f) for f in os.listdir(DOWNLOADS_DIR) if f.endswith(".pdf")],
                key=os.path.getctime,
                default=None
            )

            if indirilen_dosya and os.path.exists(indirilen_dosya):
                shutil.move(indirilen_dosya, dosya_yolu)
                print(f"Taşındı: {dosya_yolu}")
            else:
                print("Dosya bulunamadı.")

        except Exception as e:
            print(f"Hata oluştu: {e}")
            continue

    try:
        ileri_buton = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.pagination li a[aria-label='Next']"))
        )
        ileri_buton.click()
        sayfa += 1
    except Exception as e:
        print("Sayfa sonu ya da ileri butonu bulunamadı:", e)
        break
