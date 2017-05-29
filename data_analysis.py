# -*- coding: utf-8 -*-
"""
Created on Mon May 29 08:33:33 2017

@author: redhated
"""
import shelve
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid

def readlog(logname):
    d = shelve.open(logname)
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
        #print('请注意，旧版生成的文件由于没有active_card属性，无法读取\n')
        for name in filter(lambda f: os.path.isfile(f) and os.path.getsize(f) != 0, file_list):
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
           
    
    for key in Teams.keys():
        print(key)
        if key in Teams_win.keys():
            print(Teams_win[key],"/",Teams[key])
        else:
            print(0)
        print('win for', win_Reasons[key])
        print('lose for', lose_Reasons[key])
        print()

    
    
        
            
                
            
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
       
    
