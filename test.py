import pandas as pd

df = pd.DataFrame({
    'name': ['Jason','Toto','Tata'],
    'coverage': [25.1,4,63]
})

print(df)
print(df.to_dict())
print(df.set_index('name')['coverage'].to_dict())
print(df.to_dict('records'))
print(df.to_dict('list'))