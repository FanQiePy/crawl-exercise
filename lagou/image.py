# -*- coding: utf-8 -*-
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv('job-info.csv')


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%({v:d})'.format(p=pct,v=val)
    return my_autopct


# 职位起薪柱形图
def job_bar(column, title):
    salary = pd.value_counts(data[column].str.findall('\d{1,2}').str[0])
    index = [int(x) for x in salary.keys()]
    min_salary = min(index)
    max_salary = max(index) + 1
    salary_frame = pd.DataFrame(data=salary.values, index=index, columns=['com_num'])
    empty_frame = pd.DataFrame(data=None, index=[x for x in range(min_salary, max_salary)], columns=['com_num'])
    frame = pd.merge(salary_frame, empty_frame, how='outer', on='com_num', left_index=True, right_index=True)
    frame = frame.sort_index(axis=0, kind='mergesort')
    frame.plot(kind='bar')
    plt.title(title.decode('utf-8'))
    plt.show()


# 工作经验，学历，公司规模园饼图
def job_pie(column, title):
    col_data = pd.value_counts(data[column])
    plt.pie(col_data, labels=[x.decode('utf-8') for x in col_data.keys()], autopct=make_autopct(col_data))
    plt.title(title.decode('utf-8'))
    plt.show()


# job_pie('workYear', '工作经验')
job_bar('salary', '职位起薪')

