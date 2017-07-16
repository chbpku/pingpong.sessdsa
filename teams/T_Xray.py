from table import RacketAction,Card,Table, LogEntry, RacketData, BallData, TableData,DIM, TMAX, PL, RS,BALL_V,BALL_POS
import random

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度

def serve(op_side: str, ds: dict) -> tuple:
    # 发球往对方边角处发
    return BALL_POS[1], 278

# 基本的加速策略--打向对方相反边角
def accbase(tb):

    # 对方位置靠近上边角
    if tb.op_side['position'].y > 900000:
        # 球速为正
        if tb.ball['velocity'].y > 0:
            edgeV11 = ((2000000 - tb.ball['position'].y) / 1800) + 1
            acc = edgeV11 - tb.ball['velocity'].y
        # 球速为负
        else:
            edgeV21 = ((tb.ball['position'].y) / 1800) + 1
            edgeV22 = ((2000000 + tb.ball['position'].y) / 1800) - 1
            acc21 = abs(-edgeV21 - tb.ball['velocity'].y)
            acc22 = abs(-edgeV22 - tb.ball['velocity'].y)
            # 取最小值
            if acc21 < acc22:
                acc = -edgeV21 - tb.ball['velocity'].y
            else:
                acc = -edgeV22 - tb.ball['velocity'].y
    # 对方位置靠近下边角
    elif tb.op_side['position'].y < 100000:
        # 球速为正
        if tb.ball['velocity'].y > 0:
            edgeV31 = ((1000000 - tb.ball['position'].y) / 1800) + 1
            edgeV32 = ((3000000 - tb.ball['position'].y) / 1800) - 1
            acc31 = abs(edgeV31 - tb.ball['velocity'].y)
            acc32 = abs(edgeV32 - tb.ball['velocity'].y)
            # 取最小值
            if acc31 < acc32:
                acc = edgeV31 - tb.ball['velocity'].y
            else:
                acc = edgeV32 - tb.ball['velocity'].y
        # 球速为负
        else:
            edgeV41 = ((1000000 + tb.ball['position'].y) / 1800) + 1
            acc = -edgeV41 - tb.ball['velocity'].y
    # 对方位置靠近中间
    else:
        # 球速为正
        if tb.ball['velocity'].y > 0:
            edgeV11 = ((2000000 - tb.ball['position'].y) / 1800) + 1
            edgeV12 = ((1000000 - tb.ball['position'].y) / 1800) + 1
            edgeV13 = ((3000000 - tb.ball['position'].y) / 1800) - 1
            acc1 = abs(edgeV11 - tb.ball['velocity'].y)
            acc2 = abs(edgeV12 - tb.ball['velocity'].y)
            acc3 = abs(edgeV13 - tb.ball['velocity'].y)
            # 取最小值
            if acc1 == min(acc1, acc2, acc3):
                acc = edgeV11 - tb.ball['velocity'].y
            elif acc2 == min(acc1, acc2, acc3):
                acc = edgeV12 - tb.ball['velocity'].y
            else:
                acc = edgeV13 - tb.ball['velocity'].y
        # 球速为负
        else:
            edgeV21 = ((tb.ball['position'].y) / 1800) + 1
            edgeV22 = ((1000000 + tb.ball['position'].y) / 1800) + 1
            edgeV23 = ((2000000 + tb.ball['position'].y) / 1800) - 1
            acc1 = abs(-edgeV21 - tb.ball['velocity'].y)
            acc2 = abs(-edgeV22 - tb.ball['velocity'].y)
            acc3 = abs(-edgeV23 - tb.ball['velocity'].y)
            # 取最小值
            if acc1 == min(acc1, acc2, acc3):
                acc = -edgeV21 - tb.ball['velocity'].y
            elif acc2 == min(acc1, acc2, acc3):
                acc = -edgeV22 - tb.ball['velocity'].y
            else:
                acc = -edgeV23 - tb.ball['velocity'].y
    return acc

# 计算击打卡牌所需的加速度，并估算各种情况的收益值，取最优的收益值
def profit(tb,card):

    # 正常打球的加速度
    acc = accbase(tb)

    # 预估卡牌的价值
    if card == 'IL'or card == 'DL' :
        cardvalue = 2000
    elif card == 'AM':
        cardvalue = 625
    elif card == 'TP':
        cardvalue = 160
    elif card == 'SP':
        cardvalue = 100
    else:
        cardvalue =1

    # 记录计算所需的位置参数
    cardy = card.pos.y
    cardx = card.pos.x
    bally = tb.ball['position'].y
    ballx = tb.ball['position'].x

    # 对函数中的变量进行初始化
    acc1 = 0
    acc2 = 0
    acc3 = 0
    profit1 =0
    profit21 = 0
    profit22 = 0
    profit2 = 0
    profit3 = 0
    profit31 = 0
    profit32 = 0
    acc21 = 0
    acc31 = 0
    acc32 = 0


    k01 = (bally - 1000000) / (2 * ballx)
    k02 = bally / (2 * ballx)
    k03 = (bally + 2000000) / (2 * ballx)
    k04 = (bally - 3000000) / (2 * ballx)
    if (cardy > k03 * (cardx - ballx) + bally and cardy < k04 * (cardx - ballx) + bally):

        # 直接打道具的情况
        k1 = ((cardy - bally) / (cardx - ballx))
        #分情况计算加速度和收益值
        if cardy > k01 * (cardx - ballx) + bally or cardy < k02 * (cardx - ballx) + bally:
            vy1 = (k1 * (-2) * (ballx)) / 1800
            acc1 = vy1 - tb.ball['velocity'].y
            y1 = bally - 2 * k1 * ballx
            if y1 < 0:
                y1 = (-1) * y1
            else:
                y1 = 2000000 - y1
            muchcost1 = (acc1 / 20) ** 2 - (acc / 20) ** 2 + (625 - ((500000 - y1) / 20000) ** 2) * 2
            profit1 = cardvalue - muchcost1
        else:
            profit1 = -1000000
            acc1 = 0

        # 第一次反弹后的路径中打到道具
        k21 = ((cardy + bally) / (ballx - cardx))
        vy21 = (k21 * (-2) * (ballx)) / 1800
        k22 = ((cardy + bally - 2000000) / (ballx - cardx))
        vy22 = (k22 * (-2) * (ballx)) / 1800
        profit2 = -1000000
        acc2 = 0
        #分情况计算加速度和收益值
        if (ballx > 0 and k21 < k03) or (ballx < 0 and k21 > k03):
            acc21 = vy21 - tb.ball['velocity'].y
            y21 = 2 * k21 * ballx - bally
            muchcost21 = (acc21 / 20) ** 2 - (acc / 20) ** 2 + (625 - ((500000 - y21) / 20000) ** 2) * 2
            profit21 = cardvalue - muchcost21
            k21 = 0
        if (ballx > 0 and k22 > k04) or (ballx < 0 and k22 < k04):
            acc22 = vy22 - tb.ball['velocity'].y
            y22 = - 2 * k22 * ballx + bally - 2000000
            muchcost22 = (acc22 / 20) ** 2 - (acc / 20) ** 2 + (625 - ((500000 - y22) / 20000) ** 2) * 2
            profit22 = cardvalue - muchcost22
            k22 = 0
        if k21 == 0 and k22 == 0:
            profit21 == max(profit21, profit22)
            profit2 = profit21
            acc2 = acc21
        if k21 == 0 and k22 != 0:
            profit2 = profit21
            acc2 = acc21
        if k22 == 0 and k21 != 0:
            profit2 = profit22
            acc2 = acc22

        # 第二次反弹后的路径中打到道具
        k31 = ((2000000 - cardy + bally) / (ballx - cardx))
        vy31 = (k31 * (-2) * (ballx)) / 1800
        k32 = ((- cardy + bally - 2000000) / (ballx - cardx))
        vy32 = (k32 * (-2) * (ballx)) / 1800
        profit3 = -1000000
        acc3 = 0
        #分情况计算加速度和收益值
        if (ballx > 0 and k31 < k03) or (ballx < 0 and k31 > k03):
            acc31 = vy31 - tb.ball['velocity'].y
            y31 = - 2 * k31 * ballx + bally + 2000000
            muchcost31 = (acc31 / 20) ** 2 - (acc / 20) ** 2 + (625 - ((500000 - y31) / 20000) ** 2) * 2
            profit31 = cardvalue - muchcost31
            k31 = 0
        if (ballx > 0 and k32 > k04) or (ballx < 0 and k32 < k04):
            acc32 = vy32 - tb.ball['velocity'].y
            y32 = - 2 * k32 * ballx + bally - 2000000
            muchcost32 = (acc32 / 20) ** 2 - (acc / 20) ** 2 + (625 - ((500000 - y32) / 20000) ** 2) * 2
            profit32 = cardvalue - muchcost32
            k32 = 0

        if k31 == 0 and k32 == 0:
            profit31 == max(profit31, profit32)
            profit3 = profit31
            acc3 = acc31
        if k31 == 0 and k32 != 0:
            profit3 = profit31
            acc3 = acc31
        if k32 == 0 and k31 != 0:
            profit3 = profit32
            acc3 = acc32
        k01 = 1

    # 返回最大收益的收益值及加速度
    if k01 != 1:
        return -1000000, 0
    else:
        if profit1 == max(profit1, profit2, profit3):
            return profit1, acc1
        elif profit2 == max(profit1, profit2, profit3):
            return profit2, acc2
        else:
            return profit3, acc3
        
# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
# play 函数
def play(tb: TableData, ds: dict) -> RacketAction:
    # 一个回合内球的运动时间--固定不变
    tick_time = tb.step
    # ds信息记录
    if tb.tick == 1800 or tb.tick == 0:
        ds['oplife'] = [tb.op_side['life']]
        ds['oprun'] = [tb.op_side['run_vector']]
        ds['ballyofpos'] = [tb.ball['position'].y]

    else:
        ds['oplife'].append(tb.op_side['life'])
        ds['oprun'].append(tb.op_side['run_vector'])
        ds['ballyofpos'].append(tb.ball['position'].y)

    # 将我方所有可以打到的卡牌存储到一个列表cardables中
    # 参数初始化
    cardables = []
    cardy = 0
    cardx = 0
    bally = 0
    ballx = 0
    for card in  tb.cards['cards'] :
        cardy = card.pos.y
        cardx = card.pos.x
        bally = tb.ball['position'].y
        ballx = tb.ball['position'].x
        # 判断可以击打到的卡牌
        if cardy < ((bally - 3000000)/(2*ballx))*(cardx - ballx) + bally and cardy > ((bally + 2000000)/(2*ballx))*(cardx - ballx) + bally:
            cardables.append(card)

    # 对于cardables 里面的卡牌进行优先级排序,返回一个优先级排好序的列表
    # 列表初始化
    cardfirstlist = []
    cardsecondlist = []
    cardthirdlist = []
    cardforcelist = []
    cardfifthlist = []
    cardorders = []
    for cardable in cardables:
        if cardable == 'IL'or cardable == 'DL' :
            cardfirstlist.append(cardable)
        elif cardable == 'AM':
            cardsecondlist.append(cardable)
        elif cardable == 'SP':
            cardforcelist.append(cardable)
        elif cardable == 'TP':
            cardthirdlist.append(cardable)

    cardorders = cardfirstlist + cardsecondlist + cardthirdlist + cardforcelist + cardfifthlist

    # 迎球策略以及卡牌使用策略
    # 初始化参数
    cardside = None
    cardbeused = None
    acc = 0
    if len(cardorders) > 0 :
        # 调用收益值估算函数，得出收益值
        profitcrad = profit(tb, cardorders[0])[0]
        # 若收益值为正，击打卡牌
        if profitcrad > 0:
            acc = profit(tb, cardorders[0])[1]
        # 收益值为负，正常迎球
        else:
           acc = accbase(tb)
    # 如果可打卡牌列表为空，正常迎球
    else:
      acc = accbase(tb)

    # 跑位策略
    #  基于ds的存储数据， 如果对方两次连续向我方同一边角打，选择不跑位;否则，向中间位置跑位。
    if len(ds['ballyofpos']) > 1:
        # 连续两次打向下边角
        if ds['ballyofpos'][len(ds['ballyofpos']) - 1] < 100000 and ds['ballyofpos'][
                    len(ds['ballyofpos']) - 2] <100000  :
            run = 0
        # 连续两次打向上边角
        elif ds['ballyofpos'][len(ds['ballyofpos']) - 1] > 900000 and ds['ballyofpos'][
                len(ds['ballyofpos']) - 2] > 900000  :
            run = 0
        # 其他情况
        else:
            run = 500000 - tb.ball['position'].y
    else:
        run = 500000 - tb.ball['position'].y

    # 卡牌使用，获得卡牌立即使用
    if len(tb.side['cards']) > 0:
        carduse = tb.side['cards'][0]
        if carduse == 'IL' or carduse == 'TP' or carduse == 'DS':
            cardside = tb.side
            cardbeused = carduse
        elif carduse == 'DL' or carduse == 'SP' or carduse == 'AM':
            cardside = tb.op_side
            cardbeused = carduse
        else:
            cardside = None
            cardbeused = None
    else:
        cardside = None
        cardbeused = None

    # 卡牌应对策略
    # 若对方对我使出旋转球；其余卡牌暂时无法应对
    accend = 0
    if tb.op_side['active_card'][1] != None:
        # 若对方对我方使出旋转球
        if tb.op_side['active_card'][1] == 'SP':
            ballvy = tb.ball['velocity'].y
            # 球速为正方向时，
            if ballvy > 0:
                y1max = 3000000 - tb.ball['position'].y
                y1min = 1000000 - tb.ball['position'].y
                # 如果直接回球不非法撞击，取最小加速度0，令其直接反弹
                if ballvy * 1800 < y1max and ballvy * 1800 > y1min :
                    accend = 1
                # 不能直接反弹，计算得出最小的加速度，令其加倍反弹
                else:
                    # 存储各种可能加速度的列表
                    acclist1 =[]
                    for vi1 in range(int(y1min/1800) + 1 , int(y1max / 1800)):
                        acclist1.append(abs(vi1 - ballvy))
                    # 找到绝对值最小的加速度
                    accending1 = min(acclist1)* 2 + 1
                    if ballvy * 1800 <= y1min:
                        accend = accending1
                    else:
                        accend = - accending1
            # 球速为负方向时，
            else:
                y2max = 2000000 + tb.ball['position'].y
                y2min = tb.ball['position'].y
                # 如果直接回球不非法撞击，取最小加速度0，令其直接反弹
                if ballvy *(-1800) < y2max  and  ballvy * (-1800) > y2min:
                    accend = 1
                # 不能直接反弹，计算得出最小的加速度，令其加倍反弹
                else:
                    # 存储各种可能加速度的列表
                    acclist2 = []
                    for vi2 in range(int(y2min / 1800)+ 1, int(y2max / 1800)):
                        acclist2.append(abs(- vi2 - ballvy))
                    accending2 = (min(acclist2))* 2 + 1
                    # 找到绝对值最小的加速度
                    if ballvy * (-1800) <=  y2min:
                        accend = -accending2
                    else:
                        accend = accending2
        # 对方使出的卡牌不是旋转球，暂不应对
        else:
            accend = acc
    # 对方未使用卡牌
    else:
        accend = acc

    # 单独处理接发球的函数，获得最小加速度
    if tb.tick == 1800:
        # 球速为正
        if tb.ball['velocity'].y > 0:
            edgeV11 = ((2000000 - tb.ball['position'].y) / 1800) + 1
            edgeV12 = ((1000000 - tb.ball['position'].y) / 1800) + 1
            edgeV13 = ((3000000 - tb.ball['position'].y) / 1800) - 1
            acc1 = abs(edgeV11 - tb.ball['velocity'].y)
            acc2 = abs(edgeV12 - tb.ball['velocity'].y)
            acc3 = abs(edgeV13 - tb.ball['velocity'].y)
            # 得到最小加速度
            if acc1 == min(acc1, acc2, acc3):
                acc = edgeV11 - tb.ball['velocity'].y
            elif acc2 == min(acc1, acc2, acc3):
                acc = edgeV12 - tb.ball['velocity'].y
            else:
                acc = edgeV13 - tb.ball['velocity'].y
        # 球速为负
        else:
            edgeV21 = ((tb.ball['position'].y) / 1800) + 1
            edgeV22 = ((1000000 + tb.ball['position'].y) / 1800) + 1
            edgeV23 = ((2000000 + tb.ball['position'].y) / 1800) - 1
            acc1 = abs(-edgeV21 - tb.ball['velocity'].y)
            acc2 = abs(-edgeV22 - tb.ball['velocity'].y)
            acc3 = abs(-edgeV23 - tb.ball['velocity'].y)
            # 得到最小加速度
            if acc1 == min(acc1, acc2, acc3):
                acc = -edgeV21 - tb.ball['velocity'].y
            elif acc2 == min(acc1, acc2, acc3):
                acc = -edgeV22 - tb.ball['velocity'].y
            else:
                acc = -edgeV23 - tb.ball['velocity'].y
        accended = acc
    # 不是接发球状态
    else:
        accended = accend

    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, accended, run ,cardside, cardbeused )

# 这个函数由于时间和能力的限制没有具体使用
def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return
