from table import *
import random
'''
以下这些参数代表将位置，速度，加速度等空间分成若干份，
实现离散化，以便于作统计上的分析
'''
POSD = 20  # 0-19
XD = 20  # -10-9
VD = 20  # -10-9
AD = 20  # -10-9
LIFED = 6  # 0-5
DIRECTIOND = 2

# 下面至506左右，为处理和分析ds的代码
def myrandom():
    x = random.randint(0, 1)
    return -1 if x == 0 else x


# 以下函数用于将连续变量离散化
def posToInt(pos):
    return int(pos // int(1000000 // POSD))


def xToInt(x):
    return int(x // int(1000000 // (XD // 2)))


def vToInt(v):
    return int(v // int(3000 // (VD // 2)))  # 300 per unit


def aToInt(a):
    if a >= 0:
        if a > 1000:
            return 10
        else:
            return a // 100
    elif a < 0:
        if a < -1000:
            return -11
        else:
            return a // 100
            # 300 per unit a \in -3000-3000


def lifeToInt(life):
    return 1 if life > 55000 else -1


def product(values):
    result = 1
    for x in values:
        result *= x
    return result


class Data:
    def __init__(self):
        # 生成字典记录频数
        # 以下部分均是不同状态下频数的记录。采用嵌套的字典来记录它们。
        self.data = {
            # 对方的跑位
            # 球速
            ('ballv', 'run'): {(m, n): 0 for m in range(-VD // 2, VD // 2 + 1, 1) for n in
                               range(-XD // 2, XD // 2 + 1, 1)},
            # 位置
            ('pos', 'run'): {(m, n): 0 for m in range(POSD + 1) for n in range(-XD // 2, XD // 2 + 1, 1)},
            # 对方的位置
            ('op_pos', 'run'): {(m, n): 0 for m in range(POSD + 1) for n in range(-XD // 2, XD // 2 + 1, 1)},
            # 己方的生命值
            ('life', 'run'): {(m, n): 0 for m in (-1, 1) for n in range(-XD // 2, XD // 2 + 1, 1)},
            # 对方的生命值
            ('op_life', 'run'): {(m, n): 0 for m in (-1, 1) for n in range(-XD // 2, XD // 2 + 1, 1)},
            # 方向
            ('direction', 'run'): {(m, n): 0 for m in (-1, 1) for n in range(-XD // 2, XD // 2 + 1, 1)},
            ('run_itself', 'run'): {(1, n): 0 for n in range(-XD // 2, XD // 2 + 1, 1)},
            # 对方的球的落点
            ('ballv', 'placement'): {(m, n): 0 for m in range(-VD // 2, VD // 2 + 1, 1) for n in range(POSD + 1)},
            ('pos', 'placement'): {(m, n): 0 for m in range(POSD + 1) for n in range(POSD + 1)},
            ('op_pos', 'placement'): {(m, n): 0 for m in range(POSD + 1) for n in range(POSD + 1)},
            ('life', 'placement'): {(m, n): 0 for m in (-1, 1) for n in range(POSD + 1)},
            ('op_life', 'placement'): {(m, n): 0 for m in (-1, 1) for n in range(POSD + 1)},
            ('direction', 'placement'): {(m, n): 0 for m in (-1, 1) for n in range(POSD + 1)},
            ('placement_itself', 'placement'): {(1, n): 0 for n in range(POSD + 1)},
            # 对方的球的加速度
            ('ballv', 'acc'): {(m, n): 0 for m in range(-VD // 2, VD // 2 + 1, 1) for n in
                               range(-AD // 2 - 1, AD // 2 + 1, 1)},
            ('pos', 'acc'): {(m, n): 0 for m in range(POSD + 1) for n in range(-AD // 2 - 1, AD // 2 + 1, 1)},
            ('op_pos', 'acc'): {(m, n): 0 for m in range(POSD + 1) for n in range(-AD // 2 - 1, AD // 2 + 1, 1)},
            ('life', 'acc'): {(m, n): 0 for m in (-1, 1) for n in range(-AD // 2 - 1, AD // 2 + 1, 1)},
            ('op_life', 'acc'): {(m, n): 0 for m in (-1, 1) for n in range(-AD // 2 - 1, AD // 2 + 1, 1)},
            ('direction', 'acc'): {(m, n): 0 for m in (-1, 1) for n in range(-AD // 2 - 1, AD // 2 + 1, 1)},
            ('acc_itself', 'acc'): {(1, n): 0 for n in range(-AD // 2 - 1, AD // 2 + 1, 1)},
            # 对方跑位后跑到的位置
            ('ballv', 'run_placement'): {(m, n): 0 for m in range(-VD // 2, VD // 2 + 1, 1) for n in range(POSD + 1)},
            ('pos', 'run_placement'): {(m, n): 0 for m in range(POSD + 1) for n in range(POSD + 1)},
            ('op_pos', 'run_placement'): {(m, n): 0 for m in range(POSD + 1) for n in range(POSD + 1)},
            ('life', 'run_placement'): {(m, n): 0 for m in (-1, 1) for n in range(POSD + 1)},
            ('op_life', 'run_placement'): {(m, n): 0 for m in (-1, 1) for n in range(POSD + 1)},
            ('direction', 'run_placement'): {(m, n): 0 for m in (-1, 1) for n in range(POSD + 1)},
            ('run_placement_itself', 'run_placement'): {(1, n): 0 for n in range(POSD + 1)}}
        # 这里的 direction 是我方跑位的方向。加速度方向影响应该不大，故而暂时不考虑。
        # 这里是 x, a 本身的频率

    # 用于更新频数的记录。每一个回合调用一次。更新跑位的频数
    def update_run(self, r_ballv, r_pos, r_op_pos, r_life, r_op_life, direction, r_run):
        # 这个字典用于方便下面的迭代的实现。
        dict = {'pos': posToInt(r_pos),
                'op_pos': posToInt(r_op_pos),
                'life': lifeToInt(r_life),
                'op_life': lifeToInt(r_op_life),
                'ballv': vToInt(r_ballv),
                'direction': direction,
                'run_itself': 1}
        # 转换为离散的值
        run = xToInt(r_run)
        # 在字典中迭代，计数增加1
        for key in dict:
            if dict[key] != None:
                self.data[(key, 'run')][(dict[key], run)] += 1
        return
    # 更新落点的频数。以下均为不同类型频数的更新函数。
    def update_placement(self, r_ballv, r_pos, r_op_pos, r_life, r_op_life, direction, r_placement):
        dict = {'pos': posToInt(r_pos),
                'op_pos': posToInt(r_op_pos),
                'life': lifeToInt(r_life),
                'op_life': lifeToInt(r_op_life),
                'ballv': vToInt(r_ballv),
                'direction': direction,
                'placement_itself': 1}
        placement = posToInt(r_placement)
        # 隐身术导致的None
        for key in dict:
            self.data[(key, 'placement')][(dict[key], placement)] += 1
        return
    # 加速度频数的更新
    def update_acc(self, r_ballv, r_pos, r_op_pos, r_life, r_op_life, direction, r_acc):
        dict = {'pos': posToInt(r_pos),
                'op_pos': posToInt(r_op_pos),
                'life': lifeToInt(r_life),
                'op_life': lifeToInt(r_op_life),
                'ballv': vToInt(r_ballv),
                'direction': direction,
                'acc_itself': 1}
        acc = aToInt(r_acc)
        # 隐身术导致的None
        for key in dict:
            # print(key)
            # print(self.data[(key,'acc')])
            self.data[(key, 'acc')][(dict[key], acc)] += 1
        return
    # 跑位位置频数的更新。
    def update_run_placement(self, r_ballv, r_pos, r_op_pos, r_life, r_op_life, direction, r_run_placement):
        dict = {'pos': posToInt(r_pos),
                'op_pos': posToInt(r_op_pos),
                'life': lifeToInt(r_life),
                'op_life': lifeToInt(r_op_life),
                'ballv': vToInt(r_ballv),
                'direction': direction,
                'run_placement_itself': 1}
        run_placement = posToInt(r_run_placement)
        # 隐身术导致的None
        for key in dict:
            self.data[(key, 'run_placement')][(dict[key], run_placement)] += 1
        return


def leighton(tb, ds):  # 计算上个回合对方的跑位 action.run 和 对方的迎球 action.bat
    last_tb = ds['last_tb']  # 获得上一回合的信息
    op_active_card = last_tb.op_side['active_card'][1]  # 对方上回合所用的道具
    active_card = ds['last_return'][2]  # 我方上次所用的道具
    op_distance = tb.op_side['position'].y - last_tb.op_side['position'].y  # 对方跑位、迎球的总距离（实际距离）
    # 求对方设置的球的加速值
    # 1.计算对方加速前速度，即last_bounced_vy
    last_side_acced_vy = last_tb.ball['velocity'].y + ds['last_return'][0] \
                                                      * (CARD_SPIN_PARAM if op_active_card == CARD_SPIN else 1)
    Y1 = last_side_acced_vy * tb.step + last_tb.ball['position'].y
    if Y1 % DIM[3] != 0:
        count = Y1 // DIM[3]
        last_bounced_vy = last_side_acced_vy * ((count + 1) % 2 * 2 - 1)
    else:
        count = (Y1 // DIM[3]) if (Y1 > 0) else (1 - Y1 // DIM[3])
        last_bounced_vy = last_side_acced_vy * ((count + 1) % 2 * 2 - 1)
    # 2.计算对方加速后速度，即last_opside_acced_vy
    Y2 = - tb.ball['velocity'].y * tb.step + tb.ball['position'].y
    if Y2 % DIM[3] != 0:
        count = Y2 // DIM[3]
        last_opside_acced_vy = tb.ball['velocity'].y * ((count + 1) % 2 * 2 - 1)
    else:
        count = (Y2 // DIM[3]) if (Y2 > 0) else (1 - Y2 // DIM[3])
        last_opside_acced_vy = - tb.ball['velocity'].y * ((count + 1) % 2 * 2 - 1)
    acc_vector = (last_opside_acced_vy - last_bounced_vy) \
                 * (2 if active_card == CARD_SPIN else 1)
    # 求球的（实际）加速（对方设置加速+我方道具影响）
    acc_vector_real = last_opside_acced_vy - last_bounced_vy
    if op_active_card == CARD_TLPT:  # 对方使用瞬移术
        return (None, None, acc_vector_real)
    # 0 求上回合对方生命值的减少量（因为加速、跑位、迎球的减少量）
    life_reduce = last_tb.op_side['life'] - tb.op_side['life']
    if active_card == CARD_DECL:  # 若我方给对方掉血
        life_reduce -= CARD_DECL_PARAM
    if tb.op_side['active_card'][1] == CARD_INCL:  # 若对方自己加血
        life_reduce += CARD_INCL_PARAM
    # 1 求上回合对方给球加速减少的生命值
    if active_card is None:
        life_reduce1 = (abs(acc_vector) ** 2 // FACTOR_SPEED ** 2)
    else:
        life_reduce1 = (abs(acc_vector) ** 2 // FACTOR_SPEED ** 2) * \
                       (CARD_AMPL_PARAM if active_card == CARD_AMPL else 1)

    # 2 求上回合对方跑位、迎球减少的生命值
    life_reduce2 = life_reduce - life_reduce1
    life_reduce2 += 1  # 防止取整误差导致复数解
    # 3 具体求出跑位、迎球
    if active_card == CARD_AMPL:  # 我方使用变压器
        delta = 12 * life_reduce2 * (FACTOR_DISTANCE ** 2) - 8 * (op_distance ** 2)
        x1 = op_distance / 3 * 2 + (delta ** 0.5) / 6
        x2 = op_distance / 3 * 2 - (delta ** 0.5) / 6
        if isinstance(x1, complex):
            return None, None, acc_vector_real
        else:
            x1, x2 = int(x1), int(x2)
            if abs(x1) >= 1000000 or abs(x2) >= 1000000:
                return None, None, acc_vector_real
            if op_distance ** 2 > life_reduce2 * (FACTOR_DISTANCE ** 2):  # 如果方向相同
                return (x1, x2, acc_vector_real) \
                    if abs(x1) < abs(x2) else (x2, x1, acc_vector_real)
            elif op_active_card != CARD_DSPR and min(abs(x1), abs(x2)) > 10000:  # 如果对方上一局没用隐身术:
                return (x1, x2, acc_vector_real) \
                    if last_tb.op_side['run_vector'] > 0 else (x2, x1, acc_vector_real)
            else:
                return (x1, x2, acc_vector_real) \
                    if abs(x1) < abs(x2) else (x2, x1, acc_vector_real)
    else:  # 啥道具都没有，美滋滋
        delta = 8 * life_reduce2 * (FACTOR_DISTANCE ** 2) - 4 * (op_distance ** 2)
        x1 = op_distance / 2 + (delta ** 0.5) / 4
        x2 = op_distance / 2 - (delta ** 0.5) / 4
        if isinstance(x1, complex):
            return None, None, acc_vector_real
        else:
            x1, x2 = int(x1), int(x2)
            if op_distance ** 2 > life_reduce2 * (FACTOR_DISTANCE ** 2):  # 如果方向相同
                return (x1, x2, acc_vector_real) \
                    if abs(x1) < abs(x2) else (x2, x1, acc_vector_real)
            elif op_active_card != CARD_DSPR and min(abs(x1), abs(x2)) > 10000:  # 如果对方上一局用了隐身术
                return (x1, x2, acc_vector_real) \
                    if last_tb.op_side['run_vector'] > 0 else (x2, x1, acc_vector_real)
            else:
                return (x1, x2, acc_vector_real) \
                    if abs(x1) < abs(x2) else (x2, x1, acc_vector_real)


# 根据己方这回合有的tb和储存的ds，推算出下回合对方迎球时接收到的tb数据
def newtb(tb, acc, run, cardaction):
    Y = int(tb.ball['velocity'].y + acc) * tb.step + tb.ball['position'].y
    count = Y // DIM[3]
    op_pos_y = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
    dict_side = {
        'name': tb.op_side['name'],
        'position': tb.op_side['position'],  # 跑位前的位置
        'life': tb.op_side['life'],  # 有些许偏差
        'cards': tb.op_side['cards']}
    dict_op_side = {
        'name': tb.side['name'],
        'position': Position(tb.side['position'].x, tb.ball['position'].y),
        'life': tb.side['life'],  # 有些许偏差
        'cards': tb.side['cards'],
        'active_card': cardaction,
        'accelerate': myrandom() if cardaction == CARD_DSPR else
        (-1 if acc < 0 else 1),
        'run_vector': myrandom() if cardaction == CARD_DSPR else
        (-1 if run < 0 else 1)}
    dict_ball = {
        'position': Position(tb.op_side['position'].x, op_pos_y),
        'velocity': Vector(-tb.ball['velocity'].x, (tb.ball['velocity'].y + acc) * (1 - 2 * (count % 2)))}
    dict_card = {
        'card_tick': tb.cards['card_tick'],
        'cards': tb.cards['cards']}  # 由于产生新的道具，会有误差
    # 调用，返回迎球方的动作
    return TableData(tb.tick, tb.step, dict_side, dict_op_side, dict_ball, dict_card)


# 调用此函数更新新的数据，更新完之后再计算本回合预测概率。注意最后要添加一个direction作为自己这回合的跑位方向进去。
# ds的结构：字典中有两个键值对，一个是'lala_tb'，记录的是我方上上个回合看到的桌面信息，用于计算对方决策跑位时看到的状况（和我方这个回合计算出来的对方上上回合的跑位一起用于计算概率），即双方的体力值，球的速度，对方当时的位置（也就是我方上上上个回合球的落点），我方当时的位置
# 另一个是'last_tb'，记录我方上个回合的桌面状况，用于计算上个回合对方决策加速度时看到的状况，这一个和我们这个回合计算出来的加速度一起用于估计加速度相关的概率
# 这一个函数用于在计算出上一局对方的情况后，更新概率值。
def update_ds_tb(tb, ds):
    if 'lala_tb' in ds:
        op_strategy = leighton(tb, ds)
        last_tb = ds['last_tb']
        op_last_tb = ds['op_last_tb']
        lala_tb = ds['lala_tb']
        op_lala_tb = ds['op_lala_tb']
        #   op_strategy = (100000, 200000, 2000)     # 测试用
        if op_strategy[0] != None:
            # 这一段代码本用于测试bug
            # if not xToInt(op_strategy[0]) in list(range(-XD//2, XD//2 + 1, 1)):
            #     op_active_card = ds['last_tb'].op_side['active_card'][1]  # 对方上回合所用的道具
            #     active_card = ds['last_return'][2]
            #     print(op_active_card.code if op_active_card != None else None)
            #     print(active_card.code if active_card != None else None)
            # 关于对方跑位的数据
            state_run = (op_lala_tb.ball['velocity'].y, op_lala_tb.ball['position'].y, op_lala_tb.op_side['position'].y,
                         op_lala_tb.side['life'], op_lala_tb.op_side['life'], op_lala_tb.op_side['run_vector'])
            op_run = op_strategy[0]
            try:
                ds['data'].update_run(*state_run, op_run)
            except:
                if op_run > 1000000:
                    op_run = 1000000
                elif op_run < 1000000:
                    op_run = 1000000
                else:
                    pass
            # 以下代码本用于可能将两个解弄反的情形
            # if op_lala_tb.ball['position'].y + op_strategy[0] < 0 or op_lala_tb.ball['position'].y + op_strategy[0] > 1000000:
            #     op_run = op_strategy[1]
            # else:
            #     op_run = op_strategy[0]
            # 关于对方跑位位置的数据
            op_run_placement = op_lala_tb.ball['position'].y + op_run
            try:
                ds['data'].update_run_placement(*state_run, op_run_placement)
            except:
                try:
                    ds['data'].update_run_placement(*state_run, op_lala_tb.ball['position'].y + op_strategy[2])
                except:
                    if op_run_placement > 1000000:
                        op_run_placement = 1000000
                    elif op_run_placement < 0:
                        op_run_placement = 0
                    else:
                        pass
                        # 关于对方击球落点的数据
        state_placement = (
        op_last_tb.ball['velocity'].y, op_last_tb.ball['position'].y, op_last_tb.op_side['position'].y,
        op_last_tb.side['life'], op_last_tb.op_side['life'], op_last_tb.op_side['run_vector'])
        ds['data'].update_placement(*state_placement, tb.ball['position'].y)
        # 对方加速度的数据
        state_acc = (op_last_tb.ball['velocity'].y, op_last_tb.ball['position'].y, op_last_tb.op_side['position'].y,
                     op_last_tb.side['life'], op_last_tb.op_side['life'], op_last_tb.op_side['run_vector'])
        ds['data'].update_acc(*state_acc, op_strategy[2])

    if 'last_tb' in ds:
        ds['lala_tb'] = copy.deepcopy(ds['last_tb'])
    ds['last_tb'] = copy.deepcopy(tb)


# 这一个函数用于根据我们这局的决策算出下一局对方面对的情况后，更新对方面对情况的记录
def update_ds_op_tb(tb, ds, acc, run, cardaction):
    if 'op_last_tb' in ds:
        ds['op_lala_tb'] = copy.deepcopy(ds['op_last_tb'])
    ds['op_last_tb'] = copy.deepcopy(newtb(tb, acc, run, cardaction))
    ds['last_return'] = (int(acc), int(run), cardaction)


# 为了提高计算速度，针对每一种状态单独计算概率。以下三个函数分别以[(probability, value)]的形式返回
def eval_prob_placement(tb, ds, acc, run, cardaction):
    op_tb = newtb(tb, acc, run, cardaction)
    data = ds['data'].data
    dict = {'pos': posToInt(op_tb.ball['position'].y),
            'op_pos': posToInt(op_tb.op_side['position'].y),
            'life': lifeToInt(op_tb.side['life']),
            'op_life': lifeToInt(op_tb.op_side['life']),
            'ballv': vToInt(op_tb.ball['velocity'].y),
            'direction': op_tb.op_side['run_vector'],
            'placement_itself': 1}
    # 为了优化速度，这里采用的特殊的计算方法，通过公式推导，将本来应该是不同概率相乘的朴素贝叶斯法在数学推导之后化成只计算每种状态下单独概率的形式。并且将其化为整数乘除法。概率的列表如下。可能显得比较复杂。但大大降低了算法复杂度。以下的函数均雷同。
    myprob = [
        ((product([data[(namekey, 'placement')][(dict[namekey], x)] / data[('placement_itself', 'placement')][(1, x)] \
                   for namekey in dict]) * data[('placement_itself', 'placement')][(1, x)] if
          data[('placement_itself', 'placement')][(1, x)] != 0 else 0), x) \
        for x in range(POSD + 1)]
    # 这是总的概率的替代值的和。用于归一化。因为为了优化计算速度，概率并未提前归一化，而是依相应比例用整数来表示。
    factor = sum([x[0] for x in myprob])
    return [(x[0] / factor if factor != 0 else 0, x[1]) \
            for x in myprob]

# 计算跑位的概率。
def eval_prob_run(tb, ds):
    data = ds['data'].data
    op_last_tb = ds['op_last_tb']
    dict = {'pos': posToInt(op_last_tb.ball['position'].y),
            'op_pos': posToInt(op_last_tb.op_side['position'].y),
            'life': lifeToInt(op_last_tb.side['life']),
            'op_life': lifeToInt(op_last_tb.op_side['life']),
            'ballv': vToInt(op_last_tb.ball['velocity'].y),
            'direction': op_last_tb.op_side['run_vector'],
            'run_itself': 1}
    # 不再赘言
    myprob = [((product([data[(namekey, 'run')][(dict[namekey], x)] / data[('run_itself', 'run')][(1, x)] \
                         for namekey in dict]) * data[('run_itself', 'run')][(1, x)] if data[('run_itself', 'run')][
                                                                                            (1, x)] != 0 else 0), x) \
              for x in range(-XD // 2, XD // 2 + 1, 1)]
    factor = sum([x[0] for x in myprob])
    return [(x[0] / factor if factor != 0 else 0, x[1]) \
            for x in myprob]

# 计算跑位位置的概率。
def eval_prob_run_placement(tb, ds):
    data = ds['data'].data
    op_last_tb = ds['op_last_tb']
    dict = {'pos': posToInt(op_last_tb.ball['position'].y),
            'op_pos': posToInt(op_last_tb.op_side['position'].y),
            'life': lifeToInt(op_last_tb.side['life']),
            'op_life': lifeToInt(op_last_tb.op_side['life']),
            'ballv': vToInt(op_last_tb.ball['velocity'].y),
            'direction': op_last_tb.op_side['run_vector'],
            'run_placement_itself': 1}
    # 不再赘言。
    myprob = [((product(
        [data[(namekey, 'run_placement')][(dict[namekey], x)] / data[('run_placement_itself', 'run_placement')][(1, x)] \
         for namekey in dict]) * data[('run_placement_itself', 'run_placement')][(1, x)] if
                data[('run_placement_itself', 'run_placement')][(1, x)] != 0 else 0), x) \
              for x in range(POSD + 1)]
    factor = sum([x[0] for x in myprob])
    return [(x[0] / factor if factor != 0 else 0, x[1]) \
            for x in myprob]

# 计算加速度的概率
def eval_prob_acc(tb, ds):
    data = ds['data'].data
    op_last_tb = ds['op_last_tb']
    dict = {'pos': posToInt(op_last_tb.ball['position'].y),
            'op_pos': posToInt(op_last_tb.op_side['position'].y),
            'life': lifeToInt(op_last_tb.side['life']),
            'op_life': lifeToInt(op_last_tb.op_side['life']),
            'ballv': vToInt(op_last_tb.ball['velocity'].y),
            'direction': op_last_tb.op_side['run_vector'],
            'acc_itself': 1}
    # 这里在这个字典中进行迭代。
    myprob = [((product([data[(namekey, 'acc')][(dict[namekey], x)] / data[('acc_itself', 'acc')][(1, x)] \
                         for namekey in dict]) * data[('acc_itself', 'acc')][(1, x)] if data[('acc_itself', 'acc')][
                                                                                            (1, x)] != 0 else 0), x) \
              for x in range(-AD // 2 - 1, AD // 2 + 1, 1)]
    factor = sum([x[0] for x in myprob])
    return [(x[0] / factor if factor != 0 else 0, x[1]) \
            for x in myprob]

# 以下函数用于处理得到的概率的列表，评估其信度，并返回我们预测到的具体的值。
def assess_run_acc(prob):
    # 这里取倒数是为了利用python的最大最小值的字典序的特性。以下同。
    reci_prob = [(1 / element[0], abs(element[1]), element[1]) for element in prob if element[0] > 0.01]
    if reci_prob == []:
        return None, None
    else:
        return min(reci_prob)[2], min(reci_prob)[0]

# 同上。用于处理的得到的落点的概率的列表。
def assess_placement(prob):
    new_prob = [(element[0], abs(element[1] - 10), element[1]) for element in prob if element[0] > 0.01]
    if new_prob == []:
        return None
    else:
        return max(new_prob)[2], max(new_prob)[0]

# 同上
def assess_run_placement(prob):
    reci_prob = [(1 / element[0], abs(element[1] - 10), element[1]) for element in prob if element[0] > 0.01]
    if reci_prob == []:
        return None
    else:
        return min(reci_prob)[2], min(reci_prob)[0]


def serve(name, ds):
    return BALL_POS[1], 278


# 利用对对方跑位的估计算加速
def eval_acc(tb, ds):
    xmin, xmax, ymin, ymax = DIM
    tick_step = (xmax - xmin) // BALL_V[0]
    if 'op_last_tb' in ds:
        run = assess_run_acc(eval_prob_run(tb, ds))
        op_run_placement = assess_run_placement(eval_prob_run_placement(tb, ds))
        if run == None:
            run = 0
        if op_run_placement == None:
            op_run_placement = 0
            # 根据run_placement猜测的跑位后的位置
    else:
        run = 0
        op_run_placement = 10
    # 估计的对方跑位后的位置
    op_pos = (tb.op_side['position'].y + (run * 100000 + 50000) + op_run_placement * 100000) / 2
    if op_pos >= 1000000:
        op_pos = 999000
    elif op_pos <= -1000000:
        op_pos = -999000
    # 下面的列表用于记录不同方案的生命值消耗
    # 采用迭代的方法来计算出自己本回合的最优方案。由于已经预测出了对方的行为，因此迭代域不大，速度很快。
    acc_life = []
    if tb.op_side['life'] > 30000:
        for acc in range(-1000, 1001, 10):
            ball = Ball(DIM, Position(DIM[0], tb.ball['position'].y), Vector(BALL_V[0], tb.ball['velocity'].y + acc))
            count = ball.fly(tick_step, [])[0]
            if count in (1, 2):
                life = - ((ball.pos.y - op_pos) / 20000) ** 2 + (acc / 20) ** 2
                acc_life.append((life, acc))
    else:
        for acc in range(-1000, 1010, 10):
            ball = Ball(DIM, Position(DIM[0], tb.ball['position'].y), Vector(BALL_V[0], tb.ball['velocity'].y + acc))
            count = ball.fly(tick_step, [])[0]
            if count in (1, 2):
                life = -((ball.pos.y - op_pos) / 20000) ** 2
                acc_life.append((life, acc))
    # 为了防止出bug，对可能出现的没有可行值的情况再做讨论
    if acc_life == []:
        for acc in range(-900, 1000, 10):
            ball = Ball(DIM, Position(DIM[0], tb.ball['position'].y), Vector(BALL_V[0], tb.ball['velocity'].y + acc))
            count = ball.fly(tick_step, [])[0]
            if count in (1, 2):
                life = -((ball.pos.y - 500000) / 20000) ** 2 + (acc / 20) ** 2 - (
                                                                                 (ball.pos.y - op_pos) / 2 / 20000) ** 2
                acc_life.append((life, acc))
    return min(acc_life)[1]


# 利用对对方落点的估计算跑位
def eval_run(tb, ds, acc, run, cardaction):
    placement = assess_placement(eval_prob_placement(tb, ds, acc, run, cardaction))
    if placement == None:
        placement = 10
    if tb.side['life'] > 56000:
        run_action = (placement * 50000 + (50000 if placement != 20 else 0) // 2 - tb.ball['position'].y) // 2
    # 体力值较低的时候为了防止被绝杀，向中间靠拢。
    elif tb.side['life'] > 40000:
        run_action = ((placement * 50000 + (50000 if placement != 20 else 0) // 2 + tb.ball[
            'position'].y) // 2 + 500000) // 2 - tb.ball['position'].y
    else:
        run_action = (500000 - tb.ball['position'].y)
    return run_action

# 最简单的加速情形。用于在程序出现错误退出时的补救方案。
def naive_acc(tb, ds):
    acc_life = []
    xmin, xmax, ymin, ymax = DIM
    tick_step = (xmax - xmin) // BALL_V[0]
    for acc in range(-3000, 3010, 10):
        ball = Ball(DIM, Position(DIM[0], tb.ball['position'].y), Vector(BALL_V[0], tb.ball['velocity'].y + acc))
        count = ball.fly(tick_step, [])[0]
        if count in (1, 2):
            life = -((ball.pos.y - tb.op_side['position'].y) / 20000) ** 2 + (acc / 20) ** 2
            acc_life.append((life, acc))
    return min(acc_life)[1]


def selectCard(tb, ds, acc, run, lst_a):
    myCard = tb.side['cards']  # 我方现有道具箱
    # selectedCard 返回值，本回合所用道具
    # 0 如果没有任何道具，返回None
    if not bool(myCard):
        selectedCard = None
    else:
        # 1 如果有掉血包、补血包、隐身术 直接用
        if CARD_INCL in myCard:
            selectedCard = CARD_INCL
        elif CARD_DECL in myCard:
            selectedCard = CARD_DECL
        elif CARD_DSPR in myCard:
            selectedCard = CARD_DSPR
        else:
            # =======================================
            # 引用李逸飞算法，求出本回合我方击球后球的落点
            ticks = 2 * DIM[1] // abs(BALL_V[0])
            velocity_y = acc - tb.ball['velocity'].y
            Y = velocity_y * ticks + tb.side['position'].y  # Y是没有墙壁时到达的位置
            if Y % DIM[3] != 0:  # case1：未在边界
                count = Y // DIM[3]  # 穿过了多少次墙（可以是负的，最后取绝对值）
                pos = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
            else:
                pos = Y % (2 * self.extent[3])
            # =======================================
            if lst_a == None:
                op_acc = 700
            else:
                op_acc = lst_a[0] * 200
            # 预测对方加速
            op_bat = abs(pos - tb.op_side['position'].y)  # 预测对方迎球
            # =======================================以上有待完善
            # 2 如果我方跑位超过CARD_TLPT_PARAM,或者任何一方生命值较低【游戏快结束】，并且有瞬移术 就使用瞬移术
            if (abs(run) >= CARD_TLPT_PARAM or tb.side['life'] <= 40000 or tb.op_side['life'] <= 40000) \
                    and CARD_TLPT in myCard:
                selectedCard = CARD_TLPT
            # 3 如果对方加速超过 【200】,或者任何一方生命值较低【游戏快结束】，并且有变压器，就用变压器
            elif ((abs(op_acc) >= 500 and op_bat >= (DIM[3] // 4)) or tb.side['life'] <= 40000 or tb.op_side[
                'life'] <= 40000) \
                    and CARD_AMPL in myCard:
                selectedCard = CARD_AMPL
            # 4 如果对方加速超过【200】 ，或者任何一方生命值较低【游戏快结束】，并有旋转球，就用旋转球
            elif (abs(op_acc) >= 500 or tb.side['life'] <= 40000 or tb.op_side['life'] <= 40000) \
                    and CARD_SPIN in myCard:
                selectedCard = CARD_SPIN
            else:
                # 5 如果我方道具盒已满，（在不满足上述条件下的）优先级为变压器>旋转球>瞬移术
                if myCard.isfull():
                    if CARD_SPIN in myCard:
                        selectedCard = CARD_AMPL
                    elif CARD_AMPL in myCard:
                        selectedCard = CARD_SPIN
                    else:
                        selectedCard = CARD_TLPT
                else:
                    selectedCard = None
    return selectedCard


'''
对ds，tb进行分析，选择出合适的加速度方式，这里以打分的形式对打角，
接道具，不加速三种进行评估，最终选择分数值（对方的生命损失-己方损失）最高的方式，
己方损失是acc损失，对方损失是迎球的移动损失，对于接道具则有额外的分数加成。
'''


def play_acc(tb, ds, prob_acc, prob_run, newrandom):
    def play_corner(tb, prob_run, newrandom):
        # 八种打角落方法，分别计算消耗生命的差值，选取最大差值对应的加速度方法，考虑对方可能跑位和加速

        acc = [None] * 8
        for x in range(0, 3):
            # 向上打的三种方法
            acc[x] = int((((x + 1) * DIM[3] - tb.ball['position'].y) /
                          (DIM[1] - DIM[0]) * BALL_V[0])) - tb.ball['velocity'].y
        for x in range(3, 6):
            # 向下打的三种方法
            acc[x + 1] = int((((3 - x) * DIM[3] - tb.ball['position'].y) /
                              (DIM[1] - DIM[0]) * BALL_V[0])) - tb.ball['velocity'].y
        # 防止临界情况出现invalid_bounce，加速度偏离一点，造成的对手接球的体力消耗误差小于1，可忽略
        acc[3] = acc[1] + 2
        acc[7] = acc[5] - 2
        acc[0] += 1
        acc[1] -= 1
        acc[4] -= 1
        acc[5] += 1
        acc[6] += 1
        acc[2] -= 1
        # 上面是打角的方式，下面是对八种方式的先期评估，即在这八种里选出一个最好的
        life_side = [None] * 8
        life_opside = [None] * 8
        life_earned = [None] * 8
        for x in range(0, 8):
            # 模仿李逸飞算法计算落点，得到八种方法对应赚得的体力
            vel_y = tb.ball['velocity'].y + acc[x]
            Y1 = vel_y * tb.step + tb.ball['position'].y
            count1 = Y1 // DIM[3]
            op_pos_y = (Y1 - count1 * DIM[3]) * (1 - 2 * (count1 % 2)) + DIM[3] * (count1 % 2)
            if prob_run == None or prob_run[1] > 2:
                life_opside[x] = 0.2 * abs(op_pos_y - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2
                if newrandom == 0:
                    life_opside[x] = abs(op_pos_y - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2
            elif prob_run[1] > 1.5:
                life_opside[x] = 0.7 * abs(
                    op_pos_y - (tb.op_side['position'].y + prob_run[0] * 100000 + 50000)) ** 2 // FACTOR_DISTANCE ** 2
            else:
                life_opside[x] = abs(
                    op_pos_y - (tb.op_side['position'].y + prob_run[0] * 100000 + 50000)) ** 2 // FACTOR_DISTANCE ** 2
            life_side[x] = abs(acc[x]) ** 2 // FACTOR_SPEED ** 2
            # 对方体力下降，偏向于打角落
            if tb.op_side['life'] < RACKET_LIFE * 0.5:
                proportion1 = 1.2
            else:
                proportion1 = 1
            # 旋转球改变体力损失的参数
            if tb.op_side['active_card'][1] == CARD_SPIN:
                factor = 4
            else:
                factor = 1
            life_earned[x] = proportion1 * life_opside[x] - factor * life_side[x]
        # 如果存在赚得体力的方法，选取最大赚得体力对应方法
        for x in range(0, 8):
            if life_earned[x] == max(life_earned):
                return acc[x], life_earned[x]

    # 不加速的情况，实际上可不必考虑该情形，极值全都在接道具和打角中取到
    def play_idiot(tb, prob_run, newrandom):
        Y = tb.ball['velocity'].y * tb.step + tb.ball['position'].y
        count = Y // DIM[3]
        op_pos_y = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
        life_side = 0
        # 如果对方跑位方向和我方预测相同，造成对方体力损失效果好，反之效果差
        if prob_run == None or prob_run[1] > 2:
            life_opside = 0.2 * abs(
                op_pos_y - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2
            if newrandom == 0:
                life_opside = abs(op_pos_y - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2
        elif prob_run[1] > 1.5:
            life_opside = 0.7 * abs(op_pos_y - (
                tb.op_side['position'].y + prob_run[0] * 100000 + 50000)) ** 2 // FACTOR_DISTANCE ** 2
        else:
            life_opside = abs(op_pos_y - (
                tb.op_side['position'].y + prob_run[0] * 100000 + 50000)) ** 2 // FACTOR_DISTANCE ** 2
        # 对方体力下降，偏向于打角落
        if tb.op_side['life'] < RACKET_LIFE * 0.5:
            proportion1 = 1.2
        else:
            proportion1 = 1
        # 旋转球改变体力损失的参数
        if tb.op_side['active_card'][1] == CARD_SPIN:
            factor = 4
        else:
            factor = 1
        life_earned = proportion1 * life_opside - factor * life_side
        if count in (1, 2):
            return 0, life_earned
        else:
            return 0, -100000

    # 接道具的情况
    def play_acc1(tb, prob_run, newrandom):
        available_acc = {}
        ball = tb.ball
        u, v = -ball['velocity'].x, ball['velocity'].y
        x0, y0 = ball['position'].x, ball['position'].y
        cardlist = tb.cards['cards']
        # 如果此时场上无道具，那么这种策略不可能
        if not bool(cardlist):
            return 0, -100000
        for card in cardlist:
            x1, y1 = card.pos.x, card.pos.y
            l = DIM[3]
            ticks = tb.step
            acc = []
            acc.append(u * (y0 - y1) / (x0 - x1) - v)
            acc.append(u * (y0 + y1 - 2 * l) / (x0 - x1) - v)
            acc.append(u * (y1 + y0) / (x0 - x1) - v)
            acc.append(u * (y0 - y1 - 2 * l) / (x0 - x1) - v)
            acc.append(u * (y0 - y1 + 2 * l) / (x0 - x1) - v)
            for i in range(5):
                v1 = ball['velocity'].y + int(acc[i])
                if v1 == 0:
                    acc[i] = None
                Y = v1 * ticks + ball['position'].y
                if Y % l != 0:
                    count = Y // l
                    if abs(count) not in (1, 2):
                        acc[i] = None
                else:
                    count = (Y // l) if (Y > 0) else (1 - Y // l)
                    if count not in (1, 2):
                        acc[i] = None
            acc_value = [acc[i] for i in range(5) if acc[i] != None]
            if bool(acc_value):
                available_acc[card.code] = acc_value
        # 如果没有符合条件的acc
        if not bool(available_acc):
            return 0, -100000
        # acc_value即为不会发生invalid bounce的接道具的解
        temp = {}
        for name, acctuple in available_acc.items():
            score3 = []
            for acce in acctuple:
                # 模仿李逸飞算法计算落点，得到方法对应赚得的体力
                vel_y = tb.ball['velocity'].y + acce
                Y1 = vel_y * tb.step + tb.ball['position'].y
                count1 = Y1 // DIM[3]
                op_pos_y = (Y1 - count1 * DIM[3]) * (1 - 2 * (count1 % 2)) + DIM[3] * (count1 % 2)
                if prob_run == None or prob_run[1] > 2:
                    life_opside = 0.2 * abs(
                        op_pos_y - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2
                    if newrandom == 0:
                        life_opside = abs(op_pos_y - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2
                elif prob_run[1] > 1.5:
                    life_opside = 0.7 * abs(op_pos_y - (
                        tb.op_side['position'].y + prob_run[0] * 100000 + 50000)) ** 2 // FACTOR_DISTANCE ** 2
                else:
                    life_opside = abs(op_pos_y - (
                        tb.op_side['position'].y + prob_run[0] * 100000 + 50000)) ** 2 // FACTOR_DISTANCE ** 2
                life_side = abs(acce) ** 2 // FACTOR_SPEED ** 2
                # 如果对方跑位方向和我方预测相同，造成对方体力损失效果好，反之效果差
                # 对方体力下降，偏向于打角落
                if tb.op_side['life'] < RACKET_LIFE * 0.5:
                    proportion1 = 1.2
                else:
                    proportion1 = 1
                # 旋转球
                if tb.op_side['active_card'][1] == CARD_SPIN:
                    factor = 4
                else:
                    factor = 1
                life_earned = proportion1 * life_opside - factor * life_side
                score3.append([acce, life_earned])
            maxacc = max(score3, key=lambda x: x[1])
            temp[name] = maxacc
            # 道具的分数加成，例如：如果是补血和减血包，则加2000
            if name == 'IL' or name == 'DL':
                temp[name][1] += 2000
            elif name == 'DS':
                temp[name][1] += 200
            else:
                temp[name][1] += 500
        alist = list(temp.values())
        bestchoice = max(alist, key=lambda x: x[1])
        return bestchoice

    action1, score1 = play_corner(tb, prob_run, newrandom)
    action2, score2 = play_idiot(tb, prob_run, newrandom)
    action3, score3 = play_acc1(tb, prob_run, newrandom)
    # 在以上三种方式中选出分数最高的对策
    if score1 > score2:
        if score1 > score3:
            return action1
        else:
            return action3
    else:
        if score2 > score3:
            return action2
        else:
            return action3


def play(tb, ds):
    # 对ds的初始处理
    if not 'data' in ds:
        ds['data'] = Data()
    if not 'name' in ds:
        ds['name'] = tb.op_side['name']
    if 'data' in ds and 'name' in ds:
        if ds['name'] != tb.op_side['name']:
            ds['name'] = tb.op_side['name']
            ds['data'] = Data()
    update_ds_tb(tb, ds)  # 更新ds
    if tb.op_side['life'] > RACKET_LIFE * 0.43:
        newrandom = random.randint(0, 1)
    else:
        newrandom = random.randint(0, 5)
    # 加入随机应对学习算法
    if 'op_last_tb' in ds:
        prob_run = assess_run_placement(eval_prob_run(tb, ds))
        prob_acc = assess_run_acc(eval_prob_acc(tb, ds))
    else:
        prob_acc = None
        prob_run = None
        # prob_acc和prob_run是ds处理得出的预测

    # 仅根据tb的run判断
    def run_tb(tb):
        # 该函数只根据此回合己方接球后的位置来决定跑位，设置两个比例将位置分为三个对称的区间，分别采取不同的跑位
        proportion1, proportion2 = 0.4, 0.1
        if abs(tb.ball['position'].y - DIM[3] / 2) > proportion1 * DIM[3]:
            # 靠近角落则跑位为到另一角落一半的距离（感觉其实都按这样跑可能比较好）
            run = (DIM[3] * 0.5 * (1 + sign(DIM[3] / 2 - tb.ball['position'].y)) - tb.ball['position'].y) // 3
        elif abs(tb.ball['position'].y - DIM[3] / 2) > proportion2 * DIM[3]:  # 不靠近角落也不靠近中间则跑位到中间
            run = DIM[3] / 2 - tb.ball['position'].y
        else:  # 靠近中间则往中间跑一格（假跑位）
            run = sign(DIM[3] / 2 - tb.ball['position'].y)
        return run

    accaction = play_acc(tb, ds, prob_acc, prob_run, newrandom)
    # 旋转球把速度乘以2
    if tb.op_side['active_card'][1] == CARD_SPIN:
        accaction *= 2
    # 根据ds得出的对球落点的预测
    prob_place = assess_placement(eval_prob_placement(tb, ds, accaction, myrandom(), None))
    '''
    根据剩余血量，预测精准度选择合适的跑位策略
    '''
    if tb.side['life'] < RACKET_LIFE * 0.43:
        runaction = DIM[3] / 2 - tb.ball['position'].y
    elif prob_place == None or prob_place[1] < 0.7:
        runaction = run_tb(tb)
    elif tb.side['life'] < RACKET_LIFE * 0.58:
        runaction = ((prob_place[0] * 50000 + (50000 if prob_place[0] != 20 else 0) // 2 + tb.ball[
            'position'].y) // 2 + 500000) // 2 - \
                    tb.ball['position'].y
    else:
        ball_pos = prob_place[0] * 50000 + 25000
        runaction = (ball_pos - tb.ball['position'].y) // 2
    cardaction = selectCard(tb, ds, accaction, runaction, prob_acc)
    update_ds_op_tb(tb, ds, accaction, runaction, None)
    # update_ds_op_tb(tb, ds, accaction, runaction, cardaction)
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, accaction,
                        runaction, None, cardaction)


def summarize(tick, winner, reason, west, east, ball, ds):
    if 'last_tb' in ds:
        del ds['last_tb']
    if 'lala_tb' in ds:
        del ds['lala_tb']
    if 'op_lala_tb' in ds:
        del ds['op_lala_tb']
    if 'op_last_tb' in ds:
        del ds['op_last_tb']
    if 'last_return' in ds:
        del ds['last_return']
    return
