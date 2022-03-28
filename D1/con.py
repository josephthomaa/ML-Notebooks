import pandas as pd
  
# creating the DataFrames
df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'], 
                    'B': ['B0', 'B1', 'B2', 'B3']})
# print('df1:', df1)
df2 = pd.DataFrame({'C': ['A4']})
# print('df2:', df2)
  
# concatenating
# print('After concatenating:')
# print(pd.concat([df1, df2], 
#                   keys = ['key1', 'key2']))
print(df2.columns)

for col in df2.columns:
    df1[col] = df2[col][0]
# print(df1)

print(df1.merge(df2, how='outer'))
