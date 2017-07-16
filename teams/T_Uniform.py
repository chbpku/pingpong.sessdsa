#coding = utf-8
#time: 2017/06/03

from table import *
import pickle  #文件记录的数据库

class MFunction:
    def __init__(self):
        self.ratio = 1800 # pingpong会对serve的速度向量进行取整，在时间T内y方向产生的最大误差为1800     
        self.up = [DIM[3]*3 - self.ratio, DIM[3] + self.ratio, -DIM[3]] #打上角的三种方式的“上角”纵坐标，分别为［上下上、上、下上］
        self.down = [-self.ratio, -2*DIM[3]+self.ratio, DIM[3]*2]  #打下角的三种方式的“下角”的纵坐标，分别为［下、下上下、上下］
 #       self.mid = [-DIM[3]/2, -DIM[3] * 3/2, DIM[3] * 3/2, DIM[3] * 5/2]       
        self.spin = 0  #初始化使用状态
        self.useful_card = [CARD_SPIN, CARD_INCL, CARD_DECL, CARD_AMPL]  #考虑使用的卡牌［‘旋转’，‘补血，’，‘掉血’，‘变压’］
        self.dic = None # 历史文件
        try: #write DS file
            f = open('DS_T_uniform', 'rb')
            self.dic = pickle.load(f)
            f.close()
        except:
            pass
 

    #计算从spend发球，想要经过ppass需要的速度改变
    def cal_speed(self, psend, ppass):   #psend:发球的位置坐标,ppass:想要经过的位置坐标
        t = abs(psend.x - ppass.x) / float(BALL_V[0])   #到达该点所需时间：利用横轴速度不变
        d = float(ppass.y - psend.y)    #两点在y方向上的距离（在没有墙的时候）  
        return d/t  #需要的速度，pingpong在运行时会对这个速度进行取整

    #检测碰壁次数是否合法->[1,2]
    def check(self, ypos, speed): #ypos：球当前位置，speed：y方向速度
        cross = ypos + (DIM[1] - DIM[0]) / float(BALL_V[0]) * speed #cross：没有墙的时候球的落点
        if cross > self.up[0] or cross < self.down[1]:  # 不合法范围1：碰壁超过两次
            return False
        if cross < self.up[1] and cross > self.down[0]: # 不合法范围2:碰壁少于一次
            return False
        return True
        
    
    #计算体力消耗:加速sp2->sp1
    def cost(self, sp1, sp2, card): 
        #如果被使用了“变压”，体力消耗＊2
        return ((sp1 - sp2) ** 2 / FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if card == CARD_AMPL else 1)
                  
    def card_to(self, card): #确定道具给谁用
        if card == CARD_DECL or card == CARD_AMPL:
            return 'OPNT'
        if card == CARD_DSPR or card == CARD_INCL or card == CARD_TLPT:
            return 'SELF'
        if card == CARD_SPIN and self.spin == 0: #第一次出现spin,先给自己用，想看对方是不是会默认spin给对手用，这样可以虚晃一枪
            self.spin = 1   
            return 'SELF'
        if card == CARD_SPIN and self.spin == 1:
            return 'OPNT'               
        return None

    def use_card(self, cards):  #使用道具，语句运行的时候遇到return 就停止了
        if cards.isfull():
            return cards[-1]
        for card in cards:
            return card
        return None

    def eat_card(self, tb: TableData): #判断是否吃道具
        lists = []
        psend = tb.ball['position']
        for card in tb.cards['cards']:
            if card not in self.useful_card:  #如果没有用
                continue
            ppass = card.pos
            ppass.y = -ppass.y   #向下反弹一次接住
            spd = self.cal_speed(psend, ppass)
            if self.check(psend.y, spd):
                lists.append(spd)
            
            ppass = card.pos
            ppass.y -= DIM[3] * 2   #向下弹两次接住
            spd = self.cal_speed(psend, ppass)
            if self.check(psend.y, spd):
                lists.append(spd)
            
            ppass = card.pos
            ppass.y = DIM[3] * 2 - ppass.y   #向上弹一次接住
            spd = self.cal_speed(psend, ppass)
            if self.check(psend.y, spd):
                lists.append(spd)    

            ppass = card.pos     
            ppass.y += DIM[3] * 2   #向上反弹两次接住
            spd = self.cal_speed(psend, ppass)
            if self.check(psend.y, spd):
                lists.append(spd)

        min_cost = 3000 #物品的收益约在2000左右，消耗太大就不吃了
        spd = None
        for item in lists:  #找到捕捉道具的最小体力损耗
            cost = self.cost(item, tb.ball['velocity'].y, tb.op_side['active_card'][1])
            if cost < min_cost :
                min_cost = cost
                spd = item 
        return spd

    #跑位函数：从接球处回到中点
    def move(self, tb: TableData):
        return DIM[3] / 2 - tb.ball['position'].y

    #击球函数:返回球速spd
    def hit(self, tb: TableData):
        lists = []     #lists:所有加速的列表
        hhit = self.up #hhit：球落点纵坐标,默认打上角
        #如果对方位于中点以上:打下角
        if tb.op_side['position'].y > DIM[3] / 2 :
            hhit = self.down
        
        for Loc in hhit:            #spd:使球到Loc的球速
            spd = self.cal_speed(tb.ball['position'], Position(tb.op_side['position'].x, Loc))
            lists.append(spd)

        min_change = abs(lists[0] - tb.ball['velocity'].y) #对球速列表排序，并取最小值计算加速最小值
        spd = lists[0]
        for item in lists:#再算一次,用最小加速和刚才的值比较，取最优情况
            change = abs(item - tb.ball['velocity'].y)
            if change < min_change:
                min_change = change
                spd = item
        
        #如果打远角消耗的体力太多，改打近角
        if self.cost(spd, tb.ball['velocity'].y, tb.op_side['active_card'][1]) > 1250:
            if hhit == self.up:
                hhit = self.down
            else:
                hhit = self.up
            for Loc in hhit:
                spd = self.cal_speed(tb.ball['position'], Position(tb.op_side['position'].x, Loc))
                lists.append(spd) 
        #再排一次序
        min_change = abs(lists[0] - tb.ball['velocity'].y)
        spd = lists[0]
        for item in lists:
            change = abs(item - tb.ball['velocity'].y)
            if change < min_change:
                min_change = change
                spd = item

        #学习（记录）体力消耗小的打法
        if self.dic is not None and \
                self.cost(spd, tb.ball['velocity'].y, tb.op_side['active_card'][1]) < 250:
            exec(self.dic['read_data'])
            exec(self.dic['record_data'])

        return spd

    
    def render(self, tb: TableData):
        if self.dic is not None:
            exec(self.dic['read_data'])
            exec(self.dic['modify_data'])
            
        spd = self.eat_card(tb) #默认使用卡牌
        spin = 1.0              #默认无CARD_SPIN作用
        #如果被使用了CARD_SPIN，那将加速提高一倍以到达理想坐标
        if tb.op_side['active_card'][1] == CARD_SPIN:
            spin = 2.0
        #(默认)使用卡牌的情况
        if spd:
            return (spd - tb.ball['velocity'].y) * spin
        #如果不使用卡牌，返回hit函数决定的速度
        spd = self.hit(tb)
        return (spd - tb.ball['velocity'].y) * spin
        
mf = MFunction()

def serve(op_side: str, ds: dict) -> tuple:
    return BALL_POS[1], mf.cal_speed(Position(DIM[0], BALL_POS[1]), Position(DIM[1], DIM[3]*3)) 

def play(tb: TableData, ds: dict) -> RacketAction:
    card = mf.use_card(tb.side["cards"])
    return RacketAction(tb.tick,  # 当前时间，照抄参数中的tb.tick即可
                        tb.ball['position'].y - tb.side['position'].y,  # 球拍的移动距离（有方向）
                        mf.render(tb),  # 球拍对球加速的速度（有方向）
                        mf.move(tb),  # 球拍击球后跑位的移动距离（有方向）
                        mf.card_to(card),  # 使用道具，对谁使用'SELF'/'OPNT'
                        card  # Card对象，使用什么道具
                        )
         
def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return         
