# coding=utf-8
# Charlie之最终版

from table import *
from math import *
import random

# 固定参数
# 一趟的tick数
TICK_STEP = (DIM[1]-DIM[0])//BALL_V[0]
# 打角上的误差允许
EPS=TICK_STEP
# 打角所有允许的Y值
DEST_LIST = [3*DIM[3]-EPS,2*DIM[3]+EPS,2*DIM[3],2*DIM[3]-EPS,DIM[3]+EPS,-EPS,-DIM[3]+EPS,-DIM[3],-DIM[3]-EPS,-2*DIM[3]+EPS]
UP_DEST_LIST=[3*DIM[3]-EPS,DIM[3]+EPS,-DIM[3]+EPS,-DIM[3],-DIM[3]-EPS]
DOWN_DEST_LIST=[2*DIM[3]+EPS,2*DIM[3],2*DIM[3]-EPS,-EPS,-2*DIM[3]+EPS]

# 可调参数
# 卡片价值
CARDVALUE = {'SP':600, 'DS':100, 'IL':2000, 'DL':2000, 'TP':900, 'AM':1300}
# damage中攻守系数
ATT_PARAM=1
DEF_PARAM=1
# calpos中系数
V_EPS=100
POS_EPS=DIM[3]//20
VAL_LIM=5

# 函数库（原名pingponglib.py）
# 计算从posy出发，以vy速度的撞墙次数 （copy from 李逸飞）
def knock(posy,vy):
    Y = vy * TICK_STEP + posy  # Y是没有墙壁时到达的位置
    if vy == 0:
        return 0
    if Y % DIM[3] != 0:  # case1：未在边界，碰墙次数等于穿墙次数
        count = abs(Y // DIM[3])  # 穿过了多少次墙（可以是负的，最后取绝对值）
        return count
    else:  # case2： 恰好在边界，若Y>0则无影响，若Y<0则碰墙次数等于穿墙次数加1
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])
        return count


# 计算从posy出发，以vy速度击出后的落点纵坐标 （copy from 李逸飞），用于计算result，也用于估值
def dest_y(posy,vy):
    Y = vy * TICK_STEP + posy  # Y是没有墙壁时到达的位置
    if Y % DIM[3] != 0:   # case1：未在边界
        count = Y // DIM[3]     #碰墙次数
        tgy= (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
    else:  # case2： 恰好在边界
        tgy = Y % (2 * DIM[3])
    return tgy


# 计算从posy出发，以vy速度击出后在落点处速度（modify from 李逸飞)，计算result和用于估值
def res_v(posy,vy):
    Y = vy * TICK_STEP + posy  # Y是没有墙壁时到达的位置
    if Y % DIM[3] != 0:   # case1：未在边界
        count = Y // DIM[3]     #碰墙次数
        res = vy * ((count + 1) % 2 * 2 - 1)
    else:  # case2： 恰好在边界
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])     #碰墙次数
        res = vy * ((count + 1) % 2 * 2 - 1)
    return res


# 判断从posy出发，以vy速度发球能否得到道具card (copy from 李逸飞)
def get_card(posy ,vy, card, direc ,eps=2000):
    posx = DIM[0] if direc=='W' else DIM[1]     #针对不同的方位设置不同的参数
    vx=BALL_V[0] if direc=='W' else -BALL_V[0]
    A1 = (vy * (-card.pos.x + posx) + vx * (card.pos.y - posy))     #计算道具与路线的距离所需的参数
    A2 = (vy * (-card.pos.x + posx) + vx * (-card.pos.y - posy))
    delta = (2 * abs(BALL_V[0]) * DIM[3])
    return min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(BALL_V[0] ** 2 + vy ** 2) < eps
    #利用点到直线的距离公式计算道具与路线的距离，小于误差则能捡到此道具


# 加速费血，用于估值
def loss_acc(acc):
    loss_acc = (abs(acc) ** 2 // FACTOR_SPEED ** 2)
    return loss_acc


# 跑位费血，用于估值
def loss_run(run):
    loss_run = (abs(run) ** 2 // FACTOR_DISTANCE ** 2)
    return loss_run


# 计算合法击出的最小加速度，用于己方策略的判断与对对方的估值
def legal_least_acc(posy,vy):
    if knock(posy,vy) in (1,2):   # 无需加速即可合法反弹
        return 0
    return corner_least_acc(posy,vy)   # 最小加速度出现在打角


# 计算打角的最小加速度，用于己方策略的判断和对对方的估值
def corner_least_acc(posy,vy):
    return min([(dest - posy) // TICK_STEP - vy for dest in DEST_LIST], key=abs)


# 计算将球打到远离对方上次接球位置的角所需的加速度，即暴力打角
def corner_violet_acc(posy,vy,side):
    if side=='up':      # 对方位于中点以上则打下角
        return min([(dest-posy)//TICK_STEP-vy for dest in UP_DEST_LIST],key=abs)
    else:       # 对方位于中点下上则打上角
        return min([(dest -posy)//TICK_STEP-vy for dest in DOWN_DEST_LIST],key=abs)


# 计算在考虑了使用道具的情形下的扣血值，用于估值
def damage(desty,op_vy,op_posy,mode=None,acc_param=1,bat_param=1):
    least=corner_least_acc if mode=='corner' else legal_least_acc
    # 一般假设对方以最小合法加速度击出，此为对方最小的加速消耗
    # 如对方为打角模式，改用打角最小加速度
    # 迎球伤害实际是以假设对方不跑位计算，但这在增加系数后不影响对对方跑位与迎球距离之和的反映
    return DEF_PARAM*loss_acc(acc_param*least(desty,op_vy))+ATT_PARAM*bat_param*loss_run(desty-op_posy)


# 用统计平均方法预测对方的击球策略
def Calpos(T,A,y0,v0):
    # 这里，A,T是存储的历史数据，v0，y0是本回合的速度和纵坐标这一个数对
    totCount = 0
    hlist = []
    for i in range(1,len(T)-1):
        y = T[i].ball['position'].y
        v = T[i].ball['velocity'].y+A[i].acc
        h = T[i+1].ball['position'].y
        # 完成一个搜索，遍历之前每一次击出球的位置和纵坐标，以及对方的返回的落点
        if abs(v-v0) < V_EPS and abs(y-y0) < POS_EPS:
            # 如果与当前回合的（v,y）数对很接近，那么我们就将这一个数对作为本回合的有用的数对
            hlist.append(h)
            totCount = totCount + 1
    if totCount > VAL_LIM:  # 当符合条件的样本数量积累到一定程度时
        h = Aver(hlist)  # 先给出对于对方落点的预测值，即直接求平均
    else:
        h = DIM[3]//2
    return h


# 跑位计算用到的求平均值函数
def Aver(alist):
    n = len(alist)
    s = 0
    for i in range(n):
        s = s + alist[i]
    return s/n

# 跑位计算用到的求标准差函数
def Variance(alist):
    average = Aver(alist)
    n = len(alist)
    s = 0
    for i in range(n):
        s = s + (alist[i]-average)**2
    variance = math.sqrt(s/n)
    return variance

# 模式判别模块（原名analysis.py）
# ds的维护与模式分析
def analysis(tb,ds):
    # 判断ds中是否有数据
    if 'current' not in ds.keys():
        ds['current']={'pattern':[],'data':[],'action':[]}
        ds['history']={}
    # 判断是否对战过，如果有，那么就直接维护历史的pattern,若没有，在历史中加入当前对手
    res={'domin':None,'pattern':[],'state':[]}
    # 面对对方的使用了隐身术的情况进行处理，避免出现使用None进行计算
    if tb.op_side['position'] is None:
        tb.op_side['position']=(DIM[0] if tb.side['position'].x==DIM[1] else DIM[0],dest_y(tb.ball['position'].y,-tb.ball['velocity'].y))
    if tb.op_side['run_vector'] is None :
        tb.op_side['run_vector']=1
    # 对方的加速是可以直接算出来的
    v0=v1=0  # v0和v1表示对方接到球时球速和击出球的球速
    if len(ds['current']['data'])==0:
        v0=BALL_V[1]
        # 如果是己方的第一局，那么没有对方的击球数据，默认对方是不加速的。只是一局的不精确，对于大局没有什么影响。
    else:
        v0=res_v(ds['current']['data'][-1].ball['position'].y,
             ds['current']['data'][-1].ball['velocity'].y+ds['current']['action'][-1].acc)
        # 对于v0的计算，这仅由上一局己方的击球决定。
    v1=-res_v(tb.ball['position'].y,-tb.ball['velocity'].y)
    # 对于v1的推算，将球速反向后击出，则结果的相反数就是对方击出球的速度。
    tb.op_side['accelerate'] = v1 - v0

    # 对跑位的计算,这里的跑位有着一定的猜测因素，不一定准确
    if len(ds['current']['data']) > 0:  # 如果没有历史数据，就跳过
        life_loss = ds['current']['data'][-1].op_side['life'] - tb.op_side['life']
        # 对方在两局间的生命值损失
        acc_loss = loss_acc(tb.op_side['accelerate'])
        # 由于加速导致的损失，这一部分是可以精确计算的。
        delta = tb.op_side['position'].y - ds['current']['data'][-1].op_side['position'].y  # 这里的delta和F都是为了解二元方程写起来方便。
        F = FACTOR_DISTANCE
        tmp = sqrt(abs(-delta ** 2 + 2 * (life_loss - acc_loss) * F ** 2))
        run_vector = [(delta + tmp) / 2, (delta - tmp) / 2]
        # run_vector作为一个列表，里面放了两个解，分别是迎球和跑位的距离。
        tmp_pos = ds['current']['data'][-1].op_side['position'].y
        # 下面是对这两个解中哪一个是跑位的猜测。
        if tmp_pos + run_vector[1] > DIM[3] or tmp_pos + run_vector[1] < DIM[2]:
            run_vector = run_vector[1]  # 如果跑出场外，那么肯定是不合理的。
        elif tmp_pos + run_vector[0] > DIM[3] or tmp_pos + run_vector[1] < DIM[2]:
            run_vector = run_vector[0]  # 同上
        elif run_vector[0] * run_vector[1] < 0:
            # 如果两个结果反向，那么基本可以肯定对方是往中位跑位
            if tmp_pos > DIM[3] // 2:
                run_vector = min(run_vector)
            else:
                run_vector = max(run_vector)
        else:
            # 如果到这里都还没法确定，那么只能猜测对方跑位比迎球多。
            run_vector = max(run_vector, key=abs)
        # 将run_vector进行修改
        ds['current']['data'][-1].op_side['run_vector'] = run_vector
    # 数据的反推结束，将当前局数据加入ds中。
    ds['current']['data'].append(tb)
    # 如果有过历史对决，那么直接维护以前的pattern
    if tb.op_side['name'] in ds['history'].keys():
        ds['current']['pattern'] = ds['history'][tb.op_side['name']]['pattern'][:]
    # ct是count的简写，表示进行的局数
    ct = len(ds['current']['data'])

    # 对于主导方的判断，只是简单地比较生命值，目前还想不到有更好的判断方法
    if tb.side['life'] > tb.op_side['life']:
        res['domin'] = 'side'
    else:
        res['domin'] = 'op_side'

    # 对于模式的判定
    p = pattern(ds)
    # 回合数比较小，更加依赖于以前的数据
    if ct <= 5:
        for x in p:
            if x not in ds['current']['pattern']:
                ds['current']['pattern'].append(x)
    # 数据比较多时，可以直接使用当前盘数据
    else:
        ds['current']['pattern'] = p[:]
    res['pattern'] = ds['current']['pattern'][:]

    # 对于对战状态的判断
    if abs(tb.side['life'] - tb.op_side['life']) < 1000:  # 生命值差比较小
        res['state'].append('deadlock')
    else:
        if tb.side['life'] - tb.op_side['life'] > 5000:  # 生命值差距较大
            res['state'].append('safe')
        elif tb.op_side['life'] - tb.side['life'] > 5000:
            res['state'].append('dangerous')
    # 足够五局，可以分析前一段时间的趋势
    if ct>=5:
        pre = ds['current']['data'][ct - 5]  # 五局前
        now = ds['current']['data'][ct - 1]
        # 前几局的生命值损耗
        if (pre.op_side['life'] - now.op_side['life'])>(pre.side['life']-now.side['life']):
            res['state'].append('good')
        else:
            res['state'].append('bad')
        repeat=False
        # 记录重复的开始回合数
        rec=None
        # 对于是否呈现循环进行判断，similar是一个比较两个数据是否相似的函数，以相对误差作为标准。
        for i in reversed(range(0,ct-1)):
            pre=ds['current']['data'][i]  # pre表示之前的某个对局
            if  similar(pre.op_side['accelerate'],now.op_side['accelerate'],BALL_V[0]) and\
                    similar(pre.op_side['position'].y,now.op_side['position'].y,DIM[3]) and\
                    similar(pre.side['position'].y,now.side['position'].y,DIM[3]) and\
                    similar(pre.ball['velocity'].y,now.ball['velocity'].y,1000):
                # 如果当前局完全复现了历史局，那么是进入了循环
                repeat=True
                rec=i
                break
        if repeat:  # 如果在一个周期中，我方损失大于对方损失，则为坏循环，反之则为好循环。
            res['state'].append('repeat')
            if ds['current']['data'][rec].side['life']-tb.side['life']>\
                ds['current']['data'][rec].op_side['life']-tb.op_side['life']:
                res['state'].append('bad_repeat')
            else:
                res['state'].append('good_repeat')
    return res

# 识别模式的函数,L是一个TableData的列表
def pattern(ds):
    T=ds['current']['data']
    # 到目前为止盘数，盘数的计算方法是己方第一次准备击球算是第一局
    ct = len(T)
    if ct ==1 :
        return []
    # 对于暴力打角,idiot和midgo的分析
    corner = True
    idiot = True
    midgo = True
    lazy = True
    for i in range(max(0, ct - 10), ct):  # 这里只选择了前10盘的数据，为的是检测对方在前一段时间内的行为。
        posy = dest_y(T[i].ball['position'].y, -T[i].ball['velocity'].y)
        acc = ds['current']['data'][i].op_side['accelerate']
        # 对corner的分析是最简单的，直接看是否打角
        if not similar(T[i].ball['position'].y, 0, DIM[3],0.005) and not similar(T[i].ball['position'].y, DIM[3], DIM[3],0.005):
            corner = False
        # 对idiot的分析，考虑life损耗是否与该模式符合
        if not similar(acc, 0, 1000):
            idiot = False
        # 对midgo的分析，考虑跑位的life损耗是否与该模式符合
        run = DIM[3] // 2 - T[i - 1].op_side['position'].y
        bat = posy - DIM[3] // 2
        damage = loss_acc(acc) + loss_run(bat) + loss_run(run)
        if not similar(T[i - 1].op_side['life'] - T[i].op_side['life'], damage, RACKET_LIFE):
            midgo = False
        # 对lazy的分析，采用己方的lazy策略，计算出来的加速是否与预期相符,在可以打角的情况下没有打角而是acc=0
        v0=res_v(T[i-1].ball['position'].y,T[i-1].ball['position'].y+ds['current']['action'][i-1].acc)
        least_acc = legal_least_acc(posy, v0)
        if not similar(least_acc, acc, 1000):
            lazy = False
    p = []
    if corner:
        p.append('corner')
    if idiot:
        p.append('idiot')
    if midgo:
        p.append('midgo')
    if lazy:
        p.append('lazy')
    return p

# 判断循环模式要用到的相对误差函数
def similar(data1, data2, r,param=0.01):
    eps = abs(data1 - data2) / r
    if eps < param:
        return True
    else:
        return False

# 主程序
def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    if not ds['current']['data']:
        return  # 如果是自己和自己对战，这些数据已经被处理过时，就跳过
    op_name = ds['current']['data'][0].op_side['name']
    if op_name not in ds['history'].keys():
        # 如果还没有过历史对决，为其新建一个字典。
        ds['history'][op_name]={'data':[],'pattern':[],'action':[]}
    ds['history'][op_name]['data'] += ds['current']['data'][:]
    ds['history'][op_name]['action'] += ds['current']['action'][:]
    ds['history'][op_name]['pattern'] = ds['current']['pattern'][:]
    l = len(ds['history'][op_name]['data'])
    if l > 1000:
        # 如果历史数据太多，大于了1000，那么会影响计算速度，删去最旧的数据。
        del ds['history'][op_name]['data'][0:l - 1000]
        del ds['history'][op_name]['action'][0:l - 1000]
    # 将ds['current']清空。
    del ds['current']['data'][:]
    del ds['current']['pattern'][:]
    del ds['current']['action'][:]

def serve(opname,ds):
    return DIM[3] // 2, 280
    # 此为搜索过后对方损失最大的打法，直接打到上角


def play(tb, ds):
    situation = analysis(tb, ds) # 完成对ds的维护、对局面和模式的分析
    direc = 'W' if tb.side['position'].x == DIM[0] else 'E' # 我方所处的位置

    # 接球指令，除了跑到球的落点别无选择
    bat = tb.ball['position'].y - tb.side['position'].y

    # 道具使用指令
    side=None
    card=None
    acc_param = 1
    bat_param = 1 # 初始化，防止出错
    if tb.side['cards']:  # 如果有卡
        # 确定使用顺序，掉血包和补血包是最优先的
        for c in tb.side['cards']:
            if c.code == 'DL' or c.code == 'IL':
                card=c
                break
        if card is None:
            card = tb.side['cards'].pop()
        if card.code in ['SP', 'DL', 'AM']:  # 负面效应卡,分别是旋转球，掉血包，变压器
            side = "OPNT"
        elif card.code in ['DS', 'IL', 'TP']:  # 正面效应的卡，分别是隐身卡，加血包，瞬移术
            side = "SELF"
    if card: # 改变参数，使估值更准确，更好发挥道具效果
        if card.code == "SP":
            acc_param = 2   # 旋转球改变加速参数
        if card.code == 'AM':
            bat_param = 2   # 变压器改变跑位参数

    # 加速度指令
    # 首先根据识别出的对方模式采用不同的己方模式
    # 若判断对方为打角算法，我方的策略为估值算法为主，最小加速打角与随机打角相辅
    if 'corner' in ds['current']['pattern']:
        mode = random.choice(['evaluate','evaluate','corner','random_corner'])
        # 列表中的项及数目不是固定的，可根据对手打法临时修改，下同
        # 最初用lazy应对打角，发现过于保守，无法战胜不调整跑位的打角算法
    # 若判断对方为最小体力消耗或原路回球，我方的策略为打角
    elif 'lazy' in ds['current']['pattern'] or 'idiot' in ds['current']['pattern']:
        mode = 'corner'
    # 否则我方的策略为估值算法为主，打角为辅
    else:
        mode = random.choice(['evaluate','evaluate','corner','random_corner'])
    # 若判断我方进入了一个坏循环，为跳出循环，改变击球策略，以最小体力消耗跳出不利循环
    if 'bad_repeat' in situation['state']:
        mode = random.choice(['lazy', 'lazy', 'evaluate'])
    # 若判断对方的跑位策略不是中点跑位，生命值已不高，且存在死角，则采用暴力打角，试图一击制胜
    if 'midgo' not in situation['pattern'] \
            and int((tb.op_side['life'] / RACKET_LIFE) * BALL_V[0] * TICK_STEP) < \
                    max(tb.op_side['position'].y - DIM[2], DIM[3] - tb.op_side['position'].y):
        mode = 'violet_corner'
    # 若对方使用了旋转球，我方对旋转球进行防御
    if tb.op_side['active_card'] and tb.op_side['active_card'][1] == 'SP':
        mode = 'spinned'

    acc = None  #初始化加速度
    # 我方的具体策略
    # 模式1：估值算法，核心策略
    # 主要思路是计算每次击球我方生命值消耗与对方生命值最小消耗，找到对我方最有利的击球加速度
    if mode == 'evaluate':
        m='corner' if 'corner' in situation['pattern'] else 'legal' # 对方模式参数
        # 加速度初始赋值为最小合法击球加速度，保证击球合法
        acc = legal_least_acc(tb.ball['position'].y, tb.ball['velocity'].y)
        # 计算我方此次击球带来的收益（具体计算方法见damage函数）
        curW = damage(dest_y(tb.ball['position'].y, tb.ball['velocity'].y + acc),
                      res_v(tb.ball['position'].y, tb.ball['velocity'].y + acc),
                      tb.op_side['position'].y,m, acc_param, bat_param) - loss_acc(acc)
        #若桌上有道具，且道具出现在路径上，造成的收益还要加上道具的价值
        for card in tb.cards['cards']:
            if get_card(tb.ball['position'].y, tb.ball['velocity'].y + acc, card, direc):
                curW += 1.5*CARDVALUE[card.code]
        #对所有可能的击球加速度遍历搜索
        for vy in range(-2000, 2000):
            myacc = vy - tb.ball['velocity'].y      # 计算加速度值
            if knock(tb.ball['position'].y, vy) in (1, 2):      # 判断该加速度击球是否合法
                dest = dest_y(tb.ball['position'].y, vy)
                opvy = res_v(tb.ball['position'].y, vy)
            # 计算此次击球带来的收益
                W = damage(dest, opvy, tb.op_side['position'].y, acc_param, bat_param) - loss_acc(myacc)
                for card in tb.cards['cards']:
                    if get_card(tb.ball['position'].y, vy, card, direc):
                        W += 1.5*CARDVALUE[card.code]
            # 遍历，保存收益最大的击球加速度
                if W > curW:
                    acc = myacc
                    curW = W
    # 模式2：随机打角模式，随机打上角或下角
    elif mode =='random_corner':
        acc = corner_violet_acc(tb.ball['position'].y, tb.ball['velocity'].y,random.choice(['up','down']))
    # 模式3：最小消耗打角模式，采用消耗最小的打角加速度
    elif mode == 'corner':
        acc = corner_least_acc(tb.ball['position'].y, tb.ball['velocity'].y)
    # 模式4：暴力打角模式，判断对方位置，打远端角
    elif mode=='violet_corner':
        if tb.op_side['position'].y>=DIM[3]//2:
            side='down'
        else:
            side='up'
        acc = corner_violet_acc(tb.ball['position'].y, tb.ball['velocity'].y,side)
    # 模式5：lazy模式，采用消耗最少的合法击球加速度
    elif mode == 'lazy':
        acc = legal_least_acc(tb.ball['position'].y, tb.ball['velocity'].y)
    # 模式6：防御旋转球，加速度赋值为最小合法加速度，考虑到旋转球的效果，加速度放大到两倍
    elif mode == 'spinned':
        acc = 2 * legal_least_acc(tb.ball['position'].y, tb.ball['velocity'].y)
    # 模式7：随机模式，保证合法击球的情况下随机打一板子（实战中未用到）
    elif mode == 'random':  # 获取大量数据，以便计算
        acc=random.randint(-2000,2000)
        while knock(tb.ball['position'].y,tb.ball['velocity'].y+acc) not in (1,2):
            acc = random.randint(-3000, 3000)

    # 跑位指令
    # 为学习型跑位算法补充历史数据
    if not tb.op_side['name'] in ds['history'].keys():
        extraT=[]
        extraA=[]
    else:
        extraT=ds['history'][tb.op_side['name']]['data']
        extraA=ds['history'][tb.op_side['name']]['action']
    # 己方速度、位置在当前值一定范围内时对方平均落点
    avepos=Calpos(extraT+ds['current']['data'],extraA+ds['current']['action'],
                  tb.ball['position'].y,tb.ball['velocity'].y+acc)
    if abs(avepos-DIM[3]//2) >= DIM[3]//6:
        run = (avepos-tb.ball['position'].y)//2
    else:
        # 如果对方平均落点接近中点，极可能是上角下角平均，不采用
        run = DIM[3] // 2 - tb.ball['position'].y
    # 如果自己出现死角，改为跑中位
    if tb.side['life']<=RACKET_LIFE*0.5:
        run = DIM[3]//2-tb.ball['position'].y
    R = RacketAction(tb.tick, bat, acc, run, side, card)
    ds['current']['action'].append(R) # 添加此回合己方决策
    return R
