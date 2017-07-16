from table import *

# 发球函数，总是做为West才发球
# op_side为对手方名称，以便从ds中查询以往记录数据
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side: str, ds: dict) -> tuple:
    if (ds == {}):
        ds = {'pre':[] ,'now':[]}
    originalposition = (DIM[3] - DIM[2]) / 2
    originalvelocity = int((originalposition) / ((DIM[1] - DIM[0]) / BALL_V[0])) + 1
    ds['now'].append((op_side,BALL_POS[1],BALL_V[1]))
    return originalposition, originalvelocity  # 返回球的y坐标，和y方向上的速度

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb:TableData, ds:dict) -> RacketAction:
    # 设定字典
    if (ds == {}):
        ds = {'pre':[] ,'now':[]}
    # 道具使用优先级，4最优先
    CardUsing = {'IL':4 ,'DL':4 ,'TP':4 ,'AM':3 ,'SP':2 ,'DS':1}
    # 道具价值
    CardValue = {'TP':2500 ,'IL':2000 ,'DL':2000 ,'AM':1500 ,'SP':1200 ,'DS':1000}
    # 来球信息
    pos = tb.ball['position']                 # 来球位置
    vel = tb.ball['velocity']                 # 来球速度
    # 对手信息
    op_lif = tb.op_side['life']               # 生命
    op_pos = tb.op_side['position'].y        # 位置
    op_car = tb.op_side['cards']              # 道具箱
    op_acc = tb.op_side['accelerate']        # 加速
    op_act_car = tb.op_side['active_card']   # 用的道具
    op_run = tb.op_side['run_vector']        # 跑位
    # 我方信息
    my_lif = tb.side['life']                 # 生命
    my_pos = tb.side['position'].y          # 位置
    my_car = tb.side['cards']                # 道具箱
    # 球桌信息
    tb_car = tb.cards['cards']                # 桌上有什么道具
    tb_car_tic = tb.cards['card_tick']       # 道具沙漏
    y = DIM[3] - DIM[2]                      # 球桌的宽
    x = DIM[1] - DIM[0]                      # 球桌的长
    # 分析出球速度
    t = x / vel.x    # 球的飞行时间
    vy_max_nor = int((3 * y - pos.y) / t) - 100    # 球向北击出的最大速度（正值）
    vy_min_nor = int((y - pos.y) / t) + 100    # 球向北击出的最小速度（正值）
    vy_max_sou = -(int((2 * y + pos.y) / t)) + 100    # 球向南击出的最大速度（负值）
    vy_min_sou = -(int(pos.y / t)) - 100    # 球向南击出的最小速度（负值）
    # 迎球
    bat = pos.y - my_pos
    # 用道具
    card_use = None
    card_side = None
    if (len(my_car) > 0):    # 如果我方有道具
        card_use = my_car[0]
        for c in my_car:    # 就选出优先级最高的来用
            if (CardUsing[c.code] > CardUsing[card_use.code]):
                card_use = c
    if (card_use != None):    # 如果我方有道具，就选择被用道具方
        if (card_use.code in ['DS','IL','TP']):    # 隐身、加血、瞬移用于我们自己
            card_side = 'SELF'
        else:
            card_side = 'OPNT'
    # 捡道具
    pick = False  # 捡道具标志
    pick_car = []    # 把桌上所有应该捡的道具存入该列表
    car_pick = None    # 最终捡的道具
    if (len(tb_car) > 0):  # 如果桌子上有道具
        if (my_car.isfull()): # 如果我方道具箱已满，就和要溢出的道具进行价值比较
            for c in tb_car:  # 对桌上的道具循环
                if (CardValue[my_car[0].code] < CardValue[c.code]):  # 如果比要溢出的道具有价值就加入捡的列表
                    pick_car.append(c)
            if (pick_car != []):    # 如果有应捡道具在列表中
                pick = True    # 将捡道具标志设为True
                for i in range(len(pick_car)):    # 用冒泡法将列表中的道具按价值从大到小排序
                    for j in range(i, len(pick_car)):
                        if (CardValue[pick_car[i].code] < CardValue[pick_car[j].code]):
                            pick_car[i], pick_car[j] = pick_car[j], pick_car[i]
        else:  # 如果道具箱没满，就将桌上所有道具存入列表
            pick = True    # 标记为TRUE
            pick_car = tb_car    # 将桌上所有道具存入列表
            for i in range(len(tb_car)):    # 用冒泡法按其价值从大到小排序
                for j in range(i,len(tb_car)):
                    if (CardValue[pick_car[i].code] < CardValue[pick_car[j].code]):
                        pick_car[i],pick_car[j] = pick_car[j],pick_car[i]
    # 加速
    if (op_lif > 0.35 * RACKET_LIFE):    # 如果对方生命大于55.5%
        if (op_act_car[1] != CARD_DSPR):    # 如果对方没有使用隐身术
            if (op_pos >= ((5 * y) // 8)):    # 如果对方迎球位置在5/8处以上
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他向北跑位至可跑距离的1/4处
                    op_new_pos = op_pos + ((y - op_pos) // 4)
                else:    # 如果对方向南跑位，就假设他归中
                    op_new_pos = y // 2
            elif (op_pos <= ((3 * y) // 8)):    # 如果对方迎球位置在3/8处以下
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他归中
                    op_new_pos = y // 2
                else:    # 如果对方向南跑位，就假设他向南跑位至可跑距离的1/4处
                    op_new_pos = op_pos - (op_pos // 4)
            elif ((op_pos < ((5 * y) // 8)) and (op_pos > (y // 2))):    # 如果对方迎球位置在5/8到1/2之间
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他在2/3处
                    op_new_pos = (2 * y) // 3
                else:   # 如果对方向南跑位，就假设他归中
                    op_new_pos = y // 2
            elif (op_pos == y // 2):    # 如果对方迎球位置在中点
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他在5/8处
                    op_new_pos = (5 * y) // 8
                else:    # 如果对方向南跑，就假设他在3/8处
                    op_new_pos = (3 * y) // 8
            else:    # 如果对方迎球位置在3/8到1/2之间
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他归中
                    op_new_pos = y // 2
                else:    # 如果对方向南跑位，就假设他在1/3处
                    op_new_pos = y // 3
        else:    # 如果对方用了隐身术
            op_new_pos = y // 2
        # 遍历所有能达到的速度，并选出最优出球速度
        lif_comp = lif_pic_comp = (0,0)     # 前者是所有方案中的最好方案，后者是所有能捡到道具的方案中的最好方案
        # 遍历所有朝南的出球速度
        for v in range(vy_max_sou,vy_min_sou):
            temp_lif_comp = temp_lif_pic_comp = (0,0)    # 前者存本次方案，若能捡到道具则也存入后者
            temp_acc = int(v - vel.y)    # 本方案需要的加速度
            acc_vel = temp_acc + vel.y    # 加速后的实际速度（考虑到加速度被int会使得实际速度与设想有偏差）
            if (acc_vel <= -(y + pos.y) / t):    # 如果要碰壁两次，op_bat_dis为对方迎球距离
                op_bat_dis = pos.y + 2 * y + acc_vel * t - op_new_pos
            else:    # 如果只碰壁一次
                op_bat_dis = -pos.y - acc_vel * t - op_new_pos
            if (op_act_car[1] == CARD_SPIN):    # 如果对方使用旋转球，则需要将加速度放大一倍
                temp_acc *= 2
            my_de_lif = ((abs(temp_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1))  # 我方加速耗血量
            op_de_lif = (abs(op_bat_dis) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if card_use == CARD_AMPL else 1)  # 对方迎球耗血量
            if ((card_use != None) and (card_use != CARD_AMPL)):  # 如果我方用了道具，就用它的价值来抵消损耗的生命值
                my_de_lif -= CardValue[card_use.code]
            temp_lif_comp = (temp_acc,op_de_lif - my_de_lif)    # 以(加速度，对方耗血与我方耗血之差)的形式记录本次方案
            # 如果要捡道具
            if pick:
                for c in pick_car:    # 遍历要捡的道具
                    A1 = (acc_vel * (-c.pos.x + pos.x) + vel.x * (c.pos.y - pos.y))
                    A2 = (acc_vel * (-c.pos.x + pos.x) + vel.x * (-c.pos.y - pos.y))
                    delta = (2 * abs(vel.x) * DIM[3])
                    if ((min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(vel.x ** 2 + acc_vel ** 2)) < 1800):    # 如果能拿到就做记录
                        temp_lif_comp = list(temp_lif_comp)
                        temp_lif_comp[1] += CardValue[c.code]
                        temp_lif_comp = tuple(temp_lif_comp)
                        my_de_lif = ((abs(temp_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1)) - CardValue[c.code]    # 我方加速耗血量，如果对方用变压器就加倍
                        op_de_lif = (abs(op_bat_dis) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if card_use == CARD_AMPL else 1)    # 对方迎球耗血量，如果我方用变压器就加倍
                        if ((card_use != None) and (card_use != CARD_AMPL)):    # 如果我方用了除变压器外的道具，就用它的价值来抵消损耗的生命值
                            my_de_lif -= CardValue[card_use.code]
                        temp_lif_pic_comp = (temp_acc,op_de_lif - my_de_lif)    # 存入本次方案
                        if (temp_lif_pic_comp[1] > lif_pic_comp[1]):    # 若本次方案优于之前的最优方案则替换之
                            lif_pic_comp = temp_lif_pic_comp
                        break    # 若已有能拿到的道具就退出循环
            if (temp_lif_comp[1] > lif_comp[1]):    # 如果之前的最优方案不如本次，则替换之
                lif_comp = temp_lif_comp
        if (lif_comp[1] > lif_pic_comp[1]):
            best1 = lif_comp
        else:
            best1 = lif_pic_comp
        lif_comp = lif_pic_comp = (0,0)    # 同上
        for v in range(vy_min_nor,vy_max_nor):    # 对向北出球的速度进行遍历
            temp_lif_comp = temp_lif_pic_comp = (0,0)
            temp_acc = int(v - vel.y)
            acc_vel = vel.y + temp_acc
            if (acc_vel <= (2 * y - pos.y) / t):
                op_bat_dis = 2 * y - pos.y - acc_vel * t - op_new_pos
            else:
                op_bat_dis = acc_vel * t + pos.y - 2 * y - op_new_pos
            if (op_act_car[1] == CARD_SPIN):
                temp_acc *= 2
            my_de_lif = ((abs(temp_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1))  # 我方加速耗血量
            op_de_lif = (abs(op_bat_dis) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if card_use == CARD_AMPL else 1)  # 对方迎球耗血量
            if ((card_use != None) and (card_use != CARD_AMPL)):  # 如果我方用了道具，就用它的价值来抵消损耗的生命值
                my_de_lif -= CardValue[card_use.code]
            temp_lif_comp = (temp_acc,op_de_lif - my_de_lif)
            if pick:
                for c in pick_car:
                    A1 = (acc_vel * (-c.pos.x + pos.x) + vel.x * (c.pos.y - pos.y))
                    A2 = (acc_vel * (-c.pos.x + pos.x) + vel.x * (-c.pos.y - pos.y))
                    delta = (2 * abs(vel.x) * DIM[3])
                    if (min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(vel.x ** 2 + acc_vel ** 2) < 1800):  # 如果能拿到就做记录
                        temp_lif_comp = list(temp_lif_comp)
                        temp_lif_comp[1] += CardValue[c.code]
                        temp_lif_comp = tuple(temp_lif_comp)
                        my_de_lif = ((abs(temp_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1)) - CardValue[c.code]  # 我方加速耗血量
                        op_de_lif = (abs(op_bat_dis) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if card_use == CARD_AMPL else 1)  # 对方迎球耗血量
                        if ((card_use != None) and (card_use != CARD_AMPL)):  # 如果我方用了道具，就用它的价值来抵消损耗的生命值
                            my_de_lif -= CardValue[card_use.code]
                        temp_lif_pic_comp = (temp_acc,op_de_lif - my_de_lif)
                        if (temp_lif_pic_comp[1] > lif_pic_comp[1]):
                            lif_pic_comp = temp_lif_pic_comp
                        break
            if (temp_lif_comp[1] > lif_comp[1]):
                lif_comp = temp_lif_comp
        if (lif_comp[1] > lif_pic_comp[1]):
            best2 = lif_comp
        else:
            best2 = lif_pic_comp
        # 从向北和向南出球的最佳方案中选出最佳方案
        if (best1[1] > best2[1]):
            best = best1
        else:
            best = best2
        acc = best[0]
    else:    # 如果对方生命值小于35%
        if (op_act_car[1] != CARD_DSPR):    # 如果对方没有使用隐身术
            if (op_pos >= ((5 * y) // 8)):    # 如果对方迎球位置在5/8处以上
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他向北跑位至可跑距离的1/4处
                    op_new_pos = op_pos + ((y - op_pos) // 4)
                else:    # 如果对方向南跑位，就假设他归中
                    op_new_pos = y // 2
            elif (op_pos <= ((3 * y) // 8)):    # 如果对方迎球位置在3/8处以下
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他归中
                    op_new_pos = y // 2
                else:    # 如果对方向南跑位，就假设他向南跑位至可跑距离的1/4处
                    op_new_pos = op_pos - (op_pos // 4)
            elif ((op_pos < ((5 * y) // 8)) and (op_pos > (y // 2))):    # 如果对方迎球位置在5/8到1/2之间
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他在2/3处
                    op_new_pos = (2 * y) // 3
                else:   # 如果对方向南跑位，就假设他归中
                    op_new_pos = y // 2
            elif (op_pos == y // 2):    # 如果对方迎球位置在中点
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他在5/8处
                    op_new_pos = (5 * y) // 8
                else:    # 如果对方向南跑，就假设他在3/8处
                    op_new_pos = (3 * y) // 8
            else:    # 如果对方迎球位置在3/8到1/2之间
                if (op_run >= 1):    # 如果对方向北跑位或不跑，就假设他归中
                    op_new_pos = y // 2
                else:    # 如果对方向南跑位，就假设他在1/3处
                    op_new_pos = y // 3
        else:    # 如果对方用了隐身术
            op_new_pos = y // 2
        # 判断是否可以一击必杀（打角）
        nor_dis = y - op_new_pos  # 打北角对方需要移动的距离
        sou_dis = op_new_pos - DIM[2]  # 打南角对方需要移动的距离
        nor_fly = sou_fly = con_fly = False  # 分别为打北角、打南角、打角的标记
        # 先判断北角
        if (int(((op_lif / RACKET_LIFE) * BALL_V[0]) * t) < nor_dis):
            best_acc = int(-(y + pos.y) / t - vel.y)
            if (op_act_car[1] == CARD_SPIN):
                best_acc *= 2
            nor_de_lif = (4 if op_act_car[1] == CARD_SPIN else 1) * ((abs(best_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1))  # 我方加速耗血量
            if (my_lif > nor_de_lif):
                nor_fly = True
                nor_acc = best_acc
        # 再判断南角
        if (int(((op_lif / RACKET_LIFE) * BALL_V[0]) * t) < sou_dis):
            best_acc = int((2 * y - pos.y) / t - vel.y)
            if (op_act_car[1] == CARD_SPIN):
                best_acc *= 2
            sou_de_lif = (4 if op_act_car[1] == CARD_SPIN else 1) * ((abs(best_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1))  # 我方加速耗血量
            if (my_lif >sou_de_lif):
                sou_fly = True
                sou_acc = best_acc
        # 选出最佳一击必杀方案
        if nor_fly and sou_fly:
            con_fly = True
            if (abs(nor_acc) > abs(sou_acc)):
                acc = sou_acc
            else:
                acc = nor_acc
        elif nor_fly:
            con_fly = True
            acc = nor_acc
        elif sou_fly:
            con_fly = True
            acc = sou_acc
        # 如果不一击必杀
        if not con_fly:
            lif_comp = lif_pic_comp = (0, 0)
            for v in range(vy_max_sou, vy_min_sou):
                temp_lif_comp = temp_lif_pic_comp = (0, 0)
                temp_acc = int(v - vel.y)
                acc_vel = temp_acc + vel.y
                if (acc_vel <= -(y + pos.y) / t):
                    op_bat_dis = pos.y + 2 * y + acc_vel * t - op_new_pos
                else:
                    op_bat_dis = -pos.y - acc_vel * t - op_new_pos
                if (op_act_car[1] == CARD_SPIN):
                    temp_acc *= 2
                my_de_lif = ((abs(temp_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1))  # 我方加速耗血量
                op_de_lif = (abs(op_bat_dis) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if card_use == CARD_AMPL else 1)  # 对方迎球耗血量
                if ((card_use != None) and (card_use != CARD_AMPL)):  # 如果我方用了道具，就用它的价值来抵消损耗的生命值
                    my_de_lif -= CardValue[card_use.code]
                temp_lif_comp = (temp_acc, op_de_lif - my_de_lif)
                if pick:
                    for c in pick_car:
                        A1 = (acc_vel * (-c.pos.x + pos.x) + vel.x * (c.pos.y - pos.y))
                        A2 = (acc_vel * (-c.pos.x + pos.x) + vel.x * (-c.pos.y - pos.y))
                        delta = (2 * abs(vel.x) * DIM[3])
                        if (min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(vel.x ** 2 + acc_vel ** 2) < 1800):  # 如果能拿到就做记录
                            temp_lif_comp = list(temp_lif_comp)
                            temp_lif_comp[1] += CardValue[c.code]
                            temp_lif_comp = tuple(temp_lif_comp)
                            my_de_lif = ((abs(temp_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1)) - CardValue[c.code]  # 我方加速耗血量
                            op_de_lif = (abs(op_bat_dis) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if card_use == CARD_AMPL else 1)  # 对方迎球耗血量
                            if ((card_use != None) and (card_use != CARD_AMPL)):  # 如果我方用了道具，就用它的价值来抵消损耗的生命值
                                my_de_lif -= CardValue[card_use.code]
                            temp_lif_pic_comp = (temp_acc, op_de_lif - my_de_lif)
                            if (temp_lif_pic_comp[1] > lif_pic_comp[1]):
                                lif_pic_comp = temp_lif_pic_comp
                            break
                if (temp_lif_comp[1] > lif_comp[1]):
                    lif_comp = temp_lif_comp
            if (lif_comp[1] > lif_pic_comp[1]):
                best1 = lif_comp
            else:
                best1 = lif_pic_comp
            lif_comp = lif_pic_comp = (0, 0)
            for v in range(vy_min_nor, vy_max_nor):
                temp_lif_comp = temp_lif_pic_comp = (0, 0)
                temp_acc = int(v - vel.y)
                acc_vel = vel.y + temp_acc
                if (acc_vel <= (2 * y - pos.y) / t):
                    op_bat_dis = 2 * y - pos.y - acc_vel * t - op_new_pos
                else:
                    op_bat_dis = acc_vel * t + pos.y - 2 * y - op_new_pos
                if (op_act_car[1] == CARD_SPIN):
                    temp_acc *= 2
                my_de_lif = ((abs(temp_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1))  # 我方加速耗血量
                op_de_lif = (abs(op_bat_dis) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if card_use == CARD_AMPL else 1)  # 对方迎球耗血量
                if ((card_use != None) and (card_use != CARD_AMPL)):  # 如果我方用了道具，就用它的价值来抵消损耗的生命值
                    my_de_lif -= CardValue[card_use.code]
                temp_lif_comp = (temp_acc, op_de_lif - my_de_lif)
                if pick:
                    for c in pick_car:
                        A1 = (acc_vel * (-c.pos.x + pos.x) + vel.x * (c.pos.y - pos.y))
                        A2 = (acc_vel * (-c.pos.x + pos.x) + vel.x * (-c.pos.y - pos.y))
                        delta = (2 * abs(vel.x) * DIM[3])
                        if (min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(vel.x ** 2 + acc_vel ** 2) < 1800):  # 如果能拿到就做记录
                            temp_lif_comp = list(temp_lif_comp)
                            temp_lif_comp[1] += CardValue[c.code]
                            temp_lif_comp = tuple(temp_lif_comp)
                            my_de_lif = ((abs(temp_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_act_car[1] == CARD_AMPL else 1)) - CardValue[c.code]  # 我方加速耗血量
                            op_de_lif = (abs(op_bat_dis) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if card_use == CARD_AMPL else 1)  # 对方迎球耗血量
                            if ((card_use != None) and (card_use != CARD_AMPL)):  # 如果我方用了道具，就用它的价值来抵消损耗的生命值
                                my_de_lif -= CardValue[card_use.code]
                            temp_lif_pic_comp = (temp_acc, op_de_lif - my_de_lif)
                            if (temp_lif_pic_comp[1] > lif_pic_comp[1]):
                                lif_pic_comp = temp_lif_pic_comp
                            break
                if (temp_lif_comp[1] > lif_comp[1]):
                    lif_comp = temp_lif_comp
            if (lif_comp[1] > lif_pic_comp[1]):
                best2 = lif_comp
            else:
                best2 = lif_pic_comp
            if (best1[1] > best2[1]):
                best = best1
            else:
                best = best2
            acc = best[0]
    # 跑位
    run = ((DIM[3] - DIM[2]) // 2) - pos.y
    # ds数据导入
    ds['now'].append((tb,bat,acc,run,card_side,card_use))
    print((tb.tick, bat, acc, run, card_side, card_use))
    return RacketAction(tb.tick, bat, acc, run, card_side, card_use)

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    if (ds == {}):
        ds = {'pre':[] ,'now':[]}
    ds['now'].append((winner,reason,west,east,ball))
    ds['pre'].append(ds['now'])
    ds['now'] = []
    return ds
