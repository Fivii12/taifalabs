import numpy as np
import pandas as pd
import numpy as np

df = pd.read_csv('mili_input.csv', sep=';')
print(df)
arrays = [df[col].values for col in df.columns]

# Печать результата
for array in arrays:
    print(array)
arrays = arrays[1:]

def extract_number(s):
    return s.split('/')[1]

equality_arr = []

for i, col1 in enumerate(arrays):
    for j, col2 in enumerate(arrays):
        if np.array_equal(col1, col2):
            equality_arr.append(j + 1)
    equality_arr.append(i + 1)
print(equality_arr)

