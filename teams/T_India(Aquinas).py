from table import *
import math
import copy
import random

APP_PRRORITY = [CARD_SPIN, CARD_INCL, CARD_AMPL, CARD_DECL, CARD_TLPT, CARD_DSPR]
PICK_PRIORITY = [CARD_INCL, CARD_SPIN, CARD_AMPL, CARD_DECL, CARD_TLPT, CARD_DSPR]
fac_1, fac_2, fac_3 = (1, 1, 0)
tick_step = (DIM[1] - DIM[0]) // BALL_V[0]
breadth = DIM[3]
CARD_AMPL_VALUE = 600
CARD_TLPT_VALUE = 500
CARD_DSPR_VALUE = 100
CARD_SPIN_VALUE = 500
TOOL_VALUE = {CARD_INCL: CARD_INCL_PARAM,
              CARD_DECL: CARD_DECL_PARAM,
              CARD_AMPL: CARD_AMPL_VALUE,
              CARD_TLPT: CARD_TLPT_VALUE,
              CARD_DSPR: CARD_DSPR_VALUE,
              CARD_SPIN: CARD_SPIN_VALUE,
              'NOCARD': 0}


# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve( op_side,ds: dict) -> tuple:
    tick_step = (DIM[1] - DIM[0]) // BALL_V[0]
    Vy = 3 * (DIM[3] - DIM[2]) // tick_step // 2
    return ((DIM[2] + DIM[3]) // 2, Vy)


# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
# 永远打角
def play(tb, ds):
    mid_point = breadth // 2
    # acc = to_corner(tb.ball['position'].y, tb.ball['velocity'].y, sign(mid_point - tb.op_side['position'].y))
    acc = get_acc(tb, ds)
    velocity_new = tb.ball['velocity'].y + acc
    # bounce, reflect_y = reflect_calculate(tb.ball['position'].y, velocity_new)
    bat_move = tb.ball['position'].y - tb.side['position'].y
    time = tb.tick // (2 * tick_step) + 1
    datastore = copy.copy(tb)
    datastore.side['acc'] = acc
    ds[time] = datastore
    delta_dist = positioning(tb, ds, time, acc, bat_move)
    if tb.op_side['life'] <= 27100:
        acc = to_corner(tb.ball['position'].y, tb.ball['velocity'].y, sign(mid_point - tb.op_side['position'].y))
    return RacketAction(tb.tick, bat_move, acc,
                        delta_dist, None, None)


# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick, winner, reason, west, east, ball, ds):
    return


# 输入数值，返回符号（int）
def sign(value):
    if value >= 0:
        return 1
    else:
        return -1


# 输入数值列表，返回绝对值最小的数值原值（int）
def abs_min(val_list):
    minabs = float('inf')
    if val_list:
        for val in val_list:
            if abs(val) < minabs:
                minimum = val
                minabs = abs(val)
            else:
                pass
    else:
        minimum = None
    return minimum


# 输入击球位置，速度，返回反弹数（int）
def judge_bounce(pos1, velocity):
    return abs((pos1 + velocity * tick_step) // breadth)


# 输入击球位置，速度方向，返回有效反弹数的速度区间（tuple(min,max)）
def valid_bounce(pos1, direction):
    if direction == 1:
        minimal = (breadth - pos1) / tick_step
        maximal = (3 * breadth - pos1) / tick_step
    else:
        minimal = (-2 * breadth - pos1) / tick_step
        maximal = (- pos1) / tick_step
    return int(minimal) + 1, int(maximal)


# 输入击球位置，速度，返回若对方正常反弹时的反弹数，回弹位置（tuple）
def reflect_calculate(pos1, velocity):
    reflect = pos1 + velocity * tick_step * 2
    bounce, remain = divmod(reflect, breadth)
    if bounce % 2 == 0:
        final = remain
    else:
        final = breadth - remain
    bounce1 = (pos1 + velocity * tick_step) // breadth
    return abs(bounce1), final


# 输入击球位置，速度，返回对面落点（int）
def opposite_calculate(pos1, velocity):
    position = pos1 + velocity * tick_step
    bounce, remain = divmod(position, breadth)
    if bounce % 2 == 0:
        final = remain
    else:
        final = breadth - remain
    return remain


# 输入击球位置，速度，返回达到有效反弹数的最小加速度（int）
def min_acc_valid_bounce(pos1, velocity):
    direction = sign(velocity)
    minimum, maximum = valid_bounce(pos1, direction)
    if minimum < velocity < maximum:
        acc_min = 0
    elif velocity <= minimum:
        acc_min = minimum - velocity + 1
    elif velocity >= maximum:
        acc_min = maximum - velocity - 1
    else:
        pass
    return acc_min


# 输入击球位置，道具位置，速度，返回达到有小反弹数且得到道具的加速度列表（list）
def acc_card(pos1, card_pos, velocity):
    step = card_pos.x / BALL_V[0]
    up1 = int((2 * breadth - card_pos.y - pos1) / step)
    up2 = int((2 * breadth + card_pos.y - pos1) / step)
    down1 = int((- card_pos.y - pos1) / step)
    down2 = int((- 2 * breadth + card_pos.y - pos1) / step)
    choicelist = [up1, up2, up3, up4]
    acc_list = [acc for acc in choicelist if judge_bounce(pos1, velocity + acc) in (1, 2)]
    return acc_list


# 输入击球位置，球速度，角落号，返回达到该角落的最小加速度（int）
def to_corner(pos1, velocity, corner):
    acc = None
    if corner == -1:
        temp_y = pos1 + tick_step * velocity
        acc1 = (2 * breadth - temp_y) // tick_step
        acc2 = (- temp_y) // tick_step
        acc3 = (- 2 * breadth - temp_y) // tick_step
        choice_list = [acc1, acc2 - 2, acc3 + 2]
        acc = abs_min(choice_list)
    elif corner == 1:
        temp_y = pos1 + tick_step * velocity
        acc1 = (3 * breadth - temp_y) // tick_step
        acc2 = (breadth - temp_y) // tick_step
        acc3 = (- breadth - temp_y) // tick_step
        choice_list = [acc1 - 2, acc2 + 3, acc3]
        acc = abs_min(choice_list)
    else:
        pass
    return acc


# 跑位函数，输入tb，ds，末次扣血delta_life，输出跑位位移
# 在约37000生命以上保持三分跑位，生命值低于37000以后连续跑到稳定点
def stable_positioning(tb, ds, delta_life):
    mid_point = (DIM[2] + DIM[3]) // 2
    tri_1 = (DIM[2] + DIM[3]) // 3
    tri_2 = DIM[3] - tri_1
    run_life = -(abs(tri_1)) ** 2 // FACTOR_DISTANCE ** 2
    run_life2 = -(abs(500000)) ** 2 // FACTOR_DISTANCE ** 2
    if int(((tb.side['life'] + delta_life + run_life) / RACKET_LIFE) * BALL_V[0]) * tick_step > tri_2:
        if tb.ball['position'].y < tri_1:
            destine = tri_1
        elif tb.ball['position'].y > tri_2:
            destine = tri_2
        else:
            destine = mid_point
    elif int(((tb.side['life'] + delta_life + run_life2) / RACKET_LIFE) * BALL_V[0]) * tick_step > mid_point:
        div_2 = int(((tb.side['life'] + delta_life + run_life2) / RACKET_LIFE) * BALL_V[0]) * tick_step
        div_1 = DIM[3] - div_2
        if tb.ball['position'].y > div_2:
            destine = div_2
        elif tb.ball['position'].y < div_1:
            destine = div_1
        else:
            destine = mid_point
    else:
        destine = mid_point
    movement = destine - tb.ball['position'].y
    return movement


# 跑位的强行熔断机制
def judge_validity(tb, ds, delta_life):
    run_life = -(abs(500000)) ** 2 // FACTOR_DISTANCE ** 2
    div_2 = int(((tb.side['life'] + delta_life + run_life) / RACKET_LIFE) * BALL_V[0]) * tick_step
    return div_2


# 计算一个列表中所有数值的平均值
def average(list1):
    ave = sum(list1) / len(list1)
    return ave


# 计算一个列表中所有元素的方差
def mean(list1):
    mean_sum = 0
    ave = average(list1)
    for num in list1:
        mean_sum += (num - ave) ** 2
    result = mean_sum / len(list1)
    return result


# 计算一个列表中所有元素的标准差
def root_mean_square(list1):
    mean_sum = 0
    ave = average(list1)
    for num in list1:
        mean_sum += (num - ave) ** 2
    result = math.sqrt(mean_sum / len(list1))
    return result


# 计算相邻元素差的平方和
def adjacent_judge_pos(list1):
    result = 0
    for i in range(1, len(list1)):
        result += (list1[i] - list1[i-1]) ** 2
    result /= i
    return result


# 通过统计探索对手模式，输入当前时间，历史纪录
def pattern_judgement(tick, ds):
    case_code = None
    current = tick // (2 * tick_step) + 1
    pos_list = [ds[time].ball['position'].y for time in range(current - 8, current)]
    if mean(pos_list) >= (breadth / 2) ** 2 * 0.80:
        if adjacent_judge_pos(pos_list) >= breadth ** 2 * 0.88:
            case_code = 'Opposite Corner'
        elif breadth ** 2 * 0.45 <= adjacent_judge_pos(pos_list) <= breadth ** 2 * 0.65:
            case_code = 'Random Corner'
    elif mean(pos_list) <= (breadth / 2) ** 2 * 0.20:
        if average(pos_list) >= breadth * 17 // 20 or average(pos_list) <= breadth * 3 // 20:
            case_code = 'Original Corner'
    pos_list2 = [reflect_calculate(ds[time-1].ball['position'].y, ds[time-1].ball['velocity'].y + ds[time-1].side['acc'])[1]
                 for time in range(current - 8, current)]
    sub_list = [pos_list[i] - pos_list2[i] for i in range(len(pos_list))]
    if mean(sub_list) <= 90000 ** 2:
        case_code = 'Small Acceleration'
    return case_code


# 输入对手模式，tb，ds，加速度，击球位移，输出跑位
def pattern_positioning(pattern, tb, ds, acc, bat_move):
    mid_point = breadth // 2
    delta_life_acc = -(abs(acc) ** 2 // FACTOR_SPEED ** 2) * \
                     (CARD_AMPL_PARAM if tb.op_side['active_card'][1] == CARD_AMPL else 1)
    delta_life_bat = -(abs(bat_move) ** 2 // FACTOR_DISTANCE ** 2) * \
                     (CARD_AMPL_PARAM if tb.op_side['active_card'][1] == CARD_AMPL else 1)
    delta_life = delta_life_acc + delta_life_bat
    if pattern == 'Opposite Corner':
        target = mid_point
        delta_dist = target - tb.ball['position'].y
    elif pattern == 'Random Corner':
        div1 = breadth // 4
        div2 = breadth - div1
        if tb.ball['position'].y > div2:
            target = div2
        elif tb.ball['position'].y < div1:
            target = div1
        else:
            target = (2 * tb.ball['position'].y + mid_point) // 3
        delta_dist = target - tb.ball['position'].y
    elif pattern == 'Original Corner':
        target = (4 * tb.ball['position'].y + mid_point) // 5
        delta_dist = target - tb.ball['position'].y
    elif pattern == 'Small Acceleration':
        reflect_pos = reflect_calculate(tb.ball['position'].y, tb.ball['velocity'].y + acc)[1]
        target = (reflect_pos + tb.ball['position'].y) // 2
        delta_dist = target - tb.ball['position'].y
    if pattern is not None:
        max_move = judge_validity(tb, ds, delta_life)
        target = delta_dist + tb.ball['position'].y
        max_needed = max(target, breadth - target)
        if max_needed > max_move:
            delta_dist = stable_positioning(tb, ds, delta_life)
        else:
            pass
    else:
        delta_dist = stable_positioning(tb, ds, delta_life)
    return delta_dist


# 汇总跑位函数，在play中直接调用
def positioning(tb, ds, time, acc, bat_move):
    if time == 1:
        ds[time].side['pattern_code'] = None
    elif (time - 3) % 7 == 0 and time > 7:
        ds[time].side['pattern_code'] = pattern_judgement(tb.tick, ds)
    else:
        ds[time].side['pattern_code'] = ds[time - 1].side['pattern_code']
    pattern_code = ds[time].side['pattern_code']
    delta_dist = pattern_positioning(pattern_code, tb, ds, acc, bat_move)
    return delta_dist


# 按照使用优先级考虑使用道具，输入tb，ds，输出使用对象、道具（tuple）
def apply_card(tb, ds):
    for card in APP_PRRORITY:
        if card in tb.side['cards']:
            if card == CARD_INCL and tb.side['life'] < RACKET_LIFE - CARD_INCL_PARAM:
                return tb.side, card
            elif card == CARD_DECL or card == CARD_AMPL or card == CARD_SPIN:
                return tb.op_side, card
            elif card == CARD_TLPT or card == CARD_DSPR:
                return tb.side, card
    return None, None


# 判断一个速度是否能得到道具
def get_card(pos, velocity, card, eps=2000):
    A1 = (velocity * (-card.pos.x) + BALL_V[0] * (card.pos.y - pos))
    A2 = (velocity * (-card.pos.x) + BALL_V[0] * (-card.pos.y - pos))
    delta = (2 * abs(BALL_V[0]) * breadth)
    return min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(
        BALL_V[0] ** 2 + velocity ** 2) < eps


# 估值函数
def evaluate(tb, ds, acc):
    mid_point = breadth // 2
    time = tb.tick // (2 * tick_step) + 1
    lost = (abs(acc) ** 2 // FACTOR_SPEED ** 2) * \
           (CARD_AMPL_PARAM if tb.op_side['active_card'][1] == CARD_AMPL else 1)
    acceleration = acc * (CARD_SPIN_PARAM if tb.op_side['active_card'][1] == CARD_SPIN else 1)
    oppo_position = opposite_calculate(tb.ball['position'].y, tb.ball['velocity'].y + acceleration)
    if time > 1:
        distance = oppo_position - ds[time - 1].op_side['position'].y
    else:
        distance = oppo_position - mid_point
    op_lost_min = 2 * (abs(distance // 2) ** 2 // FACTOR_DISTANCE ** 2)
    sum_value = fac_1 * op_lost_min - fac_2 * lost
    return sum_value


def get_acc(tb, ds):
    min_up, max_up = valid_bounce(tb.ball['position'].y, 1)
    min_down, max_down = valid_bounce(tb.ball['position'].y, -1)
    acc_min_up, acc_max_up = min_up - tb.ball['velocity'].y, max_up - tb.ball['velocity'].y
    acc_min_down, acc_max_down = min_down - tb.ball['velocity'].y, max_down - tb.ball['velocity'].y
    if tb.op_side['active_card'][1] == CARD_SPIN:
        acc_min_up = acc_min_up * 2 + 1
        acc_max_up = acc_max_up * 2 - 1
        acc_min_down = acc_min_down * 2 + 1
        acc_max_down = acc_max_down * 2 - 1
        choice_up = None
        choice_up_value = float('-inf')
        for acceleration in range(acc_min_up, acc_max_up, 20):
            value = evaluate(tb, ds, acceleration)
            if value > choice_up_value:
                choice_up_value, choice_up = value, acceleration
        choice_down = None
        choice_down_value = float('-inf')
        for acceleration in range(acc_min_down, acc_max_down, 20):
            value = evaluate(tb, ds, acceleration)
            if value > choice_down_value:
                choice_down_value, choice_down = value, acceleration
        choice, val = (choice_up, choice_up_value) if choice_up_value > choice_down_value else \
            (choice_down, choice_down_value)
        return choice
    else:
        choice_up = None
        choice_up_value = float('-inf')
        for acceleration in range(acc_min_up, acc_max_up, 20):
            value = evaluate(tb, ds, acceleration)
            if value > choice_up_value:
                choice_up_value, choice_up = value, acceleration
        choice_down = None
        choice_down_value = float('-inf')
        for acceleration in range(acc_min_down, acc_max_down, 20):
            value = evaluate(tb, ds, acceleration)
            if value > choice_down_value:
                choice_down_value, choice_down = value, acceleration
        choice, val = (choice_up, choice_up_value) if choice_up_value > choice_down_value else (choice_down, choice_down_value)
        return choice


# 计算能够捡到的道具和对应的加速值
def hit_cards(tb, ds):
    retVys = []
    cards = [card.code for card in tb.cards['cards']]  # cards is list of string
    velocity = tb.ball['velocity'].y
    for card_name in PICK_PRIORITY:
        if card_name in cards:
            for card in tb.cards['cards']:
                if card.code == card_name:
                    pos = card.pos  # Vector
                    step = abs(pos.x) / BALL_V[0]
                    retVys.append((card_name, (pos.y - tb.ball['position'].y) / step - velocity))
                    retVys.append((card_name, (DIM[3] - tb.ball['position'].y + DIM[3] - pos.y) / step - velocity))
                    retVys.append((card_name,(DIM[3] - tb.ball['position'].y + DIM[3] - DIM[2] + pos.y - DIM[2]) / step - velocity))
                    retVys.append((card_name, (-1) * (tb.ball['position'].y - DIM[2] + pos.y - DIM[2]) / step - velocity))
                    retVys.append((card_name,(-1) * (tb.ball['position'].y - DIM[2] + DIM[3] - DIM[2] + DIM[3] - pos.y) / step - velocity))
    return retVys
