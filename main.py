import json

from ItChat import itchat
from ItChat.itchat.content import *
from State import StateOwner

owner = None

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
	owner.text_reply(msg)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
	owner = StateOwner()
	itchat.auto_login(enableCmdQR=2)
	itchat.run()
