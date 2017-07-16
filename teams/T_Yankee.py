from table import *
import random

def serve(name,ds):
    i = random.randint(1,10)#防止对方的ds学习我方的发球规则
    if i%2==0:
       return 0,1666#从最下角发球，打到对方右上角

    else:
       return 1000000,-1666 # 从最左上角发球，打到对方的右下角

def summarize(tick, winner, reason, west, east, ball, ds):
    ds["balldata"]=list()#配合ds学习步骤出现，每局比赛结束后更新"balldata"这个key对应的value
    return

def play(tb,ds):

    distance_y = tb.ball["position"].y#从tabledata中读取球的落点
    bat_distance = distance_y - tb.side["position"].y#拍的运动距离

    run_distance = distance_y - DIM[3]/2#从我方所在的中间位置去往落点的距离
#以下为ds学习的步骤
    if "balldata" not in ds:#刚开始和某组进行对决需要判断是不是有这个key值
        ds["balldata"] = list()#没有这个key值就可以新建一个key-value对来储存每次的落点
    else:
        ds["balldata"].append(tb.ball["position"].y)
        n = len(ds["balldata"])#列表中的数据总数
        flag1 = True  # 设立flag
        for i in ds["balldata"]:  # 判断打角
            if i <= 990000 and i >= 10000:
                flag1 = False
        if flag1 == True:
            if n == 4:  # 判断保守型打法
                flag = True  # 设立flag
                if tb.ball["position"].y > 500000:
                    for i in ds["balldata"]:
                        if i < 990000:
                            flag = False
                else:
                    for i in ds["balldata"]:
                        if i > 10000:
                            flag = False
                if flag == False:
                    run_distance = 0  # 打角且保守型打法直接不跑位


                #下面为6种可能路径长度的计算：
    select1_dis = math.sqrt(distance_y**2 + (DIM[1]-DIM[0])**2)
    select2_dis = math.sqrt((DIM[3]-distance_y)**2 + (DIM[1]-DIM[0])**2)
    select3_dis = math.sqrt((distance_y + DIM[3])**2 + (DIM[1]-DIM[0])**2)
    select4_dis = math.sqrt((DIM[3]-distance_y+DIM[3])**2 + (DIM[1]-DIM[0])**2)
    select5_dis = math.sqrt((distance_y + 2*DIM[3])**2 + (DIM[1]-DIM[0])**2)
    select6_dis = math.sqrt((DIM[3]-distance_y + 2*DIM[3])**2 + (DIM[1]-DIM[0])**2)
#计算6种路径的加速度值：
    var = [0 for x in range(6)]
    var[0] = -math.sqrt((select1_dis / 1800) ** 2 - BALL_V[0] ** 2)-2
    var[1] = math.sqrt((select2_dis / 1800) ** 2 - BALL_V[0] ** 2)+2
    var[2] = -math.sqrt((select3_dis / 1800) ** 2 - BALL_V[0] ** 2)-2
    var[3] = math.sqrt((select4_dis / 1800) ** 2 - BALL_V[0] ** 2)+2
    var[4] = -math.sqrt((select5_dis / 1800) ** 2 - BALL_V[0] ** 2)+2
    var[5] = math.sqrt((select6_dis / 1800) ** 2 - BALL_V[0] ** 2)-2

    base = abs(var[0] - tb.ball['velocity'].y)
    base2 = var[0]
    for i in range(6):#找出所需要采取的最佳回球方式
        if abs(var[i] - tb.ball['velocity'].y) < base:
            base = abs(var[i] - tb.ball['velocity'].y)
            base2 = var[i] - tb.ball['velocity'].y
    new_vectority = tb.ball["velocity"].y + base2#一般情况下计算得出的新速度
    base=base2

    y0=tb.ball["position"].y
    v0=tb.ball["velocity"].y
    for i in tb.cards["cards"]:
        x1 = i.pos.x
        y1 = i.pos.y
        if tb.ball["velocity"].x<0:#我方处于west方：
            # 小于0，以下为需要用到的，经过计算得出的参数
            element1 = -1000 - y0
            element2 = 1000 - y0
            v1 = (element1 + y1) / (x1 + 900000) * 1000
            v2 = (element2 + y1) / (x1 + 900000) * 1000
            v3 = (element1 - y1) / (x1 + 900000) * 1000
            v4 = (element2 - y1) / (x1 + 900000) * 1000
            v5 = (element1 - 2000000 + y1) / (x1 + 900000) * 1000
            v6 = (element2 - 2000000 + y1) / (x1 + 900000) * 1000  # 按照y方向菱形的计算
            element3 = (900000 + x1 - 1000) / 1000
            element4 = (900000 + x1 + 1000) / 1000
            v7 = (y1 - y0) / element3
            v8 = (y1 - y0) / element4
            v9 = (-y1 - y0) / element3
            v10 = (-y1 - y0) / element4
            v11 = (-2000000 + y1 - y0) / element3
            v12 = (-2000000 + y1 - y0) / element4  # 按照x方向菱形的计算
            # 大于0
            element5 = (x1 + 900000) / 1000
            v13 = (y1 - 1000 - y0) / element5
            v14 = (y1 - y0 + 1000) / element5
            v15 = (2000000 - y1 - 1000 - y0) / element5
            v16 = (2000000 - y1 + 1000 - y0) / element5
            v17 = (2000000 + y1 - 1000 - y0) / element5
            v18 = (2000000 + y1 + 1000 - y0) / element5  # 按照菱形的y方向
            element6 = (x1 + 900000 + 1000) / 1000
            element7 = (x1 - 1000 + 900000) / 1000
            v19 = (y1 - y0) / element6
            v20 = (y1 - y0) / element7
            v21 = (2000000 - y1 - y0) / element6
            v22 = (2000000 - y1 - y0) / element7
            v23 = (2000000 + y1 - y0) / element6
            v24 = (2000000 + y1 - y0) / element7  # 按照菱形的x方向
            acc = [0 for i in range(13)]  # 上面前12个速度分别求加速度
            acc[1] = v1 - v0
            acc[2] = v2 - v0
            acc[3] = v3 - v0
            acc[4] = v4 - v0
            acc[5] = v5 - v0
            acc[6] = v6 - v0
            acc[7] = v7 - v0
            acc[8] = v8 - v0
            acc[9] = v9 - v0
            acc[10] = v10 - v0
            acc[11] = v11 - v0
            acc[12] = v12 - v0
            min = abs(acc[1])  # 加速度的绝对值
            min_used = acc[1]  # 最终需要确定的加速度
            acc2 = [0 for i in range(13)]
            acc2[1] = v13 - v0
            acc2[2] = v14 - v0
            acc2[3] = v15 - v0
            acc2[4] = v16 - v0
            acc2[5] = v17 - v0
            acc2[6] = v18 - v0
            acc2[7] = v19 - v0
            acc2[8] = v20 - v0
            acc2[9] = v21 - v0
            acc2[10] = v22 - v0
            acc2[11] = v23 - v0
            acc2[12] = v24 - v0
            min2 = abs(acc2[1])
            min2_used = acc2[1]


            if i.code == CARD_INCL:  # 补血包代价计算
                PAY = 1  # 补血包加血的权重

                if new_vectority < 0:
                    if v1 < new_vectority < v2 or v3 < new_vectority < v4 or v5 < new_vectority < v6 or v7<new_vectority <v8 or v9<new_vectority< v10 or v11<new_vectority <v12:#当本来模拟出的速度正好能打到道具
                        pass
                    else:
                        for i in range(1,13):#这个循环是为了找出符合1~2次碰壁标准的最小加速度
                            if v0+acc[i] >= var[0] or v0+acc[i] <= var[4]:
                                continue
                            if abs(acc[i]) <= min:
                                min = abs(acc[i])
                                min_used = acc[i]
                        if (min_used / 20) ** 2 <= PAY * 2000:#如果这个最小加速度的值被认为是值得我们去打的
                            base = min_used
                        else:#不值得花体力打
                            pass
                else:
                    if v13<new_vectority <v14 or v15 < new_vectority<v16 or v17<new_vectority <v18 or v19<new_vectority< v20 or v21<new_vectority<v22 or v23<new_vectority<v24:
                        pass
                    else:
                        for i in range(1, 13):  # 这个循环是为了找出符合1~2次碰壁标准的最小加速度
                            if v0 + acc2[i] >= var[5] or v0 + acc2[i] <= var[1]:
                                continue
                            if abs(acc2[i]) <= min2:
                                min2 = abs(acc2[i])
                                min2_used = acc2[i]
                        if (min2_used / 20) ** 2 <= PAY * 2000:# 如果这个最小加速度的值被认为是值得我们去打的
                            base = min2_used
                        else:  # 不值得花体力打
                            pass

            elif i.code == CARD_TLPT:  # 掉血包代价计算
                PAY = 1  #掉血包掉血的权重

                if new_vectority < 0:
                    if v1 < new_vectority < v2 or v3 < new_vectority < v4 or v5 < new_vectority < v6 or v7<new_vectority <v8 or v9<new_vectority< v10 or v11<new_vectority <v12:
                        pass
                    else:
                        for i in range(1,13):#这个循环是为了找出符合1~2次碰壁标准的最小加速度
                            if v0+acc[i] >= var[0] or v0+acc[i] <=  var[4]:
                                continue
                            if abs(acc[i]) <= min:
                                min = abs(acc[i])
                                min_used = acc[i]
                        if (min_used / 20) ** 2 <= PAY * 2000:#如果这个最小加速度的值被认为是值得我们去打的
                            base = min_used
                        else:#不值得花体力打
                            pass
                else:
                    for i in range(1, 13):  # 这个循环是为了找出符合1~2次碰壁标准的最小加速度
                        if v0 + acc2[i] >= var[5] or v0 + acc2[i] <= var[1]:
                            continue
                        if abs(acc2[i]) <= min2:
                            min2 = abs(acc2[i])
                            min2_used = acc2[i]
                    if (min2_used / 20) ** 2 <= PAY * 2000:  # 如果这个最小加速度的值被认为是值得我们去打的
                        base = min2_used
                    else:  # 不值得花体力打
                        pass

        else:#我方处于east方
            # 小于0，以下为east方的参数
            element1 = -1000 - y0
            element2 = 1000 - y0
            v1 = (element1 + y1) / (900000 - x1) * 1000
            v2 = (element2 + y1) / (900000 - x1) * 1000
            v3 = (element1 - y1) / (900000 - x1) * 1000
            v4 = (element2 - y1) / (900000 - x1) * 1000
            v5 = (element1 - 2000000 + y1) / (900000 - x1) * 1000
            v6 = (element2 - 2000000 + y1) / (900000 - x1) * 1000 # 按照y方向菱形的计算
            element3 = (900000 - x1 - 1000) / 1000
            element4 = (900000 - x1 + 1000) / 1000
            v7 = (y1 - y0) / element3
            v8 = (y1 - y0) / element4
            v9 = (-y1 - y0) / element3
            v10 = (-y1 - y0) / element4
            v11 = (-2000000 + y1 - y0) / element3
            v12 = (-2000000 + y1 - y0) / element4  # 按照x方向菱形的计算
            # 大于0
            element5 = (-x1 + 900000) / 1000
            v13 = (y1 - y0 - 1000 ) / element5
            v14 = (y1 - y0 + 1000) / element5
            v15 = (2000000 - y1 - 1000 - y0) / element5
            v16 = (2000000 - y1 + 1000 - y0) / element5
            v17 = (2000000 + y1 - 1000 - y0) / element5
            v18 = (2000000 + y1 + 1000 - y0) / element5  # 按照菱形的y方向
            element6 = (-x1 + 900000 + 1000) / 1000
            element7 = (-x1 + 900000 - 1000) / 1000
            v19 = (y1 - y0) / element6
            v20 = (y1 - y0) / element7
            v21 = (2000000 - y1 - y0) / element6
            v22 = (2000000 - y1 - y0) / element7
            v23 = (2000000 + y1 - y0) / element6
            v24 = (2000000 + y1 - y0) / element7  # 按照菱形的x方向
            acc = [0 for i in range(13)]  # 上面前12个速度分别求加速度
            acc[1] = v1 - v0
            acc[2] = v2 - v0
            acc[3] = v3 - v0
            acc[4] = v4 - v0
            acc[5] = v5 - v0
            acc[6] = v6 - v0
            acc[7] = v7 - v0
            acc[8] = v8 - v0
            acc[9] = v9 - v0
            acc[10] = v10 - v0
            acc[11] = v11 - v0
            acc[12] = v12 - v0
            min = abs(acc[1])  # 加速度的绝对值
            min_used = acc[1]  # 最终需要确定的加速度
            acc2 = [0 for j in range(13)]
            acc2[1] = v13 - v0
            acc2[2] = v14 - v0
            acc2[3] = v15 - v0
            acc2[4] = v16 - v0
            acc2[5] = v17 - v0
            acc2[6] = v18 - v0
            acc2[7] = v19 - v0
            acc2[8] = v20 - v0
            acc2[9] = v21 - v0
            acc2[10] = v22 - v0
            acc2[11] = v23 - v0
            acc2[12] = v24 - v0
            min2 = abs(acc2[1])
            min2_used = acc2[1]

            if i.code == CARD_INCL:  # 补血包代价计算
                PAY = 1  # 补血包加血的权重

                if new_vectority < 0:
                    if v1 < new_vectority < v2 or v3 < new_vectority < v4 or v5 < new_vectority < v6 or v7 < new_vectority < v8 or v9 < new_vectority < v10 or v11 < new_vectority < v12:  # 当本来模拟出的速度正好能打到道具
                        pass
                    else:
                        for i in range(1, 13):  # 这个循环是为了找出符合1~2次碰壁标准的最小加速度
                            if v0 + acc[i] >= var[1] or v0 + acc[i] <= var[4]:
                                continue
                            if abs(acc[i]) <= min:
                                min = abs(acc[i])
                                min_used = acc[i]
                        if (min_used / 20) ** 2 <= PAY * 2000:  # 如果这个最小加速度是值得我们去打的
                            base = min_used
                        else:  # 不值得花体力打
                            pass
                else:
                    if v13 < new_vectority < v14 or v15 < new_vectority < v16 or v17 < new_vectority < v18 or v19 < new_vectority < v20 or v21 < new_vectority < v22 or v23 < new_vectority < v24:
                        pass
                    else:
                        for i in range(1, 13):  # 这个循环是为了找出符合1~2次碰壁标准的最小加速度
                            if v0 + acc2[i] >= var[5] or v0 + acc2[i] <= var[1]:
                                continue
                            if abs(acc2[i]) <= min2:
                                min2 = abs(acc2[i])
                                min2_used = acc2[i]
                        if (min2_used / 20) ** 2 <= PAY * 2000:  # 如果这个最小加速度的值被认为是值得我们去打的
                            base = min2_used
                        else:  # 不值得花体力打
                            pass

            elif i.code == CARD_TLPT:  # 掉血包代价计算
                PAY = 1  # 掉血包掉血的权重

                if new_vectority < 0:
                    if v1 < new_vectority < v2 or v3 < new_vectority < v4 or v5 < new_vectority < v6 or v7 < new_vectority < v8 or v9 < new_vectority < v10 or v11 < new_vectority < v12:
                        pass
                    else:
                        for i in range(1, 13):  # 这个循环是为了找出符合1~2次碰壁标准的最小加速度
                            if v0 + acc[i] >= var[0] or v0 + acc[i] <= var[4]:
                                continue
                            if abs(acc[i]) <= min:
                                min = abs(acc[i])
                                min_used = acc[i]
                        if (min_used / 20) ** 2 <= PAY * 2000:  # 如果这个最小加速度的值被认为是值得我们去打的
                            base = min_used
                        else:  # 不值得花体力打
                            pass
                else:
                    for i in range(1, 13):  # 这个循环是为了找出符合1~2次碰壁标准的最小加速度
                        if v0 + acc2[i] >= var[5] or v0 + acc[i] <= var[1]:
                            continue
                        if abs(acc2[i]) <= min2:
                            min2 = abs(acc2[i])
                            min2_used = acc2[i]
                    if (min2_used / 20) ** 2 <= PAY * 2000:  # 如果这个最小加速度的值被认为是值得我们去打的
                        base = min2_used
                    else:  # 不值得花体力打
                        pass

    if tb.op_side["active_card"] == (CARD_SPIN, CARD_SPIN_PARAM):#假如对方使用了旋转球
        if tb.ball["velocity"].y > 0:
            if tb.ball["velocity"].y > var[1] and tb.ball["velocity"].y  < var[5]:
                base=0#在区间内就不加速
            else:
                a1=var[1]
                a2=var[5]
                if abs(a1)>=abs(a2):
                    base=2*a2#抵消旋转球的0.5
                else:
                    base=2*a1
        else:
            if tb.ball["velocity"].y > var[4] and tb.ball["velocity"].y < var[0]:
                base = 0#在区间内就不加速
            else:
                a1=var[4]
                a2=var[0]
                if abs(a1)>=abs(a2):
                    base=2*a2#抵消旋转球的0.5
                else:
                    base=2*a1

    side1,use_card = None,None
    cardlist = tb.side['cards']
    if (CARD_INCL, CARD_INCL_PARAM) in cardlist:
        if tb.side['life'] <= 98000:#防止加血溢出
            use_card = (CARD_INCL, CARD_INCL_PARAM)
            side1 = "SELF"
        else:#血包暂时被放到最优先的保存位置，防止被更新掉
            pos_IL=cardlist.index((CARD_INCL, CARD_INCL_PARAM))
            cardlist[pos_IL],cardlist[2]=cardlist[2],cardlist[pos_IL]
    if (CARD_DECL, CARD_DECL_PARAM) in cardlist:  # 掉血术
        use_card = (CARD_DECL, CARD_DECL_PARAM)
        side1 = "OPNT"
    if (CARD_AMPL, CARD_AMPL_PARAM) in cardlist:#变压器
        use_card = (CARD_AMPL, CARD_AMPL_PARAM)
        side1 = "OPNT"
    if (CARD_SPIN, CARD_SPIN_PARAM) in cardlist:#旋转球
        use_card = (CARD_SPIN, CARD_SPIN_PARAM)
        side1 = "OPNT"
    if (CARD_TLPT, CARD_TLPT_PARAM) in cardlist:  # 瞬移术
        use_card = (CARD_TLPT, CARD_TLPT_PARAM)
        side1 = "SELF"
    if (CARD_DSPR, CARD_DSPR_PARAM) in cardlist:#隐身术
        use_card = (CARD_DSPR, CARD_DSPR_PARAM)
        side1 = "SELF"

    return RacketAction(tb.tick,bat_distance,base,run_distance,side1,use_card)
