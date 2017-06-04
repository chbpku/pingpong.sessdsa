# -*- coding: utf-8 -*-
"""
Created on Mon May 29 08:33:33 2017

@author: redhated
"""
import shelve
import math
from table import Card
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
path = r'D:\PycharmProjects\pingpong.sessdsa\test\\'
def readlog(logname):
    d = shelve.open(path+logname)
    log = d['log']
    west = d['West']
    east= d['East']
    winner = d['winner']
    reason = d['reason']
    d.close()
    return west , east , log , winner , reason


#def data_analysis(name:str):




if __name__ == '__main__':
    # 寻找文件并读取，借用show.py（其实是我本人开发的）代码
    import sys
    #path = r'D:\PycharmProjects\pingpong.sessdsa\test'
    if len(sys.argv) == 2:
        logname = sys.argv[1]
        # 兼容原来的命令行参数查找模式
        namelist = [logname]
    else:
        # 这里对当前目录进行搜索，找到一个字节数不为0的dat文件
        import os, re
        #file_list = os.listdir(os.getcwd())
        file_list = os.listdir(path)
        # 编译正则表达式，寻找对应的文件名
        r = re.compile(r'^\[[EW]\.[A-Z]\]T_[^-]+-VS-T_[^.]+\.(dat|db)$')
        # 首先保证是文件而不是目录，且不为空
        namelist = []  # 用来保存所有对战名称
        #print('请注意，旧版生成的文件由于没有active_card属性，无法读取\n')

        #for name in filter(lambda f: os.path.isfile(f) and os.path.getsize(f) != 0, file_list):
        for name in filter(lambda f: os.path.isfile(os.path.join(os.getcwd(), 'test', f)) and os.path.getsize(
                os.path.join(os.getcwd(), 'test', f)) != 0, file_list):
            m = r.match(name)
            if m is not None:
                # 不为空，则拿到了一个正确的文件
                logname = name[:name.rindex('.')]  # 去除.dat/.db后缀
                namelist.append(logname)
                # else:
                # 没找到，说明本目录下没有这个测试文件
                #   raise NameError("No Test File in this directory.")
    
    #获胜次数 初始化
    Teams_win={}     #用来记录胜场数
    Teams={}    #用来记录参赛数 
    win_Reasons={}
    lose_Reasons={}

    move_times_of = {}
    bat_of = {}
    run_of = {}
    acc_of = {}
    acc_times_of = {}
    life_cost_of = {}

    items_got_num = {}
    items_used_num = {}
    items_got ={'SP': {}, 'DS': {}, 'IL': {}, 'DL': {}, 'TP': {}, 'AM': {}}
    items_used = {'SP': {}, 'DS': {}, 'IL': {}, 'DL': {}, 'TP': {}, 'AM': {}}

    def set_default(team_name):
        move_times_of.setdefault(team_name, 0)
        bat_of.setdefault(team_name, 0)
        run_of.setdefault(team_name, 0)
        acc_of.setdefault(team_name, 0)
        acc_times_of.setdefault(team_name, 0)
        life_cost_of.setdefault(team_name, 0)

        items_got_num.setdefault(team_name, 0)
        items_used_num.setdefault(team_name, 0)
        for item_name in items_got.keys():
            items_got[item_name].setdefault(team_name, 0)
            items_used[item_name].setdefault(team_name, 0)

    for i in range(len(namelist)):
        logname = namelist[i]
        west_name , east_name, log, winner, reason = readlog(logname)
        if west_name not in Teams.keys():
            Teams[west_name]=1
        else:
            Teams[west_name]+=1
        if east_name not in Teams.keys():
            Teams[east_name]=1
        else:
            Teams[east_name]+=1
            
        if winner == 'West':
            if west_name not in Teams_win.keys():
                Teams_win[west_name]=1
            else:
                Teams_win[west_name]+=1
            if west_name not in win_Reasons.keys():
                win_Reasons[west_name]={}
            if east_name not in lose_Reasons.keys():
                lose_Reasons[east_name]={}
            if west_name not in lose_Reasons.keys():
                lose_Reasons[west_name]={}
            if east_name not in win_Reasons.keys():
                win_Reasons[east_name]={}
            if reason not in win_Reasons[west_name].keys():
                win_Reasons[west_name][reason]=1
            else:
                win_Reasons[west_name][reason]+=1
            if reason not in lose_Reasons[east_name].keys():
                lose_Reasons[east_name][reason]=1
            else:
                lose_Reasons[east_name][reason]+=1

        if winner == 'East':
            if east_name not in Teams_win.keys():
                Teams_win[east_name]=1
            else:
                Teams_win[east_name]+=1
            if west_name not in win_Reasons.keys():
                win_Reasons[west_name]={}
            if east_name not in lose_Reasons.keys():
                lose_Reasons[east_name]={}
            if west_name not in lose_Reasons.keys():
                lose_Reasons[west_name]={}
            if east_name not in win_Reasons.keys():
                win_Reasons[east_name]={}
            if reason not in win_Reasons[east_name].keys():
                win_Reasons[east_name][reason]=1
            else:
                win_Reasons[east_name][reason]+=1
            if reason not in lose_Reasons[west_name].keys():
                lose_Reasons[west_name][reason]=1
            else:
                lose_Reasons[west_name][reason]+=1

        # try to analyse features of moving by CX
        set_default(west_name)
        set_default(east_name)
        br_last_card_box_num = 0
        rr_last_card_box_num = 0
        for a_log_entry in log:
            bat_racket = a_log_entry.side
            run_racket = a_log_entry.op_side

            bat_of[bat_racket.name] += math.fabs(bat_racket.action.bat)
            run_of[run_racket.name] += math.fabs(run_racket.action.run)
            if math.fabs(bat_racket.action.bat) > 0:
                move_times_of[bat_racket.name] += 1
                if math.fabs(bat_racket.action.acc) > 0:
                    acc_times_of[bat_racket.name] += 1
                    acc_of[bat_racket.name] += math.fabs(bat_racket.action.acc)
            if math.fabs(run_racket.action.run) > 0:
                move_times_of[bat_racket.name] += 1
                if math.fabs(run_racket.action.acc) > 0:
                    acc_times_of[run_racket.name] += 1
                    acc_of[run_racket.name] += math.fabs(run_racket.action.acc)
            life_cost_of[bat_racket.name] += math.fabs(bat_racket.bat_lf) + math.fabs(bat_racket.acc_lf) \
                                             + math.fabs(bat_racket.run_lf) + math.fabs(bat_racket.card_lf)
            life_cost_of[run_racket.name] += math.fabs(run_racket.bat_lf) + math.fabs(run_racket.acc_lf) \
                                             + math.fabs(run_racket.run_lf) + math.fabs(run_racket.card_lf)
            # try to analyse features of items by CX
            # if br_last_card_box_num < len(bat_racket.card_box):
            #     items_got_num[bat_racket.name] += 1
            #     items_got[bat_racket.card_box[-1].code][bat_racket.name] += 1
            # br_last_card_box_num = len(bat_racket.card_box)
            #
            # if rr_last_card_box_num < len(run_racket.card_box):
            #     items_got_num[run_racket.name] += 1
            #     items_got[run_racket.card_box[-1].code][run_racket.name] += 1
            # rr_last_card_box_num = len(run_racket.card_box)

            ac_card = a_log_entry.card.active_card[1]
            # print(type(ac_card))
            if isinstance(ac_card, Card):
                items_used_num[run_racket.name] += 1
                items_used[ac_card.code][run_racket.name] += 1



    
    for key in Teams.keys():
        print(key)
        if key in Teams_win.keys():
            print(Teams_win[key],"/",Teams[key])
        else:
            print(0)
        print('win for', win_Reasons[key])
        print('lose for', lose_Reasons[key])
        print('\t\t---features of moving---')
        print('index\t\t\t\ttotal\t\t\t\taverage')
        print('moves\t\t\t', move_times_of[key], '\t\t\t\t', move_times_of[key] / Teams[key])
        print('bat distance:\t', bat_of[key], '\t\t', bat_of[key] / Teams[key])
        print('acc distance:\t', acc_of[key], '\t\t\t', acc_of[key] / Teams[key])
        print('acc times:\t\t', acc_times_of[key], '\t\t\t\t', acc_times_of[key] / Teams[key])
        print('run distance:\t', run_of[key], '\t\t', run_of[key] / Teams[key])
        print('life cost\t\t', life_cost_of[key], '\t\t\t', life_cost_of[key] / Teams[key])
        print()
        print('\t\t---features of card---')
        print('items used num:', items_used_num[key])
        for item_name in items_got.keys():
            print('item %s used num' % item_name, items_used[item_name][key])
        print('items used num per game:', items_used_num[key] / Teams[key])
        print()

    
    
        
            
                
            
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
       
    
