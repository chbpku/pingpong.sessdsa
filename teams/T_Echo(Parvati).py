from table import *
import random
import math

global op_speed
global op_hitpoint
global op_getspeed
global my_addspeed
global my_hitpoint
global setpoint
global namecard
op_speed = list()  # op_spped存储的是本回合结束回合对手的回球速度
op_getspeed = list()  # op_getspeed是本回合击球后下一回合对手所面临的球速
op_hitpoint = list()  # op_hitpiont是本回合击球后下一回合对手的击球点
my_addspeed = list()  # my_addspeed是我方给球加的速度
my_hitpoint = list()  # my_hitpoint是我方将球击到的位置
halftable = (DIM[3]-DIM[2])/2
crosstime = (DIM[1]-DIM[0])/BALL_V[0]
setpoint = 1
r = 1
count = 1


def serve(op_side: str, ds: dict) -> tuple:
    i = random.randint(3, 4)
    if i == 3:
        return 0, (6*halftable-2000)/crosstime  # 以各二分之一的概率将球以最大速度击向两个角落
    elif i == 4:
        return DIM[3], (-6*halftable+2000)/crosstime


def play(tb: TableData, ds: dict) -> RacketAction:
    is_new_oponent(tb.op_side['name'])
    # 该函数用来判断是否已经更换了对手，若更换了对手，则清空ds中数据

    hitplace = tb.ball['position'].y  # 球的落点
    ds = {"my_hitpoint": my_hitpoint, "op_speed": op_speed, "op_hitpoint": op_hitpoint,
          "my_addspeed": my_addspeed, "op_getspeed": op_getspeed}
    # 建立字典来存储每次的复盘数据
    ds["my_hitpoint"].append(tb.ball['position'].y)
    '''
        op_getspeed[i]是第i回合对手接到球的速度
        op_op_speed[i]是第i-1回合对手给球的加速
    '''
    if len(ds["op_getspeed"]) == 0:  # 如果是对方发球的首回合，那么记上一回合结束对手的的回球加速为0
        ds["op_speed"].append(0)
    else:  # 其他情况则记录对手面临的球速和回球速度
        enermy_getspeed = ds["op_getspeed"][len(ds["op_getspeed"])-1]
        enermy_add_speed = find_opp_addspeed(tb.ball['velocity'].y, enermy_getspeed, tb.ball['position'].y)
        ds["op_speed"].append(enermy_add_speed)

    move = tb.ball['position'].y - tb.side['position'].y  # 迎球所需要跑动的距离
    move = 0 if abs(move) < 2000 else move-2000*move//abs(move)

    MY_COST = 2500  # 初始化跑位体力损失和吃道具的体力损失
    Catchcard_Cost = -10

    if getwhichcard(tb) is not False:  # 如果要去取道具，所需的最小加速
        Catchcard_Cost = getwhichcard(tb)

    def usecard(tb):  # 定义使用道具的函数
        if len(tb.side['cards']) == 0:  # 道具箱为空
            card = None
        else:  # 选择出特定道具
            for j in tb.side['cards']:
                if j.__eq__('AM'):
                    return j
            card = tb.side['cards'][len(tb.side['cards'])-1]
        return card

    def cardside(card):  # 选择使用的道具
        if card is None:
            return None
        elif card.__eq__('SP') or card.__eq__('DL') or card.__eq__('AM'):
            return 'OPNT'
        else:
            return 'SELF'

    if hitplace <= 2000 or hitplace >= DIM[3]-2000:  # 这里讨论击球点是否为顶点，是为了避免贴边飞行的情况出现
        i = 0
        if hitplace <= 2000:  # 讨论击球点为下顶点
            if tb.op_side['position'].y < DIM[3]/2:  # 判断对手在球台上半区还是下半区
                MY_COST = int(chooseroute(hitplace, DIM[3]-2001, tb.ball['velocity'].y, move, tb, ds))+1
                # 计算个人跑位消耗
                while not isinvaild(tb, MY_COST+tb.ball['velocity'].y):  # 在合法碰壁的前提下
                    if i < 1000:
                        MY_COST += 1
                        i += 1
                    elif i >= 1000:
                        MY_COST -= 1
            else:
                MY_COST = int(chooseroute(hitplace, 2001, tb.ball['velocity'].y, move, tb, ds))-1
                while not isinvaild(tb, MY_COST+tb.ball['velocity'].y):  # 在合法碰壁的前提下
                    if i < 1000:
                        MY_COST += 1
                        i += 1
                    elif i >= 1000:
                        MY_COST -= 1
        elif hitplace >= DIM[3] - 2000:  # 讨论击球点为上顶点
            if tb.op_side['position'].y < DIM[3]/2:  # 判断对手在球台上半区还是下半区
                MY_COST = int(chooseroute(hitplace, DIM[3]-2001, tb.ball['velocity'].y, move, tb, ds))+1
                while not isinvaild(tb, MY_COST+tb.ball['velocity'].y):
                    if i < 1000:
                        MY_COST += 1
                        i += 1
                    elif i >= 1000:
                        MY_COST -= 1
            else:
                MY_COST = int(chooseroute(hitplace, 2001, tb.ball['velocity'].y, move, tb, ds))-1
                while not isinvaild(tb, MY_COST+tb.ball['velocity'].y):
                    if i < 1000:
                        MY_COST += 1
                        i += 1
                    elif i >= 1000:
                        MY_COST -= 1
    else:  # 击球点非顶点
        i = 0
        if tb.op_side['position'].y < DIM[3] / 2:
            MY_COST = int(chooseroute(hitplace, DIM[3]-2001, tb.ball['velocity'].y, move, tb, ds))+1
            while not isinvaild(tb, MY_COST+tb.ball['velocity'].y):
                if i < 1000:
                    MY_COST += 1
                    i += 1
                elif i >= 1000:
                    MY_COST -= 1
        else:
            MY_COST = int(chooseroute(hitplace, 2001, tb.ball['velocity'].y, move, tb, ds))-1
            while not isinvaild(tb, MY_COST+tb.ball['velocity'].y):
                if i < 1000:
                    MY_COST += 1
                    i += 1
                elif i >= 1000:
                    MY_COST -= 1

    if Catchcard_Cost != -10:   # 选择吃道具的情况，记录各类参数
        ds["my_addspeed"].append(Catchcard_Cost)
        velocity = get_opp_getspeed(Catchcard_Cost, tb.ball['velocity'].y, tb.ball['position'].y)
        ds["op_getspeed"].append(velocity)
        ds["op_hitpoint"].append(getlocation(hitplace, Catchcard_Cost))
        return RacketAction(tb.tick, move, Catchcard_Cost, running(tb.side['life'], tb.ball['position'].y),
                            cardside(usecard(tb)), usecard(tb))
    else:   # 选择不吃道具的情况，记录各类参数
        ds["my_addspeed"].append(MY_COST)
        velocity = get_opp_getspeed(MY_COST, tb.ball['velocity'].y, tb.ball['position'].y)
        ds["op_getspeed"].append(velocity)
        ds["op_hitpoint"].append(getlocation(hitplace, MY_COST))
        return RacketAction(tb.tick, move, MY_COST, running(tb.side['life'], tb.ball['position'].y),
                            cardside(usecard(tb)), usecard(tb))


def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return


def findlocation(position, vy):  # 本函数用于倒推对手击球的位置
    sy = -vy*crosstime+position
    location = 0  # 初始化location,location为对方击球时位置的y坐标
    if sy > 0:
        if DIM[3] < sy < 2*DIM[3]:  # 当球触碰上边一次时
            location = DIM[3]-abs(sy-DIM[3])
        elif sy >= 2*DIM[3]:
            location = sy-2*DIM[3]  # 当球先触碰下边再触碰上边时
    else:
        if abs(sy) < DIM[3]:  # 当球触碰下边一次时
            location = -sy
        elif DIM[3] <= abs(sy) <= 2*DIM[3]:  # 当球先触碰上边再触碰下边时
            location = sy+2*DIM[3]
    return location


def isinvaild(tb: TableData, vy):  # 判断是否合法碰壁
    Y = vy*crosstime+tb.ball['position'].y  # 记录移动的总距离
    if Y % DIM[3] > 2000:   # 非边角情况
        count = Y//DIM[3]   # 记录碰壁次数
        bounce_count = abs(count)
    else:
        count = (Y//DIM[3]) if (Y > 0) else (1-Y//DIM[3])   # 记录碰壁次数
        bounce_count = count
    if bounce_count in (1, 2):
        return True
    else:
        return False


def cardpoint(tb: TableData, card: Card):  # 求切点，用于吃道具

    class point:    # 定义点类
        def __init__(self, p1, p2):
            self.p1 = p1
            self.p2 = p2

    # 落点到圆心距离
    d = math.sqrt((card.pos.x-tb.ball['position'].x)*(card.pos.x-tb.ball['position'].x) +
                  (card.pos.y-tb.ball['position'].y)*(card.pos.y-tb.ball['position'].y))
    # 落点到切点的距离
    l = math.sqrt(d*d-r*r)
    # 点到圆心的单位向量
    x0 = (card.pos.x-tb.ball['position'].x)/d
    y0 = (card.pos.y-tb.ball['position'].y)/d
    # 切线与点心连线的夹角
    f = math.asin(r/d)
    # 正反两个方向旋转单位向量
    x1 = x0 * math.cos(f) - y0 * math.sin(f)
    y1 = x0 * math.sin(f) + y0 * math.cos(f)
    x2 = x0 * math.cos(f) - y0 * math.sin(f)
    y2 = x0 * math.sin(f) + y0 * math.cos(f)
    # 新坐标
    x1 = (x1 + card.pos.x) * l
    y1 = (y1 + card.pos.y) * l
    x2 = (x2 + card.pos.x) * l
    y2 = (y2 + card.pos.y) * l
    point.p1 = (x1, y1)
    point.p2 = (x2, y2)
    return point


def enermycost(hitplace, initialv, ds: dict, tb):   # 计算对手一回合中的消耗
    enermy_move = hitplace-tb.op_side['position'].y  # 计算对手的跑位距离

    if judge_opp_addspeed(hitplace, initialv, ds) != -1:
        enermy_add_speed = judge_opp_addspeed(hitplace, initialv, ds)  # 判断对手的加速
    else:
        if tb.side['position'].y <= DIM[3]/2:
            enermy_add_speed = enermy_chooseroute(hitplace, DIM[3], initialv)
        else:
            enermy_add_speed = enermy_chooseroute(hitplace, 0, initialv)

    return (enermy_move / FACTOR_DISTANCE) ** 2 + (enermy_add_speed / FACTOR_SPEED) ** 2
    # 返回对手在公式计算下的体力消耗


def judge_opp_addspeed(hitpoint, op_get_speed, ds: dict):  # 判断对手的加速
    global op_speed
    global op_hitpoint
    global op_getspeed

    for i in range(len(ds['op_hitpoint'])): #根据存储的对手在面对不同位置和不同球速时回球的情况，判断对手的可能回球策略
        if abs(hitpoint-(ds['op_hitpoint'][i])) < 2000:
            if abs(op_get_speed-ds['op_getspeed'][i]) < 2000:
                if i != len(ds['op_hitpoint'])-1:
                    return ds['op_speed'][i+1]

    return -1


def enermy_chooseroute(touchpoint, target, initialv):     # 对手的路径选择
    # touchpoint:击球点，target:球击中对侧的目标位置，initialv：击球前球在y方向上速度

    touchpointupper = DIM[3]+DIM[3]-touchpoint  # touchpointupper1:击上边1次的情况
    touchpointunder = -touchpoint  # touchpointunder1:击下边1次的情况

    targetupper = DIM[3]+DIM[3]-target
    targetunder = -target

    velocityup1 = (targetupper-touchpoint)/crosstime  # 这里可以画一个草图来研究一下，计算打不同角的边界速度
    velocitydown1 = (targetunder-touchpoint)/crosstime
    velocityup2 = -(targetunder-touchpointupper)/crosstime
    velocitydown2 = -(targetupper-touchpointunder)/crosstime
    mincost = min(abs(velocitydown1-initialv), abs(velocityup1-initialv),
                  abs(velocitydown2-initialv), abs(velocityup2-initialv))
    # 找到其中最小的体力消耗并返回
    if abs(velocitydown1-initialv) == mincost:
        return velocitydown1-initialv
    elif abs(velocityup1-initialv) == mincost:
        return velocityup1-initialv
    elif abs(velocitydown2-initialv) == mincost:
        return velocitydown2-initialv
    elif abs(velocityup2-initialv) == mincost:
        return velocityup2-initialv


def costcounting(mymove, mycost, enermycost):   # 计算体力消耗的公式
    MY_Cost = (mymove/FACTOR_DISTANCE)**2+(mycost/FACTOR_SPEED)**2
    return enermycost-MY_Cost


def is_new_oponent(name):  # 判断是否更换了对手，用于决定复盘数据是否重新记录
    global setpoint
    global namecard
    global op_speed
    global op_hitpoint
    global op_getspeed
    global my_addspeed
    global my_hitpoint

    if setpoint == 1:
        namecard = name
        setpoint = 0
    else:
        if namecard != name: #如果更换了对手，那么之前存储的关于对手的数据将被全部清空
            namecard = name
            setpoint = 1
            op_speed = list()
            op_getspeed = list()
            op_hitpoint = list()
            my_addspeed = list()
            my_hitpoint = list()


def counttouchpoint(the_velocity, my_hitpoint):     # 记录碰上方还是下方墙壁
    if the_velocity*crosstime + my_hitpoint > 2*DIM[3]:
        return 1
    elif DIM[3] < the_velocity*crosstime+my_hitpoint <= 2*DIM[3]:
        return -1
    else:
        return 1


def find_opp_addspeed(my_getspeed, opp_last_getspeed, my_hitpoint):
    # find_opp_addspeed是根据本回合我方接球位置，接球速度，和上一回合对手接球的速度来测算对手给球的加速
    the_speed = my_getspeed*counttouchpoint(-my_getspeed, my_hitpoint)
    return the_speed-opp_last_getspeed


def getlocation(position, vy):  # 本函数用于推断我方将球击出后球的落点
    sy = vy*crosstime+position
    location = 0  # 初始化location,location为对方击球时位置的y坐标
    if sy > 0:
        if sy <= DIM[3]:
            location = DIM[3]
        elif DIM[3] < sy < 2*DIM[3]:  # 当球触碰上边一次时
            location = DIM[3]-abs(sy-DIM[3])
        elif sy >= 2*DIM[3]:
            location = sy-2*DIM[3]  # 当球先触碰下边再触碰上边时
    else:
        if abs(sy) < DIM[3]:  # 当球触碰下边一次时
            location = -sy
        elif DIM[3] <= abs(sy) <= 2*DIM[3]:  # 当球先触碰上边再触碰下边时
            location = sy+2*DIM[3]
    return location


def get_opp_getspeed(my_add_velocity, orgin_velocity, my_hitpoint):  # 获取对手接到球时球的速度
    the_velocity = my_add_velocity+orgin_velocity
    the_velocity = counttouchpoint(the_velocity, my_hitpoint)*the_velocity
    return the_velocity


def getwhichcard(tb: TableData):  # 只获取变压器和旋转球
    list1 = list()  # 分别用于存四种优先级的道具的加速度
    if len(tb.cards['cards']) == 0:  # 场上没有道具
        return False
    else:
        for card in tb.cards['cards']:
            if togetcard(tb, card) is not False:
                if card.__eq__('AM')or card.__eq__('SP'):
                    list1.append(togetcard(tb, card))   # 获取变压器和旋转球
        if len(list1) != 0:
            return min(list1)   # 返回最小的加速度，也就是最优的卡片
        else:
            return False


def togetcard(tb: TableData, card):  # 获取卡片的路线选择
    t1 = (card.pos.y+1410-tb.ball['position'].y)/abs(card.pos.x-1410-tb.ball['position'].x)
    t2 = (card.pos.y-1410-tb.ball['position'].y)/abs(card.pos.x+1410-tb.ball['position'].x)
    vy1 = t1 * BALL_V[0]
    vy2 = t2 * BALL_V[0]
    acc1 = vy1 - tb.ball['velocity'].y
    acc2 = vy2 - tb.ball['velocity'].y
    acc_list = list()
    a1 = max(acc1, acc2)
    a2 = min(acc1, acc2)
    for acc in range(int(a2), int(a1)):
        if isvaild(tb, acc+tb.ball['velocity'].y) is True:  # 记录合法方法的加速度
            acc_list.append(acc)
    if len(acc_list) == 0:
        return False
    else:
        min_acc = acc_list[0]
        for acc in acc_list:
            if abs(acc) < abs(min_acc):
                min_acc = acc
        return min_acc


def isvaild(tb: TableData, vy):  # 已知y方向速度，判断是否合法碰壁
    Y = vy * crosstime + tb.ball['position'].y
    if Y % DIM[3] != 0:  # 边角情况
        count = Y//DIM[3]
        bounce_count = abs(count)
    else:
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])
        bounce_count = count
    if bounce_count == 1 or bounce_count == 2:
        return True
    else:
        return False


def running(myenergy, myposition):  # 跑位函数，体力小于60000后每次跑回中点
    if myenergy < 60000:
        return DIM[3]/2 - myposition
    return random.randint(-1, 1)


def chooseroute(touchpoint, target, initialv, move, tb, ds):  # 选择击球路线
    # touchpoint:击球点，target:球击中对侧的目标位置，initialv：击球前球在y方向上速度

    MAX_touch = 2  # MAX_touch是球行进过程中允许的最多触边次数
    touchpointupper = DIM[3] + DIM[3] - touchpoint  # touchpointupper1:击上边1次的情况
    touchpointunder = -touchpoint  # touchpointunder1:击下边1次的情况
    targetupper = DIM[3] + DIM[3] - target
    targetunder = -target

    velocity = (target-touchpoint)/crosstime
    velocityup1 = (targetupper-touchpoint)/crosstime  # 这里可以画一个草图来研究一下
    velocitydown1 = (targetunder-touchpoint)/crosstime
    velocityup2 = -(targetunder-touchpointupper)/crosstime
    velocitydown2 = -(targetupper-touchpointunder)/crosstime

    if target == 0 or target == DIM[3]:
        # 球的目标是对方的球桌顶点，相当于球在被对方击回前还有一次触边，球在行进过程中可触边的次数-1
        MAX_touch -= 1

    if len(tb.side['cards']) != 0:  # 判断是否有道具
        for j in tb.side['cards']:
            if j.__eq__('AM'):      # 若有变压器
                if MAX_touch == 1:
                    opp_cost1 = judge_opp_addspeed(getlocation(touchpoint, velocity + tb.ball['velocity'].y),
                                                   get_opp_getspeed(velocity, tb.ball['velocity'].y, touchpoint), ds)
                    opp_cost2 = judge_opp_addspeed(getlocation(touchpoint, velocityup1 + tb.ball['velocity'].y),
                                                   get_opp_getspeed(velocityup1, tb.ball['velocity'].y, touchpoint), ds)
                    opp_cost3 = judge_opp_addspeed(getlocation(touchpoint, velocitydown1 + tb.ball['velocity'].y),
                                                   get_opp_getspeed(velocitydown1, tb.ball['velocity'].y, touchpoint), ds)
                    max_opp_cost = max(abs(opp_cost1), abs(opp_cost2), abs(opp_cost3))
                    # 计算给对手最大的消耗
                    if max_opp_cost > 700:  # 返回给对手的最大消耗
                        if max_opp_cost == abs(opp_cost1):
                            return opp_cost1 - initialv
                        elif max_opp_cost == abs(opp_cost2):
                            return opp_cost2 - initialv
                        elif max_opp_cost == abs(opp_cost3):
                            return opp_cost3 - initialv
                elif MAX_touch == 2:
                    opp_cost2 = judge_opp_addspeed(getlocation(touchpoint, velocityup1 + tb.ball['velocity'].y),
                                                   get_opp_getspeed(velocityup1, tb.ball['velocity'].y, touchpoint), ds)
                    opp_cost3 = judge_opp_addspeed(getlocation(touchpoint, velocitydown1 + tb.ball['velocity'].y),
                                                   get_opp_getspeed(velocitydown1, tb.ball['velocity'].y, touchpoint), ds)
                    opp_cost4 = judge_opp_addspeed(getlocation(touchpoint, velocityup2 + tb.ball['velocity'].y),
                                                   get_opp_getspeed(velocityup2, tb.ball['velocity'].y, touchpoint), ds)
                    opp_cost5 = judge_opp_addspeed(getlocation(touchpoint, velocitydown2 + tb.ball['velocity'].y),
                                                   get_opp_getspeed(velocitydown2, tb.ball['velocity'].y, touchpoint), ds)
                    max_opp_cost = max(abs(opp_cost2), abs(opp_cost3), abs(opp_cost4), abs(opp_cost5))
                    if max_opp_cost > 700:
                        if max_opp_cost == abs(opp_cost2):
                            return opp_cost2 - initialv
                        elif max_opp_cost == abs(opp_cost3):
                            return opp_cost3 - initialv
                        elif max_opp_cost == abs(opp_cost4):
                            return opp_cost4 - initialv
                        elif max_opp_cost == abs(opp_cost5):
                            return opp_cost5 - initialv
    else:
        return enermy_chooseroute(touchpoint, target, initialv)     # 其余情况认为对手不吃道具

    if MAX_touch == 1:
        gain1 = find_out_route(move, touchpoint, velocity - initialv, tb, ds)
        gain2 = find_out_route(move, touchpoint, velocityup1 - initialv, tb, ds)
        gain3 = find_out_route(move, touchpoint, velocitydown1 - initialv, tb, ds)
        gain = max(gain1, gain2, gain3)  # 计算最大优势值
        if gain == gain1:
            return velocity - initialv
        elif gain == gain2:
            return velocityup1 - initialv
        elif gain == gain3:
            return velocitydown1 - initialv
    elif MAX_touch == 2:
        gain2 = find_out_route(move, touchpoint, velocityup1 - initialv, tb, ds)
        gain3 = find_out_route(move, touchpoint, velocitydown1 - initialv, tb, ds)
        gain4 = find_out_route(move, touchpoint, velocityup2 - initialv, tb, ds)
        gain5 = find_out_route(move, touchpoint, velocitydown2 - initialv, tb, ds)
        gain = max(gain2, gain3, gain4, gain5)
        if gain == gain2:
            return velocityup1 - initialv
        elif gain == gain3:
            return velocitydown1 - initialv
        elif gain == gain4:
            return velocityup2 - initialv
        elif gain == gain5:
            return velocitydown2 - initialv


def find_out_route(touchpoint, velocity, move, tb, ds):     # 计算对手消耗的体力
    enermy_hitpoint = getlocation(touchpoint, velocity + tb.ball['velocity'].y)
    enermy_getspeed = get_opp_getspeed(velocity, tb.ball['velocity'].y, touchpoint)
    return costcounting(move, velocity, enermycost(enermy_hitpoint, enermy_getspeed, ds, tb))
