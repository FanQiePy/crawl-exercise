# -*- coding: utf-8 -*-
import csv
import pandas as pd
import matplotlib.pyplot as plt

from loupang import AREA_DICT

# 数据预处理并保存
# out_f = open('house_pandas.csv', 'wb')
#
# with open('house.csv') as f:
#     data = csv.DictReader(f)
#     out_w = csv.writer(out_f)
#     field = [x for x in data.fieldnames]
#     field.append('square_price')
#     out_w.writerow(field)
#     for piece in data:
#         square_price = format(float(piece['price'])/float(piece['square']), '.1f')
#         values = [piece[x] for x in field[:-1]]
#         values.append(square_price)
#         out_w.writerow(values)
# f.close()
# out_f.close()


data = pd.read_csv('house_pandas.csv')
SH_data = pd.DataFrame(data[data['house_type'] == 'ershoufang'],
                       columns=['city', 'area', 'house_type', 'layout',
                                'square', 'price', 'date', 'address', 'house_url', 'square_price'])
SH_data['layout'] = SH_data['layout'].replace('\s+', '', regex=True)
hire_data = data[data['house_type'] == 'zufang']


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%({v:d})'.format(p=pct,v=val)
    return my_autopct


# 各城区二手房占比圆饼图
def house_pie(column, title):
    col_data = pd.value_counts(data[column])
    plt.pie(col_data, labels=[AREA_DICT[x].decode('utf-8') for x in col_data.keys()], autopct=make_autopct(col_data))
    plt.title(title.decode('utf-8'))
    plt.show()


# house_pie('area', '各城区二手房占比')


# 不同户型平均总价情况
# layout = SH_data['price'].groupby(SH_data['layout']).mean()
# layout.plot(kind='bar')
# plt.title('不同户型平均总价'.decode('utf-8'))
# plt.show()

# 不同户型的平均价格
# layout = SH_data['square_price'].groupby(SH_data['layout']).mean()
# layout.plot(kind='bar')
# plt.title('不同户型平均价格'.decode('utf-8'))
# plt.show()


# 一室一厅的价格情况散点图
# layout = SH_data[SH_data.layout.str.contains('1室1厅')].sort_values(by='price')
# layout.plot(kind='scatter', x='square', y='price')
# plt.title(u'一室一厅的价格分布')
# plt.show()


# 一室一厅的每平米价格情况散点图
layout = SH_data[SH_data.layout.str.contains('1室1厅')].sort_values(by='price')
layout.plot(kind='scatter', x='square', y='square_price')
plt.title(u'一室一厅的每平米价格分布')
plt.show()
