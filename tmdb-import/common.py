def create_csv(filename, import_data = {}, encoding='utf-8-sig'):
    import csv
    with open(filename, "w", newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(import_data.values())[0].csv_header)
        writer.writerows(list(import_data.values()))