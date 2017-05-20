# by 郭浩
import shelve

filename = "[W.T]T_idiot-VS-T_idiot"  # 根据待转换文件名修改
file = shelve.open(filename)
with open("[W.T]T_idiot-VS-T_idiot.txt", 'w') as output:  # 根据输出文件名修改

    output.write("DIM:")
    output.write(str(file['DIM']))
    output.write("\n")

    output.write("TMAX:")
    output.write(str(file['TMAX']))
    output.write("\n")

    output.write("tick_step:")
    output.write(str(file['tick_step']))
    output.write("\n")

    output.write("West:")
    output.write(file['West'])
    output.write("\n")

    output.write("East:")
    output.write(file['East'])
    output.write("\n")

    output.write("tick_total:")
    output.write(str(file['tick_total']))
    output.write("\n")

    output.write("winner:")
    output.write(file['winner'])
    output.write("\n")

    output.write("reason:")
    output.write(file['reason'])
    output.write("\n")

    output.write("log:")
    for entry in file["log"]:
        output.write("\n")
        output.write("tick:")
        output.write(str(entry.tick))
        output.write("\n")

        output.write("side:")
        output.write("\n")
        output.write("  life:")
        output.write(str(entry.side.life))
        output.write("\n")
        output.write("  pos:")
        output.write(str(entry.side.pos))
        output.write("\n")
        output.write("  action:")
        output.write("\n")
        output.write("    bat:")
        output.write(str(entry.side.action.bat))
        output.write("\n")
        output.write("    acc:")
        output.write(str(entry.side.action.acc))
        output.write("\n")
        output.write("    run:")
        output.write(str(entry.side.action.run))
        output.write("\n")

        output.write("op_side:")
        output.write("\n")
        output.write("  life:")
        output.write(str(entry.op_side.life))
        output.write("\n")
        output.write("  pos:")
        output.write(str(entry.op_side.pos))
        output.write("\n")
        output.write("  action:")
        output.write("\n")
        output.write("    bat:")
        output.write(str(entry.op_side.action.bat))
        output.write("\n")
        output.write("    acc:")
        output.write(str(entry.op_side.action.acc))
        output.write("\n")
        output.write("    run:")
        output.write(str(entry.op_side.action.run))
        output.write("\n")

        output.write("ball:")
        output.write("\n")
        output.write("  pos:")
        output.write(str(entry.ball.pos))
        output.write("\n")
        output.write("  velocity:")
        output.write(str(entry.ball.velocity))
        output.write("\n")
