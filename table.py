import copy

# 桌面的坐标系，单位"pace"
DIM = (-900000, 900000, 0, 1000000)
# 最大时间，单位"tick"，每个回合3600tick，200回合
TMAX = 800000
# 球的初始坐标(x,y)，在west中间
BALL_POS = (DIM[0], (DIM[3] - DIM[2]) // 2)
# 球的初速度，(vx,vy)，单位"p/t"，向东北飞行
BALL_V = (1000, 1000)
# 球拍的生命值，100个回合以上
RACKET_LIFE = 100000
# 迎球和跑位扣减距离除以系数的平方（LIFE=0-1000)
FACTOR_DISTANCE = 3000
# 加速则扣减速度除以系数结果的平方（LIFE=0-400)
FACTOR_SPEED = 50
# 游戏方代码
PL = {'West': 'W', 'East': 'E'}
# 游戏结束原因代码
RS = {'invalid_bounce': 'B', 'miss_ball': 'M', 'life_out': 'L', 'time_out': 'T'}


def sign(n):  # 返回n的符号，小于0为-1，否则为1
    return -1 if n < 0 else 1


class Vector:  # 矢量
    def __init__(self, x, y=None):
        if y is None and isinstance(x, tuple):
            self.x, self.y = x
        else:
            self.x, self.y = x, y

    def __add__(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __eq__(self, other):  # 判定相等，考虑误差+／-1
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1

    def __str__(self):
        return "<%s,%s>" % (self.x, self.y)


class Position(Vector):  # 位置
    pass


class Ball:  # 球
    def __init__(self, extent, pos, velocity):
        # 球所在的坐标系参数extent，球的位置坐标pos，球的运动速度矢量velocity
        self.extent, self.pos, self.velocity = extent, pos, velocity

    def bounce_wall(self):  # 球在墙壁上反弹
        self.velocity.y = -self.velocity.y

    def bounce_racket(self):  # 球在球拍反弹
        self.velocity.x = -self.velocity.x

    def update_velocity(self, acc_vector):  # 给球加速，球桌坐标系
        # 球改变速度，仅垂直方向
        self.velocity.y += acc_vector

    def fly(self, ticks):  # 球运动，更新位置，并返回触壁次数
        # x方向的位置
        self.pos.x += self.velocity.x * ticks

        # 以下是李逸飞同学的简短新算法
        # ===========NEW!=============
        Y = self.velocity.y * ticks + self.pos.y  # Y是没有墙壁时到达的位置
        if Y % self.extent[3] != 0:  # case1：未在边界
            count = Y // self.extent[3]  # 穿过了多少次墙（可以是负的，最后取绝对值）

            # 两种情形：a） 穿过偶数次墙，这时没有对称变换，速度保持不变。到达的位置就是Y0=Y-self.extent[3]*count
            #           b） 穿过奇数次墙，是一次对称和一次平移的复合，速度反向。先做平移，到达Y0=Y-self.extent[3]*count，再反射，到self.extent[3]-Y0
            # 综合两种情形，奇数时Y0是负的，多一个self.extent[3];偶数时Y0是正的，没有self.extent[3]。综上，ynew=Y0*(-1)^count+(1-(-1)^count)/2*self.extent[3]
            # 因不清楚负数能不能做任意整指数幂，所以用取余来表示奇偶性。

            self.pos.y = (Y - count * self.extent[3]) * (1 - 2 * (count % 2)) + self.extent[3] * (count % 2)
            self.velocity.y = self.velocity.y * ((count + 1) % 2 * 2 - 1)
            return abs(count)
        else:  # case2： 恰好在边界

            # 两种情形：a） 向上穿墙，穿了1 - Y // self.extent[3] 次（代入Y = 0验证）
            #           b） 向下穿墙，穿了 Y // self.extent[3] 次（代入Y = self.extent[3] 验证）
            # 无论怎样，实际位置要么在0，要么在self.extent[3]。直接模( 2 * self.extent[3] )即可。
            # 速度只和count奇偶有关，同上。

            count = (Y // self.extent[3]) if (Y > 0) else (1 - Y // self.extent[3])
            self.pos.y = Y % (2 * self.extent[3])
            self.velocity.y = self.velocity.y * ((count + 1) % 2 * 2 - 1)
            return count
            # ===========END==============


'''
        # y方向速度为0
        if self.velocity.y == 0:
            return 0  # y坐标不改变，触壁次数为0
        elif self.velocity.y > 0:  # 向上y+飞
            # y方向的位置，考虑触壁反弹
            bounce_ticks = (self.extent[3] - self.pos.y) / self.velocity.y
            if bounce_ticks >= ticks:  # 没有触壁
                self.pos.y += self.velocity.y * ticks
                return 0
            else:  # 至少1次触壁
                # 计算后续触壁
                ticks -= bounce_ticks
                count, remain = divmod(ticks, ((self.extent[3] - self.extent[2]) / self.velocity.y))
                if count % 2 == 0:  # 偶数，则是速度改变方向
                    self.pos.y = self.extent[3] - remain * self.velocity.y
                    self.velocity.y = -self.velocity.y
                else:  # 奇数，速度方向不变
                    self.pos.y = self.extent[2] + remain * self.velocity.y
                return count + 1
        else:  # 向下y-飞
            # y方向的位置，考虑触壁反弹
            bounce_ticks = (self.extent[2] - self.pos.y) / self.velocity.y
            if bounce_ticks >= ticks:  # 没有触壁
                self.pos.y += self.velocity.y * ticks
                return 0
            else:  # 至少1次触壁
                # 计算后续触壁
                ticks -= bounce_ticks
                count, remain = divmod(ticks, ((self.extent[2] - self.extent[3]) / self.velocity.y))
                if count % 2 == 0:  # 偶数，则是速度改变方向
                    self.pos.y = self.extent[2] - remain * self.velocity.y
                    self.velocity.y = -self.velocity.y
                else:  # 奇数，速度方向不变
                    self.pos.y = self.extent[3] + remain * self.velocity.y
                return count + 1
'''


class RacketAction:  # 球拍动作
    def __init__(self, tick, bat_vector, acc_vector, run_vector):
        # self.t0 = tick  # tick时刻的动作，都是一维矢量，仅在y轴方向
        self.bat = bat_vector  # t0~t1迎球的动作矢量（移动方向及距离）
        self.acc = acc_vector  # t1触球加速矢量（加速的方向及速度）
        self.run = run_vector  # t1~t2跑位的动作矢量（移动方向及距离）


class Racket:  # 球拍
    def __init__(self, side, pos):  # 选边'West'／'East'和位置
        self.side, self.pos = side, pos
        self.life = RACKET_LIFE
        self.name = self.serve = self.play = self.action = self.datastore = None

    def bind_play(self, name, serve, play):  # 绑定玩家名称和serve, play函数
        self.name = name
        self.serve = serve
        self.play = play

    def set_action(self, action):  # 设置球拍动作
        self.action = action

    def set_datastore(self, ds):  # 设置数据存储，一个字典
        self.datastore = ds

    def get_velocity(self):
        # 球拍的全速是球X方向速度，按照体力值比例下降，当体力值下降到55%，将出现死角
        return int((self.life / RACKET_LIFE) * BALL_V[1])

    def update_pos_bat(self, tick_step):
        # 如果指定迎球的距离大于最大速度的距离，则采用最大速度距离
        bat_distance = sign(self.action.bat) * min(abs(self.action.bat), self.get_velocity() * tick_step)
        self.pos.y += bat_distance
        # 减少生命值
        self.life -= int(abs(bat_distance) ** 2 / FACTOR_DISTANCE ** 2)

    def update_pos_run(self, tick_step):
        # 如果指定跑位的距离大于最大速度的距离，则采用最大速度距离
        run_distance = sign(self.action.run) * min(abs(self.action.run), self.get_velocity() * tick_step)
        self.pos.y += run_distance
        # 减少生命值
        self.life -= int(abs(run_distance) ** 2 / FACTOR_DISTANCE ** 2)

    def update_acc(self):
        # 按照给球加速度的指标减少生命值
        self.life -= int(abs(self.action.acc) ** 2 / FACTOR_SPEED ** 2)


class TableData:  # 球桌信息，player计算用
    def __init__(self, tick, tick_step, side, op_side, ball):
        self.tick = tick
        self.step = tick_step
        self.side = side  # 字典，迎球方信息
        self.op_side = op_side  # 字典，跑位方信息
        self.ball = ball  # 字典，球的信息


class RacketData:  # 球拍信息，记录日志用
    def __init__(self, racket):
        self.side, self.name, self.life = racket.side, racket.name, racket.life
        self.pos, self.action = copy.copy(racket.pos), copy.copy(racket.action)


class BallData:  # 球的信息，记录日志用
    def __init__(self, ball_or_pos, velocity=None):
        if velocity is None:
            self.pos, self.velocity = copy.copy(ball_or_pos.pos), \
                                      copy.copy(ball_or_pos.velocity)
        else:
            self.pos, self.velocity = ball_or_pos, velocity


class Table:  # 球桌
    def __init__(self):
        # 桌面坐标系的范围，单位"pace"
        self.xmin, self.xmax, self.ymin, self.ymax = DIM
        self.tick = 0
        self.ball = None
        # tick增加的步长
        self.tick_step = (self.xmax - self.xmin) // BALL_V[0]  # 这是水平方向速度

        # 球拍，位置是球拍坐标系
        self.players = {'West': Racket('West', Position(self.xmin, self.ymax // 2)),
                        'East': Racket('East', Position(self.xmax, self.ymax // 2))}
        self.side = 'West'  # 球的初始位置在西侧的中央，发球的首先是West
        self.op_side = 'East'
        self.players['West'].set_action(RacketAction(self.tick, 0, 0, 0))
        self.players['East'].set_action(RacketAction(self.tick, 0, 0, 0))

        # 是否结束
        self.finished = False
        self.winner = None
        self.reason = None

    def change_side(self):  # 换边
        self.side, self.op_side = self.op_side, self.side

    def serve(self):  # 发球，始终是West发球
        self.tick = 0  # 当前的时刻tick
        player = self.players[self.side]  # 现在side是West
        pos_y, velocity_y = player.serve(player.datastore)  # 只提供y方向的位置和速度
        self.ball = Ball(DIM, Position(BALL_POS[0], pos_y),
                         Vector(BALL_V[0], velocity_y))  # 球的初始化
        self.change_side()  # 换边迎球
        return

    def time_run(self):  # 球跑一趟
        # t0时刻调用在t1时刻击球的一方
        # 1，首先让球从t0飞到t1时刻（确定轨迹）
        count_bounce = self.ball.fly(self.tick_step)
        if count_bounce not in (1, 2):  # 反弹没有在1、2次，对方输了
            self.finished = True
            self.winner = self.side
            self.reason = "invalid_bounce"
            return

        # 2，调用迎球方的算法
        #    参数：t0时刻双方位置和体力值，以及跑位方的跑位方向；
        #    参数：球在t1时刻的位置和速度
        player = self.players[self.side]
        op_player = self.players[self.op_side]
        dict_side = {'position': copy.copy(player.pos),
                     'life': player.life}
        dict_op_side = {'position': copy.copy(op_player.pos),
                        'life': op_player.life,
                        'accelerate': -1 if op_player.action.acc < 0 else 1,
                        'run_vector': -1 if op_player.action.run < 0 else 1}
        dict_ball = {'position': copy.copy(self.ball.pos),
                     'velocity': copy.copy(self.ball.velocity)}
        # 调用，返回迎球方的动作
        player_action = player.play(TableData(self.tick, self.tick_step,
                                              dict_side, dict_op_side, dict_ball),
                                    player.datastore)
        player.set_action(player_action)

        # 执行迎球方的两个动作：迎球和加速
        player.update_pos_bat(self.tick_step)
        if not (player.pos == self.ball.pos):
            # 没接上球
            print(player.pos, self.ball.pos)
            self.finished = True
            self.winner = self.op_side
            self.reason = "miss_ball"
            return
        player.update_acc()
        if player.life <= 0:
            # 生命值用尽，失败
            self.finished = True
            self.winner = self.op_side
            self.reason = "life_out"
            return
        self.ball.update_velocity(player.action.acc)
        self.ball.bounce_racket()  # 球在球拍反弹

        # 执行跑位方的一个动作：跑位
        op_player.update_pos_run(self.tick_step)
        if op_player.life <= 0:
            # 生命值用尽，失败
            self.finished = True
            self.winner = self.side
            self.reason = "life_out"
            return

        self.tick += self.tick_step  # 时间从t0到t1
        if self.tick >= TMAX:
            # 时间到，生命值高的胜出
            self.finished = True
            self.winner = self.side if (player.life > op_player.life) else self.op_side
            self.reason = "time_out"
            return

        self.change_side()  # 换边迎球
        return


class LogEntry:
    def __init__(self, tick, side, op_side, ball):
        self.tick = tick
        self.side = side
        self.op_side = op_side
        self.ball = ball
