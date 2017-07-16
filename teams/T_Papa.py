from table import *

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side: str,ds:dict) -> tuple:
    rand=random.randint(0,1)
    #随机选择向上发球 or 向下发球
    if rand==1:
        return DIM[2],1666
    else:
        return DIM[3],-1666
# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb:TableData, ds:dict) -> RacketAction:
    try:
        ds['run'].insert(0, tb.ball['position'].y)
        if len(ds['run']) > 4:
            ds['run'].pop()
        total = 0
        for i in ds['run']:
            total += i
        average = total // len(ds['run'])
        if tb.side['life'] > 0.99 * RACKET_LIFE:
            ds['run'] = [DIM[3] // 2, DIM[3] // 2]
            average = DIM[3] / 2
    except:
        ds['run'] = [DIM[3] // 2, DIM[3] // 2]
        average = DIM[3] / 2
    try:
        use=ds['use']
        if tb.side['life'] == 100000:
            ds['use']=0
        if (tb.side['life'] + 3300 < tb.op_side['life'] and tb.side['life'] <85000) :
            ds['use'] +=1
    except:
        ds['use'] = 0
        use = 0
    try:
        ds['bat'][1] += 1
        if tb.side['life']>0.99 * RACKET_LIFE :
            ds['bat'][1] = 0
    except:
        ds['bat'] = [1,0]
    #得到最佳速度
    best_vel=calcuBest_vel(tb,ds)
    ds['bat'][0] = (1 if getBallpos(best_vel,tb.ball['position'].y,tb.step)>DIM[3]/2 else -1)
    #得到最佳跑
    best_run = bestRun(tb,average,use,best_vel)
    return RacketAction(tb.tick,
                        tb.ball['position'].y - tb.side['position'].y,
                        (best_vel-tb.ball['velocity'].y)/(CARD_SPIN_PARAM if tb.op_side['active_card'][1]==CARD_SPIN else 1),
                        (best_run-tb.ball['position'].y),
                        activeCards(tb,best_run,best_vel)[0], activeCards(tb,best_run,best_vel)[1])

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return


#计算最优加速函数
#返回最优加速度
'''
通过比较返回我方体力与预估对方体力消耗之差
得到最大体力差的加速值
即最优加速值
'''
def calcuBest_vel(tb,ds):
    #得到合法球路的vy范围
    aviliableV= getAviliableV(tb.step,tb.ball['position'].y)
    bestlist=[0,0]
    bestLifelist=[-10000,-10000]
    #step =3 遍历正向速度
    for ball_velocity in range(aviliableV[0], aviliableV[1],3):
        current_LifeD = LifeD(tb, ball_velocity)
        num=(0 if getBallpos(ball_velocity,tb.ball['position'].y,tb.step)>DIM[3]/2 else 1)
        if current_LifeD > bestLifelist[num]:
            bestLifelist[num] =current_LifeD
            bestlist[num] = ball_velocity
    #step =3 遍历负向速度
    for ball_velocity in range(aviliableV[2], aviliableV[3],3):
        current_LifeD = LifeD(tb, ball_velocity)
        num=(0 if getBallpos(ball_velocity,tb.ball['position'].y,tb.step)>DIM[3]/2 else 1)
        if current_LifeD > bestLifelist[num]:
            bestLifelist[num] =current_LifeD
            bestlist[num] = ball_velocity
    #记正向最佳速度 与 负向最佳速度所造成的体力差为W
    #这将是连续第N次击打在对方同一半边
    #若(W<500且N=2)或(W<1000且N>2)或N>4 选择造成体力差较小的击球方式
    #否则选择造成体力差较大的击球方式
    if (abs(bestLifelist[0]-bestLifelist[1]) <500 and ds['bat'][1]==2) \
       or (ds['bat'][1]==3 and \
           abs(bestLifelist[0]-bestLifelist[1])<1000) or (ds['bat'][1]>3 and abs(bestLifelist[0]-bestLifelist[1]) <1500) or ds['bat'][1]>5:
        if ds['bat'][0]>0:
            if getBallpos(bestlist[1],tb.ball['position'].y,tb.step)>0.1*DIM[3]:
                ball_velocityBest = bestlist[bestlist.index(max(bestlist))]
                if (ds['bat'][0]>0 and bestlist.index(max(bestlist)) == 1) or (ds['bat'][0]<0 and bestlist.index(max(bestlist)) == 0):
                    ds['bat'][1] = 0
            else:
                ball_velocityBest = bestlist[1]
                ds['bat'][1] = 0
        else:
            if getBallpos(bestlist[0],tb.ball['position'].y,tb.step)<0.9*DIM[3]:
                ball_velocityBest = bestlist[bestlist.index(max(bestlist))]
                if (ds['bat'][0]>0 and bestlist.index(max(bestlist)) == 1) or (ds['bat'][0]<0 and bestlist.index(max(bestlist)) == 0):
                    ds['bat'][1] = 0
            else:
                ball_velocityBest = bestlist[0]
                ds['bat'][1] = 0
            
            
    else:
        ball_velocityBest = bestlist[bestlist.index(max(bestlist))]
        if (ds['bat'][0]>0 and bestlist.index(max(bestlist)) == 1) or (ds['bat'][0]<0 and bestlist.index(max(bestlist)) == 0):
            ds['bat'][1] = 0
    if tb.side['life'] == 100000:
        if abs(bestlist[0]-tb.ball['velocity'].y)<abs(bestlist[1]-tb.ball['velocity'].y):
            ball_velocityBest = bestlist[0]
        else:
            ball_velocityBest = bestlist[1]
    return ball_velocityBest

#跑位函数
#返回最优跑位距离
'''
若出现过血量少于85000时血量比对手低3300的情况
运行跑位策略二
否则运行跑位策略一
'''
def bestRun(tb,average,use,best_vel):
    # 跑位策略一，跑位取决于我方前四次击球位置的平均值。跑位至(平均值*3+中点*2)/5处
    run = (average + DIM[3] // 2) // 2
    #转换策略条件：若出现过血量少于85000时血量比对手低3300
    # 跑位策略二，跑位取决于我方本次击球位置，若本次大于2/3，则跑位至2/3；
    # 若本次小于1/3，则跑位至1/3,；否则跑位至中间
    if use == 0:
        pass
    else:
        if tb.ball['position'].y > DIM[3] * 2 // 3:
            run = DIM[3] * 2 // 3
        elif tb.ball['position'].y < DIM[3] // 3:
            run = DIM[3] // 3
        else:
            run = DIM[3] // 2
    # 若跑位无法确保接到任意位置的球，则跑位至能确保的极限位置。
    # 若已没有这样的位置存在，则保证能接到一边的球
    # 求下回合开始时的最低体力值
    left_life = tb.side['life'] - (abs((best_vel - tb.ball['velocity'].y) / (
    CARD_SPIN_PARAM if tb.op_side['active_card'][1] == CARD_SPIN else 1)) ** 2 // FACTOR_SPEED ** 2) * \
                                  (CARD_AMPL_PARAM if tb.op_side['active_card'][1] == CARD_AMPL else 1) - \
                (abs(tb.ball['position'].y - tb.side['position'].y) ** 2 // FACTOR_DISTANCE ** 2) * \
                (CARD_AMPL_PARAM if tb.op_side['active_card'][1] == CARD_AMPL else 1)
    # 默认对面使用减血卡
    if CARD_DECL in tb.op_side['cards']:
        left_life -= CARD_DECL_PARAM
    # 得到迎球半径
    hit_range = hit_radius(left_life)
    if hit_range[0] + 12000 > hit_range[1] - 12000:
        run = (100000 if average < DIM[3] // 2 else 900000)
    elif run not in range(hit_range[0] + 12000, hit_range[1] - 12000):
        run = (min(hit_range[0] + 12000, DIM[3] // 2) if run < DIM[3] // 2 else max(DIM[3] // 2, hit_range[1] - 12000))
    if abs(run - tb.ball['position'].y) > DIM[3] // 2 and hit_range[0] < hit_range[1]:
        run = DIM[3] // 2
    if tb.side['life'] > 0.5 * RACKET_LIFE and activeCards(tb, run, best_vel)[1] == 'SP':
        run = DIM[3] // 2
    return run


#使用卡片函数
#返回卡片使用对象与使用的卡片
'''
通过人为估值确认使用卡片的价值
分为对方50%以上与50%以下
'''
def activeCards(tb,run,vel):
    if tb.side['cards']:
        isUse = False
        useCards = None
        aim =None
        #case1：对方生命在50%以上
        if tb.side['life']>0.5*RACKET_LIFE:
            if [card for card in tb.side['cards'] if card =='SP'] and abs(vel)>1.5*BALL_V[0] and not isUse:
                useCards=[card for card in tb.side['cards'] if card =='SP'][0]
                isUse =True
            if [card for card in tb.side['cards'] if card =='TP'] and abs(run-tb.ball['position'].y)>DIM[3]*0.45 and not isUse:
                useCards=[card for card in tb.side['cards'] if card =='TP'][0]
                isUse =True
            if [card for card in tb.side['cards'] if card == 'AM'] and ('IL' in tb.cards['cards'] or 'DL' in tb.cards['cards']) and not isUse:
                useCards = [card for card in tb.side['cards'] if card == 'AM'][0]
                isUse = True
            if [card for card in tb.side['cards'] if card =='IL' or card =='DL'] and not isUse:
                useCards = [card for card in tb.side['cards'] if card =='IL' or card =='DL'][0]
                isUse = True
            if [card for card in tb.side['cards'] if card == 'DS'] and not isUse:
                useCards = [card for card in tb.side['cards'] if card == 'DS'][0]
                isUse = True
        #case2: 对方生命在50%以下
        else:
            if [card for card in tb.side['cards'] if card =='IL' or card =='DL'] and not isUse:
                useCards = [card for card in tb.side['cards'] if card =='IL' or card =='DL'][0]
                isUse = True
            if [card for card in tb.side['cards'] if card == 'AM'] and ('IL' in tb.cards['cards'] or 'DL' in tb.cards['cards']) and not isUse:
                useCards = [card for card in tb.side['cards'] if card == 'AM'][0]
                isUse = True
            if [card for card in tb.side['cards'] if card =='TP'] and abs(run-tb.ball['position'].y)>DIM[3]*0.4 and not isUse:
                useCards=[card for card in tb.side['cards'] if card =='TP'][0]
                isUse =True
            if [card for card in tb.side['cards'] if card =='SP'] and ('IL' in tb.cards['cards'] or 'DL' in tb.cards['cards'] or abs(vel)>1.5*BALL_V[0]) and not isUse:
                useCards=[card for card in tb.side['cards'] if card =='SP'][0]
                isUse =True
            if [card for card in tb.side['cards'] if card == 'DS'] and not isUse:
                useCards = [card for card in tb.side['cards'] if card == 'DS'][0]
                isUse =True
        #得到使用卡片的对象
        if useCards:
            aim = getCardaim(useCards)
        return aim,useCards
    else:
        return None,None

#计算给定回球速度下，返回我方体力与对方体力消耗之差
def LifeD(tb,ball_velocity):
    #我方消耗体力加速消耗体力
    sideConsume = (abs((ball_velocity-tb.ball['velocity'].y)/(CARD_SPIN_PARAM if tb.op_side['active_card'][1]==CARD_SPIN else 1)) ** 2 // FACTOR_SPEED ** 2) * \
                      (CARD_AMPL_PARAM if tb.op_side['active_card'][1] == CARD_AMPL else 1)
    # 得到球路落点
    newpos = getBallpos(ball_velocity, tb.ball['position'].y, tb.step)
    # 对方跑位后的位置的期望值
    opside_pos_afterRun = (DIM[3] - DIM[2]) // 2  # 对手跑位永远回到终点
    # 计算对方跑位的体力消耗
    op_sideConsume_run = abs(tb.op_side['position'].y - opside_pos_afterRun) ** 2 // FACTOR_DISTANCE ** 2
    # 计算对方迎球的体力消耗
    op_sideConsume_bat = abs(opside_pos_afterRun - newpos) ** 2 // FACTOR_DISTANCE ** 2 * \
                      (CARD_AMPL_PARAM if (CARD_AMPL in tb.side['cards'] and abs(ball_velocity)>BALL_V[0]) else 1)
    # 计算对方加速的体力消耗
    op_sideConsume_acc = (1500 if ('SP' in tb.side['cards'] and abs(ball_velocity)>1600) else 0)
    acc_rate=1
    bat_rate=1
    #判断是否击中了卡片 将得到的卡片放入缓存卡片表
    hit_cards = [card for card in tb.cards['cards'] if getcard(-tb.ball['velocity'].x,ball_velocity,tb.side['position'].x,tb.ball['position'].y,card)]
    #预估卡片价值
    cards_value=0
    while  hit_cards:   #结束条件：卡片表为空
        #从缓存卡片表内抛出一个卡片
        current_card = hit_cards.pop()
        current_value = getCardValue_acc(current_card)
        cards_value+=current_value
    op_sideConsume = op_sideConsume_run + op_sideConsume_bat *bat_rate + op_sideConsume_acc*acc_rate+cards_value
    return op_sideConsume-sideConsume




#计算合法速度范围函数
#参数：当前球的位置
#返回合法正速度范围 与合法负速度范围
def getAviliableV(ticks,pos,DIM=DIM):
    # if velocity>0
    plus_velocityMin = int((DIM[3]-pos)/ticks)
    plus_velocityMax = int((3*DIM[3]-2*DIM[2]-pos)/ticks)
    # if velocity<0
    minus_velocityMin = int((3*DIM[2]-2*DIM[3]-pos)/ticks)
    minus_velocityMax = int((DIM[2]-pos)/ticks)
    return [plus_velocityMin+1,plus_velocityMax-1,minus_velocityMin+1,minus_velocityMax-1]

#计算球落点的函数
#参数：球速 击球点
#返回：返回球落点的y值
def getBallpos(velocity,pos,ticks,DIM=DIM):
    Y = velocity * ticks + pos
    if Y % DIM[3] != 0:
        count = Y // DIM[3]
        newpos = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
    else:
        newpos = Y % (2 * DIM[3])
    return newpos

#判断是否击中卡片
#参数：球速 球的起始位置 卡片位置
#返回：能否接到球的布尔值
def getcard(vx, vy, posx, posy, card, eps=2000):
    A1 = (vy * (-card.pos.x + posx) + vx * (card.pos.y - posy))
    A2 = (vy * (-card.pos.x + posx) + vx * (-card.pos.y - posy))
    delta = (2 * abs(vx) * DIM[3])
    return min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(
            vx ** 2 + vy ** 2) < eps

#返回能击全场球范围
#参数：自身的生命
#返回：迎球最大半径
def hit_radius(self_life):
    radius=int((self_life / RACKET_LIFE) * BALL_V[0]*(DIM[1]-DIM[0])/BALL_V[0])
    return [DIM[3]-radius,DIM[2]+radius]

#参数：击中的卡片
#返回：击中卡片的预估价值
def getCardValue_acc(card):
    
    if card == 'SP':
        # 旋转球价值 预期加速度*CARD_SPIN_PARAM
        cards_value = 1000
    if card == 'DS':
        cards_value = 0
        # 隐身球 价值为0
    if card == 'IL':
        # 加血包价值为2000
        cards_value = 2500
    if card == 'DL':
        # 减血包价值为2000
        cards_value = 2500
    if card == 'TP':
        # 瞬移术价值 abs(CARD_TLPT_PARAM*0.8) ** 2 // FACTOR_DISTANCE ** 2
        cards_value = 500
    if card == 'AM':
        # 变压器价值 预期迎球*CARD_AMPL_PARAM
        cards_value = 1000
    return cards_value

#参数：使用的卡片
#返回：卡片的使用对象
def getCardaim(useCards):
    if useCards == 'SP':
        aim = 'OPNT'
    if useCards == 'IL':
        aim = 'SELF'
    if useCards == 'DL':
        aim = 'OPNT'
    if useCards == 'AM':
        aim = 'OPNT'
    if useCards == 'TP':
        aim = 'SELF'
    if useCards == 'DS':
        aim = 'SELF'
    return aim

