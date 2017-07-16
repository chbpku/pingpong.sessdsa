from table import RacketAction,TableData

dj={'SP':0,# 旋转球
'DS':0,# 隐身术
'IL':2000,# 补血包
'DL':2000,# 掉血包
'TP':500,# 瞬移术1000
'AM':500}# 变压器1250

def zh(y):#将广义坐标与桌面坐标做转换
	return abs((y+1e6)%2e6-1e6)

def daoju(x0,y0,x,y):
	k = 1000/abs(x-x0)
	return [int(k*(y-y0)),int(k*(200+y-y0)),int(k*(200-y-y0)),int(k*(-y-y0)),int(k*(y-200-y0))]
	
	
def dajiao(y1,v0):
	yi = y1+v0*1800
	if yi>=2.5e6:
		return (3e6-y1-1)//1800
	elif yi>=1.5e6:
		return (2e6-y1-1)//1800
	elif yi>=0.5e6:
		return (1e6-y1-1)//1800+1
	elif yi>=-0.5e6:
		return -y1//1800
	elif yi>=-1.5e6:
		return (-1e6-y1)//1800+1
	else:
		return (-2e6-y1)//1800+1
def p_jiqiu(y1,v0,y0,d,ds):#对方击球预测函数
	#y1:对方击球位置
	#v0:对方接球速度
	#y0:我方上次击球位置
	#d:我方上次跑位方向
	yi = y1+v0*1800
	l = [0,0,0,0,0,0]
	y2 = 1e6*(yi//1e6)
	y3 = y1+1e6
	if yi>=3.1e6:
		return [1,0,0,0,0,0]
	elif yi<=-2.1e6:
		return [0,0,0,0,0,1]
	else:
		if yi>=3e6:
			l[0]=1
		elif yi<=-2e6:
			l[5]=1
		elif yi-y2<y3-yi:
			l[int(3-y2//1e6)]=1
		else:
			l[int(3-y3//1e6)]=1
		return l
	
def p_paowei(y1,v1,d,ds):#对方跑位预测函数
	#y1:对方击球位置
	#v1:对方击球速度
	#d:对方跑位方向
	return [0,0,0,0,1,0]
	
def paowei(y0,v0,life,ds):#我方跑位函数
	#本函数要用到p_jiqiu
	#y0:我方击球位置
	#v0:我方击球速度
	#life:击完球的血量
	yt = y0 + v0 * 1800#我方指向
	y1 = zh(yt)#对方接球位置
	l=p_jiqiu(y1,v0,y0,None,ds)
	p0 = l[1]+l[3]+l[5]
	y = y0/2 + 5e5*(1-p0)
	lm = life//100*1800
	if abs(y-5e5)>abs(lm-5e5):
		y = int(5e5 +(y-5e5)*abs((lm-5e5)/(y-5e5)))
	return y
	
def w_jiqiu(y1,v0,v1,y0,d,life,ds):#击球收益函数
	#本函数要用到p_paowei和p_jiqiu
	#y1:击球方位置
	#v0:击球方接球速度
	#v1:击球方击球速度
	#y0:接球方上次击球位置
	#d:接球方跑位方向？
	#life:击球方接球时血量
	w1 = (v1 - v0) ** 2 / 400  # 我方接球改变速度所耗体力w1
	
	yt = y1 + v1 * 1800
	if yt>=3e6 or yt<=-2e6 or (yt>0 and yt<1e6):#不合法
		return -10000000
	y2 = zh(yt)
	y3 = paowei(y1, v1, life, ds)  # y2为对方接球位置，y3为我方预测跑位位置
	list0 = p_paowei(y0, v0, d, ds)
	x = list0[0]
	px = list0[1]
	p0 = list0[2]
	p50 = list0[3]
	p100 = list0[4]# 调用对方跑位预测函数
	w2 = ((y2 - x) ** 2 * px + y2 ** 2 * p0 + (y2 - 5e5) ** 2 * p50 + (y2 - 1e6) ** 2 * p100) / 4e8  # 算出对方迎球所耗体力w2
	
	list1 = p_jiqiu(y2, v1, y1, d, ds)  # 调用对方击球预测函数得到击六个角的概率
	w3 = 0
	for i in range(6):
		yi = y2 + v1 * 1800  # 对方采用idiot打法所打到的广义坐标
		ytt = 3e6 - i * (10 ** 6) # 对方要打到的位置
		y4 = zh(ytt)  # 预测的我方再次迎球位置
		v2 = (ytt - y2) / 1800  # 预测的对方击球速度
		u1 = (ytt - yi) ** 2 / (1800 ** 2 * 400)  # 对方击球损耗
		u2 = (y1 - y3) ** 2 / 4e8  # 我方跑位损耗体力
		u3 = (y3 - y4) ** 2 / 4e8  # 我方迎球损耗体力
		# 接下来算我方再次击球损耗u4
		yi = y3 + 1800 * v2  # 算出我方再次击球采用idiot方法的坐标，而后选择较近的角打
		if yi >= 3e6:
			u4 = (yi - 3e6) ** 2 / (1800 * 2 * 400)
		elif yi <= -2e6:
			u4 = (yi + 2e6) ** 2 / (1800 ** 2 * 400)
		else:
			a = abs(yi)
			b = a % 1e6
			if b >= 5e5:
				u4 = (1e6 - b) ** 2 / (1800 ** 2 * 400)
			else:
				u4 = b ** 2 / (1800 ** 2 * 400)
		#u4 = 0
		w3 = w3 + (-u1 + u2 + u3 + u4) * list1[i]  # 将w3按对方击各个角的概率加权求和
	
	w = -w1 + w2 - w3  # 击球受益=-我方击球损耗+对方迎球损耗-对方击球受益
	return w

def jiqiu(x1,y1,v0,y0,d,cards,life,byq,ds):#我方击球函数
	#本函数需要用到w_jiqiu
	#x1:我方击球x方向位置
	#y1:我方击球y方向位置
	#v0:我方接球速度
	#y0:对方上次击球位置
	#d:对方跑位方向
	#cards:场上道具
	lw = []
	lv = [(3e6-y1-1)//1800,(2e6-y1-1)//1800,(1e6-y1-1)//1800+1,-y1//1800,(-1e6-y1)//1800+1,(-2e6-y1)//1800+1]
	for i in lv:
		lw.append(w_jiqiu(y1,v0,i,y0,d,life-((i-v0)**2//400)*byq,ds))
	for i in cards:
		l = daoju(x1,y1,i.pos.x,i.pos.y)
		lv += l
		for j in l:
			lw.append(w_jiqiu(y1,v0,j,y0,d,life-((j-v0)**2//400)*byq,ds)+dj[i.code])
	return lv[lw.index(max(lw))]

def cata_op_paowei(y1,y2,l1,l2,card,bv,op_bv):
# 本函数旨在算上一回合对方跑位的位置y,bv为上一次我方击球后球的vy,op_bv为这一次对方击球后球的vy
	return
        

def set_up_ds():#初始化datastore为一个字典,记录某一回合的历史数据(某一回合的过程为'我方击球','对方跑位','对方击球','我方跑位')
	ds = {}
	ds['Jieqiu'] = []
    #我方击球到达位置(y)
	ds['PaoWei'] = []
    #我方跑位位置(y)
	ds['op-PaoWei'] = []
    #对方跑位位置(y)
	ds['op-JiQiu'] = []
    #对方击球到达位置
	ds['op-Life'] = []
    #对方生命值
	ds['op-Ballv'] = []
    #对方击来球y方向速度
	ds['Ballv'] = []
    #我方击球球y方向速度
	ds['op-CardBox'] = []
    #记录对方Cardbox内的道具卡
	return ds
        
def store_ds(TableData,ds,vy,paowei):
    #用于我方击球前更改数据库的函数
	ds['op-Life'].append(TableData.op_side['life'])
    #加入对方生命值
	ds['op-CardBox'].append(TableData.op_side['cards'])
    #记录对方道具箱
	ds['op-Ballv'].append(TableData.ball['velocity'].y)
    #记录对方击球y方向速度
	ds['op-JiQiu'].append(TableData.ball['position'].y)
    #记录对方击球到达位置
	n = len(ds['op-Life'])
    #n表示目前回合数
	if n != 1:
    #第一回合无法判断对方跑位数据
		card = 0
        #判断道具卡加血减血
		PaoWei = cata_op_paowei(ds['JieQiu'][n-2],ds['JieQiu'][n-1],ds['op-Life'][n-2],ds["op-Life"][n-1],card,ds['Ballv'][n-2],ds['op-Ballv'][n-1])
        #计算对方上一回合跑位
		ds['op-PaoWei'].append(PaoWei)
    #添加对方上一回合的跑位位置y
	ds['Ballv'].append(vy)
    #添加我方出球球时y方向的速度
	ds['PaoWei'].append(paowei)
	return ds


def serve(op_side,ds):
	return 1199,1666

def play(tb,ds):#tb是tabledata类型，ds是datastore类型
	'''
	if len(ds['op-Life']) >= 10:
    #数据库内数据大于10组,此时数据库内的数据才有意义
		for i in range(len(ds['op-Life'])):
			pass
	'''
	#x:迎球阶段距离差
	x = tb.ball['position'].y-tb.side['position'].y
	#xx:迎球阶段最短移动距离
	xx = 0 if abs(x)<=2000 else x-2000*x//abs(x)
	active_card = tb.op_side['active_card']
	byq = 2 if active_card[1] == 'AM' else 1
	life = tb.side['life']
	life -= (xx ** 2 // 4e8) * byq
	#if active_card[1] == 'SP':#旋风球直接就近打角
	#	vy = dajiao(tb.ball['velocity'].y,tb.ball['velocity'].y)
	#else:
	vy = jiqiu(tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].y,tb.op_side['position'].y,tb.op_side['run_vector'],tb.cards['cards'],life,byq,ds)
		#vy为我方出球时球y方向的速度
	life -= (vy-tb.ball['velocity'].y) ** 2 // 400
	pw = paowei(tb.ball['position'].y,vy,life,ds)-tb.side['position'].y-xx
	#paowei为本回合我方跑位的位移
	#ds = set_up_ds()
	#ds = store_ds(tb,ds,vy,pw)
	#调用记录数据的函数
	return RacketAction(None, xx, (vy-tb.ball['velocity'].y)* (2 if active_card[1] == 'SP' else 1), pw, None, tb.side['cards'][0] if tb.side['cards'] else None)

def summarize(tick, winner, reason, west, east, ball, ds):
	return
