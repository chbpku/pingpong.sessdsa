from table import *
import random
Param_guess = 250   # 估计对手在旋转球我方使用旋转球时的加速的值，当作模拟旋转球扣减对方生命值时的参数
intervalnum = 100   # 记录对方跑位或击球落点的区间的个数
# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side: str, ds: dict) -> tuple:
    # 做一个0,1随机
    if random.randint(-1, 1) == 0:  # 是0就从下角发球碰壁两次打对面上角
        return 0, 5000/3 - 1
    else:
        return 1000000,-5000/3 + 1  # 是1就从上角发球碰壁两次打对面下角

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb:TableData, ds:dict) -> RacketAction:
    #print(tb.tick)
    counter(tb, ds) # 调用counter记录数据到ds
    tb.side['active_card'] = None   # 在tb.side里增加一项active_card，初始为None
    tb.cards['cards'] = list(filter(lambda x: not x in ['DS', 'TP'], tb.cards['cards']))    # 筛除场上的隐身和瞬移道具
    searchvalue = search(tb, None, 0, -1000000000, 1000000000, ds)  # 搜索最佳策略，返回一个列表[估值，我的加速，我的跑位，我要用的道具]
    if not searchvalue[3]:  # searchvalue[3]为道具返回值，card类
        a = None
    else:
        a = searchvalue[3].code
    ds['side_acceleration%d'%(ds['count'])] = int(searchvalue[1])   # 记录自己每次的加速的值，用于计算对方的加速度
    # 返回对自己动作的声明
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, searchvalue[1], searchvalue[2], None, a)

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return

#接下来是interval族函数，这些函数全部都是搜索枝条的选取函数，参量一般是一个tb，即桌面的情况，但对于对手的interval函数，会带上ds，即历史信息来预测对方的行为
#interval函数的返回值全部是一个列表，即搜索区间，里面包含了在树搜索中的搜索值

#我方的加速区间选取函数，参数是tb即桌面信息，返回的是一个列表，里面所有的元素是一个元组，其中第一个元素为加速之后球的目标速度值
#第二个元素为该目标速度上附带的道具信息，其中速度值的选取为人工启发，即在大量对战中人工找到的最优解，即打角或者打道具
def interval_myacc(tb:TableData):
    interval=[]
    #v1到v8分别为8个符合两次碰撞的打角速度值
    v1 =((DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)+1#1000为x方向速度的大小，即BALL_V[0]
    v2 = ((2 * DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)
    v3 = ((2 * DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)+1
    v4 = ((3 * DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)-1
    v5 = ((- tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)-1
    v6 = ((-DIM[3]- tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)
    v7 = ((-DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)-1
    v8 = ((-2*DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)+1

    #Delta_v1=(v4-v1)/3
    #Delta_v2=(v8-v5)/3
    #for i in range(4):
    #    interval.append((v1+Delta_v1*i,None))
    #    interval.append((v5+Delta_v2*i,None))
    interval.append((v1, None))
    interval.append((v5, None))
    interval.append((v2,None))
    interval.append((v6, None))
    interval.append((v3,None))
    interval.append((v4, None))
    interval.append((v7,None))
    interval.append((v8, None))
    #接下来是打道具的速度值的计算
    if len(tb.cards['cards']) != 0:
        for card in tb.cards['cards']:
            if  card==CARD_SPIN or card==CARD_INCL or card==CARD_DECL  or card==CARD_AMPL:
                cardv = [None,None,None,None,None]
                cardv[0] = (card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                cardv[1] = (2 * DIM[3] - card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                cardv[2] = (2 * DIM[3] + card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                cardv[3] = (- card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                cardv[4] = (- 2 * DIM[3] + card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                for i in range(5):
                    if (cardv[i] >= 0 and cardv[i] > v1 and cardv[i] < v4) \
                        or (cardv[i] < 0 and cardv[i] < v5 and cardv[i] > v8):#若这些打到道具的速度值能够满足一次或者两次碰撞，则加入interval
                        interval.append((cardv[i],card))
    return interval

#对方加速区间的选取函数，参量有两个，一个是tb，一个是ds，即桌面信息和历史数据，ds的作用是试图推测对方的会如何加速，返回值同上面的interval_myacc
#速度值的选取依然遵从人工启发原则，即打角速度和打道具速度，此处返回的速度也都是目标速度，而非速度的变化量
def interval_itsacc(tb:TableData,ds):
    interval = []  # interval用来存速度值目标，以元组为元素（速度值，目标（卡片名称或者None））
    # v1到v8分别为8个符合两次碰撞的打角速度值
    v1 =((DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)+1#1000为x方向速度的大小，即BALL_V[0]
    v2 = ((2 * DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)
    v3 = ((2 * DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)+1
    v4 = ((3 * DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)-1
    v5 = ((- tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)-1
    v6 = ((-DIM[3]- tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)
    v7 = ((-DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)-1
    v8 = ((-2*DIM[3] - tb.ball['position'].y) / (-DIM[0] + DIM[1]) * 1000)+1

    #Delta_v1=(v4-v1)/3
    #Delta_v2=(v8-v5)/3
    #for i in range(4):
    #    interval.append((v1+Delta_v1*i,None))
    #    interval.append((v5+Delta_v2*i,None))
    if guess_itsacc(tb, ds)[0] and guess_itsacc(tb, ds)[1] == 'dui':#若认为猜中了对方的加速而且对方是打对角原则，即远角原则，就只考虑那四个速度
        if ds['ball_position%d' % (ds['count'])] > DIM[3] / 2:#本方在跑位前的位置在球桌上方，就添加对方往下打的四个加速度
            interval.append((v2, None))
            interval.append((v3, None))
            interval.append((v5, None))
            interval.append((v8, None))
            # elif guess_itsacc(tb,ds)[1]=='fan':#由于模拟反角时，若不准确，造成的损失较大，所以删除了反角的猜测功能
            #    interval.append((v1, None))
            #    interval.append((v4, None))
            #    interval.append((v6, None))
            #    interval.append((v7, None))
        else:#若本方跑位前在球桌下方，就添加对方往上打的四个加速度
            interval.append((v1, None))
            interval.append((v4, None))
            interval.append((v6, None))
            interval.append((v7, None))
            # elif guess_itsacc(tb, ds)[1] == 'fan':#由于模拟反角时，若不准确，造成的损失较大，所以删除了反角的猜测功能
            #    interval.append((v2, None))
            #    interval.append((v3, None))
            #    interval.append((v5, None))
            #    interval.append((v8, None))
    else:#若无法判定对方如何加速，就添加对方的8个打角速度
        interval.append((v1, None))
        interval.append((v5, None))
        interval.append((v2, None))
        interval.append((v6, None))
        interval.append((v3, None))
        interval.append((v4, None))
        interval.append((v7, None))
        interval.append((v8, None))

    #对方打道具的速度计算，与interval_myacc相同
    if len(tb.cards['cards']) != 0:
        for card in tb.cards['cards']:
            if  card==CARD_SPIN or card==CARD_INCL or card==CARD_DECL  or card==CARD_AMPL:
                cardv = [None,None,None,None,None]
                cardv[0] = (card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                cardv[1] = (2 * DIM[3] - card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                cardv[2] = (2 * DIM[3] + card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                cardv[3] = (- card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                cardv[4] = (- 2 * DIM[3] + card.pos.y - tb.ball['position'].y) / abs((card.pos.x - tb.ball['position'].x)) * 1000
                for i in range(5):
                    if (cardv[i] >= 0 and cardv[i] > v1 and cardv[i] < v4) \
                        or (cardv[i] < 0 and cardv[i] < v5 and cardv[i] > v8):
                        interval.append((cardv[i],card))
    return interval

#我的跑位值的选取函数，参量是tb，返回值是一个列表，其中的元素全部是我的位置的变化量，即跑位值，跑位点的选取有人工启发和跑位范围内的平均取值
def interval_myrun(tb:TableData):
    interval = []
    if tb.side['position'].y > DIM[3] / 2:#我在上面的情况，跑位遵从不跑过中点的原则
        y2 = DIM[3] / 2 - tb.side['position'].y#y2是跑位值的最小值，此处选择跑到中点时的跑位值
        #这里是防止在之后的迎球中最大半径无法覆盖全局的死亡修正，若处在了一个对手通过打远角就可以一击必杀的位置，那么就要不能采用这种位置，即跑位区间要修改
        if int((tb.side['life'] / RACKET_LIFE) * (-DIM[0] + DIM[1]))>=DIM[3]:#近似解，若之后可以覆盖到下角
            y1=DIM[3]-tb.side['position'].y#y1就是跑到上顶端的跑位值，y1为跑位值的最大值
        else:#若之后无法覆盖到下角
            y1=18*(tb.side['life']-700)-tb.side['position'].y#y1就选择刚好能覆盖到下角的值
        if (651300-tb.side['position'].y)<y1:#此处为人工启发点651300，根据大量对战推测出的一个比较好的跑位点，若到这个点能够覆盖到最下角的话，就添加到interval中
            interval.append(651300-tb.side['position'].y)
    else:#我在下方的情况，与上面的是对称的
        y1 = DIM[3] / 2 - tb.side['position'].y
        if int((tb.side['life'] / RACKET_LIFE) * (-DIM[0] + DIM[1]))>=DIM[3]:
            y2=-tb.side['position'].y
        else:
            y2=DIM[3]-tb.side['position'].y-18*(tb.side['life']-700)
        if (348711-tb.side['position'].y)>y2:
            interval.append(348711-tb.side['position'].y)
    Delta_y=(y1-y2)/4#在从y2到y1取等四分，加入到interval中
    for i in range(5):
        interval.append(y2+i*Delta_y)
    return interval

#对手非首次跑位的取值函数，非首次跑位意味着是在模拟中的跑位，没有跑位方向这个确定量，而且模拟中偏差会较大，就没有加入ds的预测
def interval_itsrun(tb:TableData):
    if tb.op_side['position'].y>DIM[3]/2:
        if int((tb.op_side['life'] / RACKET_LIFE) * (-DIM[0] + DIM[1]))>=DIM[3]-tb.op_side['position'].y:
            y1=DIM[3]-tb.op_side['position'].y
        else:
            y1 = int(1.8 * (tb.op_side['life'] - 650) - tb.op_side['position'].y)
        y2=DIM[3]/2-tb.op_side['position'].y
    else:
        y1=DIM[3]/2-tb.op_side['position'].y
        if int((tb.op_side['life'] / RACKET_LIFE) * (-DIM[0] + DIM[1])) >=DIM[3]:
            y2 = -tb.op_side['position'].y
        else:
            y2 = int(DIM[3] - tb.op_side['position'].y - 1.8 * (tb.op_side['life'] - 650))
    interval = []
    Delta_y = (y1 - y2) /3#对手的跑位粗糙化了，只取了三等分
    for i in range(4):
        interval.append(y2 + i * Delta_y)
    return interval

#对手的 首次跑位模拟，即有确定的跑位方向的第一次跑位，此时要调用ds来预测对手的跑位值，同样遵从不跑过中点的原则
def interval_firstitsrun(tb:TableData,ds):
    interval = []
    guess=guess_itsrun(tb,ds)#guess为猜测出来的结果
    if guess[0]:#若对猜测有信心
        if guess[1]=='r':#若是距离中点长度固定的跑位方式
            if tb.op_side['position'].y>DIM[3]/2:#对手在上方时，就在interval中添加跑到的那个点的跑位值
                interval.append(DIM[3]/2+guess[2]-tb.op_side['position'].y)
            else:#下方时，同样的处理
                interval.append(DIM[3]/2-guess[2]-tb.op_side['position'].y)
        #elif guess[1]=='pos':
        #    interval.append(guess[2]-tb.op_side['position'].y)
        #elif guess[1]=='False':
        #    interval.append(0)
    else:#若认为没有猜中，则进行同样的大范围预测，y1与y2的选择与之前相同
        if tb.op_side['position'].y>DIM[3]/2:
            if int((tb.op_side['life'] / RACKET_LIFE) * (-DIM[0] + DIM[1]))>=DIM[3]-tb.op_side['position'].y:
                y1=DIM[3]-tb.op_side['position'].y
            else:
                y1=int((tb.op_side['life'] / RACKET_LIFE) * (-DIM[0] + DIM[1]))
            y2=DIM[3]/2-tb.op_side['position'].y
        else:
            y1=DIM[3]/2-tb.op_side['position'].y
            if int((tb.op_side['life'] / RACKET_LIFE) * (-DIM[0] + DIM[1])) >= tb.op_side['position'].y:
                y2 = -tb.op_side['position'].y
            else:
                y2 = -int((tb.op_side['life'] / RACKET_LIFE) * (-DIM[0] + DIM[1]))
        #针对跑位方向，更精确的确定跑位范围，依然是取三等分
        if tb.op_side['run_vector']==1:
            Delta_y = (y1) / 3
            for i in range(4):
                interval.append((3-i)*Delta_y)
        elif tb.op_side['run_vector']==-1:
            Delta_y = (y2) / 3
            for i in range(4):
                interval.append((3-i) * Delta_y)
        else:#对手使用隐身术的情况
            Delta_y = (y1-y2) / 3
            for i in range(4):
                interval.append(y2+i * Delta_y)
    return interval

#接下来是image族函数，是模拟桌面情况变化的函数，一般来说参量有两个，第一个是tb，即桌面情况，第二个是move，即递归枝条中的行动值，比如加速加多少，跑位跑多少之类
#返回值全部是为改变之后的tb

#这个函数是在模拟我的球拍迎球阶段的桌面情况变化，参量为tb，没有move值，或者说行动值唯一确定，即球的落点减去当前球拍位置的值
def image_mybat(tb:TableData):
    life = tb.side['life']
    dy = abs(tb.ball['position'].y - tb.side['position'].y)
    # 减少迎球消耗的体力值
    param=2 if tb.op_side['active_card'][1] == CARD_AMPL else 1#变压器修正
    tb.side['life'] -= (dy ** 2 // FACTOR_DISTANCE ** 2)*param
    #tb.side['life'] -= (dy ** 2 // FACTOR_DISTANCE ** 2)*(CARD_AMPL_PARAM if tb.op_side['active_card'][1] == CARD_AMPL else 1)
    # 迎球方球拍移动到球所在的位置
    tb.side['position'].y = tb.ball['position'].y
    # 再加上接不到球的死亡修正，若在迎球阶段，接不到球，则一定不能采取这种策略，将生命值调味负无穷，在接下来的evaluate中得到一个负无穷的值
    if tb.op_side['life'] > 0 and int((life / RACKET_LIFE) * (-DIM[0] + DIM[1])) < dy:
        tb.side['life'] = -100000000
    return tb

#模拟对手的迎球阶段的函数，与image_mybat类似
def image_itsbat(tb:TableData):
    life = tb.op_side['life']
    dy = abs(tb.ball['position'].y - tb.op_side['position'].y)
    # 减少迎球消耗的体力值
    tb.op_side['life'] -= (dy ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if tb.side['active_card'] == CARD_AMPL else 1)
    # 迎球方球拍移动到球所在的位置
    tb.op_side['position'].y = tb.ball['position'].y
    # 再加上接不到球的死亡修正，若在迎球阶段，接不到球，则一定不能采取这种策略，将生命值调味负无穷，在接下来的evaluate中得到一个负无穷的值
    if tb.side['life'] > 0 and int((life / RACKET_LIFE) * (-DIM[0] + DIM[1])) < dy:
        tb.op_side['life'] = -100000000
    return  tb

#模拟我方的加速过程的函数，其中也包含了加速之后球的飞行的过程中桌面情况的变化，move值为aim_v，即想要加速到的球的速度
def image_myacc(tb:TableData,aim_v):#我的加速过程模拟
    param=1
    if tb.op_side['active_card'][1]==CARD_SPIN:#旋转球修正
        param=2
    Delta_v=(aim_v[0]-tb.ball['velocity'].y)*param#Delta_v为play函数声明的加速度值，aim_v不随着旋转球改变，但是Delta_v会随着对手使用旋转球而*2
    #接下来减少加速消耗的生命值
    param_=2 if tb.op_side['active_card'][1] == CARD_AMPL else 1#变压器修正
    tb.side['life'] -= (Delta_v ** 2 // FACTOR_SPEED ** 2) *param_
    #接下来改变加速导致的球的速度
    tb.ball['velocity'].y +=int(Delta_v*(CARD_SPIN_PARAM if tb.op_side['active_card'][1] == CARD_SPIN else 1))
    # 改变桌面道具信息
    if aim_v[1] != None:
        tb.cards['cards'].pop(tb.cards['cards'].index(aim_v[1]))
        tb.side['cards'].append(aim_v[1])
    # 接下来改变加速后球飞完了之后的x坐标
    #tb.ball['position'].x=-tb.ball['position'].x
    # 接下来改变加速后球飞完了之后的y坐标
    Y = tb.ball['velocity'].y / 1000 * (-DIM[0] + DIM[1]) + tb.ball['position'].y
    count = Y // DIM[3]
    tb.ball['position'].y = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
    tb.ball['velocity'].y = tb.ball['velocity'].y * ((count + 1) % 2 * 2 - 1)
    #加上死亡修正，若此对手手生命值没到0而，加速后迎球方life到0，则一定不能采取这种策略，将生命值调味负无穷，在接下来的evaluate中得到一个负无穷的值
    #if tb.op_side['life']>0 and tb.side['life']<=0:
        #tb.side['life']=-100000000
    return tb

#对手的加速过程模拟,与image_myacc类似
def image_itsacc(tb:TableData,aim_v):
    param=1
    if tb.side['active_card']==CARD_SPIN:
        param=2
    Delta_v = (aim_v[0]-tb.ball['velocity'].y)*param
    #接下来减少加速消耗的生命值
    tb.op_side['life'] -= (Delta_v**2//FACTOR_SPEED ** 2) *(CARD_AMPL_PARAM if tb.op_side['active_card'] == CARD_AMPL else 1)
    #接下来改变加速导致的球的速度
    tb.ball['velocity'].y +=int(Delta_v*(CARD_SPIN_PARAM if tb.side['active_card'] == CARD_SPIN else 1))
    # 改变桌面道具信息
    if aim_v[1] != None:
        tb.cards['cards'].pop(tb.cards['cards'].index(aim_v[1]))
        tb.op_side['cards'].append(aim_v[1])
    # 接下来改变加速后球飞完了之后的x坐标
    #tb.ball['position'].x=-tb.ball['position'].x
    # 接下来改变加速后球飞完了之后的y坐标
    Y = tb.ball['velocity'].y / 1000 * (-DIM[0] + DIM[1]) + tb.ball['position'].y
    count = Y // DIM[3]
    tb.ball['position'].y = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
    tb.ball['velocity'].y = tb.ball['velocity'].y * ((count + 1) % 2 * 2 - 1)
    #加上死亡修正，若此对手手生命值没到0而，迎球加加速后迎球方life到0，则一定不能采取这种策略，将生命值调味负无穷，在接下来的evaluate中得到一个负无穷的值
    #if tb.side['life']>0 and tb.op_side['life']<=0:
        #tb.op_side['life']=-100000000
    return tb

#我的跑位过程的模拟，move值为真实的跑位值Delta_y
def image_myrun(tb:TableData,Delta_y):#myrun没有死亡修正，因为在之前取myruninterval时避开了死亡跑位距离
    if tb.side['active_card'] == CARD_TLPT:  # 如果碰到瞬移卡，则从距离减去CARD_TLPT_PARAM再计算体力值减少
        if abs(Delta_y)-CARD_TLPT_PARAM> 0:
            tb.side['life'] -=(Delta_y-CARD_TLPT_PARAM) ** 2 // FACTOR_DISTANCE **2
    else:
        tb.side['life']-=Delta_y ** 2 // FACTOR_DISTANCE ** 2
    tb.side['position'].y+=Delta_y#移动跑位方的球拍
    return tb

#对手的跑位过程的模拟，move值为真实的跑位值Delta_y
def image_itsrun(tb:TableData,Delta_y):
    if tb.op_side['active_card'][1] == CARD_TLPT: # 如果碰到瞬移卡，则从距离减去CARD_TLPT_PARAM再计算体力值减少
        if abs(Delta_y)-CARD_TLPT_PARAM> 0:
            tb.op_side['life'] -=(Delta_y-CARD_TLPT_PARAM) ** 2 // FACTOR_DISTANCE **2
    else:
        tb.op_side['life']-=Delta_y ** 2 // FACTOR_DISTANCE ** 2
    tb.op_side['position'].y+=Delta_y#移动跑位方的球拍
    return tb

#我的首次使用道具阶段的模拟，该过程声明道具卡后，所有道具卡的效果可以完全真实模拟出来，move值为使用的卡used_card
def image_mycard(tb:TableData,used_card):#used_card为card类，若不使用，则为None
    if used_card !=None:
        tb.side['active_card'] = used_card.code
        tb.side['cards'].pop(tb.side['cards'].index(used_card))
    else:
        tb.side['active_card']=None
    #加血减血卡立即生效
    if tb.side['active_card'] == CARD_INCL:
        tb.side['life'] += CARD_INCL_PARAM
    elif tb.side['active_card'] == CARD_DECL:
        tb.op_side['life'] -= CARD_DECL_PARAM
    return tb

#我方第二次使用道具过程的模拟，由于此二次使用道具通常是第一次加速之后接到了一个道具再使用，因此由于搜索深度不够，在模拟中，像旋转球这样的道具来不及发挥作用
#于是就有人为的估值模拟，此处其他的与image_mycard类似，但是多添加了旋转球修正
def image_nextmycard(tb:TableData,used_card,ds):#used_card为card类，若不使用，则为None
    if used_card !=None:
        tb.side['active_card'] = used_card.code
        tb.side['cards'].pop(tb.side['cards'].index(used_card))
    else:
        tb.side['active_card']=None
    if tb.side['active_card'] == CARD_INCL:
        tb.side['life'] += CARD_INCL_PARAM
    elif tb.side['active_card'] == CARD_DECL:
        tb.op_side['life'] -= CARD_DECL_PARAM
    elif tb.side['active_card'] == CARD_SPIN:#旋转球修正，减扣对手一定的体力值，通过guess_spin_to_itsacc来实现，不过由于实际效果，此处对手加速值默认为250
        tb.op_side['life']-=((2*guess_spin_to_itsacc(tb,ds)[1])** 2 // FACTOR_SPEED ** 2)
    return tb

#对手使用道具的阶段的模拟，与image_mycard类似
def image_itscard(tb:TableData,used_card):
    if used_card != None:
        tb.op_side['active_card'] =(None,used_card.code)
        tb.op_side['cards'].pop(tb.op_side['cards'].index(used_card))
    else:
        tb.op_side['active_card'] = (None,None)
    if tb.op_side['active_card'][1] == CARD_INCL:
        tb.op_side['life'] += CARD_INCL_PARAM
    elif tb.op_side['active_card'][1] == CARD_DECL:
        tb.side['life'] -= CARD_DECL_PARAM
    return tb

#接下来是guess函数，即猜测对手的行为的函数，参量有两个，第一个为tb，桌面信息，第二个为ds，即历史数据，返回值通常是一个猜测的值

#猜测我方使用旋转球之后对手的反应的函数，由于效果不是很好，模拟之后的风险比较大，所以并没有采用，而是直接默认为无法猜测
#Param_guess=250，为通过对方最少在相持中损耗的体力值推测出来的加速度，为虚假值，只是一个为了模拟对方的体力值减少而计算出来的值
def guess_spin_to_itsacc(tb:TableData,ds):
    itsacc = (False, Param_guess)
    return itsacc

#猜测对手的加速的值的函数，一般来说，为通过历史数据来判断对手是打对角还是反角（远角和近角）
def guess_itsacc(tb:TableData, ds):
    result = (False, None)
    if ds['count'] >= 2:
        pos1 = ds['ball_position%d'%(ds['count']-1)]
        pos2 = ds['ball_position%d'%(ds['count'])]
        if abs(pos1 - pos2) >= 970000:
            result = (True, 'dui')  #返回一个对手的策略，(True，'dui')，True代表对猜测有信息，'dui'代表对手会选择打到对角
        elif abs(pos1 - pos2) <= 30000:
            result = (True, 'fan')

    return result

#猜测对手的跑位值的函数
def guess_itsrun(tb:TableData,ds):
    result = (False, None)
    if ds['count'] >= 4:
        runposition1 = ds['opside_runposition%d'%(ds['count']-2)]
        runposition2 = ds['opside_runposition%d'%(ds['count']-1)]
        if runposition1 and runposition2:
            #第一种为判断对手是否会对称跑距离中点的半径，第二种为对手是否跑到同一个地方，第三种为对手是否假跑位，第二第三种效果不好，就删除了
            if abs(abs(runposition1 - DIM[3]/2) - abs(runposition2 - DIM[3])) <= 30000:
                result = (True, 'r', 0.5*(abs(runposition1 - DIM[3]/2)+abs(runposition2 - DIM[3])))#True代表对模拟的值有信息
                # 'r'代表对手的跑位策略遵从到中点的半径，0.5*(abs(runposition1 - DIM[3]/2)+abs(runposition2 - DIM[3]为对手跑位中距离中点的半径

            #elif abs(runposition2 - runposition1) <= 30000:
            #    result = (True, 'pos', 0.5*(runposition1+runposition2))
            #elif abs(runposition2-ds['opside_position%d'%(ds['count']-1)]) <= 30000 and abs(runposition1-ds['opside_position%d'%(ds['count']-2)]) <= 30000:
            #    result = (True, 'False', None)
    return result

#到达搜索深度之后的估值函数，此处选取的是我方体力值和对方体力值之差，越大对我越有利，越小对对方越有利
def evaluate(tb:TableData):
    return tb.side['life']-tb.op_side['life']


maxdepth=13#maxdepth为最大递归深度，对应一个半回合的搜索

#主体函数search，为一个递归函数，参量有6个parametertb为桌面信息，为一个TableData类，move为上一层告诉下一层应该执行的操作，depth为递归深度,
# a,b为阿尔法贝塔剪枝中的两个参量，分别表示我的操作带来的最大估值值和对手的操作带来的最小估值值，ds为历史数据
def search(parametertb:TableData,move,depth,a,b,ds):
    tb=tbcopy(parametertb)#每一次搜索时进行一次tbcopy，将传入的parametertb拷贝，使得在搜索中不改变parametertb，导致上层会被影响，而是使用一个新的tb
    #此tb也仅仅会在搜索中被改变一次，即move一次
    if(depth>maxdepth):#若超过了最大深度,此处dept为14，最后还是有一个对方使用道具卡的操作
        tb = image_itscard(tb, move)#完成对方使用道具卡的操作
        return evaluate(tb)#返回估值值
    else:#若为到达最大深度
        if depth%8==0:#第一阶段，模拟我的迎球和对手的加速，不分枝
            if depth!=0:#不是第0层时，需模拟对手的加速，move不为空
                tb = image_itsacc(tb, move)
            tb = image_mybat(tb)#若depth=0，则无需模拟对手的加速，传来的tb已经完成了
            a=search(tb,None,depth+1,a,b,ds)#往下进行搜索，此处move是None，迎球过程之后没有对下一层的操作
            return a
        if depth%8==1:#第二阶段，搜索对手跑位阶段
            if depth==1:#depth=1时，要一同返回搜索中得到的我方的最佳操作
                myacc = 0#定义了myacc，myrun，mycard最为储存最佳操作的变量
                myrun = 0
                mycard=None
                for i in interval_firstitsrun(tb,ds):#对interval_firstitsrun返回的对手跑位区间进行搜索，i是跑位值
                    if a<b:#ab剪枝算法，若a<b，则可以继续下去搜索
                        searchvalue=search(tb,i, depth + 1,a,b,ds)#进行search递归搜索，depth变为现在的depyh+1,tb,a,b,ds往下传参,move为i，searchvalue为储存的返回值
                        if b > searchvalue[0]:#此处是对手的操作阶段，所以估值参量是b若b>searchvalue[0]，说明对手的这个跑位值带来的searchvalue[0]比b更好，
                            # 那么对手会采用这种跑位值，接下来开始赋值，改变b，myacc,myrun,mycard
                            b = searchvalue[0]
                            myacc = searchvalue[1]
                            myrun = searchvalue[2]
                            mycard = searchvalue[3]
                return [b, myacc, myrun, mycard]#返回#返回带有估值值和操作值的列表
            else:#若depth!=1，则只需返回估值值，其他操作与上面相同
                for i in interval_itsrun(tb):
                    if a < b:
                        searchvalue = search(tb,i, depth + 1,a,b,ds)
                        if b > searchvalue:
                            b = searchvalue
                return b#只需返回估值值

        elif depth%8==2:# 第三阶段，搜索我使用道具阶段，由于人工启发，此处为有道具就用的策略，不存道具
            tb = image_itsrun(tb, move)#模拟传来的move值，对应的对方跑位阶段后tb的变化
            if depth==2:#depth=2时也要返回我的操作值
                i=None#i为要使用的道具，初始为None
                if tb.side['cards']:#若我的道具列表不为空
                    i=tb.side['cards'][0]#则i变为第一个道具
                searchvalue=search(tb,i,depth+1,a,b,ds)#往下搜索,i为使用的道具,此处并未分枝
                a=searchvalue[0]
                myacc=searchvalue[1]
                myrun=searchvalue[2]
                mycard=i
                return [a, myacc, myrun,mycard]#返回带有估值值和操作值的列表
            else:#depth不为2时，无需保存操作值
                i = None
                if tb.side['cards']:
                    i = tb.side['cards'][0]
                searchvalue = search(tb, i, depth + 1,a,b,ds)
                a=searchvalue
                return a

        elif depth%8==3:# 第四阶段，搜索我的加速阶段
            if depth == 3:#depth=3时，要返回我的操作值
                tb = image_mycard(tb, move)#模拟我使用道具之后的桌面情况变化
                param = 1
                if tb.op_side['active_card'][1] == CARD_SPIN:#旋转球修正
                    param = 2
                myacc = 0#myacc和myrun为两个操作值
                myrun = 0
                for i in interval_myacc(tb):#对于interval_myacc中的所有的速度值一一搜索，i为目标速度值
                    if a<b:#若a<b，则进行下去
                        searchvalue=search(tb, i, depth + 1,a,b,ds)#search进行递归搜索，move值i为目标的速度值
                        if a < searchvalue[0]:#此处是我的操作阶段，所以以a作为估值参量，若a小于这个i的searchvalue[0]，则说明这个i对应我的更优解
                            #修改a，myacc,myzun
                            a = searchvalue[0]
                            myacc = (i[0] -tb.ball['velocity'].y)*param#需要注意的是，myacc需要根据i进行一个变换，因为i并非加速值，而是加速后球的目标速度值
                            myrun =searchvalue[1]
                return [a, myacc, myrun]#返回带有估值值和操作值的列表
            else:#若发生在更深层，则无需保存操作值
                tb = image_nextmycard(tb, move,ds)
                for i in interval_myacc(tb):
                    if a<b:
                        searchvalue = search(tb, i, depth + 1,a,b,ds)
                        if a <searchvalue :
                            a =searchvalue
                return a#只需返回估值值

        elif depth%8==4: #第五阶段，模拟对手的迎球，不分枝搜索
            tb = image_myacc(tb, move)#模拟我的加速
            tb = image_itsbat(tb)  # 模拟对手迎球
            b=search(tb,None, depth + 1,a,b,ds)#不分枝
            return b

        elif depth==5:  # 第六阶段，搜索我的跑位阶段
            if depth == 5:  # 判断本步是否要返回操作，若为depth=2,则为第一个回合中的加速，要返回
                myrun=0#myrun为要返回的跑位操作值
                for i in interval_myrun(tb):#对interval_myrun区间进行搜索，i为跑位值
                    if a<b:#若a<b，继续下去搜索
                        searchvalue = search(tb, i, depth + 1,a,b,ds)#递归搜索
                        if a < searchvalue:#此处是我的操作阶段，用a表示估值参量，若a<searchvalue,则同上，修改a和myrun
                            a = searchvalue
                            myrun = i
                return [a,myrun]#s返回带有估值值和操作值的列表
            else:#若depth!=5,无需返回操作值，同上
                for i in interval_myrun(tb):
                    if a < b:
                        searchvalue = search(tb,i, depth + 1,a,b,ds)
                        if a < searchvalue:
                            a =searchvalue
                return a

        elif depth==6:  # 第七阶段，搜索对手使用道具阶段，处理方法也是猜测对手有道具就用，操作与depth%8==1相同，且此处无需返回操作值
            tb = image_myrun(tb, move)#模拟我的跑位情况带来的桌面变化
            i=None
            if tb.op_side['cards']:
                i=tb.op_side['cards'][0]
            searchvalue = search(tb,i, depth + 1,a,b,ds)
            b=searchvalue
            return b

        elif depth==13: # 搜索对手使用道具阶段，这里调换了一下顺序，为了多搜索一下对手在第二回合中的道具使用情况
            # 避开第二回合中我的跑位阶段搜索（那个阶段的搜索无意义，因为我的跑位的价值要体现在下一回合的迎球中，所以这种深度下，并无意义）
            i = None
            if tb.op_side['cards']:
                i = tb.op_side['cards'][0]
            searchvalue = search(tb, i, depth + 1, a, b,ds)
            b = searchvalue
            return b

        else:#第八阶段，搜索对手的加速阶段
            tb=image_itscard(tb,move)#模拟对手用道具带来的tb的变化
            for i in interval_itsacc(tb,ds):#对对手的每一个加速值进行搜索
                if a < b:
                    searchvalue = search(tb, i, depth + 1,a,b,ds)
                    if b > searchvalue:#此处为对手的操作，估值参量为b
                        b =searchvalue
            return b#返回估值参量

#tbcopy，为了避免使用deepcopy，自己实现一个针对TableData的copy函数
def tbcopy(tb):
    newtick = tb.tick
    newstep = tb.step
    newside = {
        'name': tb.side['name'],
        'position': Position(tb.side['position'].x, tb.side['position'].y),
        'life': tb.side['life'],
        'cards': [i for i in tb.side['cards']],
        'active_card' : tb.side['active_card']
    }
    newopside = {
        'name': tb.op_side['name'],
        'position': Position(tb.op_side['position'].x, tb.op_side['position'].y),
        'life': tb.op_side['life'],
        'cards': [i for i in tb.op_side['cards']],
        'active_card': tb.op_side['active_card'],
        'accelerate': tb.op_side['accelerate'],
        'run_vector': tb.op_side['run_vector']
    }
    newball = {
        'position': Position(tb.ball['position'].x, tb.ball['position'].y),
        'velocity': Vector(tb.ball['velocity'].x, tb.ball['velocity'].y)
    }
    newcard = {
        'card_tick': tb.cards['card_tick'],
        'cards': [i for i in tb.cards['cards']]
    }
    return TableData(newtick, newstep, newside, newopside, newball, newcard)


# for ds:
#  记录tb的数据，并作分析，最终在ds上记录
def counter(tb, ds):

    if tb.tick in (0, 1800):                                    # 开局
        ds.clear()                                              # 清空记忆
        ds['count'] = 0                                         # 计数
        ds['ball_position_list'] = [0, ]*intervalnum            # 球落点列表
        ds['opside_runposition_list'] = [0, ]*intervalnum       # 对手跑位列表

    ds['count'] += 1                                            # 计数+1
    ds['ball_position%d'%(ds['count'])] = tb.ball['position'].y # 记录对方球本次的落点
    ds['opside_position%d'%(ds['count'])] = tb.op_side['position'].y    # 记录对手本次的位置（即我方上一局球的落点）
    ds['ball_velocity%d'%(ds['count'])] = tb.ball['velocity'].y         # 记录本次接到的球的Y方向的速度
    ds['opside_rundirection%d'%(ds['count'])] = tb.op_side['run_vector']# 记录对方本次跑位的方向
    ds['opside_life%d'%(ds['count'])] = tb.op_side['life']              # 记录对方本次的生命剩余
    ds['opside_active_card%d'%(ds['count'])] = tb.op_side['active_card'][1] # 记录对方本次使用的道具
    ds['side_active_card%d'%(ds['count'])] = tb.side['cards'][0].code if tb.side['cards'] else None
    # 记录自己本次使用过的卡片（默认自己有卡片就立即使用）
    record_ball_position(tb, ds)    # 调用函数记录对方球的落点

    if ds['count'] >= 3:            # 当计数大于等于3时，开始计算并记录对方的跑位
        record_opside_runposition(tb, ds)

#记录对手的击球落点
def record_ball_position(tb, ds):
    #  将落点区域等分为intervalnum份，用列表存储落到每个等份区域中的次数
    ballposnum = int(ds['ball_position%d'%(ds['count'])] // (DIM[3]//intervalnum))
    if ballposnum == intervalnum:
        ballposnum -= 1
    ds['ball_position_list'][ballposnum] += 1

# 记录对手上一次的跑位位置
def record_opside_runposition(tb, ds):
    # 调用函数利用ds中记录的相关数据计算对上上一次的跑位位置
    opside_runposition = caculate_opside_runposition(tb, ds)
    # 将对手的跑动区域等分为intervalnum等份，用列表储存对手跑到每个区域的次数
    ds['opside_runposition%d' % (ds['count'] - 1)] = opside_runposition     # 记录每次的对手跑位位置
    if opside_runposition:  # 如果返回None，那么就放弃本次数据
        runpositionnum = int(opside_runposition//(DIM[3]//intervalnum))
        runpositionnum = intervalnum-1 if runpositionnum == intervalnum else runpositionnum
#        print(opside_runposition)
        ds['opside_runposition_list'][runpositionnum] += 1


# 已经修订之后的计算对手真实加速度值的函数，返回真实加速度，浮点类型
def caculate_opside_acc(tb, ds):    # 计算count时的对手的加速值

    velocity_y1 = ds['ball_velocity%d'%(ds['count']-1)] # 上一次接到的球的y方向速度
    position_y1 = ds['ball_position%d'%(ds['count']-1)] # 上一次接到的球的y方向位置
    velocity_y2 = ds['ball_velocity%d'%(ds['count'])] # 这一次接到的球的y方向速度
    position_y2 = ds['ball_position%d'%(ds['count'])] # 这一次接到的球的y方向位置
    # 考虑我方上一次加速对球速度的影响
    velocity_y1 += int(ds['side_acceleration%d'%(ds['count']-1)]) if ds['opside_active_card%d'%(ds['count']-1)] != 'SP' else int(ds['side_acceleration%d'%(ds['count']-1)]*0.5)
    # 下面内容拷贝自table，计算对方加速前后球的y方向的速度
    Y = position_y1 + velocity_y1*1800
    if Y%DIM[3] != 0:
        count = Y // DIM[3]
#        position_y1 = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)

    else:
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])
#        position_y1 = Y % (2 * DIM[3])

    velocity_y1 = velocity_y1 * ((count + 1) % 2 * 2 - 1)

    Y = position_y2 - velocity_y2*1800
    if Y%DIM[3] != 0:
        count = Y // DIM[3]
#        position_y2 = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
#        if position_y2 != ds['opside_position%d'%(ds['count'])]:
#            print('wrong position2')
    else:
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])
#        position_y2 = Y % (2 * DIM[3])
#        if position_y2 != ds['opside_position%d' % (ds['count'])]:
#            print('wrong position2')
    velocity_y2 = velocity_y2 * ((count + 1) % 2 * 2 - 1)

#    if position_y1 % DIM[3] == 0:
#        velocity_y2 *= -1

    acc = velocity_y2 - velocity_y1 if ds['side_active_card%d'%(ds['count']-1)] != 'SP' else (velocity_y2 - velocity_y1)*2

    # 返回一个对方的真实加速度，浮点类型
    return acc


# 修订之后的计算对手真实跑位位置的函数
def caculate_opside_runposition(tb, ds):  # 计算并记录对方历史跑位信息
    # get parameters from ds
    opside_life1 = ds['opside_life%d'%(ds['count']-1)]  # 上一次记录的对手剩余的体力值
    opside_life2 = ds['opside_life%d'%(ds['count'])]    # 这一次记录的对手剩余的体力值
    opside_acc = caculate_opside_acc(tb, ds)            # 计算对手这一次的加速度
    opside_position1 = ds['opside_position%d'%(ds['count']-1)]  # 对手上一次的位置
    opside_position2 = ds['opside_position%d'%(ds['count'])]    # 对手这一次的位置
    PARAM_AM = 2 if ds['side_active_card%d'%(ds['count']-1)] == 'AM' else 1     # 变压器参数，我放上一次使用了变压器就设为2，否则为1
#    PARAM_SP = 2 if ds['side_active_card%d'%(ds['count']-1)] == 'SP' else 1    # 旋转球参数，我放上一次使用了旋转球就设为2，否则为1
    PARAM_side_card = 2000 if ds['side_active_card%d'%(ds['count']-1)] == 'DL' else 0   # 血包参数，我方上一次使用了掉血包就设为+2000，否则为0
    PARAM_opside_card = -2000 if ds['opside_active_card%d'%(ds['count'])] == 'IL' else 0# 血包参数，对方这一次使用了加血包就设为-2000，否则为0
    PARAM_TP = 1 if ds['opside_active_card%d'%(ds['count']-1)] == 'TP' else None        # 瞬移参数，如果对手上一次使用了瞬移，那么设为1，否则为None
#    PARAM_DS = 1 if ds['opside_active_card%d'%(ds['count'])] == 'DS' else None         # 隐身参数，如果对手本次使用了隐身道具，那又怎样
    PARAM_vector = ds['opside_rundirection%d'%(ds['count']-1)]                          # 跑位方向参数，用来校对计算结果
    if PARAM_TP:        # 如果对手上一次使用了瞬移道具，那算球，放弃本次数据，返回None
        opside_runposition = None
    else:
        # get parameters for equation，计算一元二次方程的三个参数
        a = (1+PARAM_AM)/20000**2                                                   # 二次项系数
        b = -2*(opside_position1+PARAM_AM*opside_position2)/20000**2                # 一次项系数
        c = (opside_position1**2+PARAM_AM*opside_position2**2)/20000**2+(int(opside_acc)**2//20**2)*PARAM_AM\
            + PARAM_side_card + PARAM_opside_card + opside_life2 - opside_life1     # 常数项系数
        # solve the equation
        delta = (b**2 - 4*a*c)                                                      # Δ
        if delta < 0:                                                               # Δ小于0，无解（不知道为什么会出现无解），返回None
#            print('no solution')
            opside_runposition = None
        else:
            opside_runposition1 = (-b + math.sqrt(delta))/(2*a)                     # 解1
            opside_runposition2 = (-b - math.sqrt(delta))/(2*a)                     # 解2
            # 判断两个解是否有意义
            if not isValidrunposition(opside_runposition1, PARAM_vector, opside_position1):
                opside_runposition1 = None
            if not isValidrunposition(opside_runposition2, PARAM_vector, opside_position1):
                opside_runposition2 = None
            # 两个解对应的对手跑位的距离，取较小的一个对应的跑位位置为真实的跑位位置
            d1 = abs(opside_runposition1-opside_position1) if opside_runposition1 else None
            d2 = abs(opside_runposition2-opside_position1) if opside_runposition2 else None
            # 一些逻辑......
            if not d1:
                if d2:
                    opside_runposition = d2
                else:
                    opside_runposition = None
            else:
                if d2 and d1<d2:
                    opside_runposition = d1
                elif d2 and d1 >= d2:
                    opside_runposition = d2
                else:
                    opside_runposition = d1
#            print(opside_runposition)

            return opside_runposition
# 判断计算对手跑位得到的解是否有意义，基于三个参数：对手上一次的位置，解出的对手跑位的位置
def isValidrunposition(runposition,vector,position1):
    if vector:  # 如果有对方跑位方向的信息，那么当结果符合跑位方向且跑位的位置没有超出范围的情况下返回True
        return runposition >= 0 and runposition <= 1000000 and ((runposition-position1)*vector > 0)
    else:       # 如果不知道跑位方向，只检验是否超出球桌范围
        return runposition >= 0 and runposition <= 1000000
