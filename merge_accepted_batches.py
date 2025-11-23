import glob
import csv

def merge_batches(
    pattern="accepted_batch_*.csv",
    output_path="accepted_full.csv"
):
    files = sorted(glob.glob(pattern))
    print("Bulunan dosyalar:")
    for f in files:
        print(" -", f)

    first = True
    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = None

        for file in files:
            with open(file, "r", encoding="utf-8") as in_f:
                reader = csv.reader(in_f)
                header = next(reader, None)

                # İlk dosyada header yaz, diğerlerinde atla
                if first:
                    writer = csv.writer(out_f)
                    if header:
                        writer.writerow(header)
                    first = False

                for row in reader:
                    if row:   # boş satırları at
                        writer.writerow(row)

    print(f"Bitti! Çıktı: {output_path}")

if __name__ == "__main__":
    merge_batches()

