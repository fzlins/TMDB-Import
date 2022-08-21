def create_csv(filename, import_data = {}, encoding='utf-8-sig'):
    import csv
    with open(filename, "w", newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = list(list(import_data.values())[0].keys()))
        writer.writeheader()
        writer.writerows(import_data.values())