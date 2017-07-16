from table import *

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(play,ds):
    print("击球位置，球速，给球加速，加速可行范围，对方位置，每局净赚体力")
    return 600000, BALL_V[1]

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象


def play(tb, ds):
    if tb.tick < 4000:#4000保证第一回合清空所有数据
        ds.clear()
        ds['side_position'] = []
        ds['oppoball_param'] = 0#两次打球很接近的情况
        ds['pre_life'] = None
        ds['count'] = 0
    if ds['pre_life'] and ds['count'] < 3:#prelife是对手上一回合的体力值，判断是否达到三局上限
        diff = ds['pre_life'] - tb.op_side['life']
        if diff < 1000 :
            ds['count'] += 1
        else:
            ds['count'] = 0
    ds['pre_life'] = tb.op_side['life'] #更新体力值
                                    
    bat_vector = tb.ball['position'].y - tb.side['position'].y#迎球跑位
    acc_vector = optimal(tb.ball['position'].y, tb.ball['velocity'].y, tb.op_side['position'].y,tb.cards['cards'], tb.op_side['active_card'][1],tb.side['cards'],tb.side['position'].x,tb.ball['velocity'].x, ds)
    cal = calc_ball(tb.ball['position'].y,acc_vector * (0.5 if tb.op_side['active_card'][1] and tb.op_side['active_card'][1] == 'SP' else 1)+tb.ball['velocity'].y,period)
    foresee_ball = op_optimal(int(cal[0]),int(cal[1]),500000)
    run_vector = optimal_run(tb,ds,foresee_ball)
    op_pos = calc_ball(tb.ball['position'].y, tb.ball['velocity'].y + acc_vector * (0.5 if (tb.op_side['active_card'][1] and tb.op_side['active_card'][1] == 'SP') else 1), period)
    #print(op_pos)
    #eva = evaluate(tb.ball['position'].y,tb.ball['velocity'].y, acc_vector,tb.op_side['position'].y, tb.cards['cards'], tb.op_side['active_card'][1],tb.side['cards'],tb.side['position'].x,tb.ball['velocity'].x)
    card_use = use_card(tb.ball['position'].y, tb.side['cards'], op_pos[0])
    #history_data=(tb.ball['position'].y, tb.ball['velocity'].y, acc_vector,availrange(tb.ball['position'].y, tb.ball['velocity'].y), tb.op_side['position'].y,int(eva[0]), int(eva[1]),int(eva[2]))
    #print(tb.ball['position'].y, tb.ball['velocity'].y, availrange(tb.ball['position'].y, tb.ball['velocity'].y))
    return RacketAction(tb.tick, bat_vector, acc_vector,  run_vector, card_use[0], card_use[1])

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保、存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return


import math

table_y = 1000000  # 可以用DIM = (-900000, 900000, 0, 1000000)表示
table_x = 1800000  # BALL_V = (1000, 1000)
ball_vx = 1000
period = table_x / ball_vx  # =fly_time?



def optimal(self_y, self_speed, oppo_y,tbcard,op_card,self_card, self_x,velocity_x, ds):
    Min, Max = availrange(self_y, self_speed)  # 函数：计算加速有利区间
    optimal = -9999999
    choice = 0
    if op_card and op_card == 'SP':#如果用旋转球
        Min *= 2
        Max *= 2
    for accelerate in range(Min,Max):
        temp = evaluate(self_y, self_speed, accelerate, oppo_y,tbcard,op_card,self_card, self_x,velocity_x, ds)[0]  # 评价自己的位置、速度、加速度、对方位置
        if temp > optimal:  # 收益更多，则赋值给最优值
            optimal = temp
            choice = accelerate  # 用这个速度
    return choice

def optimal_run(tb,ds,foresee_ball):#跑位策略
    '''if tb.tick < 4000:
        ds.clear()
        ds['side_position'] = []
        ds['oppoball_param'] = 0
        ds['pre_life'] = None
        ds['count'] = 0'''
    if len(ds['side_position']) > 0:#position记录上一局接球位置 初始化为一空列表
        last_position = ds['side_position'].pop()
        if abs(last_position - tb.ball['position'].y) < 5000:#上一次位置和这一次位置距离差小于5000，说明位置相当接近
            ds['oppoball_param'] += 1
    if tb.side['life'] < 45000:#如果生命值太小， 跑中间，
        if tb.ball['position'].y > 500000:
            run_vector = 500000 - tb.ball['position'].y - random.randrange(0, 10000)
        elif tb.ball['position'].y < 500000:
            run_vector = 500000 - tb.ball['position'].y + random.randrange(0, 10000)
        else:
            run_vector = 0
    else:
        if ds['oppoball_param'] > 2:#判断对手是固定打角的算法
            if tb.ball['position'].y < 250000 and foresee_ball <= 10000:#foresee ball在角附近
                run_vector = 250000 - tb.ball['position'].y + random.randrange(0, 10000)
            elif tb.ball['position'].y < 250000 and foresee_ball >= 990000:
                run_vector = 500000 - tb.ball['position'].y + random.randrange(0, 10000)
            elif tb.ball['position'].y > 750000 and foresee_ball >= 990000:
                run_vector = 750000 - tb.ball['position'].y - random.randrange(0, 10000)
            elif tb.ball['position'].y > 750000 and foresee_ball <= 10000:
                run_vector = 500000 - tb.ball['position'].y - random.randrange(0, 10000)
            else:
                run_vector = 0
        else:#假设不成立，就往中间跑
            if tb.ball['position'].y > 500000:
                run_vector = 500000 - tb.ball['position'].y - random.randrange(0, 10000)
            elif tb.ball['position'].y < 500000:
                run_vector = 500000 - tb.ball['position'].y + random.randrange(0, 10000)
            else:
                run_vector = 0
    ds['side_position'].append(tb.ball['position'].y)#加入本局落点
    return run_vector

#以下函数用于判断道具的收益
def cardvalue(card):
    valuedict = {'SP':750, 'DS':0, 'IL':2000, 'DL':2000, 'TP':450, "AM":2000} #TP 跑500000和250000的差值，SP经验值， 两算法对打得出
    #valuedict = {'SP':20000, 'DS':20000, 'IL':20000, 'DL':20000, 'TP':20000, "AM":20000}
    return valuedict[card]

def get_card(velocity_x,velocity_y,pos_x,pos_y,card,eps=2000):#李逸飞超强算法
    velocity_x = -velocity_x
    A1 = (velocity_y * (-card.pos.x + pos_x) + velocity_x * (card.pos.y - pos_y))
    A2 = (velocity_y * (-card.pos.x + pos_x) + velocity_x * (-card.pos.y - pos_y))
    delta = (2 * abs(velocity_x) * 1000000)
    return min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(
        velocity_x ** 2 + velocity_y ** 2) < eps

def use_card(self_y,self_card, op_pos):#自身在y方向位置，道具箱，对手位置
    self_side = 'SELF'
    self_opside = 'OPNT'
    if len(self_card) == 0:
        return (None, None)
    else:
        card_code = []
        for card in self_card:#道具放入列表
            card_code.append(card.code)
        #print(card_code)
        if 'IL' in card_code:#直接使用
            #print('IL')
            return (self_side,self_card[card_code.index('IL')])
        elif 'DL' in card_code:#直接使用
            #print('DL')
            return (self_opside, self_card[card_code.index('DL')])
        elif 'TP' in card_code and (self_y < 250000 or self_y > 750000):#在比较偏的地方才用
            #print('TP')
            return (self_side, self_card[card_code.index('TP')])
        elif 'DS' in card_code:#直接使用
            #print('DS')
            return (self_side, self_card[card_code.index('DS')])
        elif 'SP' in card_code:#直接使用
            #print('SP')
            return (self_opside,self_card[card_code.index('SP')])
        elif 'AM' in card_code and (op_pos < 8000 or op_pos > 992000):#放大迎球消耗的体力，所以在对手比较靠边时使用
            #print('AM')
            return (self_opside,self_card[card_code.index('AM')])
        return (None,None)#如果不使用，则返回None

#tbcard是整个桌面的道具列表，ball是球的所有信息，self_card是自己的'Card_Box类'
def evaluate(self_y, self_speed, self_accelerate, oppo_y,tbcard,op_card,self_card, self_x,velocity_x, ds):
    self_consume = oppo_consume = 0
    self_consume += (self_accelerate / 20) ** 2  * (2 if op_card and op_card == 'AM' else 1)# 我方总消耗（+加速消耗,已考虑旋转球和变压器
    current_speed = self_speed + self_accelerate * (0.5 if op_card and op_card == 'SP' else 1) # 得到新的速度
    oppo_ball_y, oppo_ball_speed = calc_ball(self_y, current_speed, period)  # 算球位置（自己位置、球的新速度、过程）
    if ds['count'] < 3:
        oppo_y = 500000
    oppo_consume += ((oppo_y - oppo_ball_y - (250000 if op_card and op_card == 'TP' else 0)) / 20000) ** 2  # 对方总消耗（+迎球消耗（不计算跑位）），考虑瞬移术
    # 以下是捡道具时判断收益部分;
    for card in tbcard:
        #print('!!!!!!!!!!!!!!!!!!!!!')
        if get_card(velocity_x, current_speed,self_x,self_y,card, eps=2000):
            #print(self_card)
            if len(self_card) >4:
                print(self_card)
                self_consume = self_consume + cardvalue(self_card[4].code) - cardvalue(card.code)
            else:
                self_consume -= cardvalue(card.code)
                #print('minus' + str(cardvalue(card.code)))
    '''oppo_accelerate = oppo_optimal(oppo_ball_y, oppo_ball_speed, self_y)  # 计算下对方的优化速度
    #oppo_consume += (oppo_accelerate / 50) ** 2  # 对方总消耗（+速度消耗）
    #back_y = calc_ball(oppo_ball_y, oppo_ball_speed + oppo_accelerate, period)[0]  # 我方为了接球要跑到的位置
    #self_consume += (((self_y - back_y) / 10000) ** 2) / 2  # 我方总消耗（+跑位与迎球消耗）'''
    return (oppo_consume - self_consume, self_consume, oppo_consume)  # 两者消耗体力值差值

def calc_ball(current_y, current_speed, period):  # 计算击球后求达到对方时的位置和速度
    y = current_y + current_speed * period
    if y >= 2 * table_y:  # 向上击打墙壁2次
        return (y - 2 * table_y, current_speed)
    if y >= table_y:  # 向上击打墙壁1次
        return (2 * table_y - y, -current_speed)
    if y <= -table_y:  # 向下击打墙壁2次
        return (y + 2 * table_y, current_speed)
    if y <= 0:  # 向下击打墙壁1次
        return (-y, -current_speed)

def availrange(y, speed):  # 计算有效加速范围
    if speed > 0:  # 球从下方来
        Max = math.floor((3 * table_y - y) / period) - speed  # ？？？？
        Min = math.ceil((table_y - y) / period) - speed
    elif speed < 0:#球从上方来
        Min = math.ceil((-2 * table_y - y) / period) - speed
        Max = math.floor((-y) / period) - speed  #
    return Min+1, Max-1#缩小范围

def op_optimal(self_y, self_speed, oppo_y):#预测对方加速策略
    Min, Max = availrange(self_y, self_speed)  # 函数：有效区间 self.y  对方那边的球落点，对方那边的球速，opp_y 对方位置
    optimal = -9999999
    result = 0
    for accelerate in range(Min,Max):
        op_pos = calc_ball(self_y, self_speed + accelerate, period)[0]#计算落点
        if op_pos < 10000 or op_pos > 990000:#为减少计算量，只有落点在两个角附近，才计算收益值
            temp = op_evaluate(self_y, self_speed, accelerate, oppo_y)#求出加速度对应收益值
            if temp > optimal:
                optimal = temp
                result = op_pos
    return result#返回对方收益最大时球在我方的落点

def op_evaluate(self_y, self_speed, self_accelerate, oppo_y):#预测对方收益值
    self_consume = oppo_consume = 0#初始化
    self_consume += (self_accelerate / 20) ** 2#对方体力消耗为加速体力消耗
    current_speed = self_speed + self_accelerate#对方加速后的速度
    oppo_ball_y, oppo_ball_speed = calc_ball(self_y, current_speed, period)#我方击球位置及我方击球前球速
    oppo_consume += ((oppo_y - oppo_ball_y) / 20000) ** 2#我方消耗为迎球体力消耗
    return oppo_consume - self_consume#返回对方收益


#print(availrange(100000,-1500))

