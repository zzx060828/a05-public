#读取行和列
import pandas as pd
d = {"x":100,"y":200,"z":300}#字典
s1 = pd.Series(d)#将d字典转化为pdframe对象
print(s1)
print(s1.index)


L1 = [100,200,300]
L2 = ["x","y","z"]

s2 = pd.Series(L1,index=L2)
print(s2)
print(s2.index)
print(s2.values)


s3 = pd.Series([1,2,3],index=[1,2,3],name="A")
s4 = pd.Series([10,20,30],index=[1,2,3],name="B")
s5 = pd.Series([100,200,300],index=[2,3,4],name="C")

df = pd.DataFrame({s3.name:s3,s4.name:s4,s5.name:s5})
print(df)
df2 = pd.DataFrame([s3,s4,s5])#注意字典和列表的形式
print(df2)