import datetime
import math
import json
from threading import Timer

with open("config.json", "r", encoding="utf-8") as f:
	config = json.load(f)


class StateOwner:

	def __init__(self):
		self.state = IdleState(self)

	def try_to(self, state_cls, sender, msg):
		if state_cls.can_switch_to(sender, msg):
			old_state = self.state
			old_state.on_exit(msg.user if msg else None)

			self.state = state_cls(self)
			self.state.on_enter(msg.user)

	def text_reply(self, msg):
		if msg.user.NickName == "个个都是靓仔靓女":
			sender = msg.user.search_member(userName=msg.ActualUserName)
			print(msg.text, sender)

			self.state.text_reply(sender, msg)


class StateBase:

	def __init__(self, owner):
		self.owner = owner

	def on_enter(self, user):
		pass

	def on_exit(self, user):
		pass

	@classmethod
	def can_switch_to(cls, sender, msg):
		return True

	def text_reply(self, sender, msg):
		if msg.text == "指令列表":
			cmd = """
			开始娱乐
			结束娱乐
			"""
			for study_type in config["study"]:
				if type(config["study"][study_type]) == list:
					cmd += f"""
				开始{study_type}
				赢了{study_type}
				输了{study_type}
					"""
				else:
					cmd += f"""
				开始{study_type}
				结束{study_type}
					"""

			msg.user.send_msg(cmd)
		elif sender.NickName == "何garfield" and msg.text.startswith("重置娱乐时间"):
			try:
				FunState.set_fun_time(int(msg.text.split(" ")[1]) * 60)
				msg.user.send_msg(f"重置娱乐时间成功，剩余时间为{math.floor(FunState.get_fun_time() / 60)}分")
				self.on_reset_time()
			except:
				pass

	def on_reset_time(self):
		pass


class IdleState(StateBase):

	def text_reply(self, sender, msg):
		super().text_reply(sender, msg)

		if sender.NickName == "cmdr" and msg.text == "开始娱乐":
			self.owner.try_to(FunState, sender, msg)
		elif sender.NickName == "cmdr" and msg.text.startswith("开始"):
			self.owner.try_to(StudyState, sender, msg)


class FunState(StateBase):
	RestTime = 0
	StartFunTime = None
	WarningT = None

	def on_enter(self, user):
		super().on_enter(user)

		FunState.StartFunTime = datetime.datetime.now()
		end_time = FunState.StartFunTime + datetime.timedelta(seconds=FunState.get_fun_time())
		user.send_msg(
			f"你的娱乐时间还剩余{math.floor(FunState.get_fun_time() / 60)}分钟，截止时间为{end_time.hour}:{end_time.minute}，请注意不要娱乐过度！")

		def stop_fun_tip():
			FunState.set_fun_time(0)
			user.send_msg("你已经没有娱乐时间了，请开始你的学习为你的娱乐时间充值！")
			self.owner.try_to(IdleState, None, None)

		self.WarningT = Timer(FunState.get_fun_time(), stop_fun_tip)
		self.WarningT.start()

	def on_exit(self, user):
		super().on_exit(user)

		self.WarningT.cancel()

		FunState.set_fun_time(FunState.get_fun_time() - (datetime.datetime.now() - FunState.StartFunTime).seconds)
		if FunState.get_fun_time() < 0:
			user.send_msg(f"你已经过度娱乐，超出了{math.ceil(abs(FunState.get_fun_time()) / 60)}分，请开始你的学习！")
		else:
			user.send_msg(f"你的娱乐时间剩余{math.floor(FunState.get_fun_time() / 60)}分")

	@classmethod
	def can_switch_to(cls, sender, msg):
		if sender.NickName == "cmdr":
			if FunState.get_fun_time() > 0:
				return True
			else:
				msg.user.send_msg(
					f"你已经过度娱乐，超出了{math.ceil(abs(FunState.get_fun_time()) / 60)}分，请开始你的学习！")

		return False

	@staticmethod
	def set_fun_time(rest_time):
		FunState.RestTime = rest_time

	@staticmethod
	def get_fun_time():
		if FunState.StartFunTime is None or datetime.datetime.now().day != FunState.StartFunTime.day:
			FunState.RestTime = config["fun"] * 3600

		return FunState.RestTime

	def text_reply(self, sender, msg):
		super().text_reply(sender, msg)

		if sender.NickName == "cmdr" and msg.text == "结束娱乐":
			self.owner.try_to(IdleState, sender, msg)
		elif sender.NickName == "cmdr" and msg.text == "开始娱乐":
			if FunState.StartFunTime is not None and datetime.datetime.now().day != FunState.StartFunTime.day:
				self.on_enter(msg.user)
		elif sender.NickName == "cmdr" and msg.text.startswith("开始"):
			self.owner.try_to(StudyState, sender, msg)

	def on_reset_time(self):
		super().on_reset_time()

		if self.WarningT:
			self.WarningT.cancel()

		self.WarningT = Timer(FunState.get_fun_time(), self.WarningT.function)
		self.WarningT.start()


class StudyState(StateBase):
	StudyType = None
	StartTime = None
	Win = False

	@classmethod
	def can_switch_to(cls, sender, msg):
		if sender.NickName == "cmdr":
			action = msg.text[len("开始"):]
			if action in config["study"]:
				StudyState.StudyType = action
				return True

		return False

	def on_enter(self, user):
		super().on_enter(user)

		StudyState.StartTime = datetime.datetime.now()

		user.send_msg("收到，开始统计学习时间")

	def on_exit(self, user):
		super().on_exit(user)

		if type(config["study"][self.StudyType]) is list:
			if self.Win:
				rate = config["study"][self.StudyType][0]
			else:
				rate = config["study"][self.StudyType][1]
		else:
			rate = config["study"][self.StudyType]

		study_time = (datetime.datetime.now() - StudyState.StartTime).seconds
		charge_time = study_time * rate
		FunState.set_fun_time(FunState.get_fun_time() + charge_time)
		user.send_msg(
			f"本次学习时长为{study_time}秒，倍率为{rate}，充值时间为{charge_time}秒，剩余娱乐时间为{math.floor(FunState.get_fun_time() / 60)}分钟")

	def text_reply(self, sender, msg):
		super().text_reply(sender, msg)

		if self.StudyType is not None and msg.text == "结束" + self.StudyType:
			if self.StudyType == "围棋":
				msg.user.send_msg("请发送围棋赢了或者围棋输了")
			else:
				self.owner.try_to(IdleState, sender, msg)

		elif self.StudyType == "围棋" and ("赢了" + self.StudyType == msg.text or "输了" + self.StudyType == msg.text):
			if "赢了" in msg.text:
				self.Win = True
			else:
				self.Win = False

			self.owner.try_to(IdleState, sender, msg)

		return False
