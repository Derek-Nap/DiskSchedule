"""
    m:跨越一个磁道所需时间             设置                       约为0.2ms
    n:跨越磁道数                         计算
    s:磁臂启动时间                   设置                       约为2ms
    寻找时间Ts：Ts = m * n + s           计算
    r:磁盘转速(rad/min)              设置                       约为5400r/min
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

'''
只需一个UI页面，—————————————————————————————————————————————————————————————————————————————————————
将所有标记的地方放入一个UI页面就可以—————————————————————————————————————————————————————————————————————
UI页面需要显示的地方：
1.main中的调度算法的选择        输入
2.setParameter() 设置参数    输入
3.computeTime() 计算时间     输出
4.diplayDisk（）动态绘图      输出，由computeTime（）调用，需要在UI中保持动态效果
5.UI在输出结果后不会结束程序和退出，可以重置输入，进行新的计算，直到用户关闭窗口
'''

import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

global m, s, r, n1, n2, head, direction, request

from tkinter import *
from tkinter.ttk import *


def setParameter():  # 设置参数，需要UI设计
    global m, s, r, n1, n2, head, direction, request  # n, Ts, Tr, Ta, Tt
    m = float(num1.get())
    s = float(num2.get())
    r = float(num3.get())
    n1 = int(float(num4.get()))
    n2 = int(float(num5.get()))
    head = random.randint(0, 199)
    direction = random.randint(1, 2) % 2  # direction取0向外（左，磁道号变小）
    request = []  # 磁道请求
    request_num = random.randint(20, 40)  # 请求数

    for i in range(request_num):
        request.append(random.randint(0, 199))

    # n = Ts = Tr = Ta = Tt = 0


def computeTime(sequence):  # 计算时间，需要在ui界面显示
    global m, s, r, n1, n2, head, direction, request, seq1, Ta
    seq1 = sequence
    seq_filesize = []  # 每个磁道请求的字节数
    distance = []
    Ts = []
    Tt = []
    Ta = []
    Tr = round(1 / (2 * r / 60000), 2)  # 平均旋转延迟时间
    for i in range(1, len(seq1)):  # 计算时间参数
        distance.append(abs(seq1[i] - seq1[i - 1]))  # 每次处理请求所移动的距离
        Ts.append(round(m * distance[i - 1] + s, 2))  # 每次处理请求的寻道时间

        seq_filesize.append(random.randrange(2000, 40000, 1))  # 随机生成 每个磁道请求的数据字节数
        Tt.append(round(seq_filesize[i - 1] / (r * n1 * n2 / 60000), 2))  # 每次所处理请求的传输时间

        Ta.append(round(Ts[i - 1] + Tt[i - 1] + Tr, 2))  # 每次所处理请求的 访问处理时间

    '''
    输出展示，需要UI————————————————————————————————————————————————————————————————————————————————
    '''
    textpad.delete(1.0, END)  # 清空文本
    textpad.insert(INSERT, '不同进程访问磁道请求序列：\n' + str(request) + '\n\n')
    textpad.insert(INSERT, '初始磁头所在位置：\n' + str(head) + '\n\n')

    if direction == 0:
        textpad.insert(INSERT, '初始磁头移动方向：由内向外，向左\n\n')
    else:
        textpad.insert(INSERT, '初始磁头移动方向：由外向内，向右\n\n')

    textpad.insert(INSERT, '算法结果：\n')
    textpad.insert(INSERT, '引臂移动序列：\n' + str(seq1) + '\n\n')
    textpad.insert(INSERT, '序列对应的数据大小（Byte）：\n' + str(seq_filesize) + '\n\n')
    textpad.insert(INSERT, '磁臂移动量：：\n' + str(distance) + '\n\n')
    textpad.insert(INSERT, '寻道时间(ms)：\n' + str(Ts) + '\n\n')
    textpad.insert(INSERT, '旋转延迟(ms)：\n' + str(Tr) + '\n\n')
    textpad.insert(INSERT, '传输时间(ms)：\n' + str(Tt) + '\n\n')
    textpad.insert(INSERT, '访问处理时间(ms)：\n' + str(Ta) + '\n\n')
    textpad.insert(INSERT, '全部请求磁臂总移动量：\n' + str(sum(distance)) + '\n\n')
    textpad.insert(INSERT, '全部请求访问总处理时间(ms)：\n' + str(sum(Ta)) + '\n\n')

    '''
    动态绘制函数，需要UI————————————————————————————————————————————————————————————————————————————————
    '''


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


def shortestSeekTimeFirst():  # SSTF 最短寻道时间优先
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


def num6_get():

    select = int(num6.get())

    if select == 1:
        sequence = firstComeFirstSchedule()
    elif select == 2:
        sequence = shortestSeekTimeFirst()
    elif select == 3:
        sequence = SCAN()
    elif select == 4:
        sequence = LOOK()

    computeTime(sequence)


def displayDisk():
    '''
        动态绘制函数，需要UI————————————————————
        把动态的图像嵌入到UI里面，保留动态效果
    '''
    #
    # win = Toplevel(root)
    # win.title('绘制动态折线图')
    # win.geometry('800x500')

    fig = plt.figure(figsize=(8, 5))

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
    plt.rcParams['axes.unicode_minus'] = False

    # # 创建画布
    # canvas = FigureCanvasTkAgg(fig, master=win)
    # canvas.draw()
    # canvas.get_tk_widget().grid()

    fig.clf()
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
        obsY.append(seq1[i])  # 纵坐标是磁道
        ax.set_ylim([min(obsY), max(obsY) + 10])
        ax.set_xlim(0, max(obsX))

        # 如果图还没有画，则创建一个画图
        if line is None:
            # -代表用横线画，g代表线的颜色是绿色，.代表，画图的关键点，用点代替。也可以用*，代表关键点为五角星
            line = ax.plot(obsX, obsY, '-r', marker='*')[0]
            # canvas.draw()

        # 这里插入需要画图的参数，由于图线，是由很多个点组成的，所以这里需要的是一个列表
        line.set_xdata(obsX)
        line.set_ydata(obsY)

        # 这个就是表的刷新时间了，以秒为单位
        plt.pause(0.5)

        i += 1
        if i == len(Ta) - 1:
            pass


if __name__ == '__main__':
    sequence = []

    '''
    选择调度算法，需要放入UI页面——————————————————————————————————————————————————————————————————————————————————————
    限定只能选择四个中的一个
    '''
    # 绘制界面
    root = Tk()
    root.title('选择调度算法')
    root.geometry('820x800+40+0')

    # 设置参数
    label1 = Label(root, text='跨越磁道时间:')
    label1.place(x=20, y=20, width=90, height=30)
    num1 = StringVar(root, value='')
    entry1 = Entry(root, textvariable=num1)
    entry1.place(x=115, y=20, width=50, height=30)

    label2 = Label(root, text='磁道启动时间:')
    label2.place(x=175, y=20, width=90, height=30)
    num2 = StringVar(root, value='')
    entry2 = Entry(root, textvariable=num2)
    entry2.place(x=270, y=20, width=50, height=30)

    label3 = Label(root, text='磁盘转速:')
    label3.place(x=330, y=20, width=60, height=30)
    num3 = StringVar(root, value='')
    entry3 = Entry(root, textvariable=num3)
    entry3.place(x=395, y=20, width=50, height=30)

    label4 = Label(root, text='磁盘扇区数:')
    label4.place(x=455, y=20, width=70, height=30)
    num4 = StringVar(root, value='')
    entry4 = Entry(root, textvariable=num4)
    entry4.place(x=530, y=20, width=50, height=30)

    label5 = Label(root, text='扇区字节数:')
    label5.place(x=590, y=20, width=70, height=30)
    num5 = StringVar(root, value='')
    entry5 = Entry(root, textvariable=num5)
    entry5.place(x=665, y=20, width=50, height=30)

    button1 = Button(root, text='设置参数', command=setParameter)
    button1.place(x=730, y=15, width=70, height=40)

    # 选择调度算法 command=getMon
    label6 = Label(root, text='select = ')
    label6.place(x=20, y=75, width=60, height=30)
    num6 = StringVar(root, value='1.FCFS  2.SSTF  3.SCAN  4.LOOK')
    entry6 = Entry(root, textvariable=num6)
    entry6.place(x=80, y=75, width=490, height=30)

    button2 = Button(root, text='选择调度算法', command=num6_get)
    button2.place(x=590, y=70, width=90, height=40)

    button3 = Button(root, text='开始绘制折线图',
                     command=displayDisk)
    button3.place(x=700, y=70, width=100, height=40)

    # 创建树菜单以及每一列的名称
    textpad = Text(root)
    textpad.place(x=20, y=150, width=780, height=610)

    '''
    UI在输出结果后不会结束程序和退出，可以重置输入，进行新的计算，直到用户关闭窗口——————————————————————————————————————————————————————————
    '''
    root.mainloop()
