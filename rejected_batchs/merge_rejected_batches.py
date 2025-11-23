# merge_rejected_batches.py

import glob
import csv
import os


def merge_rejected_batches(
    pattern="rejected_batch_*.csv",
    output_path="rejected_full.csv"
):
    """
    rejected_batch_*.csv dosyalarını tek bir rejected_full.csv dosyasında birleştirir.
    - İlk bulunan dosyadan header (varsa) alınır.
    - Sonraki dosyalarda header satırı atlanır.
    """

    print("👉 Pattern ile dosya aranıyor:", pattern)
    files = sorted(glob.glob(pattern))

    if not files:
        print("⚠️ HİÇ DOSYA BULUNAMADI!")
        print("   - Şu anda bulunduğun klasör:", os.getcwd())
        print("   - Lütfen şunları kontrol et:")
        print("     * rejected_batch_*.csv dosyaları gerçekten bu klasörde mi?")
        print("     * Dosya isimleri gerçekten 'rejected_batch_' ile mi başlıyor?")
        return

    print("✅ Bulunan REJECTED batch dosyaları:")
    for f in files:
        print(" -", f)

    first = True
    total_rows = 0

    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = None

        for file in files:
            with open(file, "r", encoding="utf-8") as in_f:
                reader = csv.reader(in_f)
                header = next(reader, None)

                # İlk dosyada header'ı yaz
                if first:
                    writer = csv.writer(out_f)
                    if header and any(h.strip() for h in header):
                        writer.writerow(header)
                        print(f"[INFO] Header alındı → {file}")
                    else:
                        print(f"[INFO] {file} dosyasında header yok / boş.")
                    first = False

                # Satırları yaz
                row_count = 0
                for row in reader:
                    if row:  # boş satırları at
                        writer.writerow(row)
                        row_count += 1
                        total_rows += 1

                print(f"[OK] {file} → {row_count} satır eklendi.")

    print("======================================")
    print(f"🎉 Merge bitti! Toplam satır: {total_rows}")
    print(f"📁 Çıktı dosyası: {output_path}")
    print("======================================")


if __name__ == "__main__":
    merge_rejected_batches()
