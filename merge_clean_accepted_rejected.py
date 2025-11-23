# merge_clean_accepted_rejected.py

import csv
import os


def merge_clean_files(
    accepted_path="gradcafe_accepted_clean.csv",
    rejected_path="gradcafe_rejected_clean.csv",
    output_path="gradcafe_cs_ms_all.csv"
):
    print("🔎 Çalışma klasörü:", os.getcwd())
    print("✅ Accepted dosyası:", accepted_path)
    print("✅ Rejected dosyası:", rejected_path)

    # Output dosyasını aç
    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = None
        total_rows = 0

        # 1) Accepted'i yaz
        with open(accepted_path, newline="", encoding="utf-8") as acc_f:
            acc_reader = csv.reader(acc_f)
            acc_header = next(acc_reader, None)

            if acc_header is None:
                raise ValueError("Accepted dosyasında header yok gibi görünüyor!")

            # Output writer'ı ve header'ı ayarla
            writer = csv.writer(out_f)
            writer.writerow(acc_header)
            print(f"[INFO] Header yazıldı → {acc_header}")

            for row in acc_reader:
                if row:
                    writer.writerow(row)
                    total_rows += 1

        print(f"[OK] Accepted'tan {total_rows} satır yazıldı.")

        # 2) Rejected'i ekle (header atlanacak)
        with open(rejected_path, newline="", encoding="utf-8") as rej_f:
            rej_reader = csv.reader(rej_f)
            rej_header = next(rej_reader, None)

            # Header aynı mı kontrol edelim (debug için)
            if rej_header != acc_header:
                print("⚠️ UYARI: Rejected header'ı accepted header'ı ile birebir aynı değil!")
                print("    Accepted header:", acc_header)
                print("    Rejected header:", rej_header)
                print("    Yine de devam ediyorum, satırları ekleyeceğim...")

            rows_from_rejected = 0
            for row in rej_reader:
                if row:
                    writer.writerow(row)
                    total_rows += 1
                    rows_from_rejected += 1

        print(f"[OK] Rejected'tan {rows_from_rejected} satır eklendi.")
        print("==============================================")
        print(f"🎉 TOPLAM SATIR (Accepted + Rejected): {total_rows}")
        print(f"📁 Çıktı dosyası: {output_path}")
        print("==============================================")


if __name__ == "__main__":
    merge_clean_files()
