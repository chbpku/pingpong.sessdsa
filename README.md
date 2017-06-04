# pingpong.sessdsa 漂移乒乓
地空数算课期末作业

【北京大学地空学院数据结构与算法课程实习作业2017】

【陈斌 gischen(at)pku.edu.cn】

课程网站：[数据结构与算法Python版](http://gis4g.pku.edu.cn/course/pythonds/)

实习作业网站：[漂移乒乓](https://chbpku.github.io/pingpong.sessdsa/)

[github项目地址](https://github.com/chbpku/pingpong.sessdsa)
[oschina码云项目地址](http://git.oschina.net/chbpku/pingpong.sessdsa)

## 文件说明：
- sessdsa2017-pingpong.pdf：期末作业介绍PPT PDF
- pingpong.py：乒乓对战主程序，自动查找当前目录下“T_*.py”的文件作为算法，两两对战，并输出结果（文本）和复盘数据（以shelve模块方式保存）。
- table.py：主要类Table、LogEntry等定义
- show.py：基于pygame的复盘数据可视化
- reader.py：将复盘数据转换为文本文件
- T_idiot.py：示例对战算法，只被动接球
- README.md：本文件
- FAQ.md：常见问题
- team.py：确定各组分区的算法程序
- data_analysis.py：竞赛过程的成绩实时可视化显示
- data_analysis_cx.py：竞赛复盘数据的战术数据分析

## 修改历史

### 20170604
- 李逸飞发布了data_analysis.py，竞赛过程成绩的实时可视化进度显示；
- 陈旭发布了data_analysis_cx.py，竞赛复盘数据的战术数据统计。

### 20170527
- 陈斌在serve函数中增加一个参数，对手的名称，以便根据以往记录来决定如何发球

### 20170523
- 李逸飞修正了fly和get_card的bug

### 20170522
- 陈斌增加了算法第三个函数summarize，可以用来保存终局的分析数据；
- 陈斌修改了旋转球的param为0.5，被用道具一方对球的加速会减少50%；

### 20170520
- 增加了常见问题FAQ.md。
- 张颢丹开发GUI，使用pygame模块，实现对战记录可视化回放。
- 陈斌增加了道具系统的代码。
- 李逸飞开发了道具获取的算法函数。
- 陈斌处理了迎球方返回速度和距离值，规整为整数。
- 郭浩开发reader.py，将复盘数据转换为文本文件输出。

### 20170519
- 李逸飞重写了fly函数的主要算法，更加简洁；
- 陈斌更新了Vector判断相等方法__eq__，考虑误差+／-1；
- 陈斌修改了play函数中传递对方跑位方向；
- 陈斌增加了球拍移动的最大速度限制，与体力值相关，满体力时速度是球的横向速度2倍，按比例线性降低；
- 陈斌增加了最后一个回合的数据。

### 20170517：
- 陈斌根据同学建议完善了PPT规则，并在代码增加了发球和永久保存历史数据。

### 20170515：
- 陈斌创建代码文件和README.TXT文件。