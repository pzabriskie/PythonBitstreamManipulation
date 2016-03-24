from FradStructure import FradStructure

class FrameOperations:
	"""
	This class stores two FradStructure classes and performs various operations to compare them
	"""

	def __init__(self, fradStructure1, fradStructure2):
		self.fradStructure1 = fradStructure1
		self.fradStructure2 = fradStructure2

	def diff(self):
		"""
		Report all word differences between two FradStructure objects
		:return: Array containing (frad, word, bit) upset tuples
		"""
		self.fradStructure1.set_current_frad(0)
		self.fradStructure2.set_current_frad(0)

		upsetList = []

		for i in range(self.fradStructure1.numFrads):
			frame1 = self.fradStructure1.get_current_frame_data()
			frame2 = self.fradStructure2.get_current_frame_data()

			diffList = self.compare_frame(frame1, frame2)

			for pair in diffList:
				upsetList.append((self.fradStructure1.get_current_frad(), pair[0], pair[1]))

			self.fradStructure1.step_forward()
			self.fradStructure2.step_forward()

		return upsetList


	def find_essential_upsets(self, ebdFradStructure):
		"""
		This function finds upsets between two fradStructures and then checks to see
		if upset occurred at an essential bit location

		:param fradStructure1: First of two FradStructure objects to compare
		:param fradStructure2: Second of two FradStructure objects to compare
		:param ebdFradStructure: FradStructure object containing essential bit information
		:return: Array containing (frad, word, bit) upset tuples
		"""
		self.fradStructure1.set_current_frad(0)
		self.fradStructure2.set_current_frad(0)
		ebdFradStructure.set_current_frad(0)

		upsetList = []

		for i in range(self.fradStructure1.numLogicFrames):
			frame1 = self.fradStructure1.get_current_frame_data()
			frame2 = self.fradStructure2.get_current_frame_data()
			frame3 = ebdFradStructure.get_current_frame_data()

			diffList = self.compare_frame(frame1, frame2)

			for pair in diffList:
				if (frame3[pair[0]]) & (1 << pair[1]):
					upsetList.append((self.fradStructure1.get_current_frad(), pair[0], pair[1]))

			self.fradStructure1.step_forward()
			self.fradStructure2.step_forward()
			ebdFradStructure.step_forward()

		return upsetList


	def compare_frame(self, frame1, frame2):
		"""
		Helper function to compare frames for use diff functions

		:param frame1: Array of words in frame1
		:param frame2: Array of words in frame2
		:return: Array of (word, bit) tuples where differences are found
		"""
		return_list = []
		for i in range(len(frame1)):
			if frame1[i] != frame2[i]:
				for j in range(32):
					msk = 1 << j
					if(frame1[i] & msk) != (frame2[i] & msk):
						return_list.append((i,j))

		return return_list
