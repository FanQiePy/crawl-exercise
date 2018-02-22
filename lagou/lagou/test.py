# -*- coding: utf-8 -*-
from datetime import datetime


def test(a, b):
    c = []
    f = open('test.txt', 'wb')
    print('start at: %s' % datetime.now())
    for i in range(a, b):
        f.write(str(i))
        c.append(i)
    f.close()
    print('end at: %s' % datetime.now())


if __name__ == '__main__':
    test(10,99)
