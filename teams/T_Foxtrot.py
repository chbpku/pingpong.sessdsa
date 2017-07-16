from table import *
import random

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典，用作存储对战数据
# 函数需要返回球的y坐标，和y方向的速度
#【参数说明】op_file（对手记录）：[生命值,损失生命值（与上一回合相比）,移动损失,加速损失,使用道具,道具组,加速矢量,跑位距离,上一轮击球位置]
#【参数说明】self_file（己方记录）：[生命值,本回合跑位,加速损失,生命损失,道具被使用方,接球位置,道具组]
#【参数说明】ball_file：[己方接球后预计球速,预计球的落点]
# count 为计数器：记录一局对战内进行的回合数
def serve(op_side: str,ds) -> tuple:
    
    global gains
    tick_step = (DIM[1]-DIM[0]) // BALL_V[0] # 乒乓球运动耗时

    if len(ds) == 0 or ds['opname'] != op_side: # 若无对战历史记录，建立新记录
        ds = {'op_name':op_side,'op_file':[[100000,0,0,0,None,[],0,0,500000]],'self_file':[[10000,0,-1387,0,0,BALL_POS[1],0,None,[]]],
              'ball_file':[[-1387,(-1387)*tick_step%1000000-500000]],'count':1,
              'rundatabase':[],
              'database': [[] for m in range(0,1000000,40000)],
              'accdatabase':[],
              'database2':[[] for m in range(0,1000000,20000)]}
    elif ds['opname'] == op_side: # 若存在对战历史记录，则直接调用历史记录进行使用
        ds['op_file'].append([100000,0,0,0,None,[],0,0,0,500000,0])
        ds['self_file'].append([10000,0,-1387,0,0,BALL_POS[1],0,None,[]])
        ds['ball_file'].append([-1387,(-1387)*tick_step%1000000-500000])
        ds['count']=1

    return BALL_POS[1], -1387

# 打球函数（核心函数）
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb, ds):
    global gains#表达对一个方案收益的估值
    global para
    para = tb.side['life']/200000 # 一个参数，反映可冒的风险
    tick_step = (DIM[1]-DIM[0]) // BALL_V[0] # 乒乓球运动耗时

    # shorten函数主要用于选择击球方式：计算在某个点不同击球方式所需要的加速度，返回最小加速度
    # 需要的参数：target：球的位置；tick_step：乒乓球运动耗时
    def shorten(target,tick_step): 
        v1 = (2000000 - tb.ball['position'].y - target) // tick_step + 1
        v2 = (2000000 - tb.ball['position'].y + target) // tick_step - 1
        v3 = -((target + tb.ball['position'].y) // tick_step + 1)
        v4 = -((2000000 - target + tb.ball['position'].y) // tick_step - 1)
        deltav1 = (v1 - tb.ball['velocity'].y)
        deltav2 = (v2 - tb.ball['velocity'].y)
        deltav3 = (v3 - tb.ball['velocity'].y)
        deltav4 = (v4 - tb.ball['velocity'].y)
        lisry4 = [deltav1, deltav2, deltav3, deltav4]
        comparesquare4, count4 = deltav1 ** 2, 0
        for js in range(0, 4): # 对计算所得的不同加速度进行简单排序
            if comparesquare4 >= (lisry4[js]) ** 2:
                comparesquare4, count4 = (lisry4[js]) ** 2, js
        dv = lisry4[count4]
        return dv

    # 不选择道具的情况下的最佳战术
    def choosetarwithoutcards(tb,ds) -> tuple:
        if tb.op_side['life'] < 27500:# 打角就能赢
            if (shorten(100,tick_step))**2 > (shorten(999900,tick_step))**2:
                target = 999900
                return target,1000000
            else:
                target = 100
                return target, 1000000

        elif tb.op_side['life'] >= 27500:  # 无法暴力打角
            # para = tb.side['life'] / 200000  该参数主要用于本函数，但在其他函数有所提及
            choicelist = [] # 根据不同情况下收益与损失之差来选择相应的行动
            for i in range(500, 1000500, 1000):  # 1000个取样点
                tar = i
                tryacc = shorten(tar,tick_step)#该取样点的最佳加速度
                # 计算每个取样点的位置
                move = tar - tb.op_side['position'].y#对手理想状态下需要的移动
                pos = tb.op_side['position'].y
                guess_acc = 0#对对手回球加速度的猜测初始
                guess_run = 0#对对手跑位距离的猜测初始
                # 根据过往数据来模拟对手下次的跑位和加速
                # 猜测时认为对手在同一位置处所进行的跑位应当大致模式相同
                if len(ds['database'][(pos + 20000) // 40000-1]) >= 5:
                    length = len(ds['database'][(pos + 20000) // 40000-1])
                    t = random.randrange(0, length)#调用数据库中的数据
                    guess_run = ds['database'][(pos + 20000) // 40000-1][t]
                if len(ds['database2'][(tar - pos + 10000) // 40000-1]) >= 5:
                    length2 = len(ds['database2'][(tar - pos + 10000) // 20000-1])
                    s = random.randrange(0, length2)#调用数据库中的数据
                    guess_acc = ds['database2'][(tar - pos + 10000) // 20000-1][s](0)
                    #更新guess

                par = guess_run / (tar - tb.op_side['position'].y)#判定对方是否会有效跑位
                lost = 0
                profit = 0
                

                #计算不同情况下的收益与损失
                if tb.op_side['active_card'][1] == CARD_SPIN:

                    if par >= 0:#跑位有效

                        lost = (2 * tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2
                        profit = ((tar - tb.op_side['position'].y) // 20000) ** 2 + (guess_acc // 20) ** 2 * para
                    else:
                        lost = (2 * tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2
                        profit = ((tar - tb.op_side['position'].y) + 2 * guess_run // 20000) ** 2 + (
                                                                                                       guess_acc // 20) ** 2 * para
                elif tb.op_side['active_card'][1] == CARD_AMPL:
                    if par >= 0:

                        lost = (
                               (tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2) * 2
                        profit = ((tar - tb.op_side['position'].y) // 20000) ** 2 + (guess_acc // 20) ** 2 * para
                    else:
                        lost = (
                               (tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2) * 2
                        profit = ((tar - tb.op_side['position'].y) + 2 * guess_run // 20000) ** 2 + (
                                                                                                       guess_acc // 20) ** 2 * para
                else:
                    if par >= 0:

                        lost = (tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2
                        profit = ((tar - tb.op_side['position'].y) // 20000) ** 2 + (guess_acc // 20) ** 2 * para
                    else:
                        lost = (tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2
                        profit = ((tar - tb.op_side['position'].y) + 2 * guess_run // 20000) ** 2 + (
                                                                                                       guess_acc // 20) ** 2 * para

                gaining = profit - lost # 最终受益
                choicelist.append(gaining) # 将受益加入选择列表
            # 选择最大gaining下的策略
            current = choicelist[0]
            choice = 0
            for num in range(0,len(choicelist)):
                if choicelist[num] >= current:
                    current = choicelist[num]
                    choice = num
            target = choice*1000+500
            gaininthatsituation = current
            return target,gaininthatsituation#返回一个元组从而利于后面对比gaininthatsituation，决定target

     # validjustice函数用于判断速度是否符合要求，即不出现invalid bounce
    def validjustice(v):
        if v > 0:
            if v * tick_step < 1000000 - tb.ball['position'].y or v * tick_step > 3000000 - \
                    tb.ball['position'].y:
                return False
            else:
                return True
        if v < 0:
            if v * tick_step < tb.ball['position'].y or v * tick_step > 2000000 + tb.ball[
                'position'].y:
                return False
            else:
                return False

    # shortenandvalid函数用来选择合法前提下的最小加速度
    def shortenandvalid(target,tick_step):
        v1 = (2000000 - tb.ball['position'].y - target) // tick_step + 1
        v2 = (2000000 - tb.ball['position'].y + target) // tick_step - 1
        v3 = -((target + tb.ball['position'].y) // tick_step + 1)
        v4 = -((2000000 - target + tb.ball['position'].y) // tick_step - 1)
        deltav1 , deltav2, deltav3, deltav4 = 1000000,1000000,1000000,1000000
        # 计算不同情况下的加速度
        if validjustice(v1):
            deltav1 = (v1 - tb.ball['velocity'].y)
        else:
            deltav1 = 1000000#一个足够大排序中会被淘汰的速度，表示其invalid
        if validjustice(v2):
            deltav2 = (v2 - tb.ball['velocity'].y)
        else:
            deltav2 = 1000000#一个足够大排序中会被淘汰的速度，表示其invalid
        if validjustice(v3):
            deltav3 = (v3 - tb.ball['velocity'].y)
        else:
            deltav3 = 1000000#一个足够大排序中会被淘汰的速度，表示其invalid

        if validjustice(v4):
            deltav4 = (v4- tb.ball['velocity'].y)
        else:
            deltav4 = 1000000#一个足够大排序中会被淘汰的速度，表示其invalid

        lisry4 = [deltav1, deltav2, deltav3, deltav4]
        comparesquare4, count4 = deltav1 ** 2, 0
        for js in range(0, 4): # 简单排序，求最小加速度
            if comparesquare4 >= (lisry4[js]) ** 2:
                comparesquare4, count4 = (lisry4[js]) ** 2, js
        dv = lisry4[count4]
        if dv <=1000:
            return dv
        else:#没有合适的加速度，全部invalid
            return None


    # choosetaronlywithcards函数用于判断一定选择道具情况下击球的不同策略
    def choosetaronlywithcards(tb, ds) -> tuple:
        if len(tb.cards['cards']) == 0:
            return None,None,None
        else:
            collectable = []
            positioal = []

            for i in range(0,len(tb.cards['cards'])):# 记录道具情况
                collectable.append(tb.cards['cards'][i].code)
                positioal.append(tb.cards['cards'][i].pos)
            choicelist = []
            targetlist = []
            velocitylist = []

            for r in range(0, len(tb.cards['cards'])):
                halftarget = tb.cards['cards'][r].pos.y
                half_tickstep = abs(tb.cards['cards'][r].pos.x-tb.side['position'].x) // BALL_V[0]
                v_2 = None # 使用道具情况下的击球速度
                if shortenandvalid(halftarget,half_tickstep):
                    v_2 = shortenandvalid(halftarget,half_tickstep) + tb.ball['velocity'].y
                tar = 0
                if v_2 != None:
                    if v_2 > 0:
                        if v_2 * tick_step + tb.ball['position'].y > 2000000:
                            tar = v_2 * tick_step + tb.ball['position'].y - 2000000
                        else:
                            tar = v_2 * tick_step + tb.ball['position'].y - 1000000
                    if v_2 < 0:
                        if v_2 * tick_step - tb.ball['position'].y > 1000000:
                            tar = -v_2 * tick_step + tb.ball['position'].y + 2000000
                        else:
                            tar = v_2 * tick_step - tb.ball['position'].y
                else:
                    tar = None
                if tar == None:
                    choicelist.append(-1000000)
                    targetlist.append(tar)
                    velocitylist.append(None)
                else:
                    tryacc = shorten(tar, tick_step)
                    pos = tb.op_side['position'].y
                    guess_acc = 0
                    guess_run = 0
                    # 根据过往数据来模拟对手下次的跑位和加速
                    if len(ds['database'][(pos + 20000) // 40000-1]) >= 5:
                        length = len(ds['database'][(pos + 20000) // 40000-1])
                        t = random.randrange(0, length)
                        guess_run = ds['database'][(pos + 20000) // 40000-1][t]
                    if len(ds['database2'][(tar - pos + 10000) // 40000-1]) >= 5:
                        length2 = len(ds['database2'][(tar - pos + 10000) // 20000-1])
                        s = random.randrange(0, length2)
                        guess_acc = ds['database2'][(tar - pos + 10000) // 20000-1][s](0)
                        # 更新guess
                        # 判定对方是否会有效跑位

                    par = guess_run / (tar - tb.op_side['position'].y)
                    profit,lost,gaining = 0, 0,0
                    # 计算不同情况下的收益损失比
                    if tb.op_side['active_card'][1] == CARD_SPIN:#对方使用旋转球

                        if par >= 0:  # 跑位有效

                            lost = (2 * tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side[
                                'position'].y) // 20000) ** 2
                            profit = ((tar - tb.op_side['position'].y) // 20000) ** 2 + (guess_acc // 20) ** 2 * para
                        else:
                            lost = (2 * tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side[
                                'position'].y) // 20000) ** 2
                            profit = ((tar - tb.op_side['position'].y) + 2 * guess_run // 20000) ** 2 + (
                                                                                                            guess_acc // 20) ** 2 * para
                    elif tb.op_side['active_card'][1] == CARD_AMPL:#对方使用变压器
                        if par >= 0:

                            lost = (
                                       (tryacc // 20) ** 2 + (
                                       (tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2) * 2
                            profit = ((tar - tb.op_side['position'].y) // 20000) ** 2 + (guess_acc // 20) ** 2 * para
                        else:
                            lost = (
                                       (tryacc // 20) ** 2 + (
                                       (tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2) * 2
                            profit = ((tar - tb.op_side['position'].y) + 2 * guess_run // 20000) ** 2 + (
                                                                                                            guess_acc // 20) ** 2 * para
                    else:
                        if par >= 0:

                            lost = (tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2
                            profit = ((tar - tb.op_side['position'].y) // 20000) ** 2 + (guess_acc // 20) ** 2 * para
                        else:
                            lost = (tryacc // 20) ** 2 + ((tb.ball['position'].y - tb.side['position'].y) // 20000) ** 2
                            profit = ((tar - tb.op_side['position'].y) + 2 * guess_run // 20000) ** 2 + (
                                                                                                            guess_acc // 20) ** 2 * para

                    gaining = profit - lost
                    if collectable[r] == CARD_INCL:
                        gaining += 2000#增血道具加2000
                    elif collectable[r] == CARD_DECL:
                        gaining += 2000#减血道具减少2000
                    elif collectable[r] == CARD_SPIN:
                        gaining += 200
                    elif collectable[r] == CARD_AMPL:
                        gaining += 200

                    choicelist.append(gaining)
                    targetlist.append(tar)
                    velocitylist.append(v_2 - tb.ball['velocity'].y)
            current = choicelist[0]
            choice = 0
            target = targetlist[0]
            for num in range(0,len(tb.cards['cards'])):
                if choicelist[num] > current: # 记录最大收益策略
                    current = choicelist[num]
                    choice = num
                    target = targetlist[num]
            gaininthatsituation = current
            accneeded = velocitylist[num]
            return target, gaininthatsituation,accneeded

    # finalchoice函数: 判断不同方案（综合所有情况下的全部策略）下的收益，获取最优选择
    def finalchoice(choosetarwithoutcards:tuple,choosetarwithonlycards:tuple) -> tuple:
        target = 0
        dv = 0

        if choosetarwithonlycards[2]:
            if choosetarwithonlycards[1] > choosetarwithoutcards[1]:
                target = choosetarwithonlycards[0]
                dv =  choosetarwithonlycards[2]
            else:
                target = choosetarwithoutcards[0]
                dv = shorten(target,tick_step)
        else:
            target = choosetarwithoutcards[0]
            dv = shorten(target,tick_step)
        return target,dv

    #正式开始执行play函数时，先建立数据库

    # 击球开始前与发球函数类似，先检验是否存在对局历史记录，若有，则直接调用；若无，则重建记录
    if len(ds) == 0 or ds['opname']!= tb.op_side['name']:

        ds = {'op_name': tb.op_side['name'], 'op_file': [[100000, 0, 0, 0, tb.op_side['active_card'][1], tb.op_side['cards'], tb.ball['velocity'].y,0,500000]],
              'self_file': [],
              'ball_file': [],
              'count':1,
              'rundatabase': [],
              'database': [[] for m in range(0, 1000000, 40000)],
              'accdatabase':[],
              'database2': [[] for m in range(0, 1000000, 20000)]
              }
    elif tb.op_side['life'] == 100000:
        ds['op_file'].append([100000, 0, 0, 0, tb.op_side['active_card'][1], tb.op_side['cards'], tb.ball['velocity'].y,0,500000,0])
        ds['count'] = 1


    else:
        a = []
        b = ds['count']#计数器
        t1,t2 = 0,0
        if ds['ball_file'][b-2][0] >0:
            if  abs(ds['ball_file'][b-2][0]*tick_step -(2000000-ds['self_file'][b-2][5]-ds['ball_file'][b-2][1]))<=10000:
                t1 = 1
            else:
                t1 = 2
        else:
            if abs(ds['ball_file'][b - 2][0] * tick_step - ( ds['self_file'][b - 2][5] + ds['ball_file'][b - 2][1])) <= 10000:
                t1 = 1
            else:
                t1 = 2
        op_startspeed = ds['ball_file'][b-2][0] *((-1)**t1) # 对方的初始速度
        dis = tick_step*tb.ball['velocity']#已知初始速度和对方回球过来的速度，求加速度矢量的过程
        dis_round1 = tb.ball['position'].y+ds['ball_file'][b-2][1]
        dis_round2 = 2000000 - tb.ball['position'].y - ds['ball_file'][b - 2][1]
        dis_round3 = 2000000 + tb.ball['position'].y - ds['ball_file'][b - 2][1]
        dis_round4 = 2000000 - tb.ball['position'].y + ds['ball_file'][b - 2][1]
        d1 = abs(dis - dis_round1)
        d2 = abs(dis - dis_round2)
        d3 = abs(dis - dis_round3)
        d4 = abs(dis - dis_round4)
        trylist = [d1,d2,d3,d4]
        comsquare, counti = d1 , 0
        for i in range(0, 4): # 对方最终击球速度
            if comsquare >= (trylist[i]) :
                comsquare, counti = (trylist[i]) , i
        if counti == 0 or 1:
            op_finalspeed = tb.ball['velocity']*(-1)
        else:
            op_finalspeed = tb.ball['velocity']

        #计算对方的加速度和各类tb中不提供的数据
        op_acc = op_finalspeed - op_startspeed # 增速

        # 对方在我方使用不同道具情况下的跑位、赢球的收益（损失）
        if ds['self_file'][b-2][7] != CARD_SPIN and ds['self_file'][b-2][7] !=CARD_AMPL :
            ll_acc = ((op_acc)//20)**2
        elif ds['self_file'][b-2][7] == CARD_AMPL:
            ll_acc = 2*((op_acc)//20)**2
        elif ds['self_file'][b-2][7] == CARD_SPIN:
            ll_acc = (2*(op_acc)//20)**2
        ll_move = ds['op_file'][b-2][0]-tb.op_side['life']-ll_acc
        max_ll_paowei = min((int((tb.op_side['life'] / RACKET_LIFE) * BALL_V[0])*tick_step//20000)**2,
                            (ds['ball_file'][b-2][1]//20000)**2,((1000000-ds['ball_file'][b-2][1])//20000)**2)
        max_ll_yingqiu =((int((tb.op_side['life'] / RACKET_LIFE) * BALL_V[0])*tick_step//20000)**2,
                            2500)
        if tb.op_side['active_card'] == CARD_AMPL:
            ll_actualmove = ll_move/2
        elif tb.op_side['active_card'] == CARD_TLPT:

            ll_actualmove = ll_move
        ll_minyingqiu = ((abs(tb.op_side['position'].y-ds['op_file'][b-2][8]))//20000)**2
        if ll_actualmove - ll_minyingqiu <= -50:
            dis_move = abs(ll_actualmove)**(1/2)*20000*((tb.op_side['position'].y - ds['op_file'][b - 2][8]) / abs(
                    tb.op_side['position'].y - ds['op_file'][b - 2][8]))
            dis_move2 = tb.op_side['position'].y-ds['op_file'][b-2][8]

            dis_paowei = (abs(dis_move2)-abs(dis_move))*((tb.op_side['position'].y - ds['op_file'][b - 2][8]) / abs(
                    tb.op_side['position'].y - ds['op_file'][b - 2][8]))
            benefit = True

        elif ll_actualmove - ll_minyingqiu >= 50:
            dis_move = abs(ll_actualmove) ** (1 / 2) * 20000 * (
            (tb.op_side['position'].y - ds['op_file'][b - 2][8]) / abs(
                tb.op_side['position'].y - ds['op_file'][b - 2][8]))
            dis_move2 = tb.op_side['position'].y - ds['op_file'][b - 2][8]

            dis_paowei = -(abs(dis_move)-abs(dis_move2))/2*((tb.op_side['position'].y - ds['op_file'][b - 2][8]) / abs(
                    tb.op_side['position'].y - ds['op_file'][b - 2][8]))
            benefit = False
        else:
            c = random.randrange(1,40)
            if tb.op_side['life']<=55000:
                dis_paowei = ((tb.op_side['position'].y - ds['op_file'][b - 2][8]) / abs(
                    tb.op_side['position'].y - ds['op_file'][b - 2][8]))*abs(ds['op_file'][b - 2][8]-500000)*(c/100)
            else:
                dis_paowei = ((tb.op_side['position'].y - ds['op_file'][b - 2][8]) / abs(
                    tb.op_side['position'].y - ds['op_file'][b - 2][8])) * 100
            benefit = None



        catchandrun = (ds['op_file'][b - 2][8],dis_paowei,benefit)
        ds['rundatabase'].append(catchandrun)
        for i in range(0,1000000,40000):
            if catchandrun[0] >=i and catchandrun[0] < i+40000:
                ds['database'][i//40000].append(catchandrun[1])
        accandpos = (tb.op_side['position'].y-ds['self_file'][5],op_acc,tb.ball['position'].y)
        ds['accdatabase'].append(accandpos)
        for i in range(0,1000000,20000):
            if accandpos[0] >=i and accandpos[0] < i+20000:
                ds['database2'][i//20000].append(accandpos[1],accandpos[2])
        # 数据记录
        a.append(tb.op_side['life'])
        a.append(ds['op_file'][b-2][0]-tb.op_side['life'])
        a.append(ds['op_file'][b-2][0]-tb.op_side['life']-ll_acc)#lost life because of move
        a.append(ll_acc)#lost life because of acc
        a.append(tb.op_side['active_card'][1])
        a.append(tb.op_side['cards'])
        a.append(op_acc)
        a.append(dis_paowei)
        a.append(tb.op_side['position'].y)
        ds['op_file'].append(a)

        ds['count'] += 1

    #做出选择输出加速度
    confidential = finalchoice(choosetarwithoutcards(tb,ds),choosetaronlywithcards(tb,ds))
    dv = confidential[1]
    target = confidential[0]
    ds['ball_file'].append([tb.ball['velocity'].y + dv, target])

    if tb.op_side['active_card'][1] == CARD_SPIN: # and tb.op_side['active_card'][0] == OPNT然而没有什么用
        dv = dv*2#特殊当对手使用旋转球时需要速度＊2
    #输出迎球矢量
    bat_vec = tb.ball['position'].y - tb.side['position'].y
    #输出l跑位矢量

    def caculate_shortest_length(tb):#计算能够迎球覆盖全场的最短跑位距离（血量28000～57000）
        while tb.side['life']-(bat_vec / 20000)**2 - (dv/20)**2 - 5000 > 28000:
            #5000是进行一个安全的保护，避免己方损失过大从而出现问题，missball
            if tb.op_side['active_card'][1] == CARD_AMPL:
                maxi = (tb.side['life']-5000-2*(bat_vec / 20000)**2 -2* (dv/20)**2)/RACKET_LIFE * BALL_V[0]
            else:
                maxi = (tb.side['life']-(bat_vec / 20000)**2 - (dv/20)**2-5000)/RACKET_LIFE * BALL_V[0]
            tick_step = (DIM[1] - DIM[0]) // BALL_V[0]
            maxilen = maxi * tick_step
            coverp1 = 1000000 - maxilen + 1000 * (57000/tb.side['life'])
            coverp2 = maxilen - 1000 * (57000/tb.side['life'])
            if tb.ball['position'].y < coverp1:
                return coverp1 - tb.ball['position'].y
            elif tb.ball['position'].y> coverp2:
                return -tb.ball['position'].y + coverp2
            else:
                return 0
        else:
            return 500000 - tb.ball['position'].y

    if tb.side['life']-(bat_vec / 20000)**2 - (dv/20)**2 <= 57000 and tb.side['life']-(bat_vec / 20000)**2 - (dv/20)**2 > 28000:
        #l = 500000 - tb.ball['position'].y 旧版耗费血量最多的语句
        l = caculate_shortest_length(tb)
    elif tb.side['life']-(bat_vec / 20000)**2 - (dv/20)**2 < 28000:#血都这么少了…对方会打两边，那就跑位去两边看命了
        z = random.randrange(0,2)
        if z == 0:
            l = -tb.ball['position'].y
        else:
            l = 1000000 - tb.ball['position'].y
    else:
        l = random.randrange(-1,2)#血量多的时候跑位没有意义，故用随机数纯粹混淆对手视听

    c = tb.side['life']

    if len(tb.side['cards']) > 0:#有道具就使用
        daoju = tb.side['cards'][0]
    else:
        daoju = None
    #为了保证格式一致，需要判断道具的被使用方向
    if daoju == CARD_SPIN or daoju == CARD_AMPL or daoju == CARD_DECL:
        sides = 'OPPN'
    elif daoju == CARD_DSPR or daoju == CARD_INCL or daoju == CARD_TLPT:
        sides = 'SELF'
    else:
        sides = None

    #己方回合结束开始记录自己这一回合的工作
    ziji =[]
    ziji.append(tb.side['life'])
    ziji.append(bat_vec)
    ziji.append(dv)
    if ds['count'] ==1:
        ziji.append(0)
    else:
        ziji.append(tb.side['life']-ds['self_file'][b-2][0])
    ziji.append(None)
    ziji.append(tb.ball['position'].y)
    ziji.append(l)
    ziji.append(daoju)

    ds['self_file'].append(ziji)

    return RacketAction(tb.tick,bat_vec ,dv ,l , sides, daoju)
    #实际上，第五个参数并没有实际作用，因而在实战中为了达成混淆视听的目的完全可以写一个类似于18这种奇奇怪怪的东西混淆视听
    # return RacketAction(tb.tick,bat_vec ,dv ,l , 18, daoju)

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return
