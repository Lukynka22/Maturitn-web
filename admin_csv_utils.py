import csv


def load_products_from_csv(file_path):
    products = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        required_columns = {"nazev", "cena", "skladem", "popis", "image", "kategorie"}
        if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
            raise ValueError("CSV musí obsahovat sloupce: nazev; cena; skladem; popis; image; kategorie")

        for row in reader:
            name = (row.get("nazev") or "").strip()
            price = (row.get("cena") or "").strip()
            stock = (row.get("skladem") or "").strip()
            desc = (row.get("popis") or "").strip()
            image = (row.get("image") or "").strip()
            category = (row.get("kategorie") or "").strip()

            if not name or not price or not stock:
                continue

            try:
                price = int(price)
                stock = int(stock)
            except ValueError:
                continue

            products.append({
                "nazev": name,
                "cena": price,
                "skladem": stock,
                "popis": desc,
                "image": image,
                "kategorie": category
            })

    return products
