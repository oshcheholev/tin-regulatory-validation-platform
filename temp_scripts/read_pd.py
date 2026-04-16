import pandas as pd
df = pd.read_excel('updates.xlsx', sheet_name=None)
for k, v in df.items():
    print('SHEET:', k)
    print(v.head(20))
