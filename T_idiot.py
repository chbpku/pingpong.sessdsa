from table import *


# 发球函数，总是做为West才发球
# op_side为对手方名称，以便从ds中查询以往记录数据
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(op_side: str, ds: dict) -> tuple:
    return BALL_POS[1], BALL_V[1]  # 返回球的y坐标，和y方向上的速度


# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb: TableData, ds: dict) -> RacketAction:
    return RacketAction(tb.tick,  # 当前时间，照抄参数中的tb.tick即可
                        tb.ball['position'].y - tb.side['position'].y,  # 球拍的移动距离（有方向）
                        0,  # 球拍对球加速的速度（有方向）
                        0,  # 球拍击球后跑位的移动距离（有方向）
                        None,  # 使用道具，对谁使用'SELF'/'OPNT'
                        None  # Card对象，使用什么道具
                        )


# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
# 修改ds后，不需要返回数据
def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return
