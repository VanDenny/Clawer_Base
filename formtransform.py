import pandas as pd
# file = r'D:\Documents\WeChat Files\java1989\Files'
# df = pd.DataFrame(file)
# dict_list = df.to_dict('record')
res_list = []
for i in range(0,200):
    for j in range(i+1, 200):
        a_dict = {}
        a_dict['orign'] = i
        a_dict['target'] = j
        res_list.append(a_dict)
df = pd.DataFrame(res_list)
df.to_excel(r'D:\Documents\WeChat Files\java1989\Files\form.xlsx')
print(df)
