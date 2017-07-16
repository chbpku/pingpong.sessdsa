"""
datastore启用！开启智能新时代
不吃旋转球！
争取无敌
"""

from table import *


def serve(op_side, ds):
    """
    发球函数，总是做为West才发球
    :param op_side: 对方队名
    :param ds: 可以利用的存储字典（已弃用）
    :return: 球的y坐标，和y方向的速度
    """
    return 500000, 278


def play(tb, ds):
    """
    打球函数
    :param tb: TableData类型的对象
    :param ds: 函数可以利用的存储字典（已弃用）
    :return: 一个RacketAction对象
    """
    atick = 1800
    pos = tb.ball['position'].y
    v0 = tb.ball['velocity'].y

    acc_all = activatelist(pos, v0)[0]
    acc_up = activatelist(pos, v0)[1]
    acc_down = activatelist(pos, v0)[2]
    # 得到打两个角所需要的加速度值

    def play_helper():
        """
        不需要特意传入参数
        """
        waste = 10000000
        endacc = absmin(acc_all)

        for accs in acc_all:
            inipos = where(tb, -v0)  # 对方打过来时的位置
            endpos = where(tb, v0 + accs)  # 我们打过去的位置
            endvel = howfast(tb, v0 + accs)  # 我们打过去时的速度

            opacc_all = activatelist(endpos, endvel)[0]
            # 默认对手打角，得到他们可取的十个加速度
            opacc = absmin(opacc_all)
            # 默认对手选择了最小的打角加速度
            difwaste = (accs ** 2) // (FACTOR_SPEED ** 2) - ((inipos - endpos) ** 2) // (FACTOR_DISTANCE ** 2) // 2 -\
                       (opacc ** 2) // (FACTOR_SPEED ** 2)
            # 我们击球，对手从之前所在位置跑去迎球的最小消耗以及对手加速度的消耗

            if waste > difwaste:
                waste = difwaste
                endacc = accs
        if tb.side['life'] < 40000:
            endacc = absmin(acc_all)
        # 当我方血量降至40000以下，始终采用最小加速度
        elif tb.side['life'] < 58000 and tb.side['life'] < tb.op_side['life']:
            endacc = absmin(acc_all)
        # 当我方血量少于58000（开始出现盲区？）（这个58000还参考了老Oscar），且生命少，就选择最小加速度
        elif tb.op_side['life'] < tb.side['life'] < 58000:
            if tb.op_side['position'].y > DIM[3] / 2:
                endacc = absmin(acc_down)
            else:
                endacc = absmin(acc_up)
        # 否则来回打角
        acc = endacc

        # 对上面这段算法进行一个解释
        # 考察我方以accs回球时对方的十种回球方法，并默认对方以最小

        return acc

    acc1 = play_helper()
    acc = eatcard(tb, acc1)
    # 调用吃道具函数对加速度值进行修饰

    # 应对旋转球，且优先于吃道具
    if tb.op_side['active_card'][1] is not None:
        if tb.op_side['active_card'][1] == 'SP' or tb.op_side['active_card'][1] == 'AM':
            acc = absmin(acc_all)

    # 应对旋转球，且优先于吃道具
    if tb.op_side['active_card'][1] is not None:
        if tb.op_side['active_card'][1] == 'SP':
            acc *= 2
    endpos = where(tb, v0 + acc)
    endvel = howfast(tb, v0 + acc)

    opacc_up = activatelist(endpos, endvel)[1]
    opacc_down = activatelist(endpos, endvel)[2]
    # 对手的加速度列表
    opaccup = absmin(opacc_up)
    opaccdown = absmin(opacc_down)

    run = (opaccdown ** 2 - opaccup ** 2) // 2 + (DIM[3] / 2) - pos
    # 这个跑位通过解方程得到，此时对手打上角打下角对我方影响相同

    # 然而有时算出来的跑位会超过一半，这简直就是坠痛苦的，所以需要这一行
    if abs(run) > DIM[3] // 2:
        run = DIM[3] // 2 - pos

    # 体力不够了并且有优势的时候，或者有TP，我们开始跑位稳
    if tb.side['life'] <= 37000 and ((tb.side['life'] - tb.op_side['life'] > 0) or TPexist(tb) is True):
        run = DIM[3] // 2 - pos

    # 如果到了time out的时候，最后一下子省体力不跑位
    if tb.tick == 800000 - 444 * atick:
        run = 0

    carduse = usecard(tb, run)
    # 使用道具的过程

    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, acc, run, carduse[0], carduse[1])


def summarize(tickt, winner, reasonr, west, east, ball, ds):
    """
    此功能被弃用
    """
    return None


def absmin(alist):
    """
    求列表中绝对值最小值的函数，用于计算体力消耗最优解
    :param alist: 一个列表
    :return: 列表的最小值
    """
    for i in range(len(alist) - 1):
        if abs(alist[i]) < abs(alist[i + 1]):
            alist[i], alist[i + 1] = alist[i + 1], alist[i]
    return alist[-1]


def activatelist(pos, v):
    """
    得到所有打角的加速度
    :param pos: 球的位置
    :param v: 球当前的（y方向）速度
    :return: 三个列表：所有打角加速度，打上角的加速度，打下角的加速度
    """
    atick = 1800  # 这个是球跑一趟要的时间
    acc1 = (DIM[3] - pos + 1800) / atick - v
    acc2 = (- DIM[3] - pos + 1800) / atick - v
    acc3 = (DIM[3] * 3 - pos - 1800) / atick - v
    acc4 = (- DIM[3] - pos - 1800) / atick - v
    acc5 = (- DIM[3] - pos) / atick - v

    acc6 = (DIM[3] * 2 - pos - 1800) / atick - v
    acc7 = (DIM[3] * 2 - pos + 1800) / atick - v
    acc8 = (- DIM[3] * 2 - pos + 1800) / atick - v
    acc9 = (- pos - 1800) / atick - v
    acc10 = (DIM[3] * 2 - pos) / atick - v

    acc_all = [acc1, acc2, acc3, acc4, acc5, acc6, acc7, acc8, acc9, acc10]
    acc_up = [acc1, acc2, acc3, acc4, acc5]
    acc_down = [acc6, acc7, acc8, acc9, acc10]
    return acc_all, acc_up, acc_down


def howfast(tb, vy):
    """
    求打出球的末速度
    :param tb: TableData类型的对象
    :param vy: 击球后球的y方向速度
    :return: 打出球到达对方击球区时的速度
    """
    Y = vy * ((DIM[1] - DIM[0]) // BALL_V[0]) + tb.ball['position'].y
    if Y % DIM[3] != 0:  # case1：未在边界
        count = Y // DIM[3]  # 穿过了多少次墙（可以是负的，最后取绝对值）
        return vy * ((count + 1) % 2 * 2 - 1)
    else:
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])
        return vy * ((count + 1) % 2 * 2 - 1)


def where(tb, vy):
    """
    抄的table里的方法，求以vy回球后球到达的位置和碰撞次数
    :param tb: TableData类型的对象
    :param vy: 回球的y方向速度
    :return: 球运动到对方击打区域时的y坐标和碰撞次数
    """
    Y = vy * ((DIM[1] - DIM[0]) // BALL_V[0]) + tb.ball['position'].y
    if Y % DIM[3] != 0:
        count = Y // DIM[3]
        return (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
    else:
        return Y % (2 * DIM[3])


def accelerate_range(tb):
    """
    计算合法碰撞的情况下球可以获得的速度区间
    :param tb: TableData类型的对象
    :return: 一个列表，合法的所有加速度组成的范围区间
    """
    tickstep = ((DIM[1] - DIM[0]) // BALL_V[0])
    ball_velocity = int(tb.ball['velocity'].y)
    s_hit_minv = int(- tb.ball['position'].y // tickstep)  # 向南打的最小速度，打到对面南角，以下同理
    s_hit_maxv = int(-(tb.ball['position'].y + DIM[3] * 2) // tickstep)
    n_hit_minv = int((DIM[3] - tb.ball['position'].y) // tickstep)
    n_hit_maxv = int((3 * DIM[3] - tb.ball['position'].y) // tickstep)
    acc_range = list(range(s_hit_maxv - ball_velocity + 1, s_hit_minv - ball_velocity - 1)) +\
                list(range(n_hit_minv - ball_velocity + 1, n_hit_maxv - ball_velocity - 1))
    # 得到了所有加速度的范围区间
    return acc_range


def eatcard(tb, acc):
    """
    关于捡道具
    :param tb: TableData类型的对象
    :param acc: 目标加速度
    :return: 选择的加速度
    """
    # atick = 1800
    # 写card的过程中我们遇到过一些问题，card类型不能作为字典的键值，因此我们用每个道具的位置来标定它

    cardvalue = dict()
    cardvalue['DS'] = -1000  # 在我们当前的算法下，对手是否隐身没有影响
    cardvalue['IL'] = 2000
    cardvalue['DL'] = 2000  # 加血包减血包收益均为2000
    cardvalue['TP'] = -1000
    cardvalue['SP'] = -1000
    cardvalue['AM'] = -1000

    cardcost = {}  # 字典，接各道具的消耗
    cardacc = {}  # 字典，接各道具最佳加速

    for card in tb.cards['cards']:
        cardcost[(card.pos.x, card.pos.y)] = -cardvalue[card.code]
        cx = card.pos.x
        cy = [0] * 5
        cy[0] = card.pos.y
        cy[1] = 2 * DIM[3] - cy[0]
        cy[2] = 2 * DIM[3] + cy[0]
        cy[3] = -cy[0]
        cy[4] = cy[0] - 2 * DIM[3]  # 道具的x坐标不变，通过对称后得到五个y坐标
        t_ball = abs((cx - tb.side['position'].x) / tb.ball['velocity'].x)  # t_ball是球到道具所用的时间
        a = [0] * 5
        cost = [0] * 5
        for i in range(0, 5):
            a[i] = int((cy[i] - tb.ball['position'].y) / t_ball - tb.ball['velocity'].y)  # 各方案的加速度
            inipos = where(tb, -tb.ball['velocity'].y)  # 对方打过来时的位置
            endpos = where(tb, tb.ball['velocity'].y + a[i])  # 我们打过去的位置
            endvel = howfast(tb, tb.ball['velocity'].y + a[i])  # 我们打过去时的速度
            opacc_all = activatelist(endpos, endvel)[0]
            # 默认对手打角，得到他们可取的十个加速度
            opacc = absmin(opacc_all)
            # 默认对手选择了最小的打角加速度
            cost[i] = (a[i] ** 2) // (FACTOR_SPEED ** 2) - ((inipos - endpos) ** 2) // (FACTOR_DISTANCE ** 2) // 2 - \
                      (opacc ** 2) // (FACTOR_SPEED ** 2)
        bestway = None
        for i in range(0, 5):  # 选出最好方案（加速度在加速区间）
            if a[i] in accelerate_range(tb):
                if bestway is None:
                    bestway = i
                else:
                    if cost[i] < cost[bestway]:
                        bestway = i
        if bestway is None:  # 若所有加速度都不符合，无法接此道具，消耗无穷大
            cardcost[(card.pos.x, card.pos.y)] += 1000000
        else:
            cardcost[(card.pos.x, card.pos.y)] += cost[bestway]  # 接该道具消耗加上最好方案的消耗
            cardacc[(card.pos.x, card.pos.y)] = a[bestway]  # 接该道具的速度
    getcard = None

    inipos = where(tb, -tb.ball['velocity'].y)  # 对方打过来时的位置
    endpos = where(tb, tb.ball['velocity'].y + acc)  # 我们打过去的位置
    endvel = howfast(tb, tb.ball['velocity'].y + acc)  # 我们打过去时的速度
    opacc_all = activatelist(endpos, endvel)[0]
    # 默认对手打角，得到他们可取的十个加速度
    opacc = absmin(opacc_all)
    # 默认对手选择了最小的打角加速度

    # 我们击球，对手从之前所在位置跑去迎球的最小消耗以及对手加速度的消耗
    origincost = (acc // FACTOR_SPEED) ** 2 - ((inipos - endpos) // FACTOR_DISTANCE) ** 2 // 2 -\
                 (opacc // FACTOR_SPEED) ** 2
    # 不接道具的消耗，算法同上

    for card in tb.cards['cards']:  # 选择消耗比不接道具低的且消耗最低的道具
        if cardcost[(card.pos.x, card.pos.y)] < origincost:
            if getcard is None:
                getcard = (card.pos.x, card.pos.y)
            else:
                if cardcost[(card.pos.x, card.pos.y)] < cardcost[getcard]:
                    getcard = (card.pos.x, card.pos.y)

    if getcard is not None:  # 将加速度替换成接此道具的加速度
        acc_chosen = cardacc[getcard]
    else:
        acc_chosen = acc
    return acc_chosen


def TPexist(tb):
    """
    判断TP是否在道具盒里
    :param tb: TableData类型的对象
    :return: 在的话返回True，不在返回False
    """
    cardbox = tb.side['cards']
    if len(cardbox) != 0:
        for i in range(len(cardbox)):
            if cardbox[i] == 'TP':
                return True
        return False
    else:
        return False


def usecard(tb, dis):
    """
    使用道具
    :param tb: TableData类型的对象
    :param dis: 跑位距离
    :return: 对哪一方使用，以及使用道具的种类
    """
    cardbox = tb.side['cards']
    if len(cardbox) == 0:  # 道具为空时返回None
        return None, None
    else:
        for i in range(len(cardbox)):
            if cardbox[i] == 'TP' and ((dis > DIM[3] / 2.1) or (tb.side['life'] < 40000)):
                return 'SELF', cardbox[i]
            elif cardbox[i] == 'IL':
                return 'SELF', cardbox[i]
            elif cardbox[i] == 'DL':
                return 'OPNT', cardbox[i]
            elif cardbox[i] == 'SP':
                return 'OPNT', cardbox[i]
            elif cardbox[i] == 'AM':
                return 'OPNT', cardbox[i]
            elif cardbox[i] == 'DS':
                return 'OPNT', cardbox[i]
        return None, None
