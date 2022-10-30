"""
    m:跨越一个磁道所需时间             设置                       约为0.2ms
    n:跨越磁道数                         计算
    s:磁臂启动时间                   设置                       约为2ms
    寻找时间Ts：Ts = m * n + s           计算
    r:磁盘转速                      设置                       约为5400r/min
    延迟时间Tr：Tr = 1 / (2 * r)         计算
    b:每次访问要读写的字节数           随机生成                    设置数量级为数千、数万
    n1:磁道扇区数                    设置                       约为100到200个扇区
    n2:扇区字节数                    设置                       512B   也有4096B
    N：每一个磁道上的字节数 N=n1*n2
    传输时间：Tt = b / (r * N /60000)    计算(ms)
    处理访问时间：Ta = Ts + Tr + Tt       计算(ms)
    磁道数由外向内：0到199
    所在磁道                        随机生成
    磁头移动方向                     随机生成
"""

"""
原始版本
"""
import random

import matplotlib.pyplot as plt

global m, s, r, n1, n2, head, direction, request


def setParameter():  # 设置参数，需要UI设计
    global m, s, r, n1, n2, head, direction, request  # n, Ts, Tr, Ta, Tt
    m = float(input("跨越一个磁道所需时间（ms）:"))
    s = float(input("磁道启动时间（ms）："))
    r = float(input("磁盘转速(rad/min)："))
    n1 = int(input("磁盘扇区数:"))
    n2 = int(input("扇区字节数:"))
    head = random.randint(0, 199)
    direction = random.randint(1, 2) % 2  # direction取0向外（左，磁道号变小）
    request = []  # 磁道请求
    request_num = random.randint(20, 40)  # 请求数

    for i in range(request_num):
        request.append(random.randint(0, 199))

    print("不同进程访问磁道序列：" + str(request))  # 随机生成的数据 直接展示
    print("初始磁头所在位置：" + str(head))
    if direction == 0:
        print("初始磁头移动方向：由内向外，向左")
    else:
        print("初始磁头移动方向：由外向内，向右")
    # n = Ts = Tr = Ta = Tt = 0


def computeTime(seq):  # 计算时间，需要在ui界面显示
    global m, s, r, n1, n2, head, direction, request
    seq_filesize = []  # 每个磁道请求的字节数
    distance = []
    Ts = []
    Tt = []
    Ta = []
    Tr = round(1 / (2 * r/60000), 2)  # 平均旋转延迟时间
    for i in range(1, len(seq)): #计算时间参数
        distance.append(abs(seq[i] - seq[i - 1]))  # 每次处理请求所移动的距离
        Ts.append(round(m * distance[i - 1] + s, 2))  # 每次处理请求的寻道时间

        seq_filesize.append(random.randrange(2000,40000,1))#随机生成 每个磁道请求的数据字节数
        Tt.append(round(seq_filesize[i-1] / (r * n1 * n2 / 60000), 2))  # 每次所处理请求的传输时间

        Ta.append(round(Ts[i - 1] + Tt[i - 1] + Tr, 2))  # 每次所处理请求的 访问处理时间

    print("引臂移动序列:" + str(seq))
    print("对应磁道请求的数据大小（Byte）:" + str(seq_filesize))
    print("磁臂移动量：" + str(distance))
    print("寻道时间(ms):" + str(Ts))
    print("旋转延迟(ms):" + str(Tr))
    print("传输时间(ms):" + str(Tt))
    print("访问处理时间(ms):" + str(Ta))

    print("全部请求磁臂总移动量:" + str(sum(distance)))
    print("全部请求访问总处理时间(ms):" + str(sum(Ta)))
    displayDisk(seq, Ta)

    """seq动态绘图"""


def displayDisk(seq, Ta):
    fig = plt.figure()
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
    plt.rcParams['axes.unicode_minus'] = False

    # 创建四个表格，411代表创建4行1列，当前在1的位置
    ax = fig.add_subplot(1, 1, 1)
    # 给表的Y轴位置加上标签，rotation代表让文字横着展示，labelpad代表文字距表格多远了
    ax.set_xlabel('时间(ms)')
    ax.set_ylabel('磁道')
    # 给定一个参数，用来标识是不是第一次创建
    line = None
    # 给定一个X轴和Y轴的参数列表，用作后面承载数据
    obsX = []
    obsY = []
    i = 0
    time0 = 0
    while (i < len(Ta)):
        # 往列表插入展示的点的坐标
        time0 += Ta[i]
        obsX.append(time0)  # 横坐标是时间
        obsY.append(seq[i])  # 纵坐标是磁道

        # 如果图还没有画，则创建一个画图
        if line is None:
            # -代表用横线画，g代表线的颜色是绿色，.代表，画图的关键点，用点代替。也可以用*，代表关键点为五角星
            line = ax.plot(obsX, obsY, '-r', marker='*')[0]

        # 这里插入需要画图的参数，由于图线，是由很多个点组成的，所以这里需要的是一个列表
        line.set_xdata(obsX)
        line.set_ydata(obsY)

        # 我这里设计了一种方法，当X轴跑了100次的时候，则让X坐标的原点动起来
        '''
        if len(obsX) < 100:
            ax.set_xlim([min(obsX), max(obsX) + 30])
        else:
            ax.set_xlim([obsX[-80], max(obsX) * 1.2])
        '''
        # Y轴的话我就没让他动了，然后加一个10，防止最高的订单顶到天花板
        ax.set_ylim([min(obsY), max(obsY) + 10])
        ax.set_xlim(0, max(obsX))
        # 这个就是表的刷新时间了，以秒为单位
        plt.pause(0.5)

        i += 1
        if i == len(Ta) - 1:
            input("按任意键继续")


# ---------------------------------------------------------------FCFS 先来先服务
def firstComeFirstSchedule():  # 先来先服务
    global m, s, r, n1, n2, head, direction, request  # n, Ts, Tr, Ta, Tt
    seq = [head]  # 访问序列
    for i in range(len(request)):
        seq.append(request[i])
    return seq


# --------------------------------------------------------------- SSTF最短寻道时间优先

def calculateDifference(queue, head, diff):  # 计算请求所在磁道和磁头的距离
    for i in range(len(diff)):
        diff[i][0] = abs(queue[i] - head)


def findMin(diff):  # 找到距离磁头距离最小的磁道
    index = -1
    minimum = 999999999

    for i in range(len(diff)):
        if (not diff[i][1] and
                minimum > diff[i][0]):
            minimum = diff[i][0]
            index = i
    return index


def shortestSeekTimeFirst():  # SSTF 最短寻道时间优先  request head两个参数就可以
    global m, s, r, n1, n2, head, direction, request
    l = len(request)
    diff = [0] * l
    cur_head = head
    for i in range(l):
        diff[i] = [0, 0]

    seq = [0] * (l + 1)

    for i in range(l):
        seq[i] = cur_head
        calculateDifference(request, cur_head, diff)
        index = findMin(diff)
        diff[index][1] = True
        cur_head = request[index]

    # for last accessed track
    seq[len(seq) - 1] = cur_head
    return seq


# --------------------------------------------------------------------SCAN 电梯算法
def SCAN():
    global m, s, r, n1, n2, head, direction, request
    right = []  # 向右，是由外向内，磁道号变大 direction取1
    left = []  # 向左，是由内向外，磁道号变小，direction取0
    seq = [head]
    cur_direction = direction
    if cur_direction == 0:  # 方向向左，磁道往小
        left.append(0)  # 0是第一个磁道,最外磁道
    elif cur_direction == 1:  # 方向向右，磁道往大
        right.append(199)  # 199是最后一个磁道号，最内磁道

    for i in range(len(request)):
        if request[i] < head:
            left.append(request[i])
        if request[i] > head:
            right.append(request[i])

    left.sort()
    right.sort()

    run = 2
    while run != 0:
        if cur_direction == 0:  # 当前向左
            for i in range(len(left) - 1, -1, -1):
                seq.append(left[i])
            cur_direction = 1  # 向左访问玩，开始向右访问
        elif cur_direction == 1:  # 当前向右
            for i in range(len(right)):
                seq.append(right[i])
            cur_direction = 0
        run -= 1

    return seq


# --------------------------------------------------------------------LOOK改良版电梯算法
def LOOK():
    global m, s, r, n1, n2, head, direction, request
    right = []  # 向右，是由外向内，磁道号变大 direction取1
    left = []  # 向左，是由内向外，磁道号变小，direction取0
    seq = [head]
    cur_direction = direction

    for i in range(len(request)):
        if request[i] < head:
            left.append(request[i])
        if request[i] > head:
            right.append(request[i])

    left.sort()
    right.sort()

    run = 2
    while run != 0:
        if cur_direction == 0:  # 当前向左
            for i in range(len(left) - 1, -1, -1):
                seq.append(left[i])
            cur_direction = 1  # 向左访问玩，开始向右访问
        elif cur_direction == 1:  # 当前向右
            for i in range(len(right)):
                seq.append(right[i])
            cur_direction = 0
        run -= 1

    return seq


if __name__ == '__main__':
    sequence = []
    setParameter()
    select = int(input("选择调度算法:"))
    if select == 1:
        sequence = firstComeFirstSchedule()
    elif select == 2:
        sequence = shortestSeekTimeFirst()
    elif select == 3:
        sequence = SCAN()
    elif select == 4:
        sequence = LOOK()

    computeTime(sequence)
    '''
        鼠标点击类似“重置”，可重新设置参数，执行程序
    '''
    # --------------------------------------------重新执行，所有数据重新初始化
