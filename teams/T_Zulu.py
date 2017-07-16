from table import *
import math


# 发球函数，总是做为West才发球
# op_side为对手方名称，以便从ds中查询以往记录数据
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side: str, ds: dict) -> tuple:
    #杀招一，二弹，打到角落
    return 0, 1666

def valid_speed(p, y):
    if y > 0:
        max_v = (2999999-p)/1800
        min_v = (2000001-p)/1800
        return int(max_v), int(min_v)+1
    else:
        max_v = (1999999+p)/1800
        min_v = (1000001+p)/1800
        return -int(max_v), -(int(min_v)+1)
def get_card(tb: TableData, card, v, eps=2000):
        # 多写点注释。self.pos:(x0,y0),card.pos:(x1,y1),self.velocity:(u,v),self.extent[3]=L
        # 直线方程为 l:-v*x+u*y+v*x0-u*y0=0
        # card经过多次对称后，位置为(x1,±y1+2*k*l)
        # 点到直线距离公式dist=|-v*x1+u*(±y1+2*k*l)+v*x0-u*y0|/|self.velocity|
        # 记-v*x1+u*(±y1)+v*x0-u*y0=A1,A2,u*2*l为delta。则求最短距离，即是求A1%delta,A2%delta,-A1%delta,-A2%delta中最小值，再除以self.velocity的模长。
        A1 = (v * (-card.pos.x + tb.ball['position'].x) + tb.ball['velocity'].x * (card.pos.y - tb.ball['position'].y))
        A2 = (v * (-card.pos.x + tb.ball['position'].x) + tb.ball['velocity'].x * (-card.pos.y - tb.ball['position'].y))
        delta = (2 * abs(tb.ball['velocity'].x) * 1000000)
        return min(A1 % delta, -A1 % delta, A2 % delta, -A2 % delta) / math.sqrt(
            tb.ball['velocity'].x ** 2 + v ** 2) < eps

def get_fly_ans(v,y):
        Y = v * 1800 + y  # Y是没有墙壁时到达的位置
        if Y % 1000000 != 0:  # case1：未在边界
            count = Y // 1000000  # 穿过了多少次墙（可以是负的，最后取绝对值）

            # 两种情形：a） 穿过偶数次墙，这时没有对称变换，速度保持不变。到达的位置就是Y0=Y-self.extent[3]*count
            #         b） 穿过奇数次墙，是一次对称和一次平移的复合，速度反向。先做平移，到达Y0=Y-self.extent[3]*count，再反射，到self.extent[3]-Y0
            # 综合两种情形，奇数时Y0是负的，多一个self.extent[3];偶数时Y0是正的，没有self.extent[3]。综上，ynew=Y0*(-1)^count+(1-(-1)^count)/2*self.extent[3]
            # 因不清楚负数能不能做任意整指数幂，所以用取余来表示奇偶性。

            pos = (Y - count * 1000000) * (1 - 2 * (count % 2)) + 1000000 * (count % 2)
            y = v * ((count + 1) % 2 * 2 - 1)
            return abs(count), pos, y
        else:  # case2： 恰好在边界

            # 两种情形：a） 向上穿墙，穿了1 - Y // self.extent[3] 次（代入Y = 0验证）
            #           b） 向下穿墙，穿了 Y // self.extent[3] 次（代入Y = self.extent[3] 验证）
            # 无论怎样，实际位置要么在0，要么在self.extent[3]。直接模( 2 * self.extent[3] )即可。
            # 速度只和count奇偶有关，同上。

            count = (Y // 1000000) if (Y > 0) else (1 - Y // 1000000)
            pos = Y % (2 * 1000000)
            y = v * ((count + 1) % 2 * 2 - 1)
            return abs(count), pos, y
# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb: TableData, ds: dict) -> RacketAction:
    #满足bounce=2时的速度范围
    max_v, min_v = valid_speed(tb.ball['position'].y, tb.ball['velocity'].y)
    op_side_name = tb.op_side['name']
    #计算并记录对手的历史跑位,提供预测
    if op_side_name not in ds:
        ds[op_side_name] = op_side_name
        #预测己方最优跑位
        ds['ball_history'] = []
        #对手上一次的位置
        ds['last_pos'] = tb.op_side['position']
        #对手上一次的生命值
        ds['last_life'] = tb.op_side['life']
        #对手迎球时球的速度
        ds['y_v'] = 1000
        #上一次球到达的位置
        ds['y_p'] = 1000000
        #预测对方跑位
        ds['run_history'] = []
        #记录回合
        ds['round'] = 1
        #记录上次跑位预测结果
        ds['pred_run_pos'] = [-1, -1]
        #记录上次球预测结果
        ds['pred_ball_pos'] = [-1, -1, -1]
    #一回合损失的生命值
    delta_life = ds['last_life'] - tb.op_side['life']
    n_pos = tb.op_side['position'].y
    l_pos = ds['last_pos'].y
    n_v = tb.ball['velocity'].y
    l_v = ds['y_v']
    #print(delta_life,n_pos,l_pos,n_v,l_v)
    #对手对球速度的该变量
    delta_v = abs(n_v - l_v)
    #移动导致的体力损失量
    pos_life = (abs(delta_life) - (abs(delta_v) ** 2 // FACTOR_SPEED ** 2))*(FACTOR_DISTANCE ** 2)
    #得到上一次跑位位置real_run_pos
    #确定方程有解,方程为(l_pos-real_run_pos)^2 + (real_run_pos-n_pos)^2 = pos_life
    if (l_pos+n_pos)**2-2*(l_pos**2+n_pos**2-pos_life) > 0:
        #print(l_pos,n_pos)
        real_run_pos1 = (l_pos+n_pos+math.sqrt((l_pos+n_pos)**2-2*(l_pos**2+n_pos**2-pos_life)))//2
        real_run_pos2 = (l_pos+n_pos-math.sqrt((l_pos+n_pos)**2-2*(l_pos**2+n_pos**2-pos_life)))//2
        if real_run_pos1 <= 1000000 and real_run_pos1 >= 0:
            real_run_pos = real_run_pos1
        elif real_run_pos2 <= 1000000 and real_run_pos2 >= 0:
            real_run_pos = real_run_pos2
        else:
            real_run_pos = -1
            #print("计算上一次跑位位置失败")
    else:
        #print("计算上一次跑位位置失败")
        real_run_pos = -1
    #如果存在预测
    if ds['pred_run_pos'][0] != -1:
        if abs(ds['pred_run_pos'][1]-real_run_pos)<1000:
            #print("预测正确")
            pass
        else:
            #print("预测失败")
            #更新
            for h in ds['run_history']:
                #根据对方的位置预测，假设bounce=2，从而不改变球的运动方向
                if abs(ds['pred_run_pos'][0]-h[0]) < 1000:
                    h[1] = real_run_pos
        #print("实际位置是",real_run_pos)
        #print("预测位置是",ds['pred_run_pos'][1])
    #记录上一次跑位位置，并预测本次对手的跑位位置pred_run_pos
    pred_run_pos = -1
    if real_run_pos != -1:
        if len(ds['run_history']) == 0:
                ds['run_history'].append([l_pos, real_run_pos])
        else:
            for h in ds['run_history']:
                #根据对方的位置预测，假设bounce=2，从而不改变球的运动方向
                if abs(l_pos-h[0]) < 1000:
                    #print("预测",l_pos)
                    pred_run_pos = h[1]
                    break
            #如果历史信息中没有与当前位置匹配的信息，预测失败
            if pred_run_pos == -1:
                #print("记录",l_pos)
                ds['run_history'].append([l_pos, real_run_pos])
    else:
        pred_run_pos = l_pos
    #预测成功
    bounce_count, max_pos, max_y = get_fly_ans(max_v,tb.ball['position'].y)
    bounce_count, min_pos, min_y = get_fly_ans(min_v,tb.ball['position'].y)
    #记录到达的位置
    arrive_p = max_pos
    perfect_v = max_v
    v_y = max_y
    #采用min_v
    ds['pred_run_pos'] = [-1, -1]
    if pred_run_pos != -1 and abs(min_pos-pred_run_pos) - abs(max_pos - pred_run_pos) > 10000:
        #print("choose min_v")
        perfect_v = min_v
        arrive_p = min_pos
        v_y = min_y
    else:
        pass
        #print("choose max_v")
    #print(arrive_p)
    #print(pred_run_pos)
    if pred_run_pos != -1:
        ds['pred_run_pos'] = [l_pos, pred_run_pos]
   
    #记录到达的速度和位置
    if v_y != perfect_v:
        print("big bug!")
    ds['y_v'] = perfect_v
    ds['y_p'] = arrive_p
    v = perfect_v-tb.ball['velocity'].y
    #预测自己最优跑位方式，默认跑位到中间
    pred_ball_position = -1
    
    if ds['pred_ball_pos'][0] != -1:
        for d in ds['ball_history']:
            last_v = d[0]
            last_p = d[1]
            if sign(last_v) == sign(ds['pred_ball_pos'][0]) and abs(last_p-ds['pred_ball_pos'][1]) <= 1000:
                #print("更新预测")
                #print(tb.ball["position"].y,d[2])
                if abs(tb.ball["position"].y-d[2]) > 1000:
                    #print("update")
                    #print(d[0],d[1],d[2])
                    d[2] = tb.ball["position"].y
                else:
                    pass
                    #print("预测成功")
    if len(ds['ball_history']) == 0:
        #print(ds['y_v'], ds['y_p'], tb.ball['position'].y)
        ds['ball_history'].append([ds['y_v'], ds['y_p'], tb.ball['position'].y])
    else:
        for d in ds['ball_history']:
            last_v = d[0]
            last_p = d[1]
            if sign(last_v) == sign(perfect_v) and abs(last_p-arrive_p) <= 1000:
                #print("找到了")
                #print(d[0],d[1],d[2])
                pred_ball_position = d[2]
                break
        if pred_ball_position == -1:
            #print(ds['y_v'], ds['y_p'], tb.ball['position'].y)
            ds['ball_history'].append([ds['y_v'], ds['y_p'], tb.ball['position'].y])
    ds['pred_ball_pos'] = [-1, -1, -1]
    if pred_ball_position != -1:
        #print("预测")
        #print(pred_ball_position)
        ds['pred_ball_pos'] = [ds['y_v'], ds['y_p'], tb.ball['position'].y]
        #预测成功，跑位到预测位置一半的距离，损失体力最低
        dis = (pred_ball_position - tb.ball['position'].y)/2
    else:
        #默认跑位到中间
        dis = 500000 - tb.ball['position'].y
    #使用道具，如果有道具
    target = None
    card = None
    if len(tb.side['cards']) !=0:
        card = tb.side['cards'][0]
        if tb.side['cards'][0].code == 'SP':
            target = tb.op_side['name']
        elif tb.side['cards'][0].code == 'DS':
            target = tb.side['name']
        elif tb.side['cards'][0].code == 'IL':
            target = tb.side['name']
        elif tb.side['cards'][0].code == 'DL':
            target = tb.op_side['name']
        elif tb.side['cards'][0].code == 'TP':
            target = tb.side['name']
        else:
            target = tb.op_side['name']
    ds['last_pos'] = tb.op_side['position']
    ds['last_life'] = tb.op_side['life']
    ds['round'] += 1
    ret = RacketAction(tb.tick,  # 当前时间，照抄参数中的tb.tick即可
                        tb.ball['position'].y - tb.side['position'].y,  # 球拍的移动距离（有方向）
                        v,  # 球拍对球加速的速度（有方向）
                        dis,  # 球拍击球后跑位的移动距离（有方向）
                        target,  # 使用道具，对谁使用'SELF'/'OPNT'
                        card  # Card对象，使用什么道具
                        )
    return ret


# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
# 修改ds后，不需要返回数据
def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    ds.clear()
    return
