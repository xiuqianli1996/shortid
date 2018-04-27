# shortid

#### 1.学习的目标

初学python，希望做点简单一些的东西练练手

按照大佬的nodejs版本的shortid实现一个python版的，地址：[dylang/shortid](https://github.com/dylang/shortid)

github上搜索发现已有大佬实现的python版，所以也拿来学习参考：[corpix/shortid](https://github.com/corpix/shortid)


#### 2.开始造轮子

先写个setup.py, 这是在Pypi上发布python包的最基础的步骤，虽然我们这个也不准备发布，代码如下：
```
try:
    from setuptools import setup
except:
    from distutils.core import setup

__version__ = '0.0.1'

with open('README.md') as fp:
    long_description = fp.read()

setup(
    name='shortid',
    version=__version__,
    description='Short id generator',
    long_description=long_description,
    author='xiuqian li',
    author_email='981764793@qq.com',
    keywords=['shortid'],
    packages=['shortid'],
    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
```

内容基本上都是抄的，具体意思看语义基本都能明白，我也不太懂不过多描述。

接下来新建一个包shortid，包名和上面packages的内容对应就行,目录结构：

![](https://pic2.zhimg.com/v2-c1ecbd4a2c225da06ade5549827eaca4_b.jpg)

接下来分析一下生成的算法

![lib/build.js](https://pic2.zhimg.com/v2-8b6e92c65f8071205a1e37331c2e3eb2_b.jpg)

生成算法第一个入口就是这个，将版本号、workerId、一秒内调用的次数、当前时间戳 - REDUCETIME的秒数（不计算毫秒，让生成的id尽可能的短）编码后拼接在一起就是短id。

 其中workerId我的理解是集群部署的时候设置不同的id保证不会因为不同机器部署都导致生成的id不唯一。
 
 version和REDUCE_TIME是两个变量，因为调用生成函数时会用当前时间戳减REDUCE_TIME的结果来编码生成短id，所以作者建议每年更新一次这个时间戳来保证生成的短id长度在理想范围之内，同时为了保证更新时间后id不重复所以也需要更新version为一个以前没用过并且小于16的数。
 
 counter和previousSeconds保证并发情况下的唯一性，counter是统计同一秒内的调用次数，当然有可能出现的错误就是counter溢出，但基本上是不可能出现的，服务器也压不住这么大的并发。
 
看完build.js可以发现核心部分应该是在encode函数里，并且还有一个alphabet.lookup，接下来看一下alphabet.js,代码就不全粘了，看关键部分
![](https://pic2.zhimg.com/v2-efc6ba233171c4bdbb9e2496931553d3_b.jpg)

在前面有设置默认字符序列alphabet，并且提供了更改这个序列的函数，在这个函数里做了对字符串去重的操作，不算关键，不过多解释。

首先看暴露给encode函数调用了的lookup函数，参数是一个索引，从alphabetShuffled里取出一个字符，再看getShuffled和shuffle函数，其实就是将字符串alphabet变成一个乱序的字符数组，在python里random模块给我们提供了简单的实现。

看完这部分继续看encode.js，生成短id的核心就在这里面了。

![一个只有7行的函数](https://pic4.zhimg.com/v2-2450955ecc682426ac4675b65fc85b85_b.jpg)

回顾一下build.js里调用这个函数的代码

```
str = str + encode(alphabet.lookup, version);
```

很明显第二个参数是个数字，在encode函数里循环从lookup里取出随机一个字符拼接到字符串，最后返回的字符串就是生成的短id，并且这个循环至少会执行一次，结束条件是
```
number < (Math.pow(16, loopCounter + 1 ) );
```
可以简单的分析出版本号小于16占一位，workerId也不建议大于16所以也占一位，短id的其他几位就在一秒内并发数counter和seconds了，至于counter占几位就看并发数是16的几次方了，剩下的就是seconds占的位数

```
2018-01-01 00:00:01 1514736000

2018-12-31 23:59:59 1546271999

1546271999 - 1514736000 = 31535999
```
可以看出一年大概是这么多秒，16 ^ 6 = 16777216，16 ^ 7 = 268435456，所以如果8年不更新REDUCE_TIME都能保证不计算并发的情况下生成的shortid在9位之内。

分析完生成的id长度后再看一下关键的生成随机字符的代码
str = str + lookup( ( (number >> (4 * loopCounter)) & 0x0f ) | randomByte() );
这里用到了位运算，将number右移4 * loopCounter位之后和0x0f做与运算，保证最后的结果小于16。接下来做一个验证：

```
def encode(lookup, number):
    done = False
    loop_counter = 0
    result = []
    while not done:
        result.append(str((number >> 4 * loop_counter) & 0x0f))
        done = number < pow(16, loop_counter + 1)
        loop_counter += 1
    return ','.join(result)

for i in range(31535099, 31535999):
    print(encode(None, i))
```

![与运算后的结果](https://pic3.zhimg.com/v2-9bb3c8dcd774d9d93d05d991f6345c3c_b.jpg)

拿31535099来做个模拟，方便理解转为二进制模拟：
```
1.1111000010010111111111011 >> 0 & 0x0f = 11
2.1111000010010111111111011 >> 4 & 0x0f = 15
3.1111000010010111111111011 >> 8 & 0x0f = 15
......
```

这个位运算的结果还不能用来从字符数组里取字符，还有一步跟randomByte()的或操作，接下来看看这个代码

![](https://pic4.zhimg.com/v2-0a45aef3a4800a745a49becfc536edc9_b.jpg)

这里用到了crypto模块的randomBytes函数，生成一个随机byte（0~255）跟0x30（十进制48，二进制110000）做与运算，python也有该模块的实现，不过后面我是直接用random模块的getrandbits生成8位bit，效果应该一样。最后的返回结果大概有0、16、32、48。

看一下这个随机数和number运算的16种结果或运算的结果

```
for i in range(0, 16):
    print(i, ' ', i | 0, ' ', i | 16, ' ', i | 32, ' ', i | 48)
```

结果是0~63.

到这里逻辑应该就很清楚了，根据number循环生成一个0~63的随机数，从没有重复的字符数组里取出字符拼接，结果就是我们需要的shortid。

简单的分析了一波原理接下来就是秀一波骚操作的时候了。
```
import random
import datetime
import math
import os

class ShortId:

    def __init__(self, worker_id=0):
        self.REDUCE_TIME = 1524783675
        self.version = 0
        self.counter = 0
        self.previous_seconds = -1
        self.worker_id = worker_id
        self.__alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'
        self.alphabet = self.__alphabet
        self.shuffle = None

    def reset_alphabet(self):
        self.alphabet = self.__alphabet
        self._reset_shuffle()

    def set_alphabet(self, alphabet):
        if len(alphabet) == 0 or len(set(alphabet)) == 0:
            raise RuntimeError("alphabet can't be empty")
        self.alphabet = alphabet
        self._reset_shuffle()

    def _reset_shuffle(self):
        shuffle = list(set(self.alphabet))
        random.shuffle(shuffle)
        self.shuffle = shuffle

    def get_shuffle(self):
        if not self.shuffle:
            self._reset_shuffle()
        return self.shuffle

    def _encode(self, number):
        done = False
        loop_counter = 0
        result = ''
        while not done:
            index = ((number >> 4 * loop_counter) & 0x0f) | (random.getrandbits(8) & 0x30)
            result += str(self.get_shuffle()[index % len(self.get_shuffle())])
            done = number < pow(16, loop_counter + 1)
            loop_counter += 1
        return result

    def generate(self):
        now = math.ceil(datetime.datetime.utcnow().timestamp())
        seconds =  now - self.REDUCE_TIME
        if seconds == self.previous_seconds:
            self.counter += 1
        else:
            self.previous_seconds = seconds
            self.counter = 0
        result = ''
        result += self._encode(self.version)
        result += self._encode(self.worker_id)
        if self.counter > 0:
            result += self._encode(self.counter)
        result += self._encode(seconds)
        return result


_worker_id = os.environ.get('shortid_worker', 0)
_short_id = ShortId(_worker_id)
set_alphabet = _short_id.set_alphabet
generate = _short_id.generate
reset_alphabet = _short_id.reset_alphabet
```

然后抄了个单元测试，去掉了多实例测试，因为只设计成单例的，多实例会发生碰撞没处理（不会）。自己加了个多线程测试（似乎没必要）和自定义字符序列的测试，经过测试自定义字符序列短了很容易发生碰撞，36个字符并发生成10万个id会有5次以内碰撞，10000会有1次左右碰撞，所以这东西得慎用。

```
import unittest
import shortid
import threading

class TestShortId(unittest.TestCase):

    def test_should_be_unambiquous_on_a_bunch_of_iterations(self):
        ids = []
        shortid.reset_alphabet()
        for i in range(0, 1000000):
            ids.append(shortid.generate())

        self.assertEqual(len(set(ids)), len(ids))

    def test_generate_max_length(self):
        lengths = []
        shortid.reset_alphabet()
        for i in range(0, 50000):
            lengths.append(len(shortid.generate()))
        self.assertEqual(max(lengths) < 12, True)


    def gen(self):
        for i in range(0, 20000):
            short_id = shortid.generate()
            self.lock.acquire()
            try:
                self.multi.append(short_id)
            finally:
                self.lock.release()


    def test_multi_thread_unique(self):
        self.multi = []
        self.lock = threading.Lock()
        shortid.reset_alphabet()
        for i in range(8):
            t = threading.Thread(target=self.gen)
            t.start()
            t.join()
        self.assertEqual(len(set(self.multi)), len(self.multi))


    def test_change_alphabet(self):
        shortid.set_alphabet('qwertyuiopasdfghjklzxcvbnm1234567890')
        ids = []
        for i in range(0, 100000):
            ids.append(shortid.generate())
        print(ids)
        self.assertEqual(len(set(ids)), len(ids))
```
单测结果：
![](https://pic3.zhimg.com/80/v2-ddd1f958d4f20c5a99e588ae4bca90cd_hd.jpg)
