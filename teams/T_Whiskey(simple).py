# -*- coding: utf-8 -*-
from table import *
import random
import math
# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side,ds):
    #发球策略：站在场地中间，节省一次跑位，随机一个速度发球
    pos=DIM[3]/2
    #计算速度的上下界
    top_speend=int((2*DIM[3]+pos)/(2*DIM[1]/BALL_V[0]))
    min_speend=int((pos)/(2*DIM[1]/BALL_V[0]))
    #随机速度方向
    speed_sign=random.randrange(-1, 2,2)
    speed=random.randint(min_speend,top_speend)
    return pos,speed*speed_sign
# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb, ds):
    #贪心使用道具，有道具就用
    card_for_me=None
    card_for_enemy=None
    use_tp=0
    use_am=1
    if  len(tb.side['cards']) >0:
        active_card=tb.side['cards'][0].code
        if active_card==CARD_DSPR:
            card_for_me=CARD_DSPR
        elif active_card==CARD_INCL:
            card_for_me=CARD_INCL
        elif active_card==CARD_DECL:
            card_for_enemy=CARD_DECL
        elif active_card==CARD_TLPT:
            card_for_me=CARD_TLPT
            use_tp=1
        elif active_card==CARD_AMPL:
            card_for_enemy=CARD_AMPL
            use_am=2
    ##获取敌方信息和我方信息
    my_life=tb.side['life']
    not_know_enemy=0
    if tb.op_side!=None:
        enemy_life=tb.op_side['life']
        enemy_pos=tb.op_side['position'].y
    else:
        not_know_enemy=1
    ball_speed=tb.ball['velocity'].y
    acc=0
    ##通过穷举加速度的可能性，按照地方当前位置和我方回球位置，计算每次我方loss和敌方loss，取最大值作为这次的击球策略。
    if not_know_enemy!=1:
        gain=0.0
        select_speed=0.0    
        up_dis=DIM[3]-tb.ball['position'].y
        top_speed=int((2*DIM[3]+up_dis)/(2*DIM[1]/BALL_V[0]))
        min_speed=int(up_dis/(2*DIM[1]/BALL_V[0]))
        for speed in range(min_speed+1,top_speed-1):
            vir_dis=speed*(2*DIM[1]/BALL_V[0])-up_dis
            if vir_dis<DIM[3]:
                final_pos=DIM[3]-vir_dis
            else:
                final_pos=vir_dis-DIM[3]
            enemy_loss=abs(enemy_pos-final_pos)**2//FACTOR_DISTANCE ** 2*use_am
            my_loss=abs(speed-ball_speed)**2//FACTOR_SPEED ** 2
            if my_loss<my_life:##不能加速把自己加死
                continue
            tmp_gain=enemy_loss-my_loss  
            if tmp_gain>gain:
                gain=tmp_gain
                select_speed=speed
        down_dis=tb.ball['position'].y-DIM[3]
        top_speed=int((2*DIM[3]+down_dis)/(2*DIM[1]/BALL_V[0]))
        min_speed=int(down_dis/(2*DIM[1]/BALL_V[0]))
        for speed in range(min_speed+1,top_speed-1):
            vir_dis=speed*(2*DIM[1]/BALL_V[0])-down_dis
            if vir_dis<DIM[3]:
                final_pos=vir_dis
            else:
                final_pos=2*DIM[3]-vir_dis 
            enemy_loss=abs(enemy_pos-final_pos)**2//FACTOR_DISTANCE ** 2*use_am
            my_loss=abs(speed-ball_speed)**2//FACTOR_SPEED ** 2
            if my_life<my_loss:
                continue
            tmp_gain=enemy_loss-my_loss
            if tmp_gain>gain:
                gain=tmp_gain
                select_speed=speed
        #确定最终的加速度
        acc=speed-ball_speed
    run=0
    #在出现55%的死角之前，不跑位，只根据敌方回球位置迎球。有死角之后，每次打完球回到正中间，这样回球的时候期望距离最小。
    if my_life<55000:
        run=500000-tb.ball['position'].y
        minus_life=(abs(run) ** 2 // FACTOR_DISTANCE ** 2)
        if minus_life>(my_life/2):
	    print run,minus_life,my_life
            run=0
	print run,minus_life,my_life
    if use_tp:
        run=500000-tb.ball['position'].y
    print run
    if card_for_me==None and card_for_enemy==None:    
        return RacketAction(tb.tick, float(tb.ball['position'].y - tb.side['position'].y), acc, run, None, None)
    elif card_for_me!=None:
        return RacketAction(tb.tick, float(tb.ball['position'].y - tb.side['position'].y), acc, run, tb.side, card_for_me)
    else:
        return RacketAction(tb.tick, float(tb.ball['position'].y - tb.side['position'].y), acc, run, tb.op_side, card_for_enemy)
def summarize(tick, winner, reason, west, east, ball, ds):
	return







