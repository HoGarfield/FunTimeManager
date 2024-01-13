import math
import json
from ItChat import itchat
import datetime
from ItChat.itchat.content import *
from threading import Timer

start_fun_time: datetime.datetime | None = None
start_study_time: datetime.datetime | None = None
study_action = None
fun_rest_time = 60 * 1
warning_t = None

config = None


@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
	global fun_rest_time, warning_t, start_fun_time, study_action, start_study_time
	print(msg)
	if msg.user.NickName == "个个都是靓仔靓女":
		sender = msg.user.search_member(userName=msg.fromUserName)
		print(msg.text, sender)

		if sender.NickName == "cmdr" or True:
			if msg.text == "开始娱乐":

				if start_fun_time == None or datetime.datetime.now().day != start_fun_time.day:
					fun_rest_time = 3600 * config["fun"]

				if fun_rest_time > 0:
					start_fun_time = datetime.datetime.now()
					end_time = start_fun_time + datetime.timedelta(seconds=fun_rest_time)
					msg.user.send_msg(f"你的娱乐时间还剩余{math.floor(fun_rest_time / 60)}分钟，截止时间为{end_time.hour}:{end_time.minute}，请注意不要娱乐过度！")

					def stop_fun_tip():
						global fun_rest_time
						fun_rest_time = 0
						msg.user.send_msg("你已经没有娱乐时间了，请开始你的学习为你的娱乐时间充值！")

					warning_t = Timer(fun_rest_time, stop_fun_tip)
					warning_t.start()
				else:
					msg.user.send_msg(f"你已经没有娱乐时间了，请开始你的学习为你的娱乐时间充值！")
			elif msg.text == "娱乐停止":
				warning_t.cancel()
				if fun_rest_time > 0:
					fun_rest_time -= (datetime.datetime.now() - start_fun_time).seconds

				if fun_rest_time < 0:
					msg.user.send_msg(f"你已经过度娱乐，超出了{math.floor(fun_rest_time)}秒，请开始你的学习！")
				else:
					msg.user.send_msg(f"你的娱乐时间剩余{math.floor(fun_rest_time / 60)}分")
			elif msg.text.startswith("开始"):
				action = msg.text[len("开始"):]
				if action in config["study"]:
					study_action = action
					start_study_time = datetime.datetime.now()
					msg.user.send_msg("收到，开始统计学习时间")

			elif study_action is not None and msg.text == study_action + "结束":
				if study_action == "围棋":
					msg.user.send_msg("围棋赢了还是输了？")
				else:
					charge(msg)

			elif study_action == "围棋" and ("赢了" in msg.text or "输了" in msg.text):
				if "赢了" in msg.text:
					win = True
				else:
					win = False

				charge(msg, win)


def charge(msg, win=False):
	global fun_rest_time, study_action, start_study_time
	study_type = study_action
	study_time = (datetime.datetime.now() - start_study_time).seconds
	if type(config["study"][study_type]) is list:
		if win:
			rate = config["study"][study_type][0]
		else:
			rate = config["study"][study_type][1]
	else:
		rate = config["study"][study_type]

	charge_time = study_time * rate
	fun_rest_time += charge_time
	msg.user.send_msg(
		f"本次学习时长为{study_time}秒，倍率为{rate}，充值时间为{charge_time}秒，剩余娱乐时间为{math.floor(fun_rest_time / 60)}分钟")

	study_action = None
	start_study_time = 0


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
	with open("config.json", "r", encoding="utf-8") as f:
		config = json.load(f)

	itchat.auto_login(enableCmdQR=True)
	itchat.run()
