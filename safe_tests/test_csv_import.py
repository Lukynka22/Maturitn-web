from admin_csv_utils import load_products_from_csv


def test_load_products_from_csv(tmp_path):
    csv_file = tmp_path / "produkty.csv"
    csv_file.write_text(
        "nazev;cena;skladem;popis;image;kategorie\n"
        "Rolex Submariner;250000;3;Luxusni model;rolex.jpg;Limited\n"
        "Omega Speedmaster;180000;5;Klasika;omega.jpg;Komise\n",
        encoding="utf-8"
    )

    products = load_products_from_csv(str(csv_file))

    assert len(products) == 2
    assert products[0]["nazev"] == "Rolex Submariner"
    assert products[0]["cena"] == 250000
    assert products[1]["skladem"] == 5
