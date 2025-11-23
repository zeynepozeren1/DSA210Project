# scrape_rejected.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import csv
import glob


def scrape_gradcafe_rejected_batch(
    start_page,
    end_page,
    output_path,
    wait_seconds=15
):
    """
    Scrapes GradCafe REJECTED results for pages [start_page, end_page].
    Saves raw table rows exactly like accepted script.
    """

    print(f"========== REJECTED BATCH START: {start_page} → {end_page} ==========")

    # ---- Chrome options ----
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")  # İstersen aç
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    # SENİN VERDİĞİN URL + &page=
    base_url = (
        "https://www.thegradcafe.com/survey/"
        "?q=&sort=newest"
        "&institution="
        "&program=Computer+Science"
        "&degree=Masters"
        "&season="
        "&decision=Rejected"
        "&decision_start=&decision_end=&added_start=&added_end="
        "&page="
    )

    all_rows = []

    try:
        for page in range(start_page, end_page + 1):
            print(f"[INFO] Scraping REJECTED page {page}...")
            url = base_url + str(page)
            driver.get(url)

            # Tabloyu bekle
            try:
                table = WebDriverWait(driver, wait_seconds).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "table.tw-min-w-full")
                    )
                )
            except TimeoutException:
                print(f"[WARN] Table not found on page {page}. Skipping page.")
                continue

            # Tbody satırlarını al
            try:
                body = table.find_element(By.TAG_NAME, "tbody")
                rows = body.find_elements(By.TAG_NAME, "tr")
            except Exception as e:
                print(f"[WARN] Could not find rows on page {page}: {e}")
                continue

            if not rows:
                print(f"[INFO] No rows found on page {page}.")
                continue

            # Satırları ekle
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue
                cell_texts = [c.text.strip() for c in cells]
                all_rows.append(cell_texts)

            time.sleep(1.2)  # yükü azaltmak için

    finally:
        driver.quit()

    # CSV'e yaz
    print(f"[INFO] Saving {len(all_rows)} REJECTED rows → {output_path}")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)

    print(f"[DONE] Rejected batch saved → {output_path}")
    print("======================================================")


def merge_rejected_batches(
    pattern="rejected_batch_*.csv",
    output_path="rejected_full.csv"
):
    """
    rejected_batch_*.csv dosyalarını tek bir rejected_full.csv'de birleştirir.
    Header varsa ilk dosyadan alınır, sonrakilerde atlanır.
    """
    files = sorted(glob.glob(pattern))
    print("Bulunan REJECTED batch dosyaları:")
    for f in files:
        print(" -", f)

    if not files:
        print("[WARN] Hiç dosya bulunamadı, pattern doğru mu? (rejected_batch_*.csv)")
        return

    first = True
    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = None

        for file in files:
            with open(file, "r", encoding="utf-8") as in_f:
                reader = csv.reader(in_f)
                header = next(reader, None)

                if first:
                    writer = csv.writer(out_f)
                    if header:
                        writer.writerow(header)
                    first = False

                for row in reader:
                    if row:   # boş satırları at
                        writer.writerow(row)

    print(f"[OK] REJECTED full dataset created → {output_path}")


if __name__ == "__main__":
    """
    ----------------------------------------------------------
    BURAYI İHTİYACINA GÖRE DEĞİŞTİR:
    Her seferinde sadece 1 batch çalıştırman daha güvenli.
    ----------------------------------------------------------
    """

    # ÖRNEK: 1–50 arası rejected sayfaları çek
    scrape_gradcafe_rejected_batch(
        start_page=451,
        end_page=500,
        output_path="rejected_batch_10_451-500.csv"
    )

    # Batch’lerin hepsini çektikten sonra (ayrı bir çalıştırmada):
    # merge_rejected_batches()
