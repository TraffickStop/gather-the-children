import csv
import collections

records = []
file_name = "/Users/spencerfitzgerald/export.my-table.csv"
csv_file = open(file_name, "r", encoding='utf-8-sig')

csv_reader = csv.DictReader(csv_file)
for row in csv_reader:
    dict_row = dict(row)
    records.append(dict_row.get('caseNumber'))

duplicates = [item for item, count in collections.Counter(records).items() if count > 1]

if len(duplicates) > 0:
    print(duplicates)
else:
    print('No Duplicates')