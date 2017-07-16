from table import *
import random
import math
import shelve
# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side:str,ds: dict) -> tuple:
    if random.randrange (10)>=5:
        return 500000,-278
    else:
        return 500000,278
def play(tb: TableData, ds: dict) -> RacketAction:
    h=1000000
    t=1800
    v0=tb.ball['velocity'].y
    yb0=tb.ball['position'].y
    y0=tb.side['position'].y
    yd=tb.op_side['position'].y
    cardlit = list(tb.side['cards'])
    kg=list(tb.side['cards'])
    cardlit.append('0')#buzhishifoukexing
    max=0
    zuiyoujie = [0, 0]
    listzhongzhang = list(range(int((h - yb0) / t)+1, int((3 * h - yb0) / t)))  # 1
    listzhongzhang = listzhongzhang + list(range(int((-2 * h - yb0) / t)+1, int((-yb0) / t)))
    suoxiaofanwei=[int((h - yb0) / t) + 1, int((2 * h - yb0) / t)-1, int((3 * h - yb0) / t) - 2, int((-yb0) / t) - 1,int((-h - yb0) / t)+1, int((-2 * h - yb0) / t)+1]
    for vy in listzhongzhang:
        for card in tb.cards['cards']:
            if get_card(tb, vy, card):
                suoxiaofanwei.append(vy)
    for vy in suoxiaofanwei:
        cardvy=Output_opposite(tb, yb0, vy, yd,cardlit,ds)
        cardlit = tb.side['cards']
        cardlit.append('0')
        for r in range(len(cardvy)):
            xiaoyi=cardvy[r][1]-Output_us(tb,vy,v0)+DicProfit_Cards(tb,yb0,vy,yd,kg,ds)#计算最优效益
            if max<=xiaoyi:
                max=xiaoyi
                zuiyoujie=[cardvy[r][0],vy]
    if  len(tb.side['cards']) == 0:#判定对哪方使用道具
         who=None
         zuiyoujie[0] =None
    else:
        if zuiyoujie[0]==CARD_AMPL or CARD_DECL or CARD_SPIN:
                 who=tb.op_side['name']
        else:
            if zuiyoujie[0]==CARD_INCL or CARD_TLPT or CARD_DSPR :
                who = tb.side['name']
            else:
                zuiyoujie[0]=tb.side['cards'][0]

    if tb.op_side['active_card'][1] == CARD_SPIN:#判断是否为旋转球
        zuiyoujie[1]=2*(zuiyoujie[1]-v0)+ v0
    else:
        pass
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, zuiyoujie[1]-v0,h/2 - tb.ball['position'].y, who, zuiyoujie[0])
def Output_us(tb,vy,v0):
    k=q=1
    if tb.op_side['active_card'][1]==CARD_SPIN :# 旋转球：用于抵消被用道具方施加在球拍上的加速，使之正常反弹回来；param=0.5，增加的速度乘以parm
        k = 0.5
    else:
        pass
    if tb.op_side['active_card'][1]==CARD_AMPL:#变压器
        q=2
    else:
        pass
    return int(((abs(v0-vy)/k)** 2 / FACTOR_SPEED ** 2) *q)

def Output_opposite(tb,yb0,vy,yd,cardlit,ds):#也可决定使用什么道具
    jieguo = []
    while len(cardlit) !=0 :
        now=cardlit.pop()
        jieguo.append([now,yugu(now,yb0,vy,yd,tb,ds)])
    return jieguo#无卡以None对应

def yugu(card,yb0,vy,yd,tb,ds):
    h=1000000
    t=1800
    jiajianxie=0
    bianyacanliang=1
    if True:#本想使用历史数据判断对方跑位是否在中间，无果后默认对方跑向中间
        if card=='0':
            if vy >= int((h - yb0) / t) + 1 and vy < int((2 * h - yb0) / t):
                return (((2 * h - yb0 - vy * t - 500000) ** 2+(500000-yd)**2) // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
            else:
                if vy >= int((2 * h - yb0) / t) and vy < int((3 * h - yb0) / t):
                    return (((-2 * h + yb0 + vy * t -500000) ** 2 +(500000-yd)**2)// FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                else:
                    if vy >= int((-h - yb0) / t) and vy <= int((-yb0) / t) - 1:
                        return (((- yb0 - vy * t - 500000) ** 2+(500000-yd)**2 )// FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                    else:
                        if vy >= int((-2 * h - yb0) / t) and vy <= int((-h - yb0) / t):
                            return (((2 * h + yb0 + vy * t - 500000) ** 2+(500000-yd)**2) // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                        else:
                            pass
        else:
            if card==CARD_AMPL:
                bianyacanliang=4
            else:
                pass
            if card==CARD_DECL or CARD_INCL:
                jiajianxie=4000
            else:
                pass
            if card==CARD_TLPT:
                distance =min(abs(500000 - tb.ball['position'].y),(tb.side['life']/100000) *1000* t)
            # 减少生命值
                param = 250000
                shunyi=0
                if abs(distance) - param > 0:
                    shunyi= (abs(distance) - param) ** 2 // FACTOR_DISTANCE ** 2
                else:
                    pass
                jiajianxie=(distance**2//FACTOR_DISTANCE**2-shunyi)*2
            else:
                pass
            if card==CARD_SPIN:#旋转
                jiajianxie=1000
            else:
                pass
            if card==CARD_DSPR:#隐身
                jiajianxie=100
            else:
                pass
            if vy >= int((h - yb0) / t) + 1 and vy < int((2 * h - yb0) / t):
                return (((2 * h - yb0 - vy * t - 500000) ** 2+(500000-yd)**2) // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
            else:
                if vy >= int((2 * h - yb0) / t) and vy < int((3 * h - yb0) / t):
                    return (((-2 * h + yb0 + vy * t -500000) ** 2 +(500000-yd)**2)// FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                else:
                    if vy >= int((-h - yb0) / t) and vy <= int((-yb0) / t) - 1:
                        return (((- yb0 - vy * t - 500000) ** 2+(500000-yd)**2 )// FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                    else:
                        if vy >= int((-2 * h - yb0) / t) and vy <= int((-h - yb0) / t):
                            return (((2 * h + yb0 + vy * t - 500000) ** 2+(500000-yd)**2) // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                        else:
                            pass

    else:
        if card=='0':
            if vy >= int((h - yb0) / t) + 1 and vy < int((2 * h - yb0) / t):
                return ((2 * h - yb0 - vy * t - yd) ** 2 // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
            else:
                if vy >= int((2 * h - yb0) / t) and vy < int((3 * h - yb0) / t):
                    return ((-2 * h + yb0 + vy * t - yd) ** 2 // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                else:
                    if vy >= int((-h - yb0) / t) and vy <= int((-yb0) / t) - 1:
                        return ((- yb0 - vy * t - yd) ** 2 // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                    else:
                        if vy >= int((-2 * h - yb0) / t) and vy <= int((-h - yb0) / t):
                            return ((2 * h + yb0 + vy * t - yd) ** 2 // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                        else:
                            pass
        else:
            if card==CARD_AMPL:
                bianyacanliang=4
            else:
                pass
            if card==CARD_DECL or CARD_INCL:
                jiajianxie=4000
            else:
                pass
            if card==CARD_TLPT:
                distance =min(abs(500000 - tb.ball['position'].y),(tb.side['life']/100000) *1000* t)
            # 减少生命值
                param = 250000
                shunyi=0
                if abs(distance) - param > 0:
                    shunyi= (abs(distance) - param) ** 2 // FACTOR_DISTANCE ** 2
                else:
                    pass
                jiajianxie=(distance**2//FACTOR_DISTANCE**2-shunyi)*2
            else:
                pass
            if card==CARD_SPIN:#旋转
                jiajianxie=1000
            else:
                pass
            if card==CARD_DSPR:#隐身
                jiajianxie=100
            else:
                pass
            if vy>=int((h - yb0) / t) + 1 and vy<int((2 * h - yb0) / t):
                return ((2*h-yb0-vy*t-yd)**2//FACTOR_DISTANCE ** 2)*bianyacanliang+jiajianxie
            else:
                if vy >=int((2 * h - yb0) / t) and vy<=int((3 * h - yb0) / t) - 1:
                    return ((-2 * h +yb0 +vy * t - yd) ** 2 // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                else:
                    if vy >int((-h-yb0)/t) and vy <= int((-yb0) / t) - 1:
                        return (( - yb0 - vy * t - yd) ** 2 // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                    else:
                        if vy >=int((-2 * h - yb0) / t) and vy<=int((-h-yb0)/t):
                            return ((2 * h +yb0 +vy * t - yd) ** 2 // FACTOR_DISTANCE ** 2) * bianyacanliang + jiajianxie
                        else:
                            pass

def get_card(tb,vy,cards):
        # 多写点注释。self.pos:(x0,y0),card.pos:(x1,y1),self.velocity:(u,v),self.extent[3]=L
        # 直线方程为 l:-v*x+u*y+v*x0-u*y0=0
        # card经过多次对称后，位置为(x1,±y1+2*k*l)
        # 点到直线距离公式dist=|-v*x1+u*(±y1+2*k*l)+v*x0-u*y0|/|self.velocity|
        # 记-v*x1+u*(±y1)+v*x0-u*y0=A1,A2,u*2*l为delta。则求最短距离，即是求A1%delta,A2%delta,-A1%delta,-A2%delta中最小值，再除以self.velocity的模长。
        A1 = (vy * (-cards.pos.x+tb.ball['position'].x ) + tb.ball['velocity'].x * (cards.pos.y - tb.ball['position'].y))
        A2 = (vy * (-cards.pos.x+tb.ball['position'].x ) + tb.ball['velocity'].x * (-cards.pos.y - tb.ball['position'].y))
        delta = (2 * abs(tb.ball['velocity'].x) * 1000000)
        return min(A1 % delta, -A1 % delta,A2 % delta, -A2 % delta)/ math.sqrt(tb.ball['velocity'].x ** 2 + vy ** 2) < 2000
def fly(tb, vy):  # 球运动，更新位置，并返回触壁次数和路径经过的道具（元组）
        hit_cards=[]
        while len(hit_cards)!=0:
            hit_cards.pop()
            # 判断card.pos，如果球经过的话，就返回count的同时返回所有经过的道具列表，并从list_cards中移除。
        hit_cards = [card for card in tb.cards['cards'] if get_card(tb,vy,card)]
        # 对获得的道具按照获取时间先后进行排序
        if tb.ball['velocity'].x > 0:
            hit_cards.sort(key=lambda card: card.pos.x)
        else:
            hit_cards.sort(key=lambda card: -card.pos.x)
        return hit_cards
        # 从球桌上删除被获取的道具
def DicProfit_Cards(tb,yb0,vy,yd,cardlisttoo,ds):
    if tb.op_side['life']<=27770:
        return 0
    summarynow=0
    for i in range(len(cardlisttoo)):
        summarynow =summarynow +value(cardlisttoo[i],ds)#.code
    cardlistnew=fly(tb,vy)
    cardlistzhongzhang=cardlisttoo +cardlistnew
    cardlistzhongzhang=cardlistzhongzhang[-3:]
    summarynew=0
    for i in range(len(cardlistzhongzhang)):
        summarynew =summarynew+value(cardlistzhongzhang[i],ds)#.code
    return summarynew -summarynow
# 对局后保存历史数据函数 # ds为函数可以利用的存储字典# 本函数在对局结束后调用，用于双方分析和保存历史数据
#我觉得倒不如下面这个函数改编成summarize函数，返回一个包含各个道具及其等价体力值的字典
#该函数计算每一个道具的等价体力值
def value(card,ds):#ds自行传入我方或对方历史数据，这里应该传入对方历史数据tb.op_side.datastore
    if card=='0':
        return 0
    else:
        pass
    #当道具为加血包或掉血包时
    if card in [CARD_INCL,CARD_DECL]:
        return 2000
    else:
        pass
    #当道具为隐身术时
    if card == CARD_DSPR:
        return 1
    else:
        pass

    #当道具为瞬移术
    if card == CARD_TLPT:
        return 456
    else:
        pass
    # return 456
    #当道具为旋转球时
    if card == CARD_SPIN:
        CARD_SPIN_EQUALLIFE =3*200     #经过与T_peilian的对战，发现每次T_peilian的acc_lf平均值大致为200，使用旋转球后需乘以3
        #当ds为空时
        if not ds:
            return CARD_SPIN_EQUALLIFE
        #当ds不为空时
        else:
            #通过历史数据计算平均值得到相应等价体力值
            #暂时不知如何引用，这里用list（ds[acc_lf]）表示对方每回合的acc_lf组成的列表
            CARD_SPIN_EQUALLIFE = (sum(list(ds[acc_lf]))//len(list(ds[acc_lf])))*3
            return CARD_SPIN_EQUALLIFE
    else:
        pass
    if card == CARD_AMPL:
        CARD_AMPL_EQUALLIFE =620 + 200    #经过与T_peilian的对战，发现每次T_peilian的bat_lf和acc_lf平均值大致为620和200
        if not ds:
            return CARD_AMPL_EQUALLIFE
        else:
            CARD_AMPL_EQUALLIFE = (sum(list(ds[bat_lf]))+sum(list(ds[acc_lf])))//len(list(ds[acc_lf]))
            return CARD_AMPL_EQUALLIFE
    else:
        pass
def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return
