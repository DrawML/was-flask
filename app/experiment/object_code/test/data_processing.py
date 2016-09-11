import app.experiment.object_code.scripts.data_process as DP

set1 = [[1,2,3], [4,5,6]]
set2 = [[7,8,9], [10,11,12], [13,14,15]]
try:
    t = DP.concat([set1, set2], [-1, 3])
except ValueError as e:
    print(e)
print(t)
print(DP.transpose(set1))
