from table import *
# from test import *

# 从table中导入所有常量
from table import *
# STEP 半个来回时长
STEP = 1800
"""
修改内容：
1.完善了速度取值的边界
2.撞墙的判定可以用杨帆的函数，更加简洁
3.目前没有加血包和减血包的情况
"""

'''
# 打球函数
def play(tb:TableData, ds) -> RacketAction:
    # 创建ball_data类实例
    bd = ball_data(tb)
    # 创建player_data类（迎球方）和op_player_data类（跑位方）实例
    pd = player_data(tb)
    opd = op_player_data(tb)
    ##########然后调用下面的函数，传入tb,ds,bd,pd,opd############
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, 0, 0, None, None)
'''

# 假装打球函数
def pretend_play(tb:TableData, ds) -> RacketAction:
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, 0, 0, None, None)

class ball_data():
    def __init__(self, tb):
        self.pos_x = tb.ball['position'].x
        self.pos_y = tb.ball['position'].y
        self.vel_x = tb.ball['velocity'].x
        self.vel_y = tb.ball['velocity'].y

class player_data():
    def __init__(self, tb):
        self.life = tb.side["life"]

class op_player_data():
    def __init__(self, tb):
        self.active_card = tb.op_side["active_card"]

'''
# 这是原始的fly函数
def ball_fly_to(bd:ball_data):
    """
    根据我方出射点坐标、出射速度，算出到达对方位置
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param count: 与桌碰撞次数
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    # x方向的位置更新
    # tb.step 为 1800 tick
    bd.pos_x += bd.vel_x * STEP
    # Y 为 没有墙壁时乒乓球到达的位置
    Y = bd.vel_y * STEP + bd.pos_y
    height = DIM[3] - DIM[2]
    # 若球没有打在边界上(以下计算过程具体解释详见 table.py Ball类的fly()函数)
    if Y % height != 0:
        # 计算碰撞次数
        count = Y // height
        # 计算真实点y轴坐标
        bd.pos_y = (Y - count * height * (1 - 2 * (count % 2)) + height * (count % 2))
    # 若恰好在边界上
    else:
        # 计算碰撞次数
        count = (Y // height if (Y > 0) else (1 - Y // height))
        # 计算真实点y轴坐标
        bd.pos_y = Y % (2 * height)
    # 计算并更新y轴速度
    bd.vel_y = bd.vel_y * ((count + 1) % 2 * 2 - 1)
    return abs(count), bd
'''

def ball_fly_to(bd:ball_data):
    """
    根据我方出射点坐标、出射速度，算出到达对方位置
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param count: 与桌碰撞次数，可正可负
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    # x方向的位置更新
    # tb.step 为 1800 tick
    bd.pos_x += bd.vel_x * STEP
    # Y 为没有墙壁时乒乓球到达的位置（镜像点）
    Y = bd.vel_y * STEP + bd.pos_y
    # 把镜像点转化为真实点
    bd.pos_y = mirror2real(Y)[0]
    # 计算并更新y轴速度
    count = mirror2real(Y)[1]
    bd.vel_y = bd.vel_y * ((count + 1) % 2 * 2 - 1)
    return bd, abs(count)

def mirror2real(y_axis:int):
    """
    将镜像点映射为真实点
    :param y_axis: 镜像点y坐标
    :return: 真实点y坐标，范围0-1,000,000
    """
    n_mirror, remain = divmod(y_axis, DIM[3] - DIM[2])
    # n_mirror是穿过墙的数目，可正可负
    return {0:remain, 1:DIM[3] - remain}[n_mirror % 2], n_mirror

def side_life_consume(pd:player_data, opd:op_player_data, tb:TableData, ds):
    """
    根据我方此次决策，算出迎球+加速+跑位的总体力消耗(考虑道具)
    :param player_data: 决策前迎球方的信息
    :param op_player_data: 决策前跑位方的信息
    :param player_action: 我方此次决策结果 RocketAction类
    :param bat_distance: 此次决策指定迎球的距离
    :param run_distance: 此次决策指定跑位的距离
    :return: 执行完决策后我方体力值
    """
    # 减少体力值（考虑跑位方可能使用掉血包道具）
    if opd.active_card == CARD_DECL:
        pd.life -= CARD_DECL_PARAM
    # 获取我方此次决策结果
    player_action = pretend_play(tb, ds)
    '''
    player_action的属性： 
    .bat t0~t1迎球的动作矢量（移动方向及距离）
    .acc t1触球加速矢量（加速的方向及速度）
    .run t1~t2跑位的动作矢量（移动方向及距离）
    .card 对'SELF'/'OPNT'使用道具元组（(side, card)使用对象及道具）
    '''
    # 将迎球方动作中的距离速度等值规整化为整数
    player_action.normalize()
    # 球拍的全速是球X方向速度，按照体力值比例下降
    velocity = int((pd.life / RACKET_LIFE) * BALL_V[1])
    # bat_distance 为指定迎球的距离
    bat_distance = player_action.bat
    # 如果指定迎球的距离大于最大速度的距离，则丢球，比赛结束
    if abs(bat_distance) > velocity * tb.step:
        return False

    # 按照迎球的距离减少体力值（考虑跑位方之前可能使用变压器道具）
    pd.life -= (abs(bat_distance) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if opd.active_card == CARD_AMPL else 1)

    # 按照给球加速度的指标减少体力值（考虑跑位方之前可能使用变压器道具）
    pd.life -= (abs(player_action.acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if opd.active_card == CARD_AMPL else 1)

    # 如果指定跑位的距离大于最大速度的距离，则采用最大速度距离
    run_distance = sign(player_action.run) * min(abs(player_action.run), velocity * tb.step)

    # 按照跑位的距离减少体力值（考虑跑位方之前可能使用变压器道具）
    param = 0
    if player_action == CARD_TLPT:  # 如果碰到瞬移卡，则从距离减去CARD_TLPT_PARAM再计算体力值减少
        param = CARD_TLPT_PARAM
    if abs(run_distance) - param > 0:
        pd.life -= (abs(run_distance) - param) ** 2 // FACTOR_DISTANCE ** 2
    return pd.life

'''
def get_op_acc(bd:ball_data):
    """
    根据对方打过来的球的速度位置，反推出跑位方（对方）加速度
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :param count: 与桌碰撞次数
    :return: 跑位方（对方）加速度
    """
    # Y 为 没有墙壁时到达的位置
    Y = -bd.vel_y * STEP + bd.pos_y
    height = DIM[3] - DIM[2]
    # 若球没有打在边界上，计算碰撞次数
    if Y % height != 0:
        count = Y // height
    else:# 若恰好在边界上
        count = (Y // height if (Y > 0) else (1 - Y // height))
    return bd.vel_y * ((count + 1) % 2 * 2 - 1) - 111
    # 此次111本应该为我方上一次打球至对方处，球y轴的速度。此数据应当从pingpong.py里29行左右（记录日志项）log中获取。
    # 暂时搁置
'''
# 5.29修改，一共改动了三个函数
def ball_v_range(b_d:tuple) -> tuple:
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param STEP: 1800 tick
    :param b_d[2]: b_d[2] = tb.ball['position'].y,接球时球的纵坐标
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 可取速度的边界
    """
    height = DIM[3] - DIM[2]
    # v0,v1,v2,v3是速度的范围边界:可取[v3,v2]∪[v1,v0]
    v0 = (3 * height - b_d[2]) // STEP
    v1 = (1 * height - b_d[2]) // STEP + 1
    v2 = (0 - b_d[2]) // STEP
    v3 = (-2 * height - b_d[2]) // STEP + 1
    # 贴边打的情况算作反弹零次，需要排除
    if v2 == 0:
        v2 = -1
    # 返回一个元组，依次为速度的四个边界值
    return v0, v1, v2, v3

def fly_assistant(b_d:tuple, v_range:tuple, card:Card) -> list:
    """
    根据某个确定的道具位置和球所在的位置，计算吃到它所需要的竖直速度
    :param b_d: b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    :param v_range: 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    :param card: 是一个Card类
    :param height: 球桌宽度，DIM[3] - DIM[2]
    :param x0: x0 = b_d[0]，接球时球的横坐标
    :param y0: y0 = b_d[1]，接球时球的纵坐标
    :param vx0: vx0 = b_d[2]，球的水平速度
    :return: 返回一个list，元素为符合击中某道具要求的竖直速度
    """
    height = DIM[3] - DIM[2]
    x0, y0, vx0 = b_d[0], b_d[1], b_d[2]
    # 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    v0, v1, v2, v3 = v_range
    # 要吃的道具共有五个可能的镜像点/真实点，置于列表y中
    y = []
    y[0] = card.pos[1]
    y[1] = 2 * height + card.pos[1]
    y[2] = 2 * height - card.pos[1]
    y[3] = -card.pos[1]
    y[4] = -2 * height + card.pos[1]
    # 到达道具位置用时
    card_step = abs(x0 - card.pos[0]) // vx0
    # 在能到达道具的一系列速度中挑选出属于区间v_range的，保存到列表中并返回
    # 列表中的元素类型是int
    return [vy for vy in
        filter(lambda v: (v >= v3 and v <= v2)or(v >= v1 and v <= v0),
               map(lambda x: (x - y0) // card_step, y))]

def ball_fly_to_card(b_d:tuple, cards_al:list) -> list:
    """
    cards_al means cards_available
    根据桌面上现有的道具种类、位置和球所在的位置，计算吃到对应的各个道具所需要的竖直速度
    :param b_d: b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    :param cards_al: list，决策前桌面上道具的信息，元素是Card类
    :param height: 球桌宽度，DIM[3] - DIM[2]
    :param v_range: 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    :return: 返回一个list，其元素为符合击中某道具要求的竖直速度群，vy_list的元素和cards_al的元素是对应关系
    """
    v_range = ball_v_range(b_d)
    # 吃到序号为i的道具需要的速度（所有可能的速度）保存在v[i]中
    vy_list = []
    for i in range(len(cards_al)):
        vy_list[i] = fly_assistant(b_d, v_range, cards_al[i])
    # 返回吃到所有道具所需要的竖直速度，通过对应索引查找
    return vy_list




import time
import numpy as np
import pandas as pd

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side: str, ds:dict) -> tuple:
    return BALL_POS[1], - 500000// 1800 - 1

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
Height = 1000000
C = 0.69
# 固定的V指向区间，默认以V=0时为取余数点。分为两个数组
V_range1 = np.arange(-1999800, -1800, 3600)
V_range2 = np.arange(1000800, 2998800, 3600)
# Series共用，V_range to Series
Series1 = pd.Series(V_range1, index=V_range1)
Series2 = pd.Series(V_range2, index=V_range2)

series = pd.concat([Series1, Series2])

Random = [np.random.random() for i in range(1000000)]
# 球的
Card_Value = {
    'SP': 500,
    'DS': 0,
    'IL': 2000,
    'DL': 2000,
    'TP': 1000,
    'AM': 1500,
}


# 返回真实点的高度
def y2real(y):
    # 关于np问题的过滤
    if type(y) is np.ndarray:
        y_real = np.where(y % (2 * Height) < Height, y % Height, Height - y % Height)
        return y_real
    if y % (2 * Height) < Height:
        y_real = y % Height
    else:
        y_real = Height - y % Height
    return y_real
    # n_mirror, remain = divmod(y, DIM[3])
    # # n_mirror是穿过墙的数目
    # return {0: remain, 1: DIM[3] - remain}[n_mirror % 2]


# 对手的估值函数
def op_player_f(v, v0, y0):
    """
    对手估值函数
    :param v: 打过去的速度
    :param v0: 接到时的速度
    :param y0: 接到的位置
    :return:
    """
    lose = int(((v - v0) / FACTOR_SPEED) ** 2)
    op_lose = int(((y2real(y0 - 1800 * v0) - y2real(y0 + 1800 * v)) / FACTOR_DISTANCE) ** 2) * C

    return -(lose - op_lose)


def ball_fly(v, y0):
    """
    一次球飞过去，算出球的落点和速度
    :param v: 球飞出的速度
    :param y0: 球飞出的位置
    :return: 速度，位置
    """
    # 对数字运算

    y = y0 + 1800 * v
    if type(v) == np.ndarray:
        y_real = np.where(y % (2 * Height) < Height, y % Height, Height - y % Height)
        new_v = np.where(y % (2 * Height) < Height, v, -v)
        return y_real, new_v
    if y % (2 * Height) < Height:
        y_real = y % Height
    else:
        y_real = Height - y % Height
        v = -v
    return v, y_real


def getMax(v0, y0, target_range=None, T_start=2000, gamma=0.99, T_end=2, evaluate=op_player_f):
    """
    求给定一元函数求v_range最大值。使用模拟退火算法
    :param target_range: 指向对面坐标可以取值的范围
    :param T_end:
    :param gamma:
    :param T_start:
    :param v0:
    :param y0:
    :param evaluate:
    :return:
    """
    # 首先做v1
    if target_range == None:
        # 获取符合这个y0的v范围
        if v0 <= 0:
            target_range = V_range1 + y0 % 1800
        else:
            target_range = V_range2 + y0 % 1800
            if y0 % 1800 >= 1200:
                target_range = target_range[:-1]
    current_v = int(len(target_range) * np.random.random())
    current_value = evaluate((target_range[current_v] - y0) // 1800, v0, y0)
    # value_matrix = evaluate(target_range, v0, y0)
    # 添加BSF，制胜法宝
    BSF = current_v, current_value
    TTL = 50
    while T_start > T_end:
        # 获取下一个值：
        new_v = (int(T_start * (-0.5 + np.random.random())) + current_v) % len(target_range)
        # 获取新的估值
        new_value = evaluate((target_range[current_v] - y0) // 1800, v0, y0)
        dE = new_value - current_value
        # 获取随机
        ran = np.random.random()
        # 判断是否满足跃迁条件
        if dE > 0 or ran <= np.exp(-dE / T_start):
            current_v = new_v
            current_value = new_value
            BSF = max(BSF, (current_v, current_value), key=lambda x: x[1])
        # 降温
        T_start *= gamma
        # print(current_v, current_value, sep = ',')
    v_best = (target_range[BSF[0]] - y0) // 1800
    # print(v_best - v0, '*********************')
    return v_best, BSF[1]


def pandas_max(v0, y0, target_range=None, evaluate=op_player_f):
    """
    pandas暴力求最值
    熊猫就是无敌
    :param v0:
    :param y0:
    :param target_range:
    :return: 对方返回的速度、相应估值
    """
    if target_range is None:
        # 获取符合这个y0的v范围
        if v0 <= 0:
            target_range = Series1 + y0 % 1800
        else:
            target_range = Series2 + y0 % 1800
            # 排除最后一个值超标的情况
            if y0 % 1800 >= 1200:
                target_range = target_range[:-1]
        # 索引也同步增加
        target_range.index += y0 % 1800
    if evaluate is op_player_f:
        f = lambda v: evaluate(v, v0, y0)
    else:
        f = evaluate
    values = target_range.apply(f)
    max_v = values.argmax()
    return (max_v - y0) // 1800, values[max_v]


# t1 = time.time()
# print(pandas_max(40,10000))
# t2 = time.time()
# print(t1,t2,t2-t1)

def player_f(v, v0, y0):
    """
    我方估值函数。算两层
    :param v:
    :param v0:
    :param y0:
    :return:
    """
    # 对方发球位置
    y1 = y2real(y0 - 1800 * v0)
    # 我们打到的位置
    v_in, y2 = ball_fly(v, y0)
    # 对方打回的速度
    # TODO 用对方函数算一个最小值出来，修改op_player_f估值为负
    if v0 < 0:
        vy = -1 - y0 / 1800 + v0
    else:
        vy = 557 - y0 / 1800 + v0
    v_out = vy
    # 打回的位置
    y3 = y2real(y2 + 1800 * v_out)
    # 己方决策函数
    # 知道自己的跑位，因此这一项赋给0.5
    lose = ((v - v0) / FACTOR_SPEED) ** 2 + 0.5 * ((y0 - y3) / FACTOR_DISTANCE) ** 2  # 己方损失
    op_lose = ((v_out - v_in) / FACTOR_SPEED) ** 2 + C * ((y1 - y2) / FACTOR_DISTANCE) ** 2  # 对方损失
    # 返回对方减少 - 我方减少。这个尽可能大
    return v, op_lose - lose, y3

def ball_v_range_up(bd:ball_data):
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    #delta_height = 300
    v0 = (1 * Height - bd.pos_y) // STEP + 1
    v1 = (3 * Height - bd.pos_y) // STEP - 10
    v2 = (-1 * Height - bd.pos_y) // STEP + 1
    return v0, v1, v2

def ball_v_range_down(bd:ball_data):
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    #delta_height = 300
    v0 = (-2* Height - bd.pos_y) // STEP + 1
    v1 = (2 * Height - bd.pos_y) // STEP + 1
    v2 = (- bd.pos_y) // STEP - 1
    return v0, v1, v2

def play(tb:TableData, ds:dict) -> RacketAction:
    times = tb.tick/1800
    bd = ball_data(tb)
    pd = player_data(tb)
    opd = op_player_data(tb)

    v0, y0 = tb.ball['velocity'].y, tb.ball['position'].y

    v_best = max((pandas_max(v0, y0, Series1, lambda v: player_f(v, v0, y0)[1]),
                  pandas_max(v0, y0, Series2, lambda v: player_f(v, v0, y0)[1])), key=lambda x: x[1])[0]
    y2reach = player_f(v_best, v0, y0)[2]
    # 如果有道具，则对自己使用
    if tb.cards['cards']:
        side, item = 'SELF', tb.cards['cards'].pop(0)
    else:
        side, item = None, None
        #计算速度范围
    #t = random.randint(0,1)
    if times%4 in (1,2):
        v_range = ball_v_range_up(bd)
    else:
        v_range = ball_v_range_down(bd)
    # 计算介于可行范围内的最小的目标v

    min_index = v_range.index(min(v_range, key=lambda x: abs(x - tb.ball['velocity'].y)))
    # 是大值则-1，小值则+1
    target = v_range[min_index] + 1 - tb.ball['velocity'].y

    # 如果有道具，则对自己使用
    if tb.cards['cards']:
        side, item = 'SELF', tb.cards['cards'].pop(0)
    else:
        side, item = None, None
    # 返回
    y2reach = (y2reach + tb.ball['position'].y) // 2
    safe_zone = get_run_side(tb)
    if safe_zone[1] == 2:
        if not(safe_zone[0][0] < y2reach < safe_zone[0][1]):
            y2reach = min(safe_zone[0], key = lambda pos: abs(pos - y2reach))
        else:
            if (y2reach - 500000) * (tb.side['position'].y - 500000) < 0:
                y2reach = 500000
    elif safe_zone[1] == 3:
        if safe_zone[0][0] < y2reach < safe_zone[0][1]:
            y2reach = min(safe_zone[0], key = lambda pos: abs(pos - y2reach))
        else:
            if (y2reach - 500000) * (tb.side['position'].y - 500000) < 0:
                y2reach = 500000
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y,
                        target * (2 if tb.op_side['active_card'] == ('SELF', CARD_SPIN) else 1), y2reach - tb.ball['position'].y, side, item)

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return
    
def get_run_side(tb:TableData):
    """
    获取本次跑位的边界点位置
    :param tb: 桌面数据
    :return: (跑位边界值元组, 当前状态)。1表示55500以上，无死角；2表示27700-55500，回中无死角；3表示以下，回中也有死角。
    """
    # TODO 每局开始时调用，获取战场进度
    bat_s_max = int(((tb.side['life'] - 4000)/ RACKET_LIFE) * BALL_V[0]) * 1800
    if bat_s_max > 1000000:
        return ((0, 1000000), 1)
    elif bat_s_max > 500000:
        return ((1000000 - bat_s_max, bat_s_max), 2)
    else:
        return ((bat_s_max, 1000000 - bat_s_max), 3)