from table import *
import numpy

def serve(op_side: str, ds: dict) -> tuple:
    return 500100, 279

def play(tb, ds):

    # 目标转落点-ok
    def targettopos(tgt):
        pos = 0
        if 1000000 < tgt < 2000000:
            pos = 2000000 - tgt
        if 2000000 < tgt < 3000000:
            pos = tgt - 2000000
        if -1000000 < tgt < 0:
            pos = - tgt
        if -2000000 < tgt < -1000000:
            pos = tgt + 2000000
        return pos

    # 目标转速度-ok
    def targettovelocity(tgt, ori):
        vel = 0
        if 1000000 < tgt < 2000000 or -2000000 < tgt < -1000000:
            vel = (tgt - ori) // 1800 + 1
        if 2000000 < tgt < 3000000 or -1000000 < tgt < 0:
            vel = (tgt - ori) // 1800
        return vel

    # 计算损失生命-ok
    def callife(pos_a, pos_b, v_a, v_b):
        lostlife = (pos_a - pos_b) ** 2 // FACTOR_DISTANCE ** 2 + (v_a - v_b) ** 2 // FACTOR_SPEED ** 2
        return lostlife

    # 最佳正常回球-ok
    #   输入我方对方位置和球速
    #   输出最佳正常回球的目标编号及生命值gain
    def best_throw(w_pos, e_pos, ball_v):
        tgt_gain = []
        for i in range(6):
            gain = - am * sp**2 * callife(0, 0, ball_v, velocities[i]) + callife(e_pos, positions[i], 0, 0)
            tgt_gain.append(gain)
        best_gain = max(tgt_gain)
        best_num = tgt_gain.index(best_gain)
        return best_num, best_gain

    # 可以达到道具的所有目标-ok
    def cardtotargets(cardx, cardy, w_pos):
        all_y = []
        all_y.append(2000000 + cardy)
        all_y.append(2000000 - cardy)
        all_y.append(cardy)
        all_y.append(-cardy)
        all_y.append(-2000000 + cardy)
        all_tgt = []
        for i in range(5):
            temp = 1800000 / (-wx + cardx) * (all_y[i] - w_pos) + w_pos
            if 999999 < int(temp) < 2999999 or -1999999 < int(temp) < -1:
                all_tgt.append(temp)
        return all_tgt

    # 单道具最佳路径-ok
    #   输入道具位置
    #   输出拾取该道具所有路径中最节省路径
    #   IL DL TP AM SP DS
    def single_best(w_pos, e_pos, cardx, cardy, cardcode, ball_v):
        all_tgt = cardtotargets(cardx, cardy, w_pos)
        if all_tgt:
            all_val = []
            leng = len(all_tgt)
            for i in range(leng):
                temp = - am * sp**2 * callife(0, 0, ball_v, targettovelocity(all_tgt[i], w_pos)) \
                       + callife(e_pos, targettopos(all_tgt[i]), 0, 0)
                if cardcode == 'IL' or cardcode == 'DL':  # 加减生命
                    temp += 3500
                if cardcode == 'TP':  # 瞬移
                    temp += 1000
                if cardcode == 'AM':  # 变压器
                    temp += 1600
                if cardcode == 'SP':  # 旋转球
                    temp += 2000
                if cardcode == 'DS':
                    temp += 0
                all_val.append(temp)
            single_card_val = max(all_val)  # 最佳路径净价值
            single_card_choice = all_val.index(single_card_val)  # 最佳路径位置编号
            single_card_tgt = all_tgt[single_card_choice]  # 最佳路径目标
            single_card_pos = targettopos(single_card_tgt)  # 最佳路径落点
            single_card_v = targettovelocity(single_card_tgt, w_pos)
            return single_card_tgt, single_card_pos, single_card_val, single_card_v
        else:
            return None, None, None, None

    # 多道具回球路径-ok
    #   输入多个道具位置
    #   比较每个道具最佳路径的value
    #   输出最佳道具回球的目标位置，球速，及生命值gain
    def multi_best(w_pos, e_pos, ball_v, all_cards):
        best_val = -10000000
        best_tgt = None
        best_pos = None
        best_num = 0
        for i in range(len(all_cards)):
            tgt, pos, val, c_v = single_best(w_pos, e_pos, all_cards[i].pos.x, all_cards[i].pos.y, all_cards[i], ball_v)
            if val and best_val < val:
                best_val = val
                best_tgt = tgt
                best_pos = pos
                best_num = i
        if best_tgt:
            del all_cards[best_num]
            c_v = targettovelocity(best_tgt, w_pos)
            return best_tgt, best_pos, best_val, c_v, all_cards
        else:
            return None, None, None, None, None

    # 跑位策略集-输入跑位编号和当前位置，输出跑位
    def runtheo(theo_num, pos):
        # 策略0：不跑位
        if theo_num == 0:
            return pos
        # 策略1：跑底线中点
        if theo_num == 1:
            return 500000
        # 策略2：跑迎球中点
        if theo_num == 2:
            if pos < 500000:
                run = (pos + 1000000) // 2
            else:
                run = pos // 2
            return run
        # 策略3：跑迎球2/3处
        if theo_num == 3:
            if pos < DIM[3]/2:
                return int(DIM[3] / 3 + pos * 2 / 3)
            return pos * 2 // 3

    # 打击策略集
    def hittheo(theo_num, pos):
        # 策略0：打原角落
        if theo_num == 0:
            if pos < 500000:
                return 0
            else:
                return 1000000
        # 策略1：打对角落
        if theo_num == 1:
            if pos < 500000:
                return 1000000
            else:
                return 0

    # 跑位策略评估-输入历史击球点和历史跑位，输出最佳跑位编号
    def scoretheo(poslst, runlst):
        totaltheo = 4  # 跑位策略总数
        samplenum = 3  # 取最近的样本数
        if len(runlst) < samplenum:  # 若历史数据不够样本数
            samplenum = len(runlst)
        scores = list(range(totaltheo))  # 储存各个策略打分，分数越低，策略表现越好
        for i in range(totaltheo):
            for j in range(samplenum):
                # 第-3个击球点决定第-1个跑位
                if runlst[-1-j] is not None:
                    scores[i] += abs(runtheo(i, poslst[-2-j])-runlst[-1-j])  # 该式可以乘以与j有关的加权
        besttheonum = scores.index(min(scores))
        return besttheonum

    # 打击策略评估
    def scorehit(poslst, hitlst):
        totaltheo = 2
        samplenum = 3
        if len(hitlst) < samplenum:
            samplenum = len(hitlst)
        scores = list(range(totaltheo))
        for i in range(totaltheo):
            for j in range(samplenum):
                scores[i] += abs(hittheo(i, poslst[-2-j])-hitlst[-1-j])
        besttheonum = scores.index(min(scores))
        return besttheonum

    #   对方本轮跑位方向
    e_run_dir = tb.op_side['run_vector']
    #   对方上轮跑位
    e_last_run = 0

    '''数据取出'''
    #   当前时间
    t = tb.tick
    #   球落点
    w = tb.ball['position'].y
    #   球速
    v = tb.ball['velocity'].y
    #   我方位置
    w_last = tb.side['position'].y
    #   我方边x位置
    wx = tb.side['position'].x
    #   对方位置
    e = tb.op_side['position'].y
    #   我方生命
    w_life = tb.side['life']
    #   对方生命
    e_life = tb.op_side['life']
    #   对方用道具
    e_use_card = tb.op_side['active_card'][1]
    #   我方道具
    w_use_card = None
    #   桌上道具
    table_cards = tb.cards['cards']
    #   我方道具箱
    w_cards = tb.side['cards']
    #   对方道具箱
    e_cards = tb.op_side['cards']

    #   对方是否使用spin道具
    if e_use_card is not None and e_use_card == 'SP':
        sp = 2
    else:
        sp = 1

    #   对方是否使用ampl道具
    if e_use_card is not None and e_use_card == 'AM':
        am = 2
    else:
        am = 1

    if 2000000 < w - 1800 * v < 3000000 or -2000000 < w - 1800 * v < -1000000:
        v_out = v
    else:
        v_out = -v

    def cal_run():
        card_dc = 0
        card_ic = 0
        if ds['e_card'][-1] == CARD_INCL:
            card_ic = 2000
        if ds['w_card'][-2] == CARD_DECL:
            card_dc = 2000
        amp = 1
        spin = 1
        if ds['w_card'][-2] == CARD_SPIN:
            spin = 4
        if ds['w_card'][-2] == CARD_AMPL:
            amp = 2
        if ds['e_card'][-1] == CARD_TLPT:
            a = 0
        a = 2*amp / FACTOR_DISTANCE**2
        b = -2 *amp* ds['e_pos'][-2]/FACTOR_DISTANCE**2 - 2 *amp* ds['e_pos'][-1]/FACTOR_DISTANCE**2
        c = amp*ds['e_pos'][-2]**2/FACTOR_DISTANCE**2 + amp*ds['e_pos'][-1]**2/FACTOR_DISTANCE**2 \
            + spin*amp*callife(0, 0, ds['v_in'][-1], ds['v_out'][-1]) - e_ld - card_ic + card_dc
        if b**2 - 4*a*c < 0:
            run = None
        else:
            sol = numpy.poly1d([a, b, c])
            run = None
            if ds['e_pos'][-2] < 500000:
                for i in sol.r:
                    if -100000 < i < 510000:
                        run = i
            else:
                for i in sol.r:
                    if 490000 < i < 1100000:
                        run = i
        return run

    '''数据记录'''
    if t == 0:  # 对方发球初始化
        ds['e_life'] = [e_life]
        ds['w_life'] = [100000]
        ds['e_pos'] = [500000]
        ds['w_pos'] = [w]
        ds['v_in'] = [0]
        ds['v_out'] = [int(v_out)]
        ds['e_card'] = [None]
        ds['w_card'] = [None]
        ds['e_run'] = [0]
    elif t == 1800:  # 我方发球初始化
        ds['e_life'] = [100000, e_life]
        ds['w_life'] = [100000, w_life]
        ds['e_pos'] = [500000, e]
        ds['w_pos'] = [500000, w]
        ds['v_in'] = [-279]
        ds['v_out'] = [int(v_out)]
        ds['e_card'] = [None]
        ds['w_card'] = [None]
        ds['e_run'] = [0]
    else:
        ds['e_life'].append(e_life)
        ds['w_life'].append(w_life)
        ds['e_pos'].append(e)
        ds['w_pos'].append(w)
        ds['v_out'].append(int(v_out))
        ds['e_card'].append(e_use_card)
        ds['w_card'].append(w_use_card)
        e_ld = ds['e_life'][-2] - ds['e_life'][-1]
        e_run = cal_run()
        ds['e_run'].append(e_run)

    '''猜跑位'''
    #   猜测对方跑位
    if t / 1800 < 8:
        theo = 1
    else:
        theo = scoretheo(ds['e_pos'], ds['e_run'])
    e_guess = runtheo(theo, e)

    #   猜测对方击球
    if t / 1800 < 8:
        hitnum = 1
    else:
        hitnum = scorehit(ds['w_pos'], ds['w_pos'])

    '''设置目标'''
    #   目标列表
    targets = [2999999, 1999999, 1000001, -1, -999999, -1999999]
    #   落点列表
    positions = []
    for i in targets:
        positions.append(targettopos(i))
    # 速度列表
    velocities = []
    for i in targets:
        velocities.append(targettovelocity(i, w))

    '''决定我方击球'''
    # 最佳正常击球
    norm_num, norm_gain = best_throw(w, e_guess, v)
    w_target = targets[norm_num]

    # 最佳道具击球
    pick = False
    if table_cards:
        card_tgt, card_pos, card_gain, card_v, table__cards = multi_best(w, e_guess, v, table_cards)
        # 我方取不取道具
        if card_tgt and norm_gain < card_gain:
            w_target = card_tgt
            pick = True

    # 最终击球决策
    w_v = targettovelocity(w_target, w)
    # spin道具保险
    v_change = (w_v - v) * sp
    v_new = v_change + v

    if 2000000 < w + 1800 * v_new < 3000000 or -2000000 < w + 1800 * v_new < -1000000:
        v_in = v_new
    else:
        v_in = - v_new

    '''决定我方跑位'''
    # 对方取不取道具
    wx = -wx
    e_norm_num, e_norm_gain = best_throw(targettopos(w_target), 500000, v_in)
    e_target = targets[e_norm_num]
    e_pick = False
    if table_cards:
        e_card_tgt, card_pos, e_card_gain, card_v, table_cards = multi_best(targettopos(w_target), 500000, v_in,
                                                                            table_cards)
        if e_card_tgt and e_norm_gain < e_card_gain:
            e_target = e_card_tgt
            e_pick = True

    # 跑位策略
    if hitnum == 0:
        if (w_v * 1800 + w > 2500000 and w < 500000) or (w_v * 1800 + w < -1500000 and w > 500000):
            w_run = 500000
        else:
            if w < 500000:
                w_run = w + 1
            else:
                w_run = w - 1
    else:
        w_run = 500000

    if e_pick:
        w_run = (targettopos(e_target) + w) / 2

    # 跑位体力保险
    w_new_life = w_life - callife(w_last, w, v, v + v_change) - callife(1000000, 0, 0, 0)
    if w_run >= 1800 * int((w_new_life / RACKET_LIFE) * BALL_V[0]):
        w_run = max(1800 * int((w_new_life / RACKET_LIFE) * BALL_V[0]), 500000)
    if 1000000 - w_run >= 1800 * int((w_new_life / RACKET_LIFE) * BALL_V[0]):
        w_run = min(1000000 - 1800 * int((w_new_life / RACKET_LIFE) * BALL_V[0]), 500000)

    '''我方使用道具'''
    w_use_card = None
    if CARD_INCL in w_cards:
        w_use_card = CARD_INCL
    elif CARD_DECL in w_cards:
        w_use_card = CARD_DECL
    elif CARD_TLPT in w_cards and w_run - w > 250000:
        w_use_card = CARD_TLPT
    elif CARD_SPIN in w_cards and (
        (w_v * 1800 + w > 2900000 and w < 100000) or (w_v * 1800 + w < -1900000 and w > 900000)):
        w_use_card = CARD_SPIN
    elif CARD_AMPL in w_cards and (
        (w_v * 1800 + w > 2900000 and w < 100000) or (w_v * 1800 + w < -1900000 and w > 900000)):
        w_use_card = CARD_AMPL
    elif w_cards and w_life < 500000:
        w_use_card = w_cards[0]
    elif pick and len(w_cards) == 3:
        w_use_card = w_cards[0]

    '''数据补充记录'''
    ds['v_in'].append(int(v_in))

    return RacketAction(tb.tick, w - w_last, v_change, w_run - w, None, w_use_card)

def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return