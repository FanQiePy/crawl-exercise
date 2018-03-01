# -*- coding: utf-8 -*-
import pandas as pd
import re
import csv
import jieba
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator


def data_pre():
    # fields = ['user_id', 'gender', 'city', 'grade', 'online_time', 'join_time']
    # fields = ['title', 'block', 'reply_num', 'date']
    out_data = open('hupu-pandas.csv', 'wb')
    writer = csv.writer(out_data)
    with open('hupu.csv', 'r') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        writer.writerow(fields+['hour'])
        for data in reader:
            if re.search('2018', data['date']) is not None:
                hour = data['date'].split(' ', 1)[1].split(':', 1)[0]
                old_data = [data[x] for x in fields]
                new_data = old_data + [hour]
                writer.writerow(new_data)
    f.close()
    out_data.close()


def user_date_pre():
    out_data = open('hupu-user-pandas.csv', 'wb')
    writer = csv.writer(out_data)
    with open('hupu-user.csv') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        writer.writerow(fields+['year', 'month', 'day'])
        for data in reader:
            date = data['join_time'].split('-', 2)
            old_data = [data[x] for x in fields]
            new_data = old_data + date
            writer.writerow(new_data)
    f.close()
    out_data.close()


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%({v:d})'.format(p=pct,v=val)
    return my_autopct


def block_distribute():
    data = pd.read_csv('hupu-pandas.csv', na_values=['NULL'])
    block_dis = pd.value_counts(data['block'])[:10]
    plt.pie(block_dis, labels=[x.decode('utf-8') for x in block_dis.keys()], autopct='%.2f%%')
    plt.title('主题所在板块分布情况'.decode('utf-8'))
    plt.show()
    # block_dis = pd.value_counts(data['block'])
    # team_dis = block_dis.filter(like='专区', axis=0)[:10]
    # plt.pie(team_dis, labels=[x.decode('utf-8') for x in team_dis.keys()], autopct=make_autopct(team_dis))
    # plt.title('专区板块分布情况'.decode('utf-8'))
    # plt.show()


def block_word_cloud():
    data = pd.read_csv('hupu-pandas.csv', na_values=['NULL'])
    block_dis = pd.value_counts(data['block'])
    block_dict = {}
    i = 0
    for value in block_dis.values:
        freq = float(value)
        word = unicode(block_dis.index[i], encoding='utf-8')
        if freq == 0:
            continue
        block_dict[word] = freq
        i = i + 1
    image = Image.open(r'C:\Users\lvbiaobiao\Desktop\all-1.png')
    graph = np.array(image)
    cloud = WordCloud(font_path=r'E:\date\python\SourceHanSerifSC_EL-M\SourceHanSerifSC-Regular.otf',
                      max_font_size=56, background_color="white",
                      width=1000, height=500, relative_scaling=0,
                      mask=graph)
    block_cloud = cloud.generate_from_frequencies(block_dict)
    # plt.figure()
    image_color = ImageColorGenerator(graph)
    plt.imshow(block_cloud, interpolation='hanning')
    plt.imshow(block_cloud.recolor(color_func=image_color))
    plt.axis("off")
    plt.show()


def time_distribute():
    data = pd.read_csv('hupu-pandas.csv', na_values=['NULL'])
    hour = pd.value_counts(data['hour']).sort_index(axis=0, kind='mergesort')
    hour.plot(kind='bar')
    plt.title('主题发表时间分布情况'.decode('utf-8'))
    plt.xlabel(u'时间段')
    plt.ylabel(u'主题数量')
    plt.show()


def stop_words(texts):
    words_list = []
    word_generator = jieba.cut(texts, cut_all=False, HMM=True)  # 返回的是一个迭代器
    with open('stopwords.txt', 'r') as f:
        str_text = f.read()
        unicode_text = unicode(str_text, 'utf-8')  # 把str格式转成unicode格式
        f.close()  # stopwords文本中词的格式是'一词一行'
    with open('words.txt', 'w') as f:
        for word in word_generator:
            if word.strip() not in unicode_text:
                words_list.append(word)
                f.write(word.encode('utf-8') + ' ')
        f.close()
    return ' '.join(words_list)  # 注意是空格


def title_word_cloud():
    data = pd.read_csv('hupu-pandas.csv', na_values=['NULL'])
    title_data = data['title']
    # with open('title.txt', 'w') as f:
    #     for title in title_data.values:
    #         f.write(title)
    # f.close()
    # f = open('title.txt', 'r').read().decode('utf-8')
    # text = stop_words(f)
    text = open('words.txt').read().decode('utf-8')
    image = Image.open(r'C:\Users\lvbiaobiao\Desktop\hupu-1.jpg')
    graph = np.array(image)
    cloud = WordCloud(font_path=r'E:\date\python\SourceHanSerifSC_EL-M\SourceHanSerifSC-Regular.otf',
                      max_font_size=18, background_color="white",
                      width=640, height=200, relative_scaling=0.5,
                      mask=graph, max_words=100, colormap='nipy_spectral')
    cloud.generate_from_text(text)
    # image_color = ImageColorGenerator(graph)
    plt.imshow(cloud, interpolation='gaussian')
    # plt.imshow(cloud.recolor(color_func=image_color))
    plt.axis("off")
    plt.show()
    cloud.to_file('hupu.png')


def join_time_distribute():
    # data = pd.read_csv('hupu-user-numpy.csv', na_values=['NULL'])
    # new_data = data.drop_duplicates(['user_id'])
    # join_time_dis = pd.value_counts(new_data['join_time']).sort_index(axis=0, kind='mergesort')
    # join_time = pd.Series(join_time_dis.values, index=pd.DatetimeIndex(join_time_dis.index))
    # time = join_time.resample(rule='M', kind='period').sum()

    join_data = pd.read_csv('join_time.csv')
    # join_time = pd.Series(data['num'].values, index=data['date'])
    # join_time.plot()
    # last_time = pd.Series(time.values, index=pd.DatetimeIndex(time.index, freq='M'))
    # print time
    # print join_time
    fig, ax = plt.subplots()
    ax.plot([datetime.datetime.strptime(x, '%Y-%m') for x in join_data['date'].values], join_data['num'].values)

    # # time.plot()
    year_format = mdates.DateFormatter('%Y')
    # months = mdates.MonthLocator()
    year_locator = mdates.YearLocator()
    ax.xaxis.set_major_locator(year_locator)
    ax.xaxis.set_major_formatter(year_format)
    # ax.xaxis.set_minor_locator(months)

    plt.tick_params(axis='both', which='both', bottom='on', top='off',
                    labelbottom='on', left='on', right='off', labelleft='on')
    plt.axis(['2004-01', '2018-02', -250, 5800])
    plt.title('活跃用户注册时间分布情况'.decode('utf-8'))
    # plt.xlabel(u'年月份')
    plt.ylabel(u'月注册用户数')
    # fig.autofmt_xdate()
    ax.format_xdata = mdates.DateFormatter('%Y-%m')
    plt.show()
    # time.to_csv('join_time.csv')
    # new_data.to_csv('hupu-user-numpy.csv', index=False)


def join_time_pie():
    join_data = pd.read_csv('join_time.csv')
    index = []
    for x in join_data['date'].values:
        time_delta = datetime.datetime(2018, 2, 1) - datetime.datetime.strptime(x, '%Y-%m')
        index.append(time_delta.days/365 + 1)
    frame = pd.DataFrame(data={'year': index, 'num': join_data['num'].values}, columns=['year', 'num'])
    grouped = frame['num'].groupby(frame['year']).sum().sort_values(ascending=False)
    with open('join_year.txt', 'w') as f:
        for i in range(len(grouped.index)):
            text = "{name: '%s',value: %u},\n" % (grouped.index[i], grouped.values[i])
            f.write(text.encode('utf-8'))
    f.close()
    # grouped.to_csv('join_year.txt')


def city_distribute():

    # 读取echart格式输入文件，获取全国城市信息
    f = open('city_data.txt', 'r').read()
    name = 'name'
    value = 'value'
    city_list = eval(f)
    china_city_list = [x['name'].decode('utf-8') for x in city_list]

    # 将用户城市信息过滤，重塑，合并
    reader = csv.DictReader(open('city.csv'))
    city_data = []
    num_data = []
    for piece in reader:
        two_words = piece['city'].decode('utf-8')[:2]
        num_data.append(piece['num'])
        if two_words in china_city_list:  # 匹配上海，广州等两字城市
            city_data.append(two_words)
        elif two_words == u'地球':
            city_data.append(u'地球')
        else:
            three_word = piece['city'].decode('utf-8')[:3]  # 匹配黑龙江和内蒙古
            if three_word in china_city_list:
                city_data.append(three_word)
            else:
                city_data.append(u'其他国家')  # 将非国内城市统一未其他国家

    # 用户城市分布统计，返回echart格式的文本
    frame = pd.DataFrame({'num': [int(x) for x in num_data], 'city': city_data}, columns=['num', 'city'])
    grouped = frame['num'].groupby(frame['city']).sum().sort_values(ascending=False)
    # with open('city_for_baidu.txt', 'w') as f:
    #     for i in range(len(grouped.index)):
    #         text = "{name: '%s',value: %u}\n" % (grouped.index[i], grouped.values[i])
    #         f.write(text.encode('utf-8'))
    # f.close()

    # 选择比列前十的城市
    index = []
    for i in range(len(grouped.index)):
        if i < 10:
            index.append(grouped.index[i])
        else:
            if grouped.index[i] == u'其他国家':
                index.append(u'其他国家')
            elif grouped.index[i] == u'地球':
                index.append(u'地球')
            else:
                index.append(u'其他省份')
    ten_frame = pd.DataFrame({'num': grouped.values, 'city': index}, columns=['num', 'city'])
    ten_grouped = ten_frame['num'].groupby(ten_frame['city']).sum().sort_values(ascending=False)
    with open('ten_city_for_baidu.txt', 'w') as f:
        for i in range(len(ten_grouped.index)):
            text = "{name: '%s',value: %u}\n" % (ten_grouped.index[i], ten_grouped.values[i])
            f.write(text.encode('utf-8'))
    f.close()
    plt.pie(ten_grouped, labels=[x for x in ten_grouped.keys()], autopct='%.2f%%')
    plt.show()


def gender_distribute():
    data = pd.read_csv('hupu-user-numpy.csv')
    series = pd.value_counts(data['gender'])
    plt.pie(series, labels=[x.decode('utf-8') for x in series.keys()], autopct='%.2f%%')
    plt.title('主题所在板块分布情况'.decode('utf-8'))
    plt.show()


def online_time_distribute():
    data = pd.read_csv('hupu-user-numpy.csv')
    values = data['online_time'].values
    date = data['join_time'].values
    mean_time = []
    date_index = []
    for i in range(len(values)):
        try:
            join_time = datetime.datetime.strptime(date[i], '%Y-%m-%d')
        except TypeError:
            continue
        days = (datetime.datetime(2018, 2, 26) - join_time).days
        mean_time.append(round(float(values[i])/float(days), 2))
        date_index.append(join_time)
    frame = pd.DataFrame(data={'time': mean_time, 'date': date_index}, columns=['time', 'date'])
    series = frame['time'].groupby(frame['date']).mean()
    time_series = series.resample('M', kind='period').mean()
    time_series.to_csv('online_time.txt')


def online_time_distribute_out():
    online_time = pd.read_csv('online_time.txt')

    fig, ax = plt.subplots()
    ax.plot([datetime.datetime.strptime(x, '%Y-%m') for x in online_time['date'].values], online_time['time'].values)

    year_format = mdates.DateFormatter('%Y')
    year_locator = mdates.YearLocator()
    ax.xaxis.set_major_locator(year_locator)
    ax.xaxis.set_major_formatter(year_format)

    plt.tick_params(axis='both', which='both', bottom='on', top='off',
                    labelbottom='on', left='on', right='off', labelleft='on')
    plt.axis(['2004-01', '2018-02', 0.1, 1.5])
    plt.title('JRS每天平均在线时间'.decode('utf-8'))
    plt.xlabel(u'JRS注册年份')
    plt.ylabel(u'JRS平均每天在线时间')
    plt.show()


if __name__ == '__main__':
    # data_pre()
    # block_distribute()
    # block_word_cloud()
    # time_distribute()
    # data_pre()
    # time_distribute()
    # title_word_cloud()
    # user_date_pre()
    # join_time_distribute()
    # city_distribute()
    # gender_distribute()
    # join_time_pie()
    # online_time_distribute()
    online_time_distribute_out()
