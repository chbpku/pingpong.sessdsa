"""
@author Cobalt-Yang Fan
"""
import shelve
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid

def paint_life_time_line(name:str):
    """
    根据给定文件绘图，并保存为png文件
    :param name: 
    :return: 
    """
    try:
        # 打开shelve
        data = shelve.open(name)
        # 读取数据
        log = data['log']
        step, total_time, TMAX = data['tick_step'], data['tick_total'], data['TMAX']
        west, east, winner, reason = data['West'], data['East'], data['winner'], data['reason']
        # TODO 为当前各个图增加图例和副标题、标题
        # 设置绘图用的列表
        time_line = []
        w_health = []
        e_health = []
        ball_pos = []
        ball_speed = []
        w_pos = []
        e_pos = []
        card_data = []
        # 获取绘图数据
        for item in log:
            time_line.append(item.tick)
            if item.ball.pos.x < 0:
                # 说明球在左侧
                west_side = item.side
                east_side = item.op_side
            else:
                # 说明球在右侧
                west_side = item.op_side
                east_side = item.op_side
            # 获取左右生命值
            w_health.append(west_side.life)
            e_health.append(east_side.life)
            # 获取球的位置速度
            ball_pos.append(item.ball.pos.y)
            ball_speed.append(item.ball.velocity.y)
            # 获取左右板的位置
            w_pos.append(west_side.pos.y)
            e_pos.append(east_side.pos.y)
            # 使用道具情况（旧版本不支持道具）
            if hasattr(item.card, 'active_card'):
                card_data.append(item.card.active_card)
        # 划定绘图区域
        gs = grid.GridSpec(3,4)
        health_plot = plt.subplot(gs[0,:])
        ball_plot = plt.subplot(gs[1,:])
        bat_plot = plt.subplot(gs[2,:])
        # 绘制体力图
        # health_plot.'Life Graph -- Red for West, Blue for East'
        health_plot.plot(time_line, e_health, 'b')
        health_plot.plot(time_line, w_health, 'r')
        # 补充道具文本
        for i in range(len(card_data)):
            item = card_data[i]
            if item == (None, None):
                continue
            Side = log[i].op_side.side if item[0] == 'SELF' else log[i].side.side
            if Side == 'West':
                target = w_health
            else:
                target = e_health
            health_plot.annotate(item[1].code + ' to ' + Side, (time_line[i], target[i]))
        # 绘制球的信息图
        ball_plot.scatter(time_line, ball_pos, edgecolor = 'none', c = 'g')
        ball_plot.scatter(time_line, ball_speed, edgecolor = 'none', c = 'm')
        # 绘制板子信息图
        bat_plot.plot(time_line, w_pos, 'r-')
        bat_plot.plot(time_line, e_pos, 'b-')

        # 显示
        print('Hint：图像点较密集。若想看清每个点的细节，请放大')
        print('从上到下分别是体力图、球图和板子图')
        print('球图中，绿色为位置图，粉色为速度图')
        plt.show()

    except FileNotFoundError as e:
        print('读取发生错误：未找到文件')
        print(e)
    except KeyError as e:
        print('读取发生错误：未知键')
        print(e)

if __name__ == '__main__':
    # 寻找文件并读取，借用show.py（其实是我本人开发的）代码
    import sys
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
        print('请注意，旧版生成的文件由于没有active_card属性，无法读取\n')
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
    paint_life_time_line(logname)
