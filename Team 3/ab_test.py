import pandas as pd
import os

my_path = os.path.abspath(os.path.dirname(__file__))
data = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/response.csv'))

data = data[data.actualrating != -1]

newpredictedrating = [1 if i >= 3 else 0 for i in data.predictedrating]
newactualrating = [1 if i >= 3 else 0 for i in data.actualrating]

data['newpredictedrating'] = newpredictedrating
data['newactualrating'] = newactualrating

m1 = data[data.method == 1]
m2 = data[data.method == 2]
m3 = data[data.method == 3]

l1 = m1.newpredictedrating == m1.newactualrating
l2 = m2.newpredictedrating == m2.newactualrating
l3 = m3.newpredictedrating == m3.newactualrating

print("Matrix Factorisation", round(sum(l1) / len(l1) * 100, 2))
print("Tf-Idf", round(sum(l2) / len(l2) * 100 , 2))
print("Tf-Idf with flavour", round(sum(l3) / len(l3) * 100, 2))
