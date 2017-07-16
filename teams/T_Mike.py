# PREFACE：
# 本代码基于Yusen Zhu的基础框架和基本思路，并且参考和部分融合了其他小组成员的想法；
# 代码为SWIFT系列，version == 14，并通过algo系列、RAW系列进行测试；
# Guanli Wang做了代码外观和参数的调整以及细节的优化；
# Yusen Zhu，V11加入了根据对方跑位更改评估函数中对对方跑位的猜测以及第二生命阈值，V13加入了根据我方acc分类对方跑位，V14加入了根据跑位分类acc
# 最后更新：4:22 a.m., 8 June 2017

from table import *
import sys
import copy
import shelve

# 基本参数和对应表
LIFE_LIMIT_1 = 41667         # 1/4 跑位模式下的临界生命值
LIFE_LIMIT_2 = 27778         # 中间跑位模式下的临界生命值
OP_LIFE_LIMIT = 30000         # 对方生命值影响我方决策的自定义阈值（用于动态调整道具的应用价值）
tick_step = (DIM[1] - DIM[0]) // BALL_V[0]
card_value_menu = {'SP': 2000, 'DS': 10, 'IL': 4000, 'DL': 4010, 'TP': 400, 'AM': 2000}   # 道具价值原始列表（会动态调整）
run_menu = {}     # 跑位模式原始对应表
memory = {}     # 单局对战记录表


def sign(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0


def swap(alist):
    alist[0], alist[1] = alist[1], alist[0]


# 临界速度计算
def vel_critical(pos):
    up_ub = int((DIM[3] * 3 - pos) / tick_step) - 1                  # bounces = 2
    up_mid = int((DIM[3] * 2 - pos) / tick_step) + 1                 # bounces = 2
    up_lb = int((DIM[3] - pos) / tick_step) + 1                      # bounces = 1
    down_lb = -int((DIM[3] * 2 + pos) / tick_step) + 1               # bounces = 2
    down_mid = -int((DIM[3] + pos) / tick_step) - 1                  # bounces = 2
    down_ub = -int(pos / tick_step) - 1                              # bounces = 1
    return [[up_lb, up_mid, up_ub], [down_lb, down_mid, down_ub]]


# 判断击球是否合法
def isLegal(pos, vel):
    crit = vel_critical(pos)
    if vel > crit[0][2] or vel < crit[1][0] or crit[1][2] < vel < crit[0][0]:
        return False
    else:
        return True


# 判断pos是否在角落里（若距上下边界的长度 < 球桌宽度的1/4即视为在角落里）
def is_atcorner(pos):
    return abs(pos - DIM[3] // 2) >= DIM[3] // 4


# 球到达对方的落点
def get_op_pos(pos, vel):
    if not isLegal(pos, vel):
        return
    elif vel > 0:
        return abs(vel * tick_step - (DIM[3] - pos) - DIM[3])
    else:
        return DIM[3] - abs(vel * tick_step + pos + DIM[3])


# 球到达对方的速度
def get_op_vel(pos, vel):
    op_vel = -vel
    if vel >= (DIM[3] * 2 - pos) / tick_step or vel <= -(DIM[3] + pos) / tick_step:
        op_vel = -op_vel
    return op_vel


# memory初始化
def initialize_memory(memo):
    memo['turns'] = 0         # 拍数
    memo['rallies'] = []           # 用于存储单回合的信息（以Rally类的形式）
    memo['op_acc_cost_live'] = 0         # 动态跟踪对手的acc_cost，用于调整跑位策略


# 发球。模式：向上，速度最大
def serve(op_side: str, ds: dict) -> tuple:
    initialize_memory(memory)
    return 0, vel_critical(0)[0][0]     # 注：实际上应该return DIM[3] // 2, vel_critical(DIM[3] // 2)[0][2]


# 打球。
def play(tb: TableData, ds: dict) -> RacketAction:
    # 参数
    bat = tb.ball['position'].y - tb.side['position'].y     # 迎球策略：固定值
    routes = []                                                # 存放待考察的回球路线
    turns = tb.tick // (2 * tb.step) + 1                       # 回合数
    if turns == 1:
        initialize_memory(memory)

    # 跑位模式对应表初始化
    def initialize_run_menu():
        run_menu['HIT_UPWARDS'] = [(DIM[3] + tb.ball['position'].y) // 2 - tb.ball['position'].y,
                                   DIM[3] // 2 - tb.ball['position'].y]
        run_menu['HIT_DOWNWARDS'] = [tb.ball['position'].y // 2 - tb.ball['position'].y,
                                     DIM[3] // 2 - tb.ball['position'].y]
        run_menu['HIT_CARDS'] = [(DIM[3] + tb.ball['position'].y) // 2 - tb.ball['position'].y,
                                 tb.ball['position'].y // 2 - tb.ball['position'].y]

    initialize_run_menu()

    # 更新跑位模式对应表
    def update_run_menu(traits):
        swap(run_menu[traits])

    # 跑位模式匹配函数
    def match(traits, test_route):
        if traits == 'HIT_UPWARDS' or traits == 'HIT_DOWNWARDS':
            return run_menu[traits][0]
        elif traits == 'HIT_CARDS':                   # 回球基于目的性获取道具时的跑位策略：对角方向，最小消耗模式
            if test_route.start < DIM[3] // 2:
                return run_menu[traits][0]
            else:
                return run_menu[traits][1]

    # 测试运行结果，返回bounces, cards_hit
    def test(action):
        test_ball = Ball(DIM, copy.deepcopy(tb.ball['position']), copy.deepcopy(tb.ball['velocity']))
        test_ball.update_velocity(action.acc, copy.deepcopy(tb.op_side['active_card']))
        test_ball.bounce_racket()
        return test_ball.fly(tick_step, copy.deepcopy(tb.cards['cards']))

    # 定义类：路线
    # 包括起始位置、球的起始纵向速度、落点、对应的action、自定义的回球模式mode以及路线的反弹次数和经过的道具
    class Route:
        def __init__(self, start, vel0, action, mode):
            self.start = start
            self.vel0 = vel0
            self.end = get_op_pos(self.start, self.vel0)
            self.action = action
            self.mode = mode
            self.bounces, self.cards = test(self.action)
            self.acc = action.acc

        # 判断路线是否合法
        def isLegal(self):
            return isLegal(self.start, self.vel0)

        def getEnd(self):
            return self.end

        def getCards(self):
            return self.cards

    # 获取正常打角模式下的路线
    def hit_corners():
        crit = vel_critical(tb.ball['position'].y)
        for i in range(0, 2):
            for j in range(0, 3):
                new_action = RacketAction(tb.tick, bat, crit[i][j] - tb.ball['velocity'].y, None, None, None)
                if tb.op_side['active_card'][1] == 'SP':
                    new_action.acc = int(new_action.acc / CARD_SPIN_PARAM)
                new_route = Route(tb.ball['position'].y, crit[i][j], new_action, 'HIT_CORNERS')
                if new_route.getEnd() > (DIM[3] // 2):
                    new_route.mode = 'HIT_UPWARDS'
                else:
                    new_route.mode = 'HIT_DOWNWARDS'
                routes.append(new_route)

    # 获取有目的获取道具的路线
    def hit_cards():
        for card in copy.deepcopy(tb.cards['cards']):
            t0 = abs((tb.ball['position'].x - card.pos.x) // BALL_V[0])
            vel0 = (card.pos.y - tb.ball['position'].y) // t0
            vel1_up = (DIM[3] * 2 - tb.ball['position'].y - card.pos.y) // t0
            vel1_down = -(tb.ball['position'].y + card.pos.y) // t0
            vel2_up = (DIM[3] * 2 - tb.ball['position'].y + card.pos.y) // t0
            vel2_down = -(DIM[3] * 2 - card.pos.y + tb.ball['position'].y )
            vel_possible = [vel0 - 1, vel0, vel0 + 1,
                            vel1_up - 1, vel1_up, vel1_up + 1,
                            vel1_down - 1, vel1_down, vel1_down + 1,
                            vel2_up - 1, vel2_up, vel2_up + 1,
                            vel2_down - 1, vel2_down, vel2_down + 1]
            for vel in vel_possible:
                new_action = RacketAction(tb.tick, bat, vel - tb.ball['velocity'].y, None, None, None)
                if tb.op_side['active_card'][1] == 'SP':
                    new_action.acc = int(new_action.acc / CARD_SPIN_PARAM)
                new_route = Route(tb.ball['position'].y, vel, new_action, 'HIT_CARDS')
                if new_route.isLegal() and card in new_route.getCards():
                    routes.append(new_route)

    # 自定义类： 跑位模式
    # 包括模式参数traits，以及参数的添加和判断相等的方法
    class RunMode:
        def __init__(self):
            self.traits = ''
            self.approach = None

        def add_traits(self, new_traits):
            # if isinstance(new_traits, list):
            #     for trait in new_traits:
            #         self.traits.add(trait)
            # else:
            #     self.traits.add(new_traits)
            self.traits = new_traits

        def resembles(self, other):
            return self.traits == other.traits

    # 自定义类： 回合
    # 包括该回合中我方采取的路线，以及双方该回合的基本信息
    class Rally:
        def __init__(self, route):
            self.mode = RunMode()
            self.route = route
            self.mode.add_traits(self.route.mode)
            self.side_info = {}
            self.op_side_info = {}
            self.outcome = None

        # def extract_mode(self):
        #     self.mode.add_traits(self.route.mode)
        #     # if abs(self.route.end - tb.op_side['position'].y) >= (DIM[3] // 2):
        #     #     self.mode.add_traits('FAR_SIDE')
        #     # else:
        #     #     self.mode.add_traits('NEAR_SIDE')
        #
        # self.extract_mode()

        # 更新双方信息；（每回合要更新两次，一次在该回合开始前，另一次在下一回合开始前；用param控制）
        def update_info(self, tb_current, param):
            if param == 'INITIAL':
                self.side_info['life_initial'] = tb_current.side['life']
                self.op_side_info['life_initial'] = tb_current.op_side['life']
                self.op_side_info['card_used'] = tb_current.op_side['active_card']
                self.op_side_info['current_cards'] = tb_current.op_side['cards']
                self.op_side_info['pos_initial'] = tb_current.op_side['position']
            elif param == 'FINAL':
                self.side_info['life_final'] = tb_current.side['life']
                self.op_side_info['life_final'] = tb_current.op_side['life']
                self.op_side_info['pos_final'] = tb_current.op_side['position']
                self.outcome = (self.op_side_info['life_final'] - self.op_side_info['life_initial'])\
                               - (self.side_info['life_final'] - self.side_info['life_initial'])

    # 防止我方生命值刚刚小于LIFE_LIMIT时被斩杀
    def check(route):
        life = copy.copy(tb.side['life'])
        acc_cost = route.action.acc ** 2 // FACTOR_SPEED ** 2
        run_cost = route.action.run ** 2 // FACTOR_DISTANCE ** 2
        life = life - acc_cost - run_cost - route.action.bat ** 2 // FACTOR_DISTANCE ** 2
        for card in tb.op_side['cards']:
            if card.code == 'DL':
                life -= CARD_DECL_PARAM
                break
        if LIFE_LIMIT_2 < life < LIFE_LIMIT_1:               # 预估可能被斩杀时，修改跑位到恰好不会被斩杀的位置
            max_dist = life / RACKET_LIFE * 9 / 5 * DIM[3]
            max_dist = int(max_dist)
            max_dist -= 10000
            route_end = route.start + route.action.run
            if route_end > max_dist:
                route.action.run = max_dist - route.start
            elif DIM[3] - route_end > max_dist:
                route.action.run = DIM[3] - max_dist - route.start
        return

    # 获取跑位策略
    def get_run_strategy(route):
        # 以下情况下采取中间跑位：
        # 我方生命值低于3/4 * DIM[3]跑位阈值且高于1/2 * DIM[3]跑位阈值时；
        # 我方击球位置太靠近中间时；
        # 统计的acc_cost未给出明显倾向时
        # if LIFE_LIMIT_2 < tb.side['life'] < LIFE_LIMIT_1 or not is_atcorner(route.start):

        # if LIFE_LIMIT_2 < tb.side['life'] < LIFE_LIMIT_1 or not is_atcorner(route.start):
        #     route.action.run = DIM[3] // 2 - route.start
        #     return

        # table_cards = [card.code for card in tb.cards['cards']]
        # if CARD_INCL in table_cards or CARD_DECL in table_cards or CARD_AMPL in table_cards:
        #     route.action.run = DIM[3] // 2 - route.start
        #     return

        # 球奔着道具去的情况
        test_rally = Rally(route)
        if test_rally.mode.traits == 'HIT_CARDS':
            route.action.run = match(test_rally.mode.traits, route)
            check(route)
            return
        if not is_atcorner(route.start):
            route.action.run = DIM[3] // 2 - route.start
            check(route)
            return

        # # 应对对方捡IL，DL道具的球路的跑位
        # tb_cards = copy.deepcopy(tb.cards['cards'])
        # for card in tb_cards:
        #     if card.code == 'IL' or card.code == 'DL':
        #         if (tb.ball['position'].x > 0 and CARD_EXTENT[1] - card.pos.x <= 50000) \
        #                 or (tb.ball['position'].x < 0 and card.pos.x - CARD_EXTENT[0] <= 50000):
        #             if card.pos.y - CARD_EXTENT[2] <= 50000 or CARD_EXTENT[3] - card.pos.y <= 50000:
        #                 route.action.run = (card.pos.y + route.start) // 2 - route.start
        #                 # print('Test')
        #                 check(route)
        #                 return

        # 正常打角情况（结合动态统计结果）
        op_acc_cost_live = memory['op_acc_cost_live']
        try:
            if memory['acc_tag'] == 'run_corner':
                op_acc_cost_live = memory['op_acc_cost_live_corner']
                # print('cor')
            elif memory['acc_tag'] == 'run_mid':
                op_acc_cost_live = memory['op_acc_cost_live_mid']
                # print('mid')
        except:
            pass
        if op_acc_cost_live <= 300:       # 统计结果指示对方倾向于以acc_cost -> 0 的模式回球
            if route.start > DIM[3] // 2:
                run = DIM[3] // 4 * 3 - route.start
            else:
                run = DIM[3] // 4 - route.start
        elif 500 <= op_acc_cost_live <= 900:  # 统计结果指示对方倾向于以acc_cost -> 700 的模式回球
            if route.start > DIM[3] // 2:
                run = route.start // 2 - route.start
            else:
                run = (DIM[3] + route.start) // 2 - route.start
        else:
            run = DIM[3] // 2 - route.start    # 其他情况： 中间跑位（保守策略）
        route.action.run = run
        check(route)

        # 其他跑位方法：
        #
        # # 按自定义回球模式进行匹配
        # test_rally = Rally(route)
        # index = 0
        # count = 0
        # for pre_rally in history['rallies']:
        #     if test_rally.mode.resembles(pre_rally.mode):
        #         count += 1
        #         index += sign(pre_rally.outcome) * count // 2
        # if index >= 0:
        #     run = match(test_rally.mode.traits, route)
        # else:
        #     update_run_menu(test_rally.mode.traits)
        #     run = match(test_rally.mode.traits, route)
        #
        # 阈值 + 对角跑位
        # if tb.side['life'] < 50000:
        #     run = DIM[3] // 2 - route.start
        # elif route.start < DIM[3] // 4:
        #     run = (DIM[3] - route.start) // 2 - route.start
        # elif route.start > 3 * DIM[3] // 4:
        #     run = route.start // 2 - route.start
        # else:
        #     run = DIM[3] // 2 - route.start
        #
        # 阈值 + 1/4 跑位
        # if tb.side['life'] < LIFE_LIMIT_1:
        #     run = DIM[3] // 2 - route.start
        # elif route.start > 3 * DIM[3] // 4:
        #     run = 3 * DIM[3] // 4 - route.start
        # elif route.start < DIM[3] // 4:
        #     run = DIM[3] // 4 - route.start
        # else:
        #     run = DIM[3] // 2 - route.start

        return

    # 获取道具使用策略
    # 考察我方拥有的道具；若为IL或DL或DS，暂时设定直接使用
    # 若为SP或TP或AM：在道具使用可以保证一定收益时暂定使用
    # 若道具箱已满，直接使用
    def get_card_strategy(route):
        for card in tb.side['cards']:
            if card.code == 'IL' or card.code == 'DL' or card.code == 'DS':
                route.action.card = (None, card)
                break
            elif card.code == 'SP':
                if memory['op_acc_cost_live'] > 300:
                    route.action.card = (None, card)
                    break
            elif card.code == 'TP':
                if route.action.run ** 2 // FACTOR_DISTANCE ** 2 >= 100 or len(tb.side['cards']) >= 3:
                    route.action.card = (None, card)
                    break
            elif card.code == 'AM':
                if abs(route.end - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2 > 300 or len(tb.side['cards']) >= 3:
                    route.action.card = (None, card)
                    break

    # 评估函数（核心）
    def evaluate(route):
        cost = 0

        # 加速花费
        acc_cost = route.action.acc ** 2 // FACTOR_SPEED ** 2
        cost += acc_cost

        if tb.op_side['active_card'][1] == 'SP':
            route.action.acc *= CARD_SPIN_PARAM

        # 跑位花费
        run_cost = route.action.run ** 2 // FACTOR_DISTANCE ** 2
        cost += run_cost

        # 对方击球花费，根据对方上轮跑位预估
        aim_pos = route.getEnd()
        if tb.op_side['run_vector'] is None or (aim_pos - tb.op_side['position'].y) * tb.op_side['run_vector'] > 0:
            try:
                if memory['last_tag'] == 'item':
                    op_run = memory['op_run_item']
                elif memory['last_tag'] == 'far_end':
                    op_run = memory['op_run_far']
                    # print('far %d'%op_run)
                elif memory['last_tag'] == 'near_end':
                    op_run = memory['op_run_near']
                    # print('near %d'%op_run)
                if abs(op_run) > 360000:
                    op_run_cost = (DIM[3] // 2 - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2 / 4
                    op_bat_cost = (aim_pos - DIM[3] // 2) ** 2 // FACTOR_DISTANCE ** 2 / 4
                else:
                    op_run_cost = (aim_pos - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2 // 16
                    op_bat_cost = (aim_pos - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2 * 9 // 16
            except:
                op_run_cost = (aim_pos - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2 / 4
                op_bat_cost = (aim_pos - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2 / 4
        else:
            op_run_cost = 0
            op_bat_cost = (aim_pos - tb.op_side['position'].y) ** 2 // FACTOR_DISTANCE ** 2
        cost -= int(op_run_cost + op_bat_cost)

        # 对方加速花费(只管安全速度)
        op_vel_range = vel_critical(aim_pos)
        op_ball_vel = get_op_vel(route.start, route.vel0)
        op_acc_cost = 0
        if not isLegal(aim_pos, op_ball_vel):
            if op_ball_vel >= op_vel_range[0][2]:
                op_acc_cost = (op_ball_vel - op_vel_range[0][2]) ** 2 // FACTOR_SPEED ** 2
            elif op_ball_vel <= op_vel_range[1][0]:
                op_acc_cost = (op_ball_vel - op_vel_range[1][0]) ** 2 // FACTOR_SPEED ** 2
            elif 0 < op_ball_vel <= op_vel_range[0][0]:
                op_acc_cost = (op_ball_vel - op_vel_range[0][0]) ** 2 // FACTOR_SPEED ** 2
            elif op_vel_range[1][2] < op_ball_vel < 0:
                op_acc_cost = (op_ball_vel - op_vel_range[1][2]) ** 2 // FACTOR_SPEED ** 2
        cost -= op_acc_cost

        # 我方下次击球花费
        # 先按对方不改变速度估计好了，这个一定要学习....
        # cost += ((predictpos_back(pos, vel + acc) - pos - run) / FACTOR_DISTANCE) ** 2

        # 获取道具的等效花费（近似量化）
        card_value = copy.deepcopy(card_value_menu)
        if tb.side['life'] < LIFE_LIMIT_1:              # 我方生命值较低时，提高IL的获取价值
            card_value['IL'] += 5000
        for card in route.getCards():
            if not is_atcorner(route.getEnd()):       # 获取道具的路线的落点靠近中间时，降低道具的获取价值（容易得不偿失）
                card_value[card.code] -= 2000
            cost -= card_value[card.code]

        # 使用道具
        if route.action.card[1] is not None:
            card_used = route.action.card[1].code
        else:
            card_used = ''
        if card_used == '':   # 不使用道具的策略也赋以一定价值
            cost -= 300
        elif card_used == 'SP':
            cost -= memory['op_acc_cost_live'] * 3      # 用memory记录的对手的动态加速花费评估SP使用效果
        elif card_used == 'IL':
            cost -= 2000
            if tb.op_side['life'] < OP_LIFE_LIMIT:       # 我方生命值较低时，提高IL的使用价值
                cost -= 2000
        elif card_used == 'DL':
            cost -= 2000
            if tb.side['life'] < LIFE_LIMIT_1:             # 对方生命值较低时，提高DL的使用价值
                cost -= 2000
        elif card_used == 'TP':                          # TP的使用价值按当前路线的跑位策略评估
            cost -= run_cost
            new_run_cost = max(route.action.run - CARD_TLPT_PARAM, 0) ** 2 // FACTOR_DISTANCE ** 2
            cost += new_run_cost
        elif card_used == 'AM':
            cost -= op_bat_cost
            cost -= op_acc_cost
            if tb.op_side['life'] < OP_LIFE_LIMIT:      # 对方生命值较低时，提高AM的使用价值
                cost -= 2000

        # 斩杀系统（结合对手的最大移动距离）
        op_max_distance = tb.op_side['life'] / RACKET_LIFE * BALL_V[0] * tick_step
        if op_max_distance < DIM[3]:
            if tb.op_side['run_vector'] is None or (aim_pos - tb.op_side['position'].y) * tb.op_side['run_vector'] > 0:
                if abs(aim_pos - tb.op_side['position'].y) > 2 * op_max_distance:
                    cost -= sys.maxsize
            elif abs(aim_pos - tb.op_side['position'].y) > op_max_distance:
                cost -= sys.maxsize

        if tb.op_side['active_card'][1] == 'SP':
            route.action.acc = int(route.action.acc / CARD_SPIN_PARAM)

        return cost

    # 更新memory（单局开局时）
    def update_memory():
        memory['turns'] = turns
        pre_turns = len(memory['rallies'])
        if pre_turns >= 1:
            pre_rally = memory['rallies'][-1]
            pre_rally.update_info(tb, 'FINAL')
            vel = get_op_vel(pre_rally.route.start, pre_rally.route.vel0)
            vel0 = -get_op_vel(tb.ball['position'].y, -tb.ball['velocity'].y)
            op_acc = vel0 - vel

            # 根据上上上轮我方的跑位生成对方上轮acc所可能依据的tag
            tag_acc_prev = 'run_mid'
            if pre_turns > 1:
                pre2_rally = memory['rallies'][-2]
                if abs(pre2_rally.op_side_info['pos_initial'].y - DIM[3]/2) > 150000:
                    tag_acc_prev = 'run_corner'
            if tag_acc_prev == 'run_corner':
                memory['op_acc_cost_live_corner'] = op_acc ** 2 // FACTOR_SPEED ** 2
            else:
                memory['op_acc_cost_live_mid'] = op_acc ** 2 // FACTOR_SPEED ** 2

            # 根据上上轮我方跑位生成对方本轮acc所可能依据的tag
            tag_acc = 'run_mid'
            if abs(pre_rally.op_side_info['pos_initial'].y - DIM[3]/2) > 150000:
                tag_acc = 'run_corner'
            memory['acc_tag'] = tag_acc
            memory['op_acc_cost_live'] = op_acc ** 2 // FACTOR_SPEED ** 2  # 获取上一局对手的加速消耗

            # 根据上次的acc生成对方本轮跑位所可能依据的tag
            tag = "item"
            op_dis1 = pre_rally.op_side_info['pos_final'].y - pre_rally.op_side_info['pos_initial'].y
            op_dis1 = abs(op_dis1)
            if op_dis1 > DIM[3] * 0.9:
                tag = 'far_end'
            elif op_dis1 < DIM[3] * 0.1:
                tag = 'near_end'
            memory['last_tag'] = tag

            # 根据上上次的acc记录对方我方acc所依据的对方上次跑位所依据的tag
            tag_run = 'item'
            if pre_turns > 1:
                pre2_rally = memory['rallies'][-2]
                op_dis2 = pre2_rally.op_side_info['pos_final'].y - pre2_rally.op_side_info['pos_initial'].y
                op_dis2 = abs(op_dis2)
                if op_dis2 > DIM[3] * 0.9:
                    tag_run = 'far_end'
                elif op_dis2 < DIM[3] * 0.1:
                    tag_run = 'near_end'

            # 通过对方总消耗减去其他消耗算出对方跑位
            op_runbat_cost = pre_rally.op_side_info['life_initial'] - pre_rally.op_side_info['life_final'] - op_acc ** 2 // FACTOR_SPEED ** 2
            op_runbat = pre_rally.op_side_info['pos_final'].y - pre_rally.op_side_info['pos_initial'].y
            if len(pre_rally.op_side_info['card_used']) > 0:
                # print(pre_rally.op_side_info['card_used'])
                if (pre_rally.op_side_info['card_used'])[1] == CARD_INCL:
                    op_runbat_cost += 2000
                if pre_rally.route.action.card[1] == CARD_DECL:
                    op_runbat_cost -= 2000
                if (pre_rally.op_side_info['card_used'])[1] == CARD_TLPT:
                    pass
            op_run = abs(op_runbat) - abs(2 * op_runbat_cost * FACTOR_DISTANCE ** 2 - op_runbat ** 2) ** 0.5
            op_run /= 2
            if tag_run == 'far_end':
                memory['op_run_far'] = abs(op_run.__int__())
            elif tag_run == 'near_end':
                memory['op_run_near'] = abs(op_run.__int__())
            elif tag_run == 'item':
                memory['op_run_item'] = abs(op_run.__int__())
            memory['op_run'] = abs(op_run.__int__())
            # print(op_run)

    # 更新memory（单局结束时）
    def memorize(route):
        new_rally = Rally(route)
        new_rally.update_info(tb, 'INITIAL')
        memory['rallies'].append(new_rally)

    # 获取和执行策略（宏观流程）
    update_memory()
    hit_corners()
    hit_cards()
    index = sys.maxsize
    route_chosen = None
    for route in routes:                  # 获取最佳路线
        get_run_strategy(route)
        get_card_strategy(route)
        delta = evaluate(route)
        if delta < index:
            route_chosen = route
            index = delta
    memorize(route_chosen)

    return route_chosen.action


def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return
