from table import *
import math
import random
def serve(op_side: str, ds: dict) -> tuple:
    return BALL_POS[1], 278

def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return

def interesting(tb,direction):
      if direction == 'down':
        vy1 = (2000000 - tb.side['position'].y) // 1800-1
        vy2 = (-tb.side['position'].y - 2000000) // 1800+1
        acc_vy1 = vy1 -tb.ball['velocity'].y
        acc_vy2 = vy2 -tb.ball['velocity'].y
        if (abs(acc_vy1) > abs(acc_vy2)):
            acc_vy = acc_vy2
        else: acc_vy= acc_vy1
      if direction == 'up' :
        vy1 = (-tb.side['position'].y - 1000000) // 1800+1
        vy2 = (3000000 - tb.side['position'].y) // 1800-1
        acc_vy1 = vy1-tb.ball['velocity'].y
        acc_vy2 = vy2-tb.ball['velocity'].y
        if (abs(acc_vy1) > abs(acc_vy2)):
            acc_vy = acc_vy2
        else: acc_vy= acc_vy1
      return acc_vy

def batting(tb):
    if tb.op_side['run_vector'] == None:
        acc_vy =-50
    else :
        if tb.op_side['run_vector'] == -1:
            op_life1 = (tb.op_side['position'].y)**2 // 400000000
            op_life2 = ((1000000 - tb.op_side['position'].y))**2 // 800000000
            my_life1 =  interesting(tb,'down')*interesting(tb,'down')//400
            my_life2 =  interesting(tb,'up')*interesting(tb,'up')//400
            x=[op_life1,op_life2,my_life1,my_life2]
            y=sorted(x)
            if y[3] == my_life1 and y[2]==my_life2: #如果我方加速耗费体力大于对方跑位体力则不加速，反之则采取最好的加速
                if op_life1-my_life1 >= my_life2-op_life2:
                    acc_vy = interesting(tb,'down')
                else:
                    acc_vy = interesting(tb,'up')
            elif y[3]==my_life2 and y[2]==my_life1:
                if op_life1-my_life1 >= my_life2-op_life2:
                    acc_vy = interesting(tb,'down')
                else:
                    acc_vy = interesting(tb,'up')
            else:
                acc_vy= random.randint(-100,100)
        else:
            op_life1 =( tb.op_side['position'].y )**2//800000000
            op_life2 = ((1000000 - tb.op_side['position'].y))**2 // 400000000
            my_life1 = interesting(tb, 'down') * interesting(tb, 'down') // 400
            my_life2 = interesting(tb, 'up') * interesting(tb, 'up') // 400
            x = [op_life1, op_life2, my_life1, my_life2]
            y = sorted(x)
            if y[3] == my_life1 and y[2]==my_life2:
                if op_life1-my_life1 >= my_life2-op_life2:
                    acc_vy = interesting(tb,'down')
                else:
                    acc_vy = interesting(tb,'up')
            elif y[3]==my_life2 and y[2]==my_life1:
                if op_life1-my_life1 >= my_life2-op_life2:
                    acc_vy = interesting(tb,'down')
                else:
                    acc_vy = interesting(tb,'up')
            else:
                acc_vy=interesting(tb,'up')
    return acc_vy
def play(tb,ds):
    global new_ball_speed
    op_y = tb.op_side['position'].y
    x = tb.side['position'].x
    y = tb.side['position'].y
    ball_speed = tb.ball['velocity'].y
    ball_pos = tb.ball['position'].y
    card_box = tb.side['cards']
    now_tick = tb.tick
    hit_point = tb.ball['position'].y
    now_point = tb.side['position'].y
    bat_distance = hit_point - now_point
    bat_vector = bat_distance
    acc_vector = batting(tb)
    if sign(bat_distance) == 1:
        run_vector = -1
    else:
        run_vector = 1
    max = 0
    speed = 1000
    direction = 0
    choice_v = []
    for acard in tb.cards['cards']:
        if acard == 'IL' or acard == 'DL' or acard == 'AM':
            cardv = Vector(acard.pos.x, acard.pos.y)
            k = (cardv.y - y) / (cardv.x - x)
            if abs(k) <= 1.1 and abs(k) >= 0.6:
                choice_v.append(k)
            k = (2 * DIM[3] - cardv.y - y) / (cardv.x - x)
            if abs(k) <= (3 * DIM[3] - y) / 1800:
                choice_v.append(k)
    if len(choice_v) != 0:
        s = choice_v[0]
        for v in choice_v:
            if abs(v) < abs(s):
                s = v
        if CARD_SPIN in card_box:
            return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, s, run_vector, tb.op_side, CARD_SPIN)
        elif CARD_DSPR in card_box:
            return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, s,run_vector, tb.side, CARD_DSPR)
        elif CARD_INCL in card_box:
            return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, s, run_vector, tb.side, CARD_INCL)
        elif CARD_TLPT in card_box:
            return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, s, run_vector, tb.side, CARD_TLPT)
        elif CARD_DECL in card_box:
            return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, s, run_vector, tb.op_side, CARD_DECL)
        else:
            return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, s, run_vector, None, None)
    now_tick = tb.tick
    hit_point = tb.ball['position'].y
    now_point = tb.side['position'].y
    bat_distance = hit_point - now_point
    bat_vector = bat_distance
    acc_vector = batting(tb)
    if sign(bat_distance) == 1:
        run_vector = -1
    else:
        run_vector = 1
    now_card = tb.cards['cards']
    while len(now_card)!=0:
        if now_card[0] == 'SP':
            user = tb.side['name']
            card = now_card.pop(0)
            break
        elif now_card[0] == 'DS':
            user = tb.side['name']
            card = now_card.pop(0)
            break
        elif now_card[0] == 'IL':
            user = tb.side['name']
            card = now_card.pop(0)
            break
        elif now_card[0] == 'DL':
            user = tb.op_side['name']
            card = now_card.pop(0)
            break
        elif now_card[0] == 'TP':
            user = tb.side['name']
            card = now_card.pop(0)
            break
        else:
            user = tb.op_side['name']
            card = now_card.pop(0)
            break
    else:
        user = None
        card = None
   # ds.append()
    return RacketAction(now_tick,bat_vector,acc_vector,run_vector,user,card)
