# T_TyT 4.0 by ZHD
# 居中跑位或不跑位
# 注释是本可爱写的w
# 已实现：确定四种不同的跑位与打角方式，并根据前一回合对方的动作判断对方属于哪种策略，作出相应的应对
# 待实现：道具的灵活使用
# 最后体力值较小时，为防止接不到球，强制跑位到能接到球的地方
## 即将出现道具时还是往中间跑位

from table import *

# 各种参数：
# 不同的跑位与打角策略
IDIOT = -1
SINGLE_RUN = 0
DOUBLE_RUN = 1
SINGLE_STAY = 2
DOUBLE_STAY = 3

tick_step = 1800
# 存储道具及其价值的字典
cardvalue = {
    None: 0,
    'SP': 100,
    'DS': 0,
    'IL': 3000,
    'DL': 3000,
    'TP': 300,
    'AM': 400}


# 发球函数
def serve(opside, ds):
    return BALL_POS[1], int(1000 / 18 * 15)


# 动作主函数
# tb: 桌面状态
# ds: 储存数据的字典
def play(tb, ds):
    # 读入时间
    tick = tb.tick

    # 读入我方状态：
    side_pos = tb.side['position']  # 位置
    card_box = tb.side['cards']  # 拥有的道具
    life = tb.side['life']  # 生命值

    # 读入对方状态：
    opside_pos = tb.op_side['position']  # 位置
    op_box = tb.op_side['cards']  # 拥有的道具
    op_life = tb.op_side['life']  # 生命值
    active_card = tb.op_side['active_card'][1]  # 使用的道具
    op_acc = tb.op_side['accelerate']  # 加速度
    op_run = tb.op_side['run_vector']  # 跑位

    # 读入球的状态：
    ball_pos = tb.ball['position']  # 位置
    ball_v = tb.ball['velocity']  # 速度

    # 读入场上道具状态：
    card_tick = tb.cards['card_tick']  # 道具出现计时
    cards = tb.cards['cards']  # 场上道具

    # 判断对方有没有使用道具
    is_SP = True if active_card == 'SP' else False  # 判断对方是否用了旋转球
    is_DS = True if active_card == 'DS' else False  # 判断对方是否用了隐身术
    is_IL = True if active_card == 'IL' else False  # 判断对方是否用了补血包
    is_DL = True if active_card == 'DL' else False  # 判断对方是否用了掉血包
    is_TP = True if active_card == 'TP' else False  # 判断对方是否用了瞬移术
    is_AM = True if active_card == 'AM' else False  # 判断对方是否用了变压器

    optype = 1
    is_run = True  # 表示对方前一次是否跑位
    is_double = True  # 表示对方前一次是否打双角

    # 读ds数据
    # 根据前一回合判断对方的策略
    for i in (-1,):
        if tb.tick <= 9000:  # 第一轮不进行判断
            break
        cu = ds['log'][-1][1][i]  # 表示前一回合中的“当前状态”球桌信息
        pr = ds['log'][-1][1][i - 1]  # 表示前一回合中的“前一状态”球桌信息
        act = ds['log'][-1][2][i - 1]  # 表示前一回合的动作
        # 表示前一回合中对方消耗的体力
        dlife = (pr.op_side['life'] - cu.op_side['life']) if i != 0 else 100000 - cu.op_side['life']
        # v1表示对方接球时的速度
        temp, v1 = fly(act, pr.ball['position'].y, pr.ball['velocity'].y, pr.op_side['active_card'][1] == 'SP')
        # 直接将球原路接回的动作
        re_act = RacketAction(None, None, -2 * cu.ball['velocity'].y, None, None, None)
        # -v2表示对方接球后的速度
        temp, v2 = fly(re_act, cu.ball['position'].y, cu.ball['velocity'].y, cu.op_side['active_card'][1] == 'SP')
        opacc = -v2 - v1 if pr.op_side['active_card'][1] != 'SP' else 2 * (-v1 - v2)  # 对方的加速度
        acclife = (abs(opacc) ** 2 // FACTOR_SPEED ** 2)
        # 按居中跑位计算的体力消耗
        batlife = (abs(cu.op_side['position'].y - 500000) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if cu.op_side['active_card'][1] == 'AM' else 1)
        runlife = (abs(pr.op_side['position'].y - 500000) ** 2 // FACTOR_DISTANCE ** 2)
        # if pr.op_side['active_card'][1] == 'IL':  # 如果对方使用了补血包
        #     dlife += 2000
        # if act.card == 'DL':  # 如果上一回合对对方使用了掉血包
        #     dlife -= 2000
        # 对对方的打角及跑位方式进行判断
        # 如果实际消耗和计算的消耗相差不多，则认为对方是居中跑位（跑位）
        diff = batlife + acclife + runlife - dlife
        if diff < -1400:
            dlife -= 2000
        if diff > 1400:
            dlife += 2000
        # print(dlife, batlife + acclife + runlife - dlife)
        diff = batlife + acclife + runlife - dlife

        # 判断对方是打双角还是打单角
        if abs(cu.ball['position'].y - pr.ball['position'].y) > 800000:
            is_double = True
        else:
            is_double = False

        if abs(diff)<100:
            is_run = True
        else:  # 否则不跑位
            is_run = False

        if is_double:
            if diff >= 0 and diff < 750:
                is_run = True
            elif diff < 0 and diff > -200:
                is_run = True
            else:  # 否则不跑位
                is_run = False
        else:
            if diff >= 0 and diff < 950:
                is_run = True
            elif diff < 0 and diff > -350:
                is_run = True
            else:  # 否则不跑位
                is_run = False

    # 将对方跑位与打角的信息记录为optype
    if is_run:
        if is_double:
            optype = DOUBLE_RUN
        elif not is_double:
            optype = SINGLE_RUN
    elif not is_run:
        if is_double:
            optype = DOUBLE_STAY
        elif not is_double:
            optype = SINGLE_STAY

    # 生命值小到一定程度后则必须跑位
    if life < 55000:
        if not is_run:
            optype = 2
        else:
            optype = 1

    # if optype == 2:
    #     optype = 0
    # 打法参数
    bat = ball_pos.y - side_pos.y
    acc = 0
    run = (500000 - ball_pos.y) if optype in (-1, 1, 2, 3) else 0.4*(500000 - ball_pos.y)  # 跑位为居中或者不跑位
    card_side = None
    card_used = None

    # 使用道具判定
    # 较不完善的使用道具1.0: 如果有道具就直接使用第一个
    for card in card_box:
        if card == 'DS' and len(card_box) != 1:
            continue
        card_used = card

    # 如果使用了变压器或旋转球，则强制跑位
    if card_used == 'AM' or card_used == 'SP':
        run = (500000 - ball_pos.y)

    # 如果跑位距离过小则不使用瞬移术
    if abs(run) < 250000 and card_used == 'TP':
        card_used = None

    # 如果对方使用了变压器或旋转球，则返回加速度最小的操作
    if is_AM or is_SP:
        ma = minaction(ball_pos, ball_pos.y, ball_v.y, active_card).acc
        if count_col(ball_v.y, ma, ball_pos.y, is_SP) in (1, 2):
            action = RacketAction(tb.tick, bat, ma, run, card_side, card_used)
            if tb.tick in (0, 1800):  # 第一次还会存入对方名字
                try:
                    ds['log'].append((tb.op_side['name'], [tb], [action]))
                except KeyError:
                    ds['log'] = [(tb.op_side['name'], [tb], [action])]
            else:  # 之后每次存桌面信息和动作
                ds['log'][-1][1].append(tb)
                ds['log'][-1][2].append(action)
            return RacketAction(tb.tick, bat, ma, run, card_side, card_used)

    action_list = []
    # 选道具打
    # 较完善的吃道具3.0: 得到所有能够吃到道具的操作；体力不够的时候不吃道具
    # 列表元素格式: (操作, 吃到的道具)
    for card in cards:
        if card == 'DS':
            continue
        card_pos = card.pos
        card_code = card.code
        for ac in eatcard(card_pos, ball_pos, ball_v.y, is_SP):
            if count_col(ball_v.y, ac, ball_pos.y, is_SP) in (1, 2):
                action = RacketAction(tb.tick, bat, ac, (500000 - ball_pos.y), card_side, card_used)
                pos_y, v_y = fly(action, ball_pos.y, ball_v.y, is_SP)
                if life > 32000 or abs(500000 - pos_y) > 400000:  # 只在体力足够或者吃道具方便的时候吃
                    action_list.append((action, card.code))

    target_list = []  # 用于存储目标点的列表
    # 存入两个角
    target_list.append((None, 998000))
    target_list.append((None, 2000))

    # 对每个点求出对应的加速度及操作
    for tar in target_list:
        tar = Vector(tar)
        for ac in target(ball_pos.y, ball_v.y, tar.y, is_SP):
            if count_col(ball_v.y, ac, ball_pos.y, is_SP) in (1, 2):
                action_list.append(RacketAction(tb.tick, bat, ac, run, card_side, card_used))

    tree_list = []  # 用于存储树节点的列表
    for action in action_list:
        newtree = tree(action, is_SP, is_AM, is_TP, True)
        # 算出落点
        op_ball_pos_y, op_ball_v_y = fly(action, ball_pos.y, ball_v.y, is_SP)
        if optype not in (1,):
            newtree.addchild(opplay(opside_pos, op_ball_pos_y, op_ball_v_y, card_used, optype), card_used == 'SP',
                             card_used == 'AM', card_used == 'TP')
        tree_list.append(newtree)

    action = max(tree_list).action

    # 写ds数据
    if tb.tick in (0, 1800):  # 第一次还会存入对方名字
        try:
            ds['log'].append((tb.op_side['name'], [tb], [action]))
        except KeyError:
            ds['log'] = [(tb.op_side['name'], [tb], [action])]
    else:  # 之后每次存桌面信息和动作
        ds['log'][-1][1].append(tb)
        ds['log'][-1][2].append(action)

    return action


def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    new = {'tick': tick, 'winner': winner, 'reason': reason, 'west': west, 'east': east, 'ball': ball}
    try:
        ds['summarize'].append(new)
    except KeyError:  # 如果这个文件没有内容，说明球队尚未建立历史数据
        ds['summarize'] = [new]


# 根据落点计算需要的加速度
# Tao Yunzhu
# 参数: 当前状态, 目标落点
# 返回: 打到目标落点需要的加速度的列表
def target(ball_pos_y, ball_v_y, tar_pos_y, is_SP):
    n = 2 if is_SP else 1  # 判断对方有没有使用旋转球
    y1 = 2 * DIM[3] - tar_pos_y  # 向上碰壁一次
    y2 = - tar_pos_y  # 向下碰壁一次
    y3 = 2 * DIM[3] + tar_pos_y  # 向上碰壁两次
    y4 = -2 * DIM[3] + tar_pos_y  # 向下碰壁两次
    acc_list = []
    for y in [y1, y2, y3, y4]:
        acc = (y - ball_pos_y) / tick_step - ball_v_y
        acc_list.append(int(acc * n))
    return acc_list


# 根据道具的位置计算打道具需要的加速度
# Chang Xiaoyin
# 参数: 当前状态, 目标落点
# 返回: 打到目标落点需要的加速度的列表
def eatcard(card_pos, ball_pos, ball_v_y, is_SP):
    n = 2 if is_SP else 1  # 判断对方有没有使用旋转球
    t = abs(card_pos.x - ball_pos.x) / 1000  # 计算打到球需要的时间
    acc1 = (-ball_pos.y - card_pos.y) / t - ball_v_y  # 先向下碰壁一次
    acc2 = (-ball_pos.y + card_pos.y - 2 * DIM[3]) / t - ball_v_y  # 先向下碰壁两次
    acc3 = (-ball_pos.y - card_pos.y + 2 * DIM[3]) / t - ball_v_y  # 先向上碰壁一次
    acc4 = (-ball_pos.y + card_pos.y + 2 * DIM[3]) / t - ball_v_y  # 先向上碰壁两次
    acc5 = (-ball_pos.y + card_pos.y) / t - ball_v_y  # 先不碰壁
    acc_list = []
    for acc in (acc1, acc2, acc3, acc4, acc5):
        acc_list.append(int(acc * n))
    return acc_list


# 计算操作对应的落点
# Dai Qi
# 参数: 操作
# 返回: 落点纵坐标, 落点纵速度
def fly(action, ball_pos_y, ball_v_y, is_SP):
    # 借鉴了table.py里的fly函数, 不做注释
    n = 0.5 if is_SP else 1
    action, eatedcard = action if isinstance(action, tuple) else (action, None)
    ball_v_y += action.acc * n
    Y = ball_v_y * tick_step + ball_pos_y
    if Y % DIM[3] != 0:
        count = Y // DIM[3]
        ball_pos_y = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
        ball_v_y = ball_v_y * ((count + 1) % 2 * 2 - 1)
        return ball_pos_y, ball_v_y
    else:
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])
        ball_pos_y = Y % (2 * DIM[3])
        ball_v_y = ball_v_y * ((count + 1) % 2 * 2 - 1)
        return ball_pos_y, ball_v_y


# 计算操作对应的生命值消耗
# Wang Ruimin
# 参数: 操作
# 返回: 消耗的生命值
def delife(action, is_AM=False, is_TP=False):
    n = 2 if is_AM else 1
    l1 = 0
    if is_TP:
        if action.bat > 250000:
            l1 = (abs(action.bat - 250000) ** 2 // FACTOR_DISTANCE ** 2) * n
    else:
        l1 = (abs(action.bat) ** 2 // FACTOR_DISTANCE ** 2) * n
    l2 = (abs(action.acc) ** 2 // FACTOR_SPEED ** 2) * n
    l3 = (abs(action.run) ** 2 // FACTOR_DISTANCE ** 2)
    return l1 + l2 + l3


# 计算碰撞次数
# 参数：球的速度 加速度 位置
# 返回：撞墙的次数
def count_col(ball_v_y, acc, pos_y, is_SP):
    # 借鉴了table.py里的fly函数, 不做注释
    n = 0.5 if is_SP else 1
    acc = acc * n
    ball_v_y = ball_v_y + acc
    if ball_v_y == 0:
        return 0
    Y = ball_v_y * tick_step + pos_y
    if Y % DIM[3] != 0:
        count = Y // DIM[3]
        pos_y = (Y - count * DIM[3]) * (1 - 2 * (count % 2)) + DIM[3] * (count % 2)
        ball_v_y = ball_v_y * ((count + 1) % 2 * 2 - 1)
        return int(abs(count))
    else:
        count = (Y // DIM[3]) if (Y > 0) else (1 - Y // DIM[3])
        pos_y = Y % (2 * DIM[3])
        ball_v_y = ball_v_y * ((count + 1) % 2 * 2 - 1)
        return int(count)


# 预测对方打法3.0：根据对方策略做相应的预测
# 参数：球拍位置 球的位置和速度 使用的道具 对方的打球策略
# 返回：球拍动作
def opplay(pos, ball_pos_y, ball_v_y, active_card, optype = DOUBLE_RUN):
    acc = 0
    run = 0
    if optype == -1:  # IDIOT
        return minaction(pos, ball_pos_y, ball_v_y, active_card)
    if optype in (0, 1):  # 如果对方跑位
        bat = (ball_pos_y - pos.y) // 2
        run = (ball_pos_y - pos.y) // 2
    else:  # 如果不跑位，则直接迎球
        bat = ball_pos_y - pos.y
    action_list = []
    tree_list = []
    if optype in (0, 2):  # 如果对方打单角，得出相应的最优操作
        target_list = []
        target_list.append((None, 998000))
        target_list.append((None, 2000))
        for tar in target_list:
            tar = Vector(tar)
            for ac in target(ball_pos_y, ball_v_y, tar.y, active_card == 'SP'):
                action_list.append(RacketAction(None, bat, ac, run, None, None))
        for action in action_list:
            newtree = tree(action, active_card == 'SP', active_card == 'AM', active_card == 'TP', True)
            op_ball_pos_y, op_ball_v_y = fly(action, ball_pos_y, ball_v_y, active_card == 'SP')
            tree_list.append(newtree)
        return max(tree_list).action
    else:  # 如果对方打双角，得出相应的最优操作
        target_list = []
        target_list.append((None, 998000))
        target_list.append((None, 2000))
        for tar in target_list:
            tar = Vector(tar)
            for ac in target(ball_pos_y, ball_v_y, tar.y, active_card == 'SP'):
                action_list.append(RacketAction(None, bat, ac, run, None, None))
        for action in action_list:
            newtree = tree(action, active_card == 'SP', active_card == 'AM', active_card == 'TP', True)
            op_ball_pos_y, op_ball_v_y = fly(action, ball_pos_y, ball_v_y, active_card == 'SP')
            newtree.addchild(opplay(pos, ball_pos_y, ball_v_y, None, optype = IDIOT), active_card == 'SP',
                             active_card == 'AM', active_card == 'TP')
            tree_list.append(newtree)

    return RacketAction(None, bat, acc, run, None, None)


# 求出消耗体力最小的操作
def minaction(pos, ball_pos_y, ball_v_y, active_card):
    target_list = []  # 以两个角作为目标点
    target_list.append((None, 998000))
    target_list.append((None, 2000))
    action_list = []
    tree_list = []
    for tar in target_list:
        tar = Vector(tar)
        for ac in target(ball_pos_y, ball_v_y, tar.y, active_card == 'SP'):
            if count_col(ball_v_y, ac, ball_pos_y, active_card == 'SP') in (1, 2):
                action_list.append(RacketAction(None, (ball_pos_y - pos.y) // 2, ac, (ball_pos_y - pos.y) // 2, None, None))
    if count_col(ball_v_y, 0, pos.y, active_card == 'SP') in (1, 2):  # 以及直接反弹回去
        action_list.append(RacketAction(None, (ball_pos_y - pos.y) // 2, 0, (ball_pos_y - pos.y) // 2, None, None))
    for action in action_list:
        newtree = tree(action, active_card == 'SP', active_card == 'AM', active_card == 'TP', True)
        op_ball_pos_y, op_ball_v_y = fly(action, ball_pos_y, ball_v_y, active_card == 'SP')
        tree_list.append(newtree)
    return max(tree_list).action


class tree:  # 树节点
    def __init__(self, action, is_SP, is_AM, is_TP, is_self):
        action, eatedcard = action if isinstance(action, tuple) else (action, None)
        self.is_SP = is_SP  # 表示对方是否使用旋转球
        self.is_AM = is_AM  # 表示对方是否使用变压器
        self.is_self = is_self  # 表示是否是我方操作
        self.eatedcard = eatedcard  # 当前节点操作吃到的道具
        self.cardvalue = cardvalue[self.eatedcard]  # 当前节点操作吃到的道具的价值
        self.action = action  # 当前节点的操作
        self.life = delife(action, is_AM, is_TP)  # 当前节点操作消耗的生命值
        self.value = self.cardvalue - self.life  # 当前节点对节点方的价值
        self.value *= 1 if self.is_self else -1  # 当前节点对我方的价值
        self.parent = None  # 当前节点的父节点
        # 子节点表示对方应对的操作
        self.childlist = []  # 当前节点的子节点列表

    def addchild(self, action, is_SP, is_AM, is_TP):
        newNode = tree(action, is_SP, is_AM, is_TP, not self.is_self)
        newNode.setparent(self.parent)
        self.childlist.append(newNode)
        self.updatevalue()

    def setparent(self, parent):
        self.parent = parent

    def updatevalue(self):
        if self.is_self:
            self.value = min(self.childlist).value - self.life + self.cardvalue
        else:
            self.value = max(self.childlist).value + self.life - self.cardvalue

    def __str__(self):
        return '(%7s %5s %7s %5s %5s %4s)' % (
            self.action.bat, self.action.acc, self.action.run, self.life, int(self.value), self.eatedcard)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value