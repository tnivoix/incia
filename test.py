import numpy as np
import pandas as pd

df1 = pd.DataFrame({"Times" : [1,2,3], "GVS" : [0.5,-1,0.6]})
df2 = pd.DataFrame({"L" : [6, 0], "R" : [56,75]})
df3 = pd.concat([df1,df2], axis=1)
print(df3)