# scrape_accepted.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import csv


def scrape_gradcafe_accepted_batch(
    start_page,
    end_page,
    output_path,
    wait_seconds=15
):
    """
    Scrapes GradCafe Accepted results for pages [start_page, end_page].
    Saves raw table rows exactly like your old script.
    """

    print(f"========== BATCH START: {start_page} → {end_page} ==========")

    # ---- Chrome options ----
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")  # İstersen aç
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    base_url = (
        "https://www.thegradcafe.com/survey/"
        "?q=&sort=newest"
        "&institution="
        "&program=Computer+Science"
        "&degree=Masters"
        "&season="
        "&decision=Accepted"
        "&decision_start=&decision_end=&added_start=&added_end="
        "&page="
    )

    all_rows = []

    try:
        for page in range(start_page, end_page + 1):
            print(f"[INFO] Scraping page {page}...")
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
    print(f"[INFO] Saving {len(all_rows)} rows → {output_path}")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)

    print(f"[DONE] Batch saved → {output_path}")
    print("======================================================")


if __name__ == "__main__":
    """
    ----------------------------------------------------------
    BURASI DEĞİŞEBİLİR:
    Batch batch çekmek için aşağıya istediğin parçaları ekle.
    Her seferinde yalnızca 1 batch çalıştır.
    ----------------------------------------------------------
    """

    # ÖRNEK: ilk 50 sayfa
    scrape_gradcafe_accepted_batch(
        start_page=451,
        end_page=500,
        output_path="accepted_batch_10_451-500.csv"
    )

    # Sonra bunu değiştir → 51–100 yap
    # scrape_gradcafe_accepted_batch(
    #     start_page=51,
    #     end_page=100,
    #     output_path="accepted_batch_2_51-100.csv"
    # )

    # Sonra → 101–150
    # ...
