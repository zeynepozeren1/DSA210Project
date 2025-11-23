# clean_rejected.py

import csv
import re


def parse_meta_block(meta_text: str):
    """
    Tek hücre içindeki multi-line metinden:
    - term
    - citizenship
    - gpa_raw
    - GRE total / Q / V / AW
    ham şekilde ayırır — hiçbir düzeltme yapmaz.
    """
    term = None
    citizenship = None
    gpa_raw = None
    gre_total = None
    gre_q = None
    gre_v = None
    gre_aw = None

    lines = [l.strip() for l in meta_text.splitlines() if l.strip()]

    for line in lines:

        # TERM — Her türlü ham değeri yakala:
        # F19, F17, Spring 2026, Fall 2020...
        if term is None:
            # Kısa format (F19, S20 vs.)
            if re.match(r'^[FSW]\d{2}$', line):
                term = line
                continue
            # Uzun format (Fall 2025 vs.)
            if re.match(r'^(Fall|Spring|Summer|Winter)\s+\d{4}$', line):
                term = line
                continue

        # CITIZENSHIP
        if line in ("International", "American"):
            citizenship = line
            continue

        # GPA — Ham bırak
        if line.startswith("GPA"):
            gpa_raw = line.replace("GPA", "").strip()
            continue

        # GRE ham ayrıştırma
        if line.startswith("GRE"):
            parts = line.split()

            # Total GRE (Örn: "GRE 324")
            if len(parts) == 2:
                try:
                    gre_total = float(parts[1])
                except Exception:
                    pass

            # GRE Q / V / AW
            elif len(parts) >= 3:
                tag = parts[1]
                val = parts[2]

                try:
                    score = float(val)
                except Exception:
                    score = val  # sayı değilse bile ham olarak bırak

                if tag == "Q":
                    gre_q = score
                elif tag == "V":
                    gre_v = score
                elif tag == "AW":
                    gre_aw = score

    return term, citizenship, gpa_raw, gre_total, gre_q, gre_v, gre_aw


def clean_rejected(input_path: str, output_path: str):
    """
    Hiçbir düzeltme yapmaz.
    Sadece Rejected entrylerinin ilk 2 satırından
    ilgilenilen fieldları çıkarır.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    cleaned_rows = []

    for i, row in enumerate(rows):
        # Entry başlangıcı
        if len(row) >= 4 and (
            row[3].startswith("Accepted on") or row[3].startswith("Rejected on")
        ):
            university = row[0].strip()
            program = row[1].strip()
            decision = "Accepted" if "Accepted on" in row[3] else "Rejected"

            term = None
            citizenship = None
            gpa_raw = None
            gre_total = None
            gre_q = None
            gre_v = None
            gre_aw = None

            # Meta block (bir sonraki satır)
            if i + 1 < len(rows):
                meta_row = rows[i + 1]
                if meta_row and meta_row[0].strip():
                    (
                        term,
                        citizenship,
                        gpa_raw,
                        gre_total,
                        gre_q,
                        gre_v,
                        gre_aw,
                    ) = parse_meta_block(meta_row[0])

            cleaned_rows.append(
                [
                    university,
                    program,
                    term,
                    citizenship,
                    gpa_raw,
                    gre_total,
                    gre_q,
                    gre_v,
                    gre_aw,

                ]
            )

    # Output
    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(
            [
                "university",
                "program",
                "decision",
                "term",
                "citizenship",
                "gpa_raw",
                "gre_total",
                "gre_q",
                "gre_v",
                "gre_aw",
            ]
        )
        writer.writerows(cleaned_rows)

    print(f"[OK] Clean REJECTED data written to: {output_path}")


if __name__ == "__main__":
    # merge_rejected_batches çıktı dosyan burada:
    # rejected_full.csv
    clean_rejected("rejected_full.csv", "gradcafe_rejected_clean.csv")
