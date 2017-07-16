# coding=utf-8
from table import *
import operator
# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side, ds):
    return 200000, BALL_V[1]

def addCase(acc,case,run_dirc,b,cards):
    self_life = (abs(acc)**2 // FACTOR_SPEED**2)
    hit_cards = [card for card in cards if b.get_card(card)]
    case.append([acc, self_life,run_dirc,hit_cards])

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
# tick, tick_step, side, op_side, ball
#self.tick, self.tick_step,dict_side, dict_op_side, dict_ball, dict_card,player.datastore
def play(tb, ds):
    # （加速值，加速自身所消耗的体力值，对方跑位方向，hit_card）
    case = []

    # 迎球
    distance = tb.ball['position'].y - tb.side['position'].y

    # 跑位－>场地中间位置
    run = DIM[3] // 2 - tb.ball['position'].y

    # 使用card 策略是 只要有card 就使用
    card = None
    while len(tb.side['cards']) > 0:
        card = tb.side['cards'].pop()
        card = card.code
        # 但是如果有 加血包就晚点使用
        if card == CARD_INCL and tb.side['life'] > RACKET_LIFE - CARD_INCL_PARAM:
            card = None
            break
        else:
            break

    # 加速因子
    spin=1
    # 如果对方使用旋转球 那么加速转球
    if tb.op_side['active_card'][1]==CARD_SPIN:
        spin=2

    # 变压因子
    ampl = 1
    # 如果对方使用变压器 那么考虑加倍掉体力值
    if tb.op_side['active_card'][1]==CARD_AMPL:
        ampl=2

    # 瞬移因子
    tlpt=0
    if card== CARD_TLPT:  # 如果碰到瞬移卡，则从距离减去CARD_TLPT_PARAM再计算体力值减少
        tlpt = CARD_TLPT_PARAM

    b = Ball(DIM, copy.copy(tb.ball['position']), copy.copy(tb.ball['velocity']))
    b.bounce_racket()

    # 目标：对方向上死角
    # 1 弹一下_先上弹
    acc = (DIM[3] - tb.ball['position'].y) // tb.step + 1 - tb.ball['velocity'].y
    b.update_velocity(acc, (None, None))
    addCase(acc*spin, case,tb.op_side['run_vector'],b,tb.cards['cards'])
    b.update_velocity(-acc, (None, None))
    # 2 弹一下_先下弹
    acc = (-DIM[3] - tb.ball['position'].y) // tb.step + 1 - tb.ball['velocity'].y
    b.update_velocity(acc, (None, None))
    addCase(acc*spin, case,tb.op_side['run_vector'],b,tb.cards['cards'])
    b.update_velocity(-acc, (None, None))
    # 3 弹两下_先上弹
    acc = (3 * DIM[3] - tb.ball['position'].y) // tb.step - 1 - tb.ball['velocity'].y
    b.update_velocity(acc, (None, None))
    addCase(acc*spin, case,tb.op_side['run_vector'],b,tb.cards['cards'])
    b.update_velocity(-acc, (None, None))
    # 4 弹两下_先下弹
    acc = (-DIM[3] - tb.ball['position'].y) // tb.step - 1 - tb.ball['velocity'].y
    b.update_velocity(acc, (None, None))
    addCase(acc*spin, case,tb.op_side['run_vector'],b,tb.cards['cards'])
    b.update_velocity(-acc, (None, None))

    # 目标：对方向下死角
    # 5 弹一下_先上弹
    acc = (2 * DIM[3] - tb.ball['position'].y) // tb.step - 1 - tb.ball['velocity'].y
    b.update_velocity(acc, (None, None))
    addCase(acc*spin, case,tb.op_side['run_vector'],b,tb.cards['cards'])
    b.update_velocity(-acc, (None, None))
    # 6 弹一下_先下弹
    acc = (- tb.ball['position'].y) // tb.step - 1 - tb.ball['velocity'].y
    b.update_velocity(acc, (None, None))
    addCase(acc*spin, case,tb.op_side['run_vector'],b,tb.cards['cards'])
    b.update_velocity(-acc, (None, None))
    # 7 弹两下_先上弹
    acc = (2 * DIM[3] - tb.ball['position'].y) // tb.step + 1 - tb.ball['velocity'].y
    b.update_velocity(acc, (None, None))
    addCase(acc*spin, case,tb.op_side['run_vector'],b,tb.cards['cards'])
    b.update_velocity(-acc, (None, None))
    # 8 弹两下_先下弹
    acc = (-2 * DIM[3] - tb.ball['position'].y) // tb.step + 1 - tb.ball['velocity'].y
    b.update_velocity(acc, (None, None))
    addCase(acc*spin, case,tb.op_side['run_vector'],b,tb.cards['cards'])
    b.update_velocity(-acc, (None, None))


    # distance是迎球（受变压器影响） run是跑位（受瞬移因子影响）
    life= (abs(distance) ** 2 // FACTOR_DISTANCE ** 2) * ampl \
          +(max(abs(run)-tlpt,0)) ** 2 // FACTOR_DISTANCE ** 2

    # 因为之前的case中只是考虑了旋转球的因素
    i = 0
    while i < len(case):
        case[i][1] = case[i][1] * ampl + life
        i += 1

    # 当有优势的时候（自身life值 大于 对方life值）
    # (加速值，加速自身所消耗的体力值，对方跑位方向，hit_card）
    if tb.side['life']>tb.op_side['life']:

        # 按自身消耗体力的大小排序
        order_case=sorted(case,key=operator.itemgetter(1))
        # 过滤掉 自身所消耗的体力值>自身目前拥有的体力值 的情况
        order_case=filter(lambda x: x[1] < tb.side['life'], order_case)
        order_case=list(order_case)
        # def comp(x,y):
        #     if len(x[3])>len(y[3]):
        #         return -1
        #     elif len(x[3])<len(y[3]):
        #         return 1
        #     else:
        #         # 加血包权值最重
        #         if CARD_INCL in x:
        #             return -1
        #         elif CARD_INCL in y:
        #             return 1
        #         else:
        #             return 0
        flt_case1=filter(lambda x:x[3]!=[] ,order_case)
        flt_case1 = sorted(flt_case1,key=lambda x:len(x[3]))
        flt_case1 = list(flt_case1)
        # 过滤掉 自身所消耗的体力值-对方消耗的体力值>自身目前拥有的体力值－对方目前拥有的体力值 的情况
        # flt_case2=filter(lambda x: x[1]-x[2]<=tb.side['life']-tb.op_side['life'], order_case)

        if flt_case1:

            return RacketAction(tb.tick, distance, flt_case1[0][0], run,None,card)
        elif order_case:
            return RacketAction(tb.tick, distance, order_case[0][0], run,None,card)
        # 采取保守进攻
        else:
            pass

    # 模拟不给加速度 球是否会按要求传递过去
    count_bounce, hit_cards = b.fly(tb.step, tb.cards['cards'])
    # 模拟结果发现 ：没有在墙上反弹
    if count_bounce <1:
        # 使用case1和case6
        # 选择体力值消耗少的case，若消耗相等，看得到的hitbox
        if case[0][1]>case[5][1]:
            ans=case[5][0]
        elif case[0][1]<case[5][1]:
            ans=case[0][0]
        else:
            if len(case[0][3])>len(case[5][3]):
                ans=case[0][0]
            elif len(case[0][3])<len(case[5][3]):
                ans=case[5][0]
            else:
                if case[0][2]>0:
                    ans=case[5][0]
                else:
                    ans=case[0][0]
        return RacketAction(tb.tick, distance, ans, run,None,card)
    # 模拟结果发现 ：反弹次数太多
    elif count_bounce >2:
        if tb.ball['velocity'].y>0:
            # 使用case3
            return RacketAction(tb.tick, distance, case[2][0], run,None,card)
        else:
            # 使用case8
            return RacketAction(tb.tick,distance,  case[2][0], run,None,card)
    # 模拟结果发现 ：反弹次数符合要求，那么保守进攻不提供加速度
    else:
        return RacketAction(tb.tick, distance, 0, run,None,card)

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
#def summarize(tick, winner, reason, west, east, ball, ds):
    return
