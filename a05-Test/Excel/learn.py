import pandas as pd
df = pd.DataFrame({'ID': [1,2,3,4,5,6],'Name':['Jack','Victor','Andy','Nick','Franklin','others']})
df = df.set_index('ID')
df.to_excel('D:/A05/Excel/output.xlsx')

print("Done!")
print(df.shape)#几行几列
print(df.columns)#哪些列
print(df.head(2))#默认5列
print("===============================")
print(df.tail(2))
                                                        #没有header
example = pd.read_excel(r'D:/A05/Excel/output.xlsx',header=None)#读取文件
example.columns=['学号','姓名']
example.set_index('学号',inplace=True)
example.to_excel('D:/A05/Excel/输出.xlsx')
print("Done!")

copy = pd.read_excel(r'D:/A05/Excel/输出.xlsx',index_col="学号")#读取文件
copy.to_excel(r"D:/A05/Excel/输出2.xlsx")
print("Done!")

