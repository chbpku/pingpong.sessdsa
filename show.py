# show by pkuzhd
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
import shelve
import sys

#这个参数用来调整时间流逝的速率
#m=1时, 一来回需要3.6秒
m = 1
#各种参数
x, y = 18, 10
s_size = (1024, 600)
x_n = s_size[0]//2//18
y_n = s_size[1]//2//10
n = x_n if x_n < y_n else y_n
center = (s_size[0]/2, s_size[1]/2)
#球桌的四个角的坐标
table = (
    (center[0]-x/2*n, center[1]-y/2*n),
    (center[0]+x/2*n, center[1]-y/2*n),
    (center[0]+x/2*n, center[1]+y/2*n),
    (center[0]-x/2*n, center[1]+y/2*n),)

#读取文件, 返回文件中的log类
def readlog(logname):
    d = shelve.open(logname)
    log = d['log']
    d.close()
    return log

#把log类转换成字典
def getdata(alog):
    d = {}
    d['ball_pos'] = alog.ball.pos
    d['ball_v']= alog.ball.velocity
    d['tick'] = alog.tick
    d['player'] = {}
    d['player'][alog.side.side] = alog.side
    d['player'][alog.op_side.side] = alog.op_side
    return d

#把球桌坐标转换成pygame屏幕的坐标
def pos_trans(oldpos):
    pos_x = int((0.0+oldpos.x/(DIM[1]-DIM[0]))*n*x+center[0])
    pos_y = int((0.5-oldpos.y/(DIM[3]-DIM[2]))*n*y+center[1])
    return (pos_x, pos_y)

#画球桌
def draw_table(screen):
    polygon_1 = (
        (center[0]-x/2*n, center[1]-y/2*n),
        (center[0]+x/2*n, center[1]-y/2*n),
        (center[0]+x/2*n, center[1]-y/2*n-10),
        (center[0]-x/2*n, center[1]-y/2*n-10),)
    polygon_2 = (
        (center[0]+x/2*n, center[1]+y/2*n),
        (center[0]-x/2*n, center[1]+y/2*n),
        (center[0]-x/2*n, center[1]+y/2*n+10),
        (center[0]+x/2*n, center[1]+y/2*n+10),)
    pygame.draw.polygon(screen, (0,255,0), polygon_1, 0)
    pygame.draw.polygon(screen, (0,255,0), polygon_2, 0)

#画球
def draw_ball(screen, ball_pos):
    pos = pos_trans(ball_pos)
    pygame.draw.circle(screen, (0,0,0), pos, 8, 0)

#画球拍
def draw_player(screen, player):
    if player.side == 'West':
        color = (255, 0, 0)
        poslist = ((player.pos.x/(DIM[1]-DIM[0])*n*x+center[0]   , -(player.pos.y/(DIM[3]-DIM[2])-0.5)*n*y+center[1]-25),
                   (player.pos.x/(DIM[1]-DIM[0])*n*x+center[0]-10, -(player.pos.y/(DIM[3]-DIM[2])-0.5)*n*y+center[1]-25),
                   (player.pos.x/(DIM[1]-DIM[0])*n*x+center[0]-10, -(player.pos.y/(DIM[3]-DIM[2])-0.5)*n*y+center[1]+25),
                   (player.pos.x/(DIM[1]-DIM[0])*n*x+center[0]   , -(player.pos.y/(DIM[3]-DIM[2])-0.5)*n*y+center[1]+25))
    else:
        color = (0, 0, 255)
        poslist = ((player.pos.x/(DIM[1]-DIM[0])*n*x+center[0]   , -(player.pos.y/(DIM[3]-DIM[2])-0.5)*n*y+center[1]-25),
                   (player.pos.x/(DIM[1]-DIM[0])*n*x+center[0]+10, -(player.pos.y/(DIM[3]-DIM[2])-0.5)*n*y+center[1]-25),
                   (player.pos.x/(DIM[1]-DIM[0])*n*x+center[0]+10, -(player.pos.y/(DIM[3]-DIM[2])-0.5)*n*y+center[1]+25),
                   (player.pos.x/(DIM[1]-DIM[0])*n*x+center[0]   , -(player.pos.y/(DIM[3]-DIM[2])-0.5)*n*y+center[1]+25))
    pos = pos_trans(player.pos)
    pygame.draw.polygon(screen, color, poslist, 0)

#画
def draw_all(screen, ball_pos, player_1, player_2):
    draw_table(screen)
    draw_ball(screen, ball_pos)
    draw_player(screen, player_1)
    draw_player(screen, player_2)

#写信息
def writeinfo(screen, player, font):
    screen.blit(font.render('W', True, (0,0,0)),(table[0][0]-24-100,table[0][1]-100))
    screen.blit(font.render('E', True, (0,0,0)),(table[1][0]   +100,table[1][1]-100))
    screen.blit(font.render(player['West'].name, True, (0,0,0)),(table[0][0]-24-100-20,table[0][1]-50))
    screen.blit(font.render(player['East'].name, True, (0,0,0)),(table[1][0]   +100-20,table[1][1]-50))
    screen.blit(font.render(str(int(player['West'].life)), True, (0,0,0)),(table[0][0]-24,table[0][1]-100))
    screen.blit(font.render(str(int(player['East'].life)), True, (0,0,0)),(table[1][0]-80,table[1][1]-100))

def main():

    #判断有无命令行参数
    if len(sys.argv)==2:
        logname = sys.argv[1]
    else:
        logname = '[W.T]T_idiot-VS-T_idiot'
    
    #读出log
    log = readlog(logname)

    #pygame初始化
    pygame.init()
    screen = pygame.display.set_mode(s_size)
    font = pygame.font.SysFont("arial", 32)
    clock = pygame.time.Clock()

    #读取两轮数据
    d_current = getdata(log.pop(0))
    player = d_current['player']
    d_next = getdata(log.pop(0))
    ball_pos = d_current['ball_pos']
    ball_v = d_current['ball_v']
    tick = d_current['tick']
    next_tick = d_next['tick']
    

    clock.tick()
    over = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

        #画画        
        screen.fill((255, 255, 255))
        writeinfo(screen, player, font)
        draw_all(screen, ball_pos, player['West'], player['East'])

        t_passed = clock.tick()*m

        #最后一次记录之后再走半回合
        if over and tick > next_tick+1800:
            screen.blit(font.render('Game over', True, (0,0,0)),(center[0]-50, center[1]))
            t_passed = 0

        #时间流逝和球的移动
        tick += t_passed
        ball_pos.x+=ball_v.x*t_passed
        ball_pos.y+=ball_v.y*t_passed

        #半回合后读取下一次记录
        if not over and tick >= next_tick:
            d_current = d_next
            player = d_current['player']
            ball_pos = d_current['ball_pos']
            ball_v = d_current['ball_v']
            tick = d_current['tick']

            #判断是否为最后一次记录
            if len(log)>1:
                d_next = getdata(log.pop(0))
                next_tick = d_next['tick']
            else:
                over = True

        #碰到上下墙壁时进行反弹
        if ball_pos.y >= DIM[3]:
            ball_pos.y = (DIM[3])*2 - ball_pos.y
            ball_v.y = -ball_v.y
        elif ball_pos.y <= DIM[2]:
            ball_pos.y = (DIM[2])*2 - ball_pos.y
            ball_v.y = -ball_v.y
        
        #更新画面
        pygame.display.update()

if __name__ == '__main__':
    main()
