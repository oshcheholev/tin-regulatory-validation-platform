import openpyxl
wb = openpyxl.load_workbook('updates.xlsx')
sheet = wb.active
for i, row in enumerate(sheet.iter_rows(values_only=True)):
    if i > 15: break
    print(row)
