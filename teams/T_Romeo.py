# Team: ROMEO
# Race Partition: East
# Team-leader: Yang Zizhen
# Team-members: Feng Lu, Jiang Shihao, Li Jiayi, Liu Xiaohui, Wang Jinzhao, Wang Xubin
# Code Version: 6.1
# Historical Versions: deleted
# New Version Additions:
#    1) Simplified.


from table import *
import math
import random
EnemyName = ''


# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side, ds):
    return 400000, -BALL_V[1] // 4


def ChooseThePath1(current, target, velocity, limitations):
    time = abs((current.x - target.x) / velocity.x)
    distance_y = [2 * DIM[3] + target.y - current.y,
                  2 * DIM[3] - target.y - current.y,
                  target.y - current.y,
                  -(0 * DIM[3] + target.y + current.y),
                  -(2 * DIM[3] - target.y + current.y)]
    pre_y = velocity.y * time
    delta_vy = [round((dist - pre_y) / time) for dist in distance_y]
    abs_delta_vy = [abs(v) for v in delta_vy]
    min_delta_vy = None
    while delta_vy != []:
        index = abs_delta_vy.index(min(abs_delta_vy))
        min_delta_vy = delta_vy[index]
        if (limitations[0] >= min_delta_vy >= limitations[1]) or (limitations[2] >= min_delta_vy >= limitations[3]):
            break
        else:
            min_delta_vy = None
            delta_vy.pop(index)
            abs_delta_vy.pop(index)
    return min_delta_vy


NearCorner = 2000
def ChooseThePath2(current, target, velocity):
    time = 1800
    if target.y == DIM[2]:
        distance_y = [2 * DIM[3] - current.y + NearCorner,
                      2 * DIM[3] - current.y,
                      2 * DIM[3] - current.y - NearCorner,
                      -(0 * DIM[3] + current.y + NearCorner),
                      -(2 * DIM[3] + current.y - NearCorner)]
    else:
        distance_y = [3 * DIM[3] - current.y - NearCorner,
                      1 * DIM[3] - current.y + NearCorner,
                      -(1 * DIM[3] + current.y + NearCorner),
                      -(1 * DIM[3] + current.y),
                      -(1 * DIM[3] + current.y - NearCorner)]
    pre_y = velocity.y * time
    delta_vy = [round((dist - pre_y) / time) for dist in distance_y]
    abs_delta_vy = [abs(v) for v in delta_vy]
    return delta_vy[abs_delta_vy.index(min(abs_delta_vy))]


def ChooseThePath3(current, velocity):
    time = 1800
    distance_y = [2 * DIM[3] - current.y + NearCorner,
                  2 * DIM[3] - current.y,
                  2 * DIM[3] - current.y - NearCorner,
                  -(0 * DIM[3] + current.y + NearCorner),
                   -(2 * DIM[3] + current.y - NearCorner),
                 3 * DIM[3] - current.y - NearCorner,
                  1 * DIM[3] - current.y + NearCorner,
                  -(1 * DIM[3] + current.y + NearCorner),
                  -(1 * DIM[3] + current.y),
                  -(1 * DIM[3] + current.y - NearCorner)]
    pre_y = velocity.y * time
    delta_vy = [round((dist - pre_y) / time) for dist in distance_y]
    abs_delta_vy = [abs(v) for v in delta_vy]
    return delta_vy[abs_delta_vy.index(min(abs_delta_vy))]

def SpeedCheck(v, active_card):
    if v == None: return None
    ret = v
    if active_card[1] == CARD_SPIN: # If our rotation has been halfed.
        ret /= CARD_SPIN_PARAM
    return ret


def TryForCards(TICK, TICK_STEP, SELF, OPNT, BALL, CARD, limit_v):

    # Data initialization
    self_position, self_life, self_cards = SELF['position'], SELF['life'], SELF['cards']
    opnt_position, opnt_life, opnt_cards = OPNT['position'], OPNT['life'], OPNT['cards']
    opnt_active_card, opnt_run_vector = OPNT['active_card'], OPNT['run_vector']
    ball_position, ball_velocity = BALL['position'], BALL['velocity']
    ball_velocity.x = -ball_velocity.x
    card_cards = CARD['cards']

    # Sort the cards
    # 1. Cards for life
    # 2. Cards for flash
    # 3. Cards for double enemy's consumption
    # 4. Cards for others(rotation and disappearation)
    card_life = list()
    card_tp = list()
    card_am = list()
    card_others = list()
    for card in card_cards:
        if card == CARD_INCL or card == CARD_DECL:
            card_life.append(card)
        elif card == CARD_TLPT:
            card_tp.append(card)
        elif card == CARD_AMPL:
            card_am.append(card)
        else:
            card_others.append(card)

    # If there is a card that we want.
    # The spot which is nearest is the one to choose.
    ret_V = None

    # 1. Card for life
    for card in card_life:
        min_delta_vy = ChooseThePath1(ball_position, card.pos, ball_velocity, limit_v)
        if min_delta_vy != None and (ret_V == None or abs(ret_V) > abs(min_delta_vy)):
            ret_V = min_delta_vy
    ret_V = SpeedCheck(ret_V, opnt_active_card)
    if ret_V != None and (ret_V / FACTOR_SPEED) ** 2 <= CARD_INCL_PARAM:
        return ret_V

    # 2. Cards for flash:
    for card in card_tp:
        min_delta_vy = ChooseThePath1(ball_position, card.pos, ball_velocity, limit_v)
        if min_delta_vy != None and (ret_V == None or abs(ret_V) > abs(min_delta_vy)):
            ret_V = min_delta_vy
    ret_V = SpeedCheck(ret_V, opnt_active_card)
    if ret_V != None and (ret_V / FACTOR_SPEED) ** 2 <= (CARD_TLPT_PARAM / FACTOR_DISTANCE) ** 2:
        return ret_V
    else:
        ret_V = None

    # When it's time for a result, do something more useful.
    if self_life + opnt_life <= RACKET_LIFE:
        return None

    # 3. Cards for double enemy's consumption
    for card in card_am:
        min_delta_vy = ChooseThePath1(ball_position, card.pos, ball_velocity, limit_v)
        if min_delta_vy != None and (ret_V == None or abs(ret_V) > abs(min_delta_vy)):
            ret_V = min_delta_vy
    if ret_V != None: ret_V = SpeedCheck(ret_V, opnt_active_card)
    if ret_V != None and (ret_V / FACTOR_SPEED) ** 2 <= ((DIM[3] // 2) / FACTOR_DISTANCE) ** 2:
        return ret_V
    else:
        ret_V = None

    # 4. If we still get nothing, but we have lots of life to WASTE, we can try to get something.
    if self_life <= opnt_life:
        pass  # We are in a bad condition, so we should save our life.
    else:
        for card in card_others:
            min_delta_vy = ChooseThePath1(ball_position, card.pos, ball_velocity, limit_v)
            if min_delta_vy != None and (ret_V == None or abs(ret_V) > abs(min_delta_vy)):
                ret_V = min_delta_vy
        if ret_V != None: ret_V = SpeedCheck(ret_V, opnt_active_card)
        if ret_V != None and (ret_V / FACTOR_SPEED) ** 2 <= (self_life - opnt_life) / 20:
            return ret_V
        else:
            ret_V = None
    return ret_V


def KickToCorner(TICK, TICK_STEP, SELF, OPNT, BALL, CARD, ds):

    # Data initialization
    self_position, self_life, self_cards = SELF['position'], SELF['life'], SELF['cards']
    opnt_position, opnt_life, opnt_cards = OPNT['position'], OPNT['life'], OPNT['cards']
    opnt_active_card, opnt_run_vector = OPNT['active_card'], OPNT['run_vector']
    ball_position, ball_velocity = BALL['position'], BALL['velocity']
    ball_velocity.x = -ball_velocity.x
    card_cards = CARD['cards']

    if 'my_pre_pos' in ds.keys() and ds['my_pre_pos'] <= DIM[3] // 4 * 1 and ball_position.y <= DIM[3] // 4 * 1:
        ret_V = SpeedCheck(ChooseThePath2(ball_position, Position(opnt_position.x, DIM[2]), ball_velocity), opnt_active_card)
    elif 'my_pre_pos' in ds.keys() and ds['my_pre_pos'] >= DIM[3] // 4 * 3 and ball_position.y >= DIM[3] // 4 * 3:
        ret_V = SpeedCheck(ChooseThePath2(ball_position, Position(opnt_position.x, DIM[3]), ball_velocity), opnt_active_card)
    else:
        ret_V = SpeedCheck(ChooseThePath3(ball_position, ball_velocity), opnt_active_card)
    if not ret_V: ret_V = 0
    return ret_V


def UseCard(TICK, TICK_STEP, SELF, OPNT, BALL, CARD, vx, vy, enemy_y):

    # Data initialization
    self_position, self_life, self_cards = SELF['position'], SELF['life'], SELF['cards']
    opnt_position, opnt_life, opnt_cards = OPNT['position'], OPNT['life'], OPNT['cards']
    opnt_active_card, opnt_run_vector = OPNT['active_card'], OPNT['run_vector']
    ball_position, ball_velocity = BALL['position'], BALL['velocity']
    ball_velocity.x = -ball_velocity.x
    card_cards = CARD['cards']

    # If we have cards for life.
    for card in self_cards:
        if card == CARD_INCL:
            return ('SELF', card)
        elif card == CARD_DECL:
            return ('OPNT', card)

    # If we have no card for life, we can find a card for flash instead.
    if abs(ball_position.y - self_position.y) >= CARD_TLPT_PARAM:
        for card in self_cards:
            if card == CARD_TLPT:
                return ('SELF', card)

    # If we have no card for life or flash, we can find a card for double enemy's consumption at least.
    if abs(enemy_y - opnt_position.y) >= DIM[3] // 2:
        for card in self_cards:
            if card == CARD_AMPL:
                return ('OPNT', card)

    # If enemy doesn't give the ball an acceleration,
    # if the ball will hit the wall 0, 3, 4, 5, 6...times,
    # we use the card for rotation.
    my_y = int(enemy_y + vy * TICK_STEP)
    opnt_collision = 0
    while my_y < DIM[2] or my_y > DIM[3]:
        if my_y < DIM[2]:
            my_y = 2 * DIM[2] - my_y
        else:
            my_y = 2 * DIM[3] - my_y
        opnt_collision += 1
    if not opnt_collision in (1, 2):
        for card in self_cards:
            if card == CARD_SPIN:
                return ('OPNT', card)

    # If we use nothing, or we are in a bad condition, use something.
    # Also, if enemy prefer kicking the ball over the corner, don't use card for disappearation.
    if len(self_cards) == MAX_CARDS or self_life <= opnt_life:
        if self_cards:
            card = random.choice(self_cards)
            for i in range(6):
                if card == CARD_DSPR:
                    card = random.choice(self_cards)
            if card in (CARD_DSPR, CARD_INCL, CARD_TLPT):
                return ('SELF', card)
            else:
                return ('OPNT', card)
    return None


def Positioning(TICK, TICK_STEP, SELF, OPNT, BALL, CARD, ds, nexty):

    # Data initialization
    self_position, self_life, self_cards = SELF['position'], SELF['life'], SELF['cards']
    opnt_position, opnt_life, opnt_cards = OPNT['position'], OPNT['life'], OPNT['cards']
    opnt_active_card, opnt_run_vector = OPNT['active_card'], OPNT['run_vector']
    ball_position, ball_velocity = BALL['position'], BALL['velocity']
    ball_velocity.x = -ball_velocity.x
    card_cards = CARD['cards']

    if EnemyName == 'T_GOLF' and 'my_pre_pos' in ds.keys():
        if ds['my_pre_pos'] <= DIM[3] // 4 * 1 and ball_position.y <= DIM[3] // 4 * 1:
            return (DIM[3] - ball_position.y) // 2
        if ds['my_pre_pos'] >= DIM[3] // 4 * 3 and ball_position.y >= DIM[3] // 4 * 3:
            return (DIM[2] - ball_position.y) // 2
        return 0

    if 'my_pre_pre_pos' in ds and 'my_pre_pos' in ds:
        if ds['my_pre_pre_pos'] <= DIM[3] // 4 * 1 and ds['my_pre_pos'] <= DIM[3] // 4 * 1 and ball_position.y <= DIM[3] // 4 * 1:
            return DIM[3] // 10 * 1 - ball_position.y
        if ds['my_pre_pre_pos'] >= DIM[3] // 4 * 3 and ds['my_pre_pos'] >= DIM[3] // 4 * 3 and ball_position.y >= DIM[3] // 4 * 3:
            return DIM[3] // 10 * 9 - ball_position.y

    if nexty < DIM[3] // 2 and ball_position.y < DIM[3] // 2:
        return DIM[3] // 4 * 1 - ball_position.y
    elif nexty > DIM[3] // 2 and ball_position.y > DIM[3] // 2:
        return DIM[3] // 4 * 3 - ball_position.y
    else:
        return DIM[3] // 2 - ball_position.y


# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb, ds):

    # copy the data
    TICK = tb.tick
    TICK_STEP = tb.step
    SELF = tb.side
    OPNT = tb.op_side
    BALL = tb.ball
    CARD = tb.cards
    if TICK <= TICK_STEP * 2:
        global EnemyName
        EnemyName = OPNT['name']

    # Solve (ALL BELOW)
    RET = RacketAction(tb.tick, BALL['position'].y - SELF['position'].y, 0, DIM[3] // 2 - BALL['position'].y, None, None)

    # Set limitations
    # Collision between once or twice
    limit_v = [int(math.floor((3 * DIM[3] - BALL['position'].y) / TICK_STEP - BALL['velocity'].y)) - 1,
               int(math.ceil((1 * DIM[3] - BALL['position'].y) / TICK_STEP - BALL['velocity'].y)) + 1,
               int(math.floor((0 * DIM[3] - BALL['position'].y) / TICK_STEP - BALL['velocity'].y)) - 1,
               int(math.ceil(((-2) * DIM[3] - BALL['position'].y) / TICK_STEP - BALL['velocity'].y)) + 1]


    # Acceleration
    # First, we try every card we can get, and we finally decide which to get or get nothing.
    ret_V = TryForCards(TICK, TICK_STEP, SELF, OPNT, BALL, CARD, limit_v)

    # OK, now we have dealt with all the cards that we want to get.
    # And we have decide which to get and how to get.
    # If we still have no card to get, we kick to each corner by turn for our enemy.
    if ret_V == None:
        ret_V = KickToCorner(TICK, TICK_STEP, SELF, OPNT, BALL, CARD, ds)
    RET.acc = ret_V

    # Now we have our way to kick the ball.
    # Here we calculate the position our enemy get the ball.
    vx, vy = -BALL['velocity'].x, BALL['velocity'].y + RET.acc
    enemy_y = int(BALL['position'].y + TICK_STEP * vy)
    while enemy_y < DIM[2] or enemy_y > DIM[3]:
        if enemy_y < DIM[2]:
            enemy_y = 2 * DIM[2] - enemy_y
        else:
            enemy_y = 2 * DIM[3] - enemy_y
        vy = -vy

    nexty = enemy_y + vy * TICK_STEP
    while nexty < DIM[2] or nexty > DIM[3]:
        if nexty < DIM[2]:
            nexty = 2 * DIM[2] - nexty
        else:
            nexty = 2 * DIM[3] - nexty
        vy = -vy

    # Use our cards
    ret_Card = UseCard(TICK, TICK_STEP, SELF, OPNT, BALL, CARD, vx, vy, enemy_y)
    if ret_Card != None:
        RET.card = ret_Card

    RET.run = Positioning(TICK, TICK_STEP, SELF, OPNT, BALL, CARD, ds, nexty)

    if 'my_pre_pos' in ds.keys():
        ds['my_pre_pre_pos'] = ds['my_pre_pos']
    ds['my_pre_pos'] = BALL['position'].y
    ds['op_pre_pos'] = OPNT['position'].y
    return RET

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return


# BELIEF OF A PROGRAMMER
#
#          ******            ********
#         *******         ********
#        ***  ***       ****
#       ***   ***      ***
#      ***    ***     ***
#     ***********     ***
#    ************      ***
#   ***       ***       ****
#  ***        ***         ********
# ***         ***            ********
