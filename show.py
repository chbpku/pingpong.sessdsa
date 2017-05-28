# show by 张颢丹
# 2015/5/27 3:40 冀锐 修改 实现扣血详细信息的显示
# 读取对局文件, 把对局可视化
# 如果带了命令行参数, 打开参数里的文件
# 否则根据文件中的文件名打开文件(第116行附近)
#
# 注: 需要和table放在同一个目录下
# 注: 只输入文件名, 不要带扩展名
# 例: '[W.T]T_idiot-VS-T_idiot'

# 不要在意里面的各种神秘数字

from table import *
import pygame
from pygame.locals import *
import shelve, time
import sys

Clock = pygame.time.Clock()

# 这个参数用来调整时间流逝的速率
# game_speed=1时, 一来回需要3.6秒
game_speed = 1
# 各种参数
x, y = 18, 10
s_size = (1024, 600)
x_n = s_size[0] // 2 // 18
y_n = s_size[1] // 2 // 10
n = x_n if x_n < y_n else y_n
center = (s_size[0] / 2, s_size[1] / 2)
# 球桌的四个角的坐标
table = (
    (center[0] - x / 2 * n, center[1] - y / 2 * n),
    (center[0] + x / 2 * n, center[1] - y / 2 * n),
    (center[0] + x / 2 * n, center[1] + y / 2 * n),
    (center[0] - x / 2 * n, center[1] + y / 2 * n),)


# 读取文件, 返回文件中的log类, 胜利者, 和胜利原因
def readlog(logname):
    d = shelve.open(logname)
    log = d['log']
    winner = d['winner']
    reason = d['reason']
    d.close()
    return log, winner, reason


# 把log类转换成字典
def getdata(alog):
    d = {}
    d['ball_pos'] = alog.ball.pos
    d['ball_v'] = alog.ball.velocity
    d['tick'] = alog.tick
    d['player'] = {}
    d['player'][alog.side.side] = alog.side
    d['player'][alog.op_side.side] = alog.op_side
    d['cards'] = alog.card.cards  # 当前球桌上的散落道具，尚未被获取
    d['card_tick'] = alog.card.card_tick  # 道具出现时间的计时，0—CARD_FREQ
    d['active_card'] = alog.card.active_card  # 当前使用的道具（'SELF'/'OPNT', card_code），'SELF'指跑位方
    d['side'] = alog.side.side  # 迎球方
    d['op_side'] = alog.op_side.side  # 跑位方

    return d


# 把球桌坐标转换成pygame屏幕的坐标
def pos_trans(oldpos):
    pos_x = int((0.0 + oldpos.x / (DIM[1] - DIM[0])) * n * x + center[0])
    pos_y = int((0.5 - oldpos.y / (DIM[3] - DIM[2])) * n * y + center[1])
    return (pos_x, pos_y)


# 画球桌
def draw_table(screen):
    polygon_1 = (
        (center[0] - x / 2 * n, center[1] - y / 2 * n),
        (center[0] + x / 2 * n, center[1] - y / 2 * n),
        (center[0] + x / 2 * n, center[1] - y / 2 * n - 10),
        (center[0] - x / 2 * n, center[1] - y / 2 * n - 10),)
    polygon_2 = (
        (center[0] + x / 2 * n, center[1] + y / 2 * n),
        (center[0] - x / 2 * n, center[1] + y / 2 * n),
        (center[0] - x / 2 * n, center[1] + y / 2 * n + 10),
        (center[0] + x / 2 * n, center[1] + y / 2 * n + 10),)
    pygame.draw.polygon(screen, (0, 255, 0), polygon_1, 0)
    pygame.draw.polygon(screen, (0, 255, 0), polygon_2, 0)


# 画球
def draw_ball(screen, ball_pos):
    pos = pos_trans(ball_pos)
    pygame.draw.circle(screen, (0, 0, 0), pos, 8, 0)


# 画球拍
def draw_player(screen, player):
    if player.side == 'West':
        color = (255, 0, 0)
        poslist = ((player.pos.x / (DIM[1] - DIM[0]) * n * x + center[0],
                    -(player.pos.y / (DIM[3] - DIM[2]) - 0.5) * n * y + center[1] - 25),
                   (player.pos.x / (DIM[1] - DIM[0]) * n * x + center[0] - 10,
                    -(player.pos.y / (DIM[3] - DIM[2]) - 0.5) * n * y + center[1] - 25),
                   (player.pos.x / (DIM[1] - DIM[0]) * n * x + center[0] - 10,
                    -(player.pos.y / (DIM[3] - DIM[2]) - 0.5) * n * y + center[1] + 25),
                   (player.pos.x / (DIM[1] - DIM[0]) * n * x + center[0],
                    -(player.pos.y / (DIM[3] - DIM[2]) - 0.5) * n * y + center[1] + 25))
    else:
        color = (0, 0, 255)
        poslist = ((player.pos.x / (DIM[1] - DIM[0]) * n * x + center[0],
                    -(player.pos.y / (DIM[3] - DIM[2]) - 0.5) * n * y + center[1] - 25),
                   (player.pos.x / (DIM[1] - DIM[0]) * n * x + center[0] + 10,
                    -(player.pos.y / (DIM[3] - DIM[2]) - 0.5) * n * y + center[1] - 25),
                   (player.pos.x / (DIM[1] - DIM[0]) * n * x + center[0] + 10,
                    -(player.pos.y / (DIM[3] - DIM[2]) - 0.5) * n * y + center[1] + 25),
                   (player.pos.x / (DIM[1] - DIM[0]) * n * x + center[0],
                    -(player.pos.y / (DIM[3] - DIM[2]) - 0.5) * n * y + center[1] + 25))
    pos = pos_trans(player.pos)
    pygame.draw.polygon(screen, color, poslist, 0)


# 画
def draw_all(screen, ball_pos, player_1, player_2):
    draw_table(screen)
    draw_ball(screen, ball_pos)
    draw_player(screen, player_1)
    draw_player(screen, player_2)


# 写信息
def writeinfo(screen, player, font):
    screen.blit(font.render('W', True, (0, 0, 0)), (table[0][0] - 24 - 100, table[0][1] - 100))
    screen.blit(font.render('E', True, (0, 0, 0)), (table[1][0] + 100, table[1][1] - 100))
    screen.blit(font.render(player['West'].name, True, (0, 0, 0)), (table[0][0] - 24 - 100 - 20, table[0][1] - 50))
    screen.blit(font.render(player['East'].name, True, (0, 0, 0)), (table[1][0] + 100 - 20, table[1][1] - 50))
    screen.blit(font.render(str(int(player['West'].life)), True, (0, 0, 0)), (table[0][0] - 24, table[0][1] - 100))
    screen.blit(font.render(str(int(player['East'].life)), True, (0, 0, 0)), (table[1][0] - 80, table[1][1] - 100))


# 写血量改变
def writeChange(screen, player, font):
    screen.blit(font.render("bat:" + str(int(player['West'].bat_lf)), True, (0, 0, 0)),
                (table[0][0] - 244, table[0][1]))
    screen.blit(font.render("acc:" + str(int(player['West'].acc_lf)), True, (0, 0, 0)),
                (table[0][0] - 244, table[0][1] + 25))
    screen.blit(font.render("run:" + str(int(player['West'].run_lf)), True, (0, 0, 0)),
                (table[0][0] - 244, table[0][1] + 50))
    screen.blit(font.render("card:" + str(int(player['West'].card_lf)), True, (0, 0, 0)),
                (table[0][0] - 244, table[0][1] + 75))
    screen.blit(font.render("bat:" + str(int(player['East'].bat_lf)), True, (0, 0, 0)),
                (table[1][0] + 180, table[1][1]))
    screen.blit(font.render("acc:" + str(int(player['East'].acc_lf)), True, (0, 0, 0)),
                (table[1][0] + 180, table[1][1] + 25))
    screen.blit(font.render("run:" + str(int(player['East'].run_lf)), True, (0, 0, 0)),
                (table[1][0] + 180, table[1][1] + 50))
    screen.blit(font.render("card:" + str(int(player['East'].card_lf)), True, (0, 0, 0)),
                (table[1][0] + 180, table[1][1] + 75))


# 画道具
def draw_card(screen, cards, font):
    for card in cards:
        x, y = pos_trans(card.pos)
        image = pygame.transform.rotozoom(pygame.image.load('%s.png' % card.code.lower()), 0, 0.6)
        x -= image.get_width() / 2
        y -= image.get_height() / 2
        screen.blit(image, (x, y))


# 画道具箱
def draw_card_box(screen, player):
    i = 0
    for card in player['West'].card_box:
        image = pygame.image.load('%s.png' % card.code.lower()).convert_alpha()
        screen.blit(image, (150 - image.get_width() / 2, 170 + i))
        i += image.get_height() + 10
    i = 0
    for card in player['East'].card_box:
        image = pygame.image.load('%s.png' % card.code.lower()).convert_alpha()
        screen.blit(image, (s_size[0] - 150 - image.get_width() / 2, 170 + i))
        i += image.get_height() + 10


# 画道具使用历史
def draw_card_history(screen, player_card_history):
    # TODO 跟draw_card_box类似，需要一个新的坐标容纳各自的使用道具历史
    i = 0
    for card in player_card_history['West']:
        image = pygame.image.load('%s.png' % card[1].code.lower()).convert_alpha()
        screen.blit(image, (200 - image.get_width() / 2, 170 + i))
        i += image.get_height() + 10
    i = 0
    for card in player_card_history['East']:
        image = pygame.image.load('%s.png' % card[1].code.lower()).convert_alpha()
        screen.blit(image, (s_size[0] - 200 - image.get_width() / 2, 170 + i))
        i += image.get_height() + 10
    return


def main():
    # 判断有无命令行参数
    if len(sys.argv) == 2:
        logname = sys.argv[1]
        # 兼容原来的命令行参数查找模式
        namelist = [logname]
    else:
        # 这里对当前目录进行搜索，找到一个字节数不为0的dat文件
        import os, re
        file_list = os.listdir(os.getcwd())
        # 编译正则表达式，寻找对应的文件名
        r = re.compile(r'^\[[EW]\.[A-Z]\]T_[^-]+-VS-T_[^.]+\.(dat|db)$')
        # 首先保证是文件而不是目录，且不为空
        namelist = []  # 用来保存所有对战名称
        print('请注意，本代码不支持未找到的报错，希望有人能改正\n')
        for name in filter(lambda f: os.path.isfile(f) and os.path.getsize(f) != 0, file_list):
            m = r.match(name)
            if m is not None:
                # 不为空，则拿到了一个正确的文件
                logname = name[:name.rindex('.')]  # 去除.dat/.db后缀
                namelist.append(logname)
                # else:
                # 没找到，说明本目录下没有这个测试文件
                #   raise NameError("No Test File in this directory.")
    while True:
        try:
            if not namelist:
                raise NameError
            for i in range(len(namelist)):
                print('第', i, '个', namelist[i])
            ssssss = int(input('请输入你想看的对战的序号，从0开始，到%d结束\n' % (len(namelist) - 1)))  # 序号

            logname = namelist[ssssss]
            break
        except ValueError as e:
            # 输入了一个非数字
            print('请输入合法数字！')
        except IndexError as e:
            # 列表越界
            print('请输入范围内的数字（0-%d）' % (len(namelist) - 1))
        except NameError as e:
            print('没有测试文件！')
            input('请输入回车键退出程序')
            exit()

    # 读出log, winner, reason
    log, winner, reason = readlog(logname)
    over = False

    # pygame初始化
    pygame.init()
    screen = pygame.display.set_mode(s_size)
    font = pygame.font.SysFont("arial", 32)
    small_font = pygame.font.SysFont("arial", 16)
    clock = pygame.time.Clock()

    # 初始化cardhistory
    player_card_history = {'West': [], 'East': []}

    # 读取两轮数据
    d_current = getdata(log.pop(0))
    player = d_current['player']
    ball_pos = d_current['ball_pos']
    ball_v = d_current['ball_v']
    tick = d_current['tick']
    # 给使用道具一方(跑位方)加上当前道具
    card_tick = d_current['card_tick']
    if d_current['active_card'][0] is not None:
        player_card_history[d_current['op_side']].append(d_current['active_card'])

    next_tick = 0

    if len(log) > 1:
        d_next = getdata(log.pop(0))
        next_tick = d_next['tick']
    else:
        over = True

    clock.tick()

    while True:
        Clock.tick(100)  # 限制FPS
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

        # 画画
        screen.fill((255, 255, 255))
        writeinfo(screen, player, font)
        draw_card(screen, d_current['cards'], font)
        draw_card_box(screen, player)
        draw_card_history(screen, player_card_history)
        draw_all(screen, ball_pos, player['West'], player['East'])
        writeChange(screen, player, small_font)
        t_passed = clock.tick() * game_speed

        # 最后一次记录之后再走半回合
        if over and tick >= next_tick + 1800:
            tick = next_tick + 1800
            screen.blit(font.render(reason, True, (0, 0, 0)), (center[0] - 50, center[1] - 220))
            screen.blit(font.render("%s win!" % player[winner].name, True, (0, 0, 0)),
                        (center[0] - 60, center[1] - 270))
            t_passed = 0

        # 时间流逝和球的移动
        tick += t_passed
        card_tick += t_passed
        screen.blit(font.render("tick: %s cardtick:%s" % (tick, card_tick), True, (0, 0, 0)), (20, 20))
        ball_pos.x += ball_v.x * t_passed
        ball_pos.y += ball_v.y * t_passed

        # 半回合后读取下一次记录
        if not over and tick >= next_tick:
            d_current = d_next
            player = d_current['player']
            ball_pos = d_current['ball_pos']
            ball_v = d_current['ball_v']
            tick = d_current['tick']

            # 判断是否为最后一次记录
            if len(log) > 1:
                d_next = getdata(log.pop(0))
                next_tick = d_next['tick']
            else:
                over = True

            # 给使用道具一方(跑位方)加上当前道具
            card_tick = d_current['card_tick']
            if d_current['active_card'][0] is not None:
                player_card_history[d_current['op_side']].append(d_current['active_card'])
                while len(player_card_history[d_current['op_side']])> 7:
                    player_card_history[d_current['op_side']].pop(0)

        # 碰到上下墙壁时进行反弹
        if ball_pos.y >= DIM[3]:
            ball_pos.y = (DIM[3]) * 2 - ball_pos.y
            ball_v.y = -ball_v.y
        elif ball_pos.y <= DIM[2]:
            ball_pos.y = (DIM[2]) * 2 - ball_pos.y
            ball_v.y = -ball_v.y

        # 更新画面
        pygame.display.update()


if __name__ == '__main__':
    main()
