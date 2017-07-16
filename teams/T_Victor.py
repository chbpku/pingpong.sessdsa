# 按照预测一次的方法回球
#添加了道具——DYC
#按照老师的table中的方法判断了是否合规——ZXL
#修改了跑位！！——DYC


from table import *
import random
import math

global pos_dict, roundround_op
pos_dict = {1: 1000000, 2: 990000, 3: 980000, 4: 800000, 5: 700000, 6: 500000, 7: 300000, 8: 100000}
roundround_op = int()

# 每个单边的tick数
TICK_PER_TURN = 1800


# 获取一个合法的速度区间——XGY
def get_legal_velocity(pos):
    max_d1 = 3 * DIM[3] - pos  # 如果所有球都直接正向打过去最大位移
    min_d1 = DIM[3] - pos  # 最小位移
    max_v1 = math.floor(max_d1 / TICK_PER_TURN)  # 最大速度
    min_v1 = math.floor(min_d1 / TICK_PER_TURN) + 1  # 最小速度
    vrange1 = (min_v1, max_v1)

    max_d2 = 2 * DIM[3] + pos  # 球的速度为反向时
    min_d2 = pos
    max_v2 = math.floor(- max_d2 / TICK_PER_TURN) + 1
    min_v2 = math.floor(- min_d2 / TICK_PER_TURN)
    vrange2 = (max_v2, min_v2)  # 速度直接取范围
    vrange = (vrange1, vrange2)
    return vrange


# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
# 给发球函数加入了简单的学习功能--DYC
# 每次换对手都更新数据
def serve(op_side, ds):
    global pos_dict, name_opside, last_opside, roundround_op, serve_pos, islastwin, last_pos  # 为了和summarize中同步，全部都要global！！
    print(pos_dict)

    try:
        if last_opside != op_side:  # 如果换了对手（last_opside上一盘的对手，op_side这一盘的对手）
            name_opside = op_side  # 本局的对手
            pos_dict = {1: 1000000, 2: 990000, 3: 980000, 4: 800000, 5: 700000, 6: 500000, 7: 300000,
                        8: 100000}  # 发球位置字典回到初始状态
            serve_pos = 1000000  # 开始默认的发球位置是计算出的最好位置
            roundround_op = 0  # 总共赢了的局数
        else:
            name_opside = op_side  # 如果没换对手，上一次赢了就用上一次的发球位置
            if islastwin:
                serve_pos = last_pos
            else:
                # print('round number before choose',roundround_op)
                # 如果上一次没有赢，就从剩下的位置里面随机选择
                choose_pos = random.choice(list(pos_dict.keys()))
                serve_pos = pos_dict[choose_pos]
    except:  # 如果出错了的话，比如这是所有比赛的第一局，或者因为一直输字典已经删空了
        name_opside = op_side
        serve_pos = 1000000

    pos = serve_pos  # 得到发球位置之后和原来一样计算发球速度
    v_ranges = get_legal_velocity(pos)
    vmin, vmax = v_ranges[0]
    for v_postive in range(vmin, vmax):  # 直接取正向速度，否则发球速度损耗过大
        velocity_HP_consume = (v_postive - 1000) ** 2 / FACTOR_SPEED ** 2  # 我方改变速度消耗
        presume_op_pos, presume_op_v = Presume_ball_Status(pos, v_postive)
        op_HP_consume = (presume_op_pos - 500000) ** 2 / FACTOR_DISTANCE ** 2  # 对方跑位消耗
        difference = op_HP_consume - velocity_HP_consume
        diff_max = 0
        if difference > diff_max:
            diff_max = difference
            v_max = v_postive  # v_max keeps record of v that gives maximum difference
    return pos, v_max


# 推测在某地点，按照某速度把球打出，到达对方的位置还有速度——XGY
def Presume_ball_Status(cur_ball_pos, cur_ball_v):
    if cur_ball_v > 0:  # 速度方向为正向时
        distance = cur_ball_v * TICK_PER_TURN
        if (distance + cur_ball_pos - 2 * DIM[3]) < 0:  # 只反弹一次
            presume_pos = 2 * DIM[3] - cur_ball_pos - distance  # DIM[3] - [distance - (DIM[3] - cur_ball_pos)]
            presume_v = -cur_ball_v
        else:  # 反弹两次
            presume_pos = distance + cur_ball_pos - 2 * DIM[3]
            presume_v = cur_ball_v

    else:  # 速度方向为负时
        distance = abs(cur_ball_v) * TICK_PER_TURN  # 速度取正，求总位移
        if (distance - cur_ball_pos - DIM[3]) < 0:  # 只反弹一次
            presume_pos = distance - cur_ball_pos
            presume_v = -cur_ball_v
        else:  # 反弹两次
            presume_pos = 2 * DIM[3] - distance + cur_ball_pos  # DIM[3] - (distance - DIM[3] - cur_ball_pos)
            presume_v = cur_ball_v

    presume_ball = (presume_pos, presume_v)
    return presume_ball


# 求得该位置下和改球速下，回球的速度--XGY
######这里我改了！！！！加入了是否要捡道具的判断的调用——DYC
def velocity_range(tb: TableData, ds: dict):
    ball_op_pos = tb.op_side.get('position').y  # 对方在t0时刻的位置
    ball_pos = tb.ball.get('position').y  # 对方球y方向到达本方的位置
    ball_velocity = tb.ball.get('velocity').y  # 对方球y方向到达本方的速度

    Vranges = get_legal_velocity(ball_pos)
    vranges_postitve, vranges_negative = Vranges  # 获得击球时的返回球合法速度，分为正向，反向
    v_pos_min, v_pos_max = vranges_postitve
    v_neg_min, v_neg_max = vranges_negative
    diff_max = 0  # maximum difference of HP
    Found_one = False
    for v in range(v_pos_min, v_pos_max):  # 在所有合法速度范围内一个一个取值
        prsum_pos, prsum_velocity = Presume_ball_Status(ball_pos, v)
        v_vector = v - ball_velocity  # 速度矢量改变
        op_minHP_consume = (prsum_pos - ball_op_pos) ** 2 / FACTOR_DISTANCE ** 2  # 此时对手最小消耗
        us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
        difference = op_minHP_consume - us_HP_consume
        if Found_one == False:
            diff_max = difference
            v_max = v
            Found_one = True
        else:
            if difference > diff_max:
                Found_one = True
                diff_max = difference
                v_max = v  # v_max keeps record of v that gives maximum difference

    for v in range(v_neg_min, v_neg_max):  # 在所有合法速度范围内一个一个取值
        prsum_pos, prsum_velocity = Presume_ball_Status(ball_pos, v)
        v_vector = v - ball_velocity  # 速度矢量改变
        op_minHP_consume = (prsum_pos - ball_op_pos) ** 2 / FACTOR_DISTANCE ** 2  # 此时对手最小消耗
        us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
        difference = op_minHP_consume - us_HP_consume
        if Found_one == False:
            diff_max = difference
            v_max = v
            Found_one = True
        else:
            if difference > diff_max:
                Found_one = True
                diff_max = difference
                v_max = v  # v_max keeps record of v that gives maximum difference

    k = cardsornot(ball_op_pos, ball_pos, ball_velocity, tb, diff_max)  # 判断现在是否应该放弃原策略，改用捡道具策略
    if k == False:  # 如果判断没道具可见或者捡道具不如原计划，就原计划执行
        v_fin = v_max
    else:  # 否则的话就改速度捡道具
        v_fin = k
        print(tb.side['name'], 'hahaha I try to get card!')

    return Vector(0, v_fin - ball_velocity)


# 得到旋转球之后，计算如何操作可以使得对方被旋转球杀死。即如何回球使得对方必须改变速度
# 原本写来用于发球——XGY
# 在XGY之前写的上面做了补充--DYC
def calc_velocity(ball_pos, ball_velocity):  # 球在我们这边的位置还有y方向的速度
    v_ranges = get_legal_velocity(ball_pos)  # 每一个初始位置算出回球球速度范围
    Vrange1, Vrange2 = v_ranges
    vmin, vmax = Vrange1  # 正向回球的速度范围
    vmin2, vmax2 = Vrange2  # 反向回球的速度范围
    found_one = False  # 还没找到需要对方改变速度的方法
    min_usHP = int()  # 我们的最小消耗
    v_fin = int()  # 最小消耗时候的速度

    for v in range(vmin, vmax):  # 正向发球时，在所有发球速度范围内取值
        presume_pos, presume_v = Presume_ball_Status(ball_pos, v)  # 获得打到对方的位置和速度（都是y方向）
        if presume_pos < DIM[3]-10 and presume_pos>DIM[2]+10:
            Y = presume_v * TICK_PER_TURN + presume_pos  # Y是没有墙壁时到达的位置
            if Y % DIM[3] != 0:  # case1：未在边界
                count = abs(Y // DIM[3])  # 穿过了多少次墙（可以是负的，最后取绝对值）
            else:  # case2： 恰好在边界

                # 两种情形：a） 向上穿墙，穿了1 - Y // self.extent[3] 次（代入Y = 0验证）
                #           b） 向下穿墙，穿了 Y // self.extent[3] 次（代入Y = self.extent[3] 验证）
                # 无论怎样，实际位置要么在0，要么在self.extent[3]。直接模( 2 * self.extent[3] )即可。
                # 速度只和count奇偶有关，同上。
                #count = 1
                count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])

            if count not in (1,2):
                v_vector = v - ball_velocity  # 速度矢量改变
                us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
                if found_one == False:
                    v_fin = v
                    min_usHP = us_HP_consume

                else:
                    if us_HP_consume < min_usHP:
                        v_fin = v
                        min_usHP = us_HP_consume
                found_one=True



    for v in range(vmin2, vmax2):  # 反向回球时，在所有发球速度范围内取值
        presume_pos, presume_v = Presume_ball_Status(ball_pos, v)  # 获得打到对方的位置和速度（都是y方向）
        if presume_pos < DIM[3] - 10 and presume_pos > DIM[2] + 10:
            Y = presume_v * TICK_PER_TURN + presume_pos  # Y是没有墙壁时到达的位置
            if Y % DIM[3] != 0:  # case1：未在边界
                count = abs(Y // DIM[3])  # 穿过了多少次墙（可以是负的，最后取绝对值）
            else:  # case2： 恰好在边界

                # 两种情形：a） 向上穿墙，穿了1 - Y // self.extent[3] 次（代入Y = 0验证）
                #           b） 向下穿墙，穿了 Y // self.extent[3] 次（代入Y = self.extent[3] 验证）
                # 无论怎样，实际位置要么在0，要么在self.extent[3]。直接模( 2 * self.extent[3] )即可。
                # 速度只和count奇偶有关，同上。
                # count = 1
                count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])

            if count not in (1, 2):
                v_vector = v - ball_velocity  # 速度矢量改变
                us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
                if found_one == False:
                    v_fin = v
                    min_usHP = us_HP_consume

                else:
                    if us_HP_consume < min_usHP:
                        v_fin = v
                        min_usHP = us_HP_consume
                found_one = True

    if not found_one:  # 如果没找到合适的就算了，返回None
        return None
    else:  # 找到了让对方必须换速度的速度，就返回这个速度把对方打死

        print(v_fin)
        presume_pos, presume_v = Presume_ball_Status(ball_pos, v_fin)  # 获得打到对方的位置和速度（都是y方向）
        print('到对方',presume_v,'到对方位置',presume_pos)
        v_prsum_ranges = get_legal_velocity(presume_pos)  # 对方回击时返回球速的范围
        print(v_prsum_ranges)
        return (0, v_fin - ball_velocity)


# 计算捡道具的最大真是能耗
def caldiff(tb, eachcode):  # 这里面要返回的是符合合理速度范围的能耗差最大的那一种方法，###特别特别要注意的是，如果在符合速度范围的条件里没有能够捡到该道具的方式，回复None！！
    op_pos = tb.op_side.get('position').y  # 对方在t0时刻的位置#################修改了名字
    current_pos = tb.ball.get('position').y  # 对方球y方向到达本方的位置
    current_pos_x = tb.ball.get('position').x
    current_v = tb.ball.get('velocity').y  # 对方球y方向到达本方的速度
    pos_x = eachcode.pos.x  # 道具的x坐标
    pos_y_1 = eachcode.pos.y  # 反弹之前就捡到道具的y坐标
    pos_y_2 = 2 * DIM[3] - pos_y_1  # 反弹一次等效的道具y坐标
    pos_y_3 = 2 * DIM[3] + pos_y_1  # 反弹两次等效的道具y坐标
    pos_y_4 = -pos_y_1  # 反向时，反弹一次
    pos_y_5 = pos_y_1 - 2 * DIM[3]  # 反向时反弹两次
    v_ranges = get_legal_velocity(current_pos)  # 该位置的合法速度范围
    Vrange1, Vrange2 = v_ranges
    vmin, vmax = Vrange1  # 正向回球的速度范围
    vmin2, vmax2 = Vrange2  # 反向回球的速度范围
    found_one = False  ###################添加了这个
    diff_max = int()

    expec_v_1 = (pos_y_1 - current_pos) / abs(pos_x - current_pos_x) * 1000
    expec_v_2 = (pos_y_2 - current_pos) / abs(pos_x - current_pos_x) * 1000  # 通过两个坐标值，速度之比等于位移之比计算速度
    expec_v_3 = (pos_y_3 - current_pos) / abs(pos_x - current_pos_x) * 1000
    expec_v_4 = (pos_y_4 - current_pos) / abs(pos_x - current_pos_x) * 1000
    expec_v_5 = (pos_y_5 - current_pos) / abs(pos_x - current_pos_x) * 1000

    if expec_v_1 > vmin and expec_v_1 < vmax:  # 判断该速度合法
        prsum_pos, prsum_v = Presume_ball_Status(current_pos, expec_v_1)  # 获取到达对方的球的位置
        v_vector = expec_v_1 - current_v  # 我方速度矢量改变
        op_minHP_consume = (prsum_pos - op_pos) ** 2 / FACTOR_DISTANCE ** 2  # 此时对手最小消耗
        us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
        difference = op_minHP_consume - us_HP_consume
        if found_one == False:
            diff_max = difference
            v_max = expec_v_1
        else:
            if difference > diff_max:
                diff_max = difference
                v_max = expec_v_1  # v_max keeps record of v that gives maximum difference
        found_one = True

    if expec_v_2 > vmin and expec_v_2 < vmax:  # 计算反弹一次捡到道具的情况
        prsum_pos, prsum_v = Presume_ball_Status(current_pos, expec_v_2)
        v_vector = expec_v_2 - current_v  # 速度矢量改变
        op_minHP_consume = (prsum_pos - op_pos) ** 2 / FACTOR_DISTANCE ** 2  # 此时对手最小消耗
        us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
        difference = op_minHP_consume - us_HP_consume
        if found_one == False:
            diff_max = difference
            v_max = expec_v_2
        else:
            if difference > diff_max:
                diff_max = difference
                v_max = expec_v_2  # v_max keeps record of v that gives maximum difference
        found_one = True

        # 前两次都捡不到时,计算反弹两次捡到道具的情况
    if expec_v_3 > vmin and expec_v_3 < vmax:
        prsum_pos, prsum_v = Presume_ball_Status(current_pos, expec_v_3)
        v_vector = expec_v_3 - current_v  # 速度矢量改变
        op_minHP_consume = (prsum_pos - op_pos) ** 2 / FACTOR_DISTANCE ** 2  # 此时对手最小消耗
        us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
        difference = op_minHP_consume - us_HP_consume
        if found_one == False:
            diff_max = difference
            v_max = expec_v_3
        else:
            if difference > diff_max:
                diff_max = difference
                v_max = expec_v_3  # v_max keeps record of v that gives maximum difference
        found_one = True

    if expec_v_1 > vmin2 and expec_v_1 < vmax2:  # 判断该速度合法
        prsum_pos, prsum_v = Presume_ball_Status(current_pos, expec_v_1)
        v_vector = expec_v_1 - current_v  # 速度矢量改变
        op_minHP_consume = (prsum_pos - op_pos) ** 2 / FACTOR_DISTANCE ** 2  # 此时对手最小消耗
        us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
        difference = op_minHP_consume - us_HP_consume
        if found_one == False:
            diff_max = difference
            v_max = expec_v_1
        else:
            if difference > diff_max:
                diff_max = difference
                v_max = expec_v_1  # v_max keeps record of v that gives maximum difference
        found_one = True

    if expec_v_4 > vmin2 and expec_v_4 < vmax2:  # 计算反弹一次捡到道具的情况
        prsum_pos, prsum_v = Presume_ball_Status(current_pos, expec_v_4)
        v_vector = expec_v_4 - current_v  # 速度矢量改变
        op_minHP_consume = (prsum_pos - op_pos) ** 2 / FACTOR_DISTANCE ** 2  # 此时对手最小消耗
        us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
        difference = op_minHP_consume - us_HP_consume
        if found_one == False:
            diff_max = difference
            v_max = expec_v_4
        else:
            if difference > diff_max:
                diff_max = difference
                v_max = expec_v_4  # v_max keeps record of v that gives maximum difference
        found_one = True

        # 前两次都捡不到时,计算反弹两次捡到道具的情况
    if expec_v_5 > vmin2 and expec_v_5 < vmax2:
        prsum_pos, prsum_v = Presume_ball_Status(current_pos, expec_v_5)
        v_vector = expec_v_5 - current_v  # 速度矢量改变
        op_minHP_consume = (prsum_pos - op_pos) ** 2 / FACTOR_DISTANCE ** 2  # 此时对手最小消耗
        us_HP_consume = v_vector ** 2 / FACTOR_SPEED ** 2  # 我方消耗
        difference = op_minHP_consume - us_HP_consume
        if found_one == False:
            diff_max = difference
            v_max = expec_v_5
        else:
            if difference > diff_max:
                diff_max = difference
                v_max = expec_v_5  # v_max keeps record of v that gives maximum difference
        found_one = True

    if found_one:  # 如果有可以返回的合法速度
        return (v_max, diff_max)
    else:
        return None  # 速度不合法时，返回NONE


# 判断此时要不要捡道具，给道具评分，分数由实际的能耗差+有用程度组成，在velocity_range函数中被调用
def cardsornot(op_position, ball_pos, ball_velocity, tb: TableData, diff_max1):
    cards = tb.cards.get('cards')  # 得到目前桌面上的cards的列表，这是一个列表！！！
    found_one = False  # 开始假设没找到任何可能捡的道具
    thiscodename = str()  # 遍历时当前道具的名称
    fin_codename = str()  # 遍历结束后，选定额道具的名称
    diff_max2 = int()  # 遍历结束后，选定道具的最后得分（实际能耗差+有用程度）
    for eachcard in cards:  # 开始遍历
        if eachcard.code == 'IL' or eachcard.code == 'DL' or eachcard.code == 'SP'or eachcard.code=='AM' or eachcard.code=='DS' or eachcard.code=='TP':  # 只有补血包，掉血包和旋转球是我们想捡的，其余的碰到了用了
            calculate_card = caldiff(tb, eachcard)  # 捡这个道具的实际最大能耗差（能耗差为对方能耗减我方能耗）和对应的速度-形式：（速度，能耗差）

            if calculate_card != None:  # 如果速度合法范围内可以捡到某道具,返回捡该道具的能耗差最大值
                realdiff = calculate_card[1]

                if eachcard.code == 'IL' or eachcard.code == 'DL':  # 如果是掉血或者补血包，然后就是作比较
                    diff_in_mind = realdiff + 1000  # 得分（也就是在心目中的分量哈哈哈哈）
                    thiscodename = eachcard.code
                    if not found_one:
                        diff_max2 = diff_in_mind
                        fin_codename = thiscodename
                        v_card = calculate_card[0]  # 对应的速度
                    else:
                        if diff_in_mind > diff_max2:
                            diff_max2 = diff_in_mind
                            fin_codename = thiscodename
                            v_card = calculate_card[0]

                else:
                    if eachcard.code == 'SP':  # 如果是旋转球，反正还是作比较，就是得分的计算不同
                        diff_in_mind = realdiff + 1800
                        thiscodename = eachcard.code
                        if not found_one:
                            diff_max2 = diff_in_mind
                            fin_codename = thiscodename
                            v_card = calculate_card[0]
                        else:
                            if diff_in_mind > diff_max2:
                                diff_max2 = diff_in_mind
                                fin_codename = thiscodename
                                v_card = calculate_card[0]
                    else:
                        if eachcard.code=='AM':#如果是变压器
                            diff_in_mind = realdiff + 500
                            thiscodename = eachcard.code
                            if not found_one:
                                diff_max2 = diff_in_mind
                                fin_codename = thiscodename
                                v_card = calculate_card[0]
                            else:
                                if diff_in_mind > diff_max2:
                                    diff_max2 = diff_in_mind
                                    fin_codename = thiscodename
                                    v_card = calculate_card[0]
                        else:
                            if eachcard.code=='DS'or'TP':
                                diff_in_mind = realdiff + 100
                                thiscodename = eachcard.code
                                if not found_one:
                                    diff_max2 = diff_in_mind
                                    fin_codename = thiscodename
                                    v_card = calculate_card[0]
                                else:
                                    if diff_in_mind > diff_max2:
                                        diff_max2 = diff_in_mind
                                        fin_codename = thiscodename
                                        v_card = calculate_card[0]





                found_one = True

    if found_one:  # 如果找到了捡道具的速度并且得分比我们按照原来策略打对手的得分高的话,就返回那个速度了，没找到或者得分不如按照原计划就返回False
        if diff_max2 >= diff_max1:
            print('codename:', fin_codename)
            return v_card
        else:
            return False

    else:
        return False

def usingcards(tb:TableData,ds:dict):
    ball_pos = tb.ball.get('position').y  # 对方球y方向到达本方的位置
    ball_velocity = tb.ball.get('velocity').y  # 对方球y方向到达本方的速度
    acc_vector = velocity_range(tb, ds)  # 我们需要改变球的速度，矢量
    cardlist = tb.side['cards']
    print(tb.side['name'], 'mycardlist', cardlist)
    if len(cardlist) != 0:#如果有卡片的话
        print('cardlist0', cardlist[0].code)#就检查的时候看一眼用了啥道具
        if cardlist[0].code == 'SP':#如果最上面的一层道具是旋转球
            let_them_die = calc_velocity(ball_pos, ball_velocity)#得到让对方死掉的速度方法
            print(str(let_them_die))
            if let_them_die != None:#如果确实找到了这种方法
                print('letthemdie')
                acc_vector = Vector(let_them_die[0],let_them_die[1])#改变acc_vector到这种方法
                card_to_use=cardlist[0]
                side_to_use=tb.op_side['name']
            else:#如果没有找到这种方法
                card_to_use=None
                side_to_use=None
        else:
            if cardlist[0].code =='DS':
                card_to_use=cardlist[0]
                side_to_use=tb.side['name']
            if cardlist[0].code=='IL':
                card_to_use=cardlist[0]
                side_to_use=tb.side['name']
            if cardlist[0].code=='DL':
                card_to_use = cardlist[0]
                side_to_use = tb.op_side['name']
            if cardlist[0].code=='TP':
                card_to_use = cardlist[0]
                side_to_use=tb.side['name']
            if cardlist[0].code=='AM':
                card_to_use = cardlist[0]
                side_to_use = tb.op_side['name']
    else:
        return (acc_vector,None,None)
    #print('card_to_use',card_to_use.code,'side to use',side_to_use)
    return (acc_vector,side_to_use,card_to_use)









# 打球函数
def play(tb: TableData, ds: dict):
    print("playplayplay!!!@@@")
    print('life_newnewserve', tb.side.get('life'))
    ball_op_pos = tb.op_side.get('position')
    print('op position(means new)',ball_op_pos)
    ball_op_vector = tb.op_side.get('run_vector')
    # print('op vector',ball_op_vector)
    ball_pos = tb.ball.get('position').y  # 对方球y方向到达本方的位置
    print("ball position from new", tb.ball.get('position'), ball_pos)
    ball_velocity = tb.ball.get('velocity').y  # 对方球y方向到达本方的速度
    # print('ball v',tb.ball.get('velocity'),ball_velocity)
    racket_pos = tb.side.get('position').y  # 我方位置
    bat_vector = Vector(0, ball_pos - racket_pos)  # 预计到达位置和我方现在位置的差距,也就是t0和t1之间迎球时候移动的矢量
    acc_vector,cardside,whatcard=usingcards(tb,ds)
    v_vector = acc_vector.y  # 我们需要改变球的速度的y方向分量
    us_HP_consume_vector = v_vector ** 2 / FACTOR_SPEED ** 2  # 我们用于改变速度的体能消耗
    us_HP_consume_pos = (ball_pos - racket_pos) ** 2 / FACTOR_DISTANCE ** 2#我们用于接球的移动消耗

    bat_velocity = int(
        ((tb.side.get('life') - us_HP_consume_pos - us_HP_consume_vector) / RACKET_LIFE) * BALL_V[0])  # 球拍的全速，是整数形式int

    # 接下来考虑t1到t2之间分跑位，分成两种大情况讨论
    # 第一种是在一轮的时间内剩余体力值对应的球拍速度可以确保我们在球来之前到离目前球拍最位置最远的边。此时说明体力还够，采用迷惑策略。
    # 第二种是球拍无法按时达到最远点（即有可能一次移动接不到球），此时要向中间移动，或者向能够到最远点的位置移动，两者取最近，此时不采用迷惑策略，保存体力

    runrange_max = abs(TICK_PER_TURN * bat_velocity)  # 球拍全速移动在t1到t2或从t2到t3可以走的最远距离

    south_max = ball_pos - DIM[2]  # 离南边的最远距离
    north_max = DIM[3] - ball_pos  # 离北边的最远距离
    direction_max = 'south'  # 判断离哪边最远
    if north_max > south_max:
        needrun_max = north_max
        direction_max = 'north'
    else:
        needrun_max = south_max

    if needrun_max < runrange_max:  # 如果体力值足够，球拍可以按时到达

        if ball_pos > (DIM[2] + DIM[3]) / 2:  # 如果我们在北半边，假装往南移动一格
            run_vector = Vector(0, -0.2*(ball_pos - (DIM[2] + DIM[3]) / 2))
        else:  # 在南边，就不用动了，对方会以为我们向北移动了
            run_vector = Vector(0, -0.2*(ball_pos - (DIM[2] + DIM[3]) / 2))
    else:  # 不足以到达，需要补位的时候进行提前移动
        if needrun_max == runrange_max:  # 刚好够，不移动
            run_vector = Vector(0, 0)
        else:  # 不够，需要移动
            us_HP_consume_runmax = ((DIM[2] + DIM[3]) / 2 - ball_pos) ** 2 / FACTOR_DISTANCE ** 2  # 我们最大的用于跑位的消耗
            bat_velocity = int(
                ((tb.side.get('life') - us_HP_consume_pos - us_HP_consume_vector-us_HP_consume_runmax) / RACKET_LIFE) * BALL_V[
                    0])  # 球拍的全速，是整数形式int
            runrange_max = abs(TICK_PER_TURN * bat_velocity)  # 球拍全速移动在t1到t2或从t2到t3可以走的最远距离

            if needrun_max - runrange_max < needrun_max - (DIM[3] - DIM[2]) / 2:  # 移动使得等对方回球后，我方在t1到t2时间内可以够到全场所有的位置
                if runrange_max > needrun_max - runrange_max:
                    if direction_max == 'north':
                        run_vector = Vector(0, needrun_max - runrange_max)
                    else:
                        run_vector = Vector(0, runrange_max - needrun_max)
                else:
                    run_vector = Vector(0, 0)  # 如果这也跑不到就听天由命不动了
            else:  # 如果上一种移动方法会使得球超过中点，则适得其反，移动使得球在中点
                if runrange_max > needrun_max - (DIM[3] - DIM[2]) / 2:
                    run_vector = Vector(0, (DIM[2] + DIM[3]) / 2 - ball_pos)
                else:
                    run_vector = Vector(0, 0)



    return RacketAction(tb.tick, str(int(bat_vector.y)), str(int(acc_vector.y)), str(int(run_vector.y)), cardside,
                        whatcard)


# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
# 为发球的学习功能做辅助——DYC
def summarize(tick, winner, reason, west, east, ball, ds):
    global pos_dict, name_opside, last_opside, roundround_op, serve_pos, islastwin, last_pos
    try:
        last_opside = name_opside
        last_pos = serve_pos
        if winner == 'West':
            pos_dict[roundround_op + 9] = serve_pos
            islastwin = True
            roundround_op += 1
            print('roundnumber after win', roundround_op)
        else:
            try:
                thenumber = list(pos_dict.keys())[list(pos_dict.values()).index(serve_pos)]
                pos_dict.pop(thenumber)
                islastwin = False
                print('roundnumber after lose', roundround_op)

            except:
                islastwin = False
    except:
        return

    return
