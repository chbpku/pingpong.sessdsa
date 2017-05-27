import hashlib

teams = ['ALPHA 常啸寅',
         'BRAVO 陈宇枫',
         'CHARLIE 郭浩(地空)',
         'DELTA 贾昊凝',
         'ECHO 蒋天骥',
         'FOXTROT 李思彤',
         'GOLF 林荣',
         'HOTEL 刘立洋',
         'INDIA 闵靖涛',
         'JULIET 朴健',
         'KILO 邵俊宁',
         'LIMA 陶天阳',
         'MIKE 王梦瑶',
         'NOVEMBER 文家豪',
         'OSCAR 吴宜谦',
         'PAPA 徐晨雨',
         'QUEBEC 杨帆',
         'ROMEO 杨子珍',
         'SIERRA 张影',
         'TANGO 周云帆',
         'UNIFORM 孟柳昳',
         'VICTOR 端韵成',
         'WHISKEY 张容榕',
         'X-RAY 裴召文',
         'YANKEE 向汗青',
         'ZULU 贺旎妮']

# 计算各组的sha1散列值，并按照散列值排序
teams_hash = [(team, hashlib.sha1(team.encode()).hexdigest()) for team in teams]
teams_hash.sort(key=lambda x: x[1])

# 按照散列值排序，交错分配到NEWS四个分区
region = list('NEWSNEWSNEWSNEWSNEWSNEWSNE')
teams_region = list(zip(region, teams_hash))
teams_region.sort(key=lambda x: x[0])

# 打印输出
import pprint

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(teams_region)
