import os
import time
import shutil
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL, DOWNLOAD_DIR, DOWNLOADS_DIR

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
        # === Sayfa yüklensin diye loading overlay'in kaybolmasını bekle
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "loadingOverlay"))
    )

    # === Kategori dropdown'u tıklanabilir olunca devam et
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
    
with open("mevzuatlar_egitim_ogrenci_isleri_tam.json", "r", encoding="utf-8") as f:
    veri = json.load(f)
    
isim_haritasi = {}
for item in veri:
            # Eski ve yeni key farklılıklarına göre kontrol
    if isinstance(item, dict):
        key = item.get("original") or item.get("title")
        val = item.get("filename") or item.get("file_name", "dosya_adi_bulunamadi")
        if key:
            isim_haritasi[key.strip()] = val.strip()

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
                    

    row_count = len(driver.find_elements(By.CSS_SELECTOR, "#mevzuatBody tr"))
    for i in range(row_count):
        try:
            # her seferinde elemanları tekrar çek
            rows = driver.find_elements(By.CSS_SELECTOR, "#mevzuatBody tr")
            row = rows[i]
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 4:
                continue
            belge_adi = cols[1].text.strip()
            dosya_adi = isim_haritasi.get(belge_adi, "dosya_adi_bulunamadi")
            dosya_yolu = os.path.join(KATEGORI_KLASORU, f"{dosya_adi}.pdf")

            if os.path.exists(dosya_yolu):
                continue

            # === Sekmeye geçerek indirme ===
            original_window = driver.current_window_handle
            link = cols[3].find_element(By.CSS_SELECTOR, "a.btn-pdf")
            link.click()
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

            new_window = [w for w in driver.window_handles if w != original_window][0]
            driver.switch_to.window(new_window)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)

            # URL'den indir
            import requests
            response = requests.get(driver.current_url, verify=False)
            if response.status_code == 200:
                with open(dosya_yolu, "wb") as f:
                    f.write(response.content)
                print(f"İndirildi: {dosya_yolu}")
            else:
                print(f"İndirme başarısız: {response.status_code}")

            driver.close()
            driver.switch_to.window(original_window)

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
