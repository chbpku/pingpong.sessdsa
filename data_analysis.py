# -*- coding: utf-8 -*-
"""
Created on Mon May 29 08:33:33 2017
@author: redhated
17.6.3 新增数据数据分析功能
"""
import shelve
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
import time

TITLE = 'Results by team'


def print_none(*args, **kwargs):
    pass
    return


print = print_none


def readlog(logname):
    d = shelve.open(logname)
    log = d['log']
    west = d['West']
    east = d['East']
    winner = d['winner']
    reason = d['reason']
    winner_life = d['winner_life']

    d.close()
    return west, east, log, winner, reason, winner_life


# 新增preprocess函数
def preprocess(data):  # data[0]=(teamname,win,life)
    import numpy as np
    data.sort(key=lambda s: (s[1], s[2]))
    n_groups = len(data)
    LIFE = 0
    MAX = 0
    for i in data:
        LIFE += i[2]
        MAX = max(MAX, i[2])
    team_win = [i[1] for i in data]
    team_life = [i[2] * max(team_win) / MAX for i in data]
    team_name = [i[0][2:] for i in data]
    index = np.arange(n_groups)
    return index, team_win, team_life, team_name


def Main():
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
        # print('请注意，旧版生成的文件由于没有active_card属性，无法读取\n')
        for name in filter(lambda f: os.path.isfile(f) and os.path.getsize(f) != 0, file_list):
            m = r.match(name)
            if m is not None:
                # 不为空，则拿到了一个正确的文件
                logname = name[:name.rindex('.')]  # 去除.dat/.db后缀
                namelist.append(logname)
                # else:
                # 没找到，说明本目录下没有这个测试文件
                #   raise NameError("No Test File in this directory.")

    # 获胜次数 初始化
    Teams_win = {}  # 用来记录胜场数
    Teams = {}  # 用来记录参赛数
    win_Reasons = {}
    lose_Reasons = {}
    Teams_winner_life = {}

    for i in range(len(namelist)):
        logname = namelist[i]
        west_name, east_name, log, winner, reason, winner_life = readlog(logname)
        if west_name not in Teams.keys():
            Teams[west_name] = 1
        else:
            Teams[west_name] += 1
        if east_name not in Teams.keys():
            Teams[east_name] = 1
        else:
            Teams[east_name] += 1

        if winner == 'West':
            if west_name not in Teams_win.keys():
                Teams_win[west_name] = 1
                Teams_winner_life[west_name] = winner_life
            else:
                Teams_win[west_name] += 1
                Teams_winner_life[west_name] += winner_life
            if west_name not in win_Reasons.keys():
                win_Reasons[west_name] = {}
            if east_name not in lose_Reasons.keys():
                lose_Reasons[east_name] = {}
            if west_name not in lose_Reasons.keys():
                lose_Reasons[west_name] = {}
            if east_name not in win_Reasons.keys():
                win_Reasons[east_name] = {}
            if reason not in win_Reasons[west_name].keys():
                win_Reasons[west_name][reason] = 1
            else:
                win_Reasons[west_name][reason] += 1
            if reason not in lose_Reasons[east_name].keys():
                lose_Reasons[east_name][reason] = 1
            else:
                lose_Reasons[east_name][reason] += 1

        if winner == 'East':
            if east_name not in Teams_win.keys():
                Teams_win[east_name] = 1
                Teams_winner_life[east_name] = winner_life
            else:
                Teams_win[east_name] += 1
                Teams_winner_life[east_name] += winner_life
            if west_name not in win_Reasons.keys():
                win_Reasons[west_name] = {}
            if east_name not in lose_Reasons.keys():
                lose_Reasons[east_name] = {}
            if west_name not in lose_Reasons.keys():
                lose_Reasons[west_name] = {}
            if east_name not in win_Reasons.keys():
                win_Reasons[east_name] = {}
            if reason not in win_Reasons[east_name].keys():
                win_Reasons[east_name][reason] = 1
            else:
                win_Reasons[east_name][reason] += 1
            if reason not in lose_Reasons[west_name].keys():
                lose_Reasons[west_name][reason] = 1
            else:
                lose_Reasons[west_name][reason] += 1

    data = list()
    for key in Teams.keys():
        temp = list()
        print(key)
        if key in Teams_win.keys():
            print(Teams_win[key], "/", Teams[key])
        else:
            print(0)
        print('win for', win_Reasons[key])
        print('lose for', lose_Reasons[key])
        print()
        temp = key, Teams_win[key] if key in Teams_win else 0, Teams_winner_life[key] if key in Teams_winner_life else 0
        data.append(temp)
    return data


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
plt.ion()  # interactive mode on

if __name__ == '__main__':  # 新增交互式数据分析
    while 1:
        data = Main()
        index, team_win, team_life, team_name = preprocess(data)

        bar_width = 0.35
        opacity = 0.4
        plt.clf()
        plt.barh(index + bar_width, team_win, bar_width, alpha=opacity, color='b', label='Win')
        plt.barh(index, team_life, bar_width, alpha=opacity, color='r', label='Life')

        for x, y in zip(team_win, index):
            plt.text(x + 0.25, y + 0.35, '%d' % x, ha='center', va='bottom', fontsize=12)

        plt.xlabel('Value')
        plt.ylabel('Team')
        plt.title(TITLE)
        plt.yticks(index + bar_width, team_name)
        plt.legend(loc='lower right')
        plt.tight_layout()
        plt.pause(1)
