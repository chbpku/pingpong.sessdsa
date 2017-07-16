
from table import *
import math
import shelve
import math


def serve(op_side: str, ds: dict):
    return BALL_POS[1],850




def find_run(ds,tb,opname):   # 按跑中间计算，如果对方有跑中间倾向返回True

    v0 = ds[opname]['myvel'][-1]
    d_vy = abs(abs(v0) - abs(tb.ball['velocity'].y))
    d_life = ds[opname]['op_life'][-1] - tb.op_side['life']
    d_life1 =1250 + d_vy**2/400     #(500000 - ds['oppos'][-1])**2/200000000 + d_vy**2/400
    if abs(d_life1 - d_life) <= 60:
        ds[opname]['middle'] += 1
    else :
        ds[opname]['notmid'] += 1
    if ds[opname]['middle'] /(ds[opname]['middle'] + ds[opname]['notmid']) >= 0.8 :
        return True
    else :
        return False

def find_batting(pos,ds,tb,opname):        #统计对方pos1附近区域的频率，以调整跑位策略
    if abs(1000000 - pos) >= abs(pos):
        if tb.ball['position'].y <= 100000:
            ds[opname]['cornor'] += 1
        else:
            ds[opname]['notcor'] += 1
    else :
        if tb.ball['position'].y >= 900000:
            ds[opname]['cornor'] += 1
        else:
            ds[opname]['notcor'] += 1
    if ds[opname]['cornor'] /(ds[opname]['cornor'] + ds[opname]['notcor']) >= 0.85:
        return True
    else :
        return False



usecard = [False,None,None,8]


def play(tb,ds):

    opname = tb.op_side['name']
    if tb.tick == 0 or tb.tick == tb.step:  # 处于开局
        try:
            a = ds[opname]  # 按对手划分
        except KeyError:  # 如果这个文件没有内容，说明球队尚未建立历史数据
            ds[opname] = {}
            ds[opname]['mypos'] = [500000]  # 我方位置
            ds[opname]['myvel'] = [850]  # 我方速度 （我方发球时，第一个速度是850）
            ds[opname]['oppos'] = [500000]  # 对方位置 (我方发球时，对方初始位置是中央）
            ds[opname]['op_life'] = [tb.op_side['life']]  # 对方生命
            ds[opname]['middle'] = 0            #对方跑中间的次数
            ds[opname]['notmid'] = 0            #对方不跑中间的次数
            ds[opname]['cornor'] = 0             #对方打到省力角的次数
            ds[opname]['notcor'] = 0             #对方打到不省力角的次数
            ds[opname]['batpos'] = [500000]


    if tb.op_side['active_card'] == 'AM': # 如果对方使用了变压器，进行满足要求的最小加速
        d_vy = waytosolveAM(tb, ds)
    elif tb.op_side['active_card'] == 'SP':        #如果对方使用了
        d_vy = 2*waytosolveAM(tb, ds)
    else:
        d_vy = batting(tb,ds,opname)[0]
        d_vy = isvaluable(tb,d_vy)
    d_life = d_vy**2//400
    my_pos = get_point(tb.ball['position'].y,tb.ball['velocity'].y + d_vy)[0]                  #记录自己的击球位置
    pos1 = get_point(get_point(tb.ball['position'].y, tb.ball['velocity'].y + d_vy)[0],
                     get_point(tb.ball['position'].y, tb.ball['velocity'].y + d_vy)[1])[0]
    # 计算对方若不对球进行加速求反弹回的位置
    s1 = pos1 - tb.ball['position'].y
    pos2 = (DIM[3] - DIM[2]) // 2  # 球桌中点位置
    s2 = pos2 - tb.ball['position'].y
    if not find_batting(ds[opname]['batpos'][-1], ds, tb, opname) or tb.side['life'] <= 58000:  # 如果对方没有打pos1附近区域的习惯，跑到中点
        run = 500000 - tb.ball['position'].y
    else:
        if pos1 > pos2:  # 跑向中点与pos1中较近的那个点（但不与pos1反向）
            if tb.ball['position'].y > pos2:
                run = s1
            else:
                run = s2

        else:
            if tb.ball['position'].y > pos2:
                run = s2
            else:
                run = s1


    ds[opname]['batpos'].append(pos1)
    ds[opname]['myvel'].append(tb.ball['velocity'].y + d_vy)     #记录自己的击球速度
    ds[opname]['op_life'].append(tb.op_side['life'])         #记录对方生命值
                      #记录击球时对方位置

    for i in range(len(tb.side['cards'])):        #判定是否使用道具
        use(tb, tb.side['cards'][i].code, d_life, pos1,run)
    if len(tb.side['cards']) == 3 and usecard[1] == None:     #如果道具和已满 则使用道具
        usecard[1] = tb.side['cards'][0].code
        if usecard[1] == 'TP' or usecard[1] == 'IL' or usecard[1]== 'DS':
            usecard[2] = 'SELF'
        else :
            usecard[2] = 'OPNT'
    cardname = usecard[1]
    cardside = usecard[2]
    usecard[2],usecard[1],usecard[3] = None,None,8


    return RacketAction(tb.tick,tb.ball['position'].y-tb.side['position'].y,d_vy,run,cardside,cardname)

def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return

def get_min(a,b,c):
    min = a
    if abs(b) < abs(a):
        min = b
    if abs(c) < abs(min):
        min = c
    return min

def cornor(tb,side):         #得到打角所需的最小速度改变量，及其所消耗的生命值
    if side == 'south':
        vy_kill1 = (2000000 - tb.ball['position'].y) // 1800 - 1
        vy_kill2 = -(tb.ball['position'].y + 2000000) // 1800 + 1
        vy_kill3 = - tb.ball['position'].y // 1800 - 1
        dvy_kill1 = -tb.ball['velocity'].y +vy_kill1
        dvy_kill2 = -tb.ball['velocity'].y +vy_kill2
        dvy_kill3 = -tb.ball['velocity'].y +vy_kill3
        dvy_kill = get_min(dvy_kill1,dvy_kill2,dvy_kill3)
    if side == 'north' :
        vy_kill1 = -(tb.ball['position'].y + 1000000) // 1800 + 1
        vy_kill2 = (3000000 - tb.ball['position'].y) // 1800 - 1
        vy_kill3 = (1000000-tb.ball['position'].y) // 1800 + 1
        dvy_kill1 = -tb.ball['velocity'].y + vy_kill1
        dvy_kill2 = -tb.ball['velocity'].y + vy_kill2
        dvy_kill3 = -tb.ball['velocity'].y + vy_kill3
        dvy_kill = get_min(dvy_kill1, dvy_kill2, dvy_kill3)
    cd = {}
    cd['life'] = dvy_kill * dvy_kill//400
    cd['choice'] = dvy_kill * dvy_kill//400 < tb.side['life']
    cd['d_vy'] = dvy_kill
    return cd


def use(tb,name,d_life,pos1,run):      #给出使用道具的条件，在有多个道具满足条件的情况下，根据优先级判断
    if name == 'TP' and usecard[3] > 5:    #如果跑位距离大于40000,使用瞬移术
        if abs(run) >= 400000 and usecard[3] > 5:
            usecard[1] = 'TP'
            usecard[2] = 'SELf'
            usecard[3] = 5

    if name == 'IL' and usecard[3] > 1:      #补血包，体力小于98000，立即使用
        if tb.side['life'] < 98000:
            usecard[1] = 'IL'
            usecard[2] = 'SELf'
            usecard[3] = 1

    if name == 'DL'and usecard[3] > 2:       #掉血包，立即使用
        usecard[1] = 'DL'
        usecard[2] = 'OPNT'
        usecard[3] = 2

    if name == 'DS'and usecard[3] > 6:        #隐身术
        usecard[1] = 'DS'
        usecard[2] = 'SELf'
        usecard[3] = 6

    if name == 'AM' and usecard[3] > 3:       #变压器，在对方单回合消耗较多时使用
        if d_life > 400:
            usecard[1] = 'AM'
            usecard[2] = 'OPNT'
            usecard[3] = 3

    if name == 'SP' and usecard[3] > 4:
        #旋转球 ，立即使用
        if  pos1 <=700000 and pos1 >=300000:
            usecard[1] = 'SP'
            usecard[2] = 'OPNT'
            usecard[3] = 4


def batting(tb,ds,opname):        #击球
    cd1 = cornor(tb, 'south')
    cd2 = cornor(tb, 'north')
    if find_run(ds,tb,opname) == False or abs(tb.op_side['life'] - ds[opname]['op_life'][-1]) < 50:        #如果对方没有跑中间的习惯，按照对方总能采取最优跑位的情况计算
        if tb.op_side['run_vector'] == -1:
            d_life1 = tb.op_side['position'].y ** 2 // 800000000 - cd1['life']
            d_life2 = (1000000 - tb.op_side['position'].y) ** 2 // 400000000 - cd2['life']
            if d_life1 >= d_life2:
                d_vy = cd1['d_vy']
                d_life = d_life1

            else:
                d_vy = cd2['d_vy']
                d_life = d_life2
        elif tb.op_side['run_vector'] == None:
            if abs(cd1['d_vy']) <= abs(cd2['d_vy']):
                d_vy = cd1['d_vy']
                d_life = cd1['life']

            else:
                d_vy = cd2['d_vy']
                d_life = cd2['life']

        else:
            d_life1 = tb.op_side['position'].y** 2 // 400000000 - cd1['life']
            d_life2 = (1000000 - tb.op_side['position'].y) ** 2 // 800000000 - cd2['life']
            if d_life1 >= d_life2:
                d_vy = cd1['d_vy']
                d_life = d_life1

            else:
                d_vy = cd2['d_vy']
                d_life = d_life2
    else:     #如果对方跑中间，打省力的角

        if abs(cd1['d_vy']) <= abs(cd2['d_vy']):
            d_vy = cd1['d_vy']
            d_life = cd1['life']

        else:
            d_vy = cd2['d_vy']
            d_life = cd2['life']
    return d_vy,d_life


def get_point(y,vy):      #计算球的落点，及速度（y）
    point = 0
    table_width = 1000000
    run_y = 1800 * vy + y
    if run_y > table_width and run_y <= 2*table_width:
        point = 2 * table_width - run_y
        vy = -vy                                              #如果在北墙反弹一次
    if run_y > 2*table_width and run_y <= 3*table_width:      #如果速度向北，反弹两次
        point = run_y - 2 * table_width
        vy = vy
    if run_y >= -1 * table_width and run_y < 0:               #如果速度向南，反弹一次
        point = -run_y
        vy = -vy
    if run_y >= -2 * table_width and run_y < -1*table_width:  #如果速度向南，反弹两次
        point = 2*table_width + run_y
        vy = vy
    return point,vy

def isvaluable(tb,d_vy):   #计算是否捡拾道具，若在最优方案的相邻区域，则捡道具,有多个满足题哦啊煎的道具，则按优先级确定
    x = [None for i in range(10)]
    y = [[None for i in range(6)] for j in range (10)]
    d_vy1= d_vy
    vy = d_vy1 + tb.ball['velocity'].y
    pr={CARD_INCL:1,CARD_DECL:2,CARD_TLPT:5,CARD_AMPL:3,CARD_SPIN:4,CARD_DSPR:6}  #确定在有多个可捡拾道具时的优先级
    b = 7
    for i in range(len(tb.cards['cards'])):
        if b > pr[tb.cards['cards'][i].code]:
            x[i] = abs(tb.ball['position'].x - tb.cards['cards'][i].pos.x)
            y[i][1] = 2 * DIM[3] + tb.cards['cards'][i].pos.y - tb.ball['position'].y
            y[i][2] = 2 * DIM[3] - tb.cards['cards'][i].pos.y - tb.ball['position'].y
            y[i][3] = tb.cards['cards'][i].pos.y - tb.ball['position'].y
            y[i][4] = -tb.cards['cards'][i].pos.y - tb.ball['position'].y
            y[i][5] = -2 * DIM[3] + tb.cards['cards'][i].pos.y - tb.ball['position'].y    #确定捡不同道具所需的速度
            a = (200) if (tb.cards['cards'][i].code == CARD_INCL or tb.cards['cards'][i].code ==CARD_DECL )\
            else (100)        #确定不同道具的相邻区域
            b = 2*a/3
            for j in range(1, 6):
                Vy = y[i][j] * BALL_V[0] / x[i]
                if Vy >= vy - a and Vy <= vy + b and count(tb,Vy) == True:
                    b = pr[tb.cards['cards'][i].code]
                    d_vy1 = Vy - tb.ball['velocity'].y
                    break

    return d_vy1



def count(tb,vy):
    result = True
    Y = vy * 1800 + tb.ball['position'].y
    if Y % 1000000 != 0:
        count = Y // 1000000
    else:
        count = (Y //1000000) if (Y > 0) else (1 - Y // 1000000)
    if count == 0 or abs(count) >= 3:
        result = False

    return result

def count1(y,v): #数碰壁数
    ticks = (DIM[1] - DIM[0]) // BALL_V[0]
    Y = v * ticks + y  # Y是没有墙壁时到达的位置
    if Y % DIM[3] != 0:  # case1：未在边界
        count = Y // DIM[3]
        return abs(count)
    else:  # case2： 恰好在边界
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])
        return count






def waytosolveAM(tb:TableData, ds:dict):    #如果对方使用变压器，则采取最省力的打角算法

    flag = 0
    acc = 0
    if count1(tb.ball['velocity'].y, tb.ball['position'].y) > 0 & \
            count1(tb.ball['velocity'].y, tb.ball['position'].y) < 3:  # 不需要加速
        d_vy = 0
    elif count1(tb.ball['velocity'].y, tb.ball['position'].y) == 0:
        v1 = (DIM[3] - tb.ball['position'].y) * BALL_V[0] // (DIM[1] - DIM[0])  # 打上角
        v2 = -tb.ball['position'].y * BALL_V[0] // (DIM[1] - DIM[0])  # 打下角
        if abs(v1 - tb.ball['velocity'].y) <= abs(v2 - tb.ball['velocity'].y):
            acc = v1 - tb.ball['velocity'].y
            flag = 1  # v1可能需要些许放大
        else:
            acc = v2 - tb.ball['velocity'].y
            flag = 2  # v2可能需要些许减小
    else:
        v1 = (3 * DIM[3] - tb.ball['position'].y) * BALL_V[0] //(DIM[1] - DIM[0])  # 打上角
        v2 = -(tb.ball['position'].y + 2 * DIM[3]) * BALL_V[0] // (DIM[1] - DIM[0])  # 打下角
        if abs(v1 - tb.ball['velocity'].y) <= abs(v2 - tb.ball['velocity'].y):
            acc = v1 - tb.ball['velocity'].y
            flag = 2  # v1可能需要些许减小
        else:
            acc = v2 - tb.ball['velocity'].y
            flag = 1  # v2可能需要些许放大
    while count1(tb.ball['velocity'].y + acc, tb.ball['position'].y) > 2 \
            or count1(tb.ball['velocity'].y + acc, tb.ball['position'].y) < 1:  # 如果做此加速不满足碰壁次数的话
        if flag == 1:
            acc += 5
        else:
            acc -= 5
    return int(acc)




















