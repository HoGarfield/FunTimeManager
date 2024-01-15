import math
import json
from ItChat import itchat
import datetime
from ItChat.itchat.content import *
from threading import Timer
from State import StateOwner

owner = None
config = None


@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
	owner.text_reply(msg)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
	with open("config.json", "r", encoding="utf-8") as f:
		config = json.load(f)
		owner = StateOwner(config)

	itchat.auto_login(enableCmdQR=2)
	itchat.run()
