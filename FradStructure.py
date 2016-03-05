import binascii

class FradStructure:
	"""This class is a special data structure that fascillitates navigation
	of the frame addresses in the device"""

	def __init__(self, series):
		# Constant definitions
		self.FRAD_OUT_OF_BOUNDS = -1
		self.FRAD_OK = 0
		self.MAX_LINE_SIZE = 256
		self.ADDRESS_SIZE = 8
		self.ADDRESS_START = 4

		self.FIVE_SIX_TYPE_MASK = 0xE00000
		self.SEVEN_ULTRASCALE_TYPE_MASK = 0x3800000
		self.FIVE_SIX_TOP_BOTTOM_MASK = 0x100000
		self.SEVEN_TOP_BOTTOM_MASK = 0x400000
		self.ULTRASCALE_ROW_MASK = 0x7E0000
		self.FIVE_SIX_ROW_MASK = 0xF8000
		self.SEVEN_ROW_MASK = 0x3E0000
		self.FIVE_SIX_COLUMN_MASK = 0x7F80
		self.SEVEN_ULTRASCALE_COLUMN_MASK = 0x1FF80
		self.MINOR_MASK = 0x7F

		self.FIVE_SIX_TYPE_SHIFT = 21
		self.SEVEN_ULTRASCALE_TYPE_SHIFT = 23
		self.SEVEN_TOP_BOTTOM_SHIFT = 22
		self.FIVE_SIX_TOP_BOTTOM_SHIFT = 20
		self.SEVEN_ULTRASCALE_ROW_SHIFT = 17
		self.FIVE_SIX_ROW_SHIFT = 15
		self.COLUMN_SHIFT = 7

		self.DUMMY_FRAME = 0xFF000000

		self.series = series
		self.fradStructure = []
		self.fradArray = []
		self.type = 0
		self.topBottom = 0
		self.row = 0
		self.column = 0
		self.minor = 0

		if(series == 5 or series == 6):
			self.typeMask = self.FIVE_SIX_TYPE_MASK
			self.typeShift = self.FIVE_SIX_TYPE_SHIFT
			self.topBottomMask = self.FIVE_SIX_TOP_BOTTOM_MASK
			self.topBottomShift = self.FIVE_SIX_TOP_BOTTOM_SHIFT
			self.rowMask = self.FIVE_SIX_ROW_MASK
			self.rowShift = self.FIVE_SIX_ROW_SHIFT
			self.columnMask = self.FIVE_SIX_COLUMN_MASK
		elif(series == 7):
			self.typeMask = self.SEVEN_ULTRASCALE_TYPE_MASK
			self.typeShift = self.SEVEN_ULTRASCALE_TYPE_SHIFT
			self.topBottomMask = self.SEVEN_TOP_BOTTOM_MASK
			self.topBottomShift = self.SEVEN_TOP_BOTTOM_SHIFT
			self.rowMask = self.SEVEN_ROW_MASK
			self.rowShift = self.SEVEN_ULTRASCALE_ROW_SHIFT
			self.columnMask = self.SEVEN_ULTRASCALE_COLUMN_MASK
		elif(series == 8):
			self.typeMask = self.SEVEN_ULTRASCALE_TYPE_MASK
			self.typeShift = self.SEVEN_ULTRASCALE_TYPE_SHIFT
			self.topBottomMask = 0
			self.topBottomShift = 0
			self.rowMask = self.ULTRASCALE_ROW_MASK
			self.rowShift = self.SEVEN_ULTRASCALE_ROW_SHIFT
			self.columnMask = self.SEVEN_ULTRASCALE_COLUMN_MASK

		self.minorMask = self.MINOR_MASK
		self.columnShift = self.COLUMN_SHIFT

	def load_frads(self, fradFile):
		frads = open(fradFile, 'r')
		prevType = -1
		prevTopBottom = -1
		prevRow = -1
		prevColumn = -1

		for line in frads:
			fradString = '0x' + line[self.ADDRESS_START:self.ADDRESS_START+self.ADDRESS_SIZE]
			fradVal = int(fradString, 16)
			self.fradArray.append(fradVal)

			# load frad structure
			if fradVal == self.DUMMY_FRAME:
				prevRow = -1
				prevColumn = -1
				continue
			curType = (fradVal & self.typeMask) >> self.typeShift
			curTopBottom = 0 if (self.series == 8) else (fradVal & self.topBottomMask) >> self.topBottomShift
			curRow = (fradVal & self.rowMask) >> self.rowShift
			curColumn = (fradVal & self.columnMask) >> self.columnShift
			if(curType != prevType):
				self.fradStructure.append([])
				prevType = curType
				if(self.series == 8):
					prevTopBottom = -1
			if(curTopBottom != prevTopBottom):
				self.fradStructure[curType].append([])
				prevTopBottom = curTopBottom
			if(curRow != prevRow):
				self.fradStructure[curType][curTopBottom].append([])
				prevRow = curRow
			if(curColumn != prevColumn):
				self.fradStructure[curType][curTopBottom][curRow].append([])
				prevColumn = curColumn
			self.fradStructure[curType][curTopBottom][curRow][curColumn].append(fradVal)

	def get_current_frad(self):
		return self.fradStructure[self.type][self.topBottom][self.row][self.column][self.minor]

	def step_forward(self):
		# increment minor. If end of column is reached, set minor to 0
		if (self.minor < len(self.fradStructure[self.type][self.topBottom][self.row][self.column]) - 1):
			self.minor += 1
			return self.get_current_frad()
		
		else:
			self.minor = 0
		
		# increment column if minor reaches end of column. If end of row is reached, set column to 0
		if(self.column < len(self.fradStructure[self.type][self.topBottom][self.row]) - 1):
			self.column += 1
			return self.get_current_frad()
		
		else:
			self.column = 0
		
		# increment row if last column is reached. Set row to 0 if switching from top to bottom is necessary
		if(self.row < len(self.fradStructure[self.type][self.topBottom]) - 1):
			self.row += 1
			return self.get_current_frad()
		
		else:
			self.row = 0
		
		
		# change topBottom if last row on half is reached. Not applicable for ultrascale
		if(self.series != 8):
			if(self.topBottom < len(self.fradStructure[self.type]) - 1):
				self.topBottom += 1
				return self.get_current_frad()
			
			else:
				self.topBottom = 0
			
		
		
		# change type if end of type is reached. Return to type 0 if end of configuration is reached
		if(self.type < len(self.fradStructure) - 1):
			self.type += 1
			return self.get_current_frad()
		
		else:
			self.type = 0
		
	
		return self.get_current_frad()



if __name__ == '__main__':
	frads = FradStructure(7)
	frads.load_frads('./frads/xc7k325t_frads.txt')
	print "length of frads.fradStructure: " + str(len(frads.fradStructure))
	for i in frads.fradArray:
		print hex(frads.step_forward())