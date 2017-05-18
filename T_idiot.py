from table import *

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(ds):
    return BALL_POS[1], BALL_V[1]

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb, ds):
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, 0, 0)
