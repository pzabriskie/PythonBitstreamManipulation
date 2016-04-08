__author__ = 'Peter Zabriskie'

class FradStructure:
	"""
	This class is a special data structure that fascilitates navigation
	of the frame addresses in the device
	"""

	def __init__(self, series):
		"""
		Construct a new FradStructure object. Frad = Frame Address
		:param series: The series of the device
		:return: returns nothing
		"""

		# Constant definitions
		self.FRAD_OUT_OF_BOUNDS = -1
		self.WORD_OUT_OF_BOUNDS = -2
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
		self.numFrads = 0
		self.numLogicFrames = 0
		self.numBramFrames = 0
		self.numType2Frames = 0
		self.numType3Frames = 0
		self.numType4Frames = 0
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

		if(series == 5):
			self.wordsPerFrame = 41
		elif(series == 6):
			self.wordsPerFrame = 81
		elif(series == 7):
			self.wordsPerFrame = 101
		elif(series == 8):
			self.wordsPerFrame = 123
		elif(series == 9):
			self.wordsPerFrame = 93

	def load_frads(self, fradFile):
		"""
		Loads the FradStructure according to a list of frame addresses for a device

		:param fradFile: Path to file containing list of frame addresses
		:return: returns nothing
		"""
		frads = open(fradFile, 'r').read().split("\n")
		prevType = -1
		prevTopBottom = -1
		prevRow = -1
		prevColumn = -1

		for line in frads:
			if (len(line) == 0):
				continue

			fradString = line[self.ADDRESS_START:self.ADDRESS_START+self.ADDRESS_SIZE]
			fradVal = int(fradString, 16)
			self.fradArray.append(fradVal)

			loadTopBottom = 0
			loadRow = 0
			loadColumn = 0

			if fradVal == self.DUMMY_FRAME:
				continue

			curType = (fradVal & self.typeMask) >> self.typeShift
			curTopBottom = 0 if (self.series == 8) else (fradVal & self.topBottomMask) >> self.topBottomShift
			curRow = (fradVal & self.rowMask) >> self.rowShift
			curColumn = (fradVal & self.columnMask) >> self.columnShift

			if(curType != prevType):
				self.fradStructure.append([])
				prevType = curType
				loadTopBottom = 1
				if(self.series == 8):
					prevTopBottom = -1
			if(curTopBottom != prevTopBottom or loadTopBottom == 1):
				self.fradStructure[curType].append([])
				prevTopBottom = curTopBottom
				loadRow = 1
			if(curRow != prevRow or loadRow == 1):
				self.fradStructure[curType][curTopBottom].append([])
				prevRow = curRow
				loadColumn = 1
			if(curColumn != prevColumn or loadColumn == 1):
				self.fradStructure[curType][curTopBottom][curRow].append([])
				prevColumn = curColumn
			self.fradStructure[curType][curTopBottom][curRow][curColumn].append([]) # append another array to hold words
			self.numFrads += 1
			if curType == 0:
				self.numLogicFrames += 1
			if curType == 1:
				self.numBramFrames += 1
			if curType == 2:
				self.numType2Frames += 1
			if curType == 3:
				self.numType3Frames += 1
			if curType == 4:
				self.numType4Frames += 1

	def append_word(self, word):
		"""
		This function appends the specified word to the current frame
		:param word: 32 bit word to be added
		:return: returns nothing
		"""
		self.fradStructure[self.type][self.topBottom][self.row][self.column][self.minor].append(word)

	def get_word_from_current_frad(self, wordNum):
		"""
		This function returns the specified word from the current frame.
		:param wordNum: Index of desired word
		:return: Returns value of word at specified location
		"""

		if wordNum >= self.wordsPerFrame:
			print "wordNum out of bounds in FradStructure:get_word_in_current_frame()"
		else:
			return self.fradStructure[self.type][self.topBottom][self.row][self.column][self.minor][wordNum]

	def get_word_from_frad(self, frad, wordNum):
		"""
		This function returns the specified word from the specified frame.
		:param frad: Frame address where desired word is located
		:param wordNum: Index of desired word
		:return: Returns value of word at specified location
		"""

		newType = (frad & self.typeMask) >> self.typeShift
		newTopBottom = 0 if (self.series == 8) else (frad & self.topBottomMask) >> self.topBottomShift
		newRow = (frad & self.rowMask) >> self.rowShift
		newColumn = (frad & self.columnMask) >> self.columnShift
		newMinor = frad & self.minorMask
		if(self.check_location(newType, newTopBottom, newRow, newColumn, newMinor) == self.FRAD_OUT_OF_BOUNDS):
			print "FRAD out of bounds in FradStructure:get_word_from_frad()"
			return self.FRAD_OUT_OF_BOUNDS
		if wordNum >= self.wordsPerFrame:
			print "wordNum out of bounds in FradStructure:get_word_in_current_frame()"
			return self.WORD_OUT_OF_BOUNDS
		else:
			return self.fradStructure[newType][newTopBottom][newRow][newColumn][newMinor][wordNum]

	def get_frame_data(self, frad):
		"""
		This function returns an array of all the words at the specified frame address.
		:param frad: Frame address where desired data is located
		:return: An array of all the words at the specified address
		"""

		newType = (frad & self.typeMask) >> self.typeShift
		newTopBottom = 0 if (self.series == 8) else (frad & self.topBottomMask) >> self.topBottomShift
		newRow = (frad & self.rowMask) >> self.rowShift
		newColumn = (frad & self.columnMask) >> self.columnShift
		newMinor = frad & self.minorMask
		if(self.check_location(newType, newTopBottom, newRow, newColumn, newMinor) == self.FRAD_OUT_OF_BOUNDS):
			print "FRAD out of bounds in FradStructure:get_frame_data()"
			return self.FRAD_OUT_OF_BOUNDS

		return self.fradStructure[newType][newTopBottom][newRow][newColumn][newMinor]

	def get_current_frame_data(self):
		"""
		This function returns an array of all the words at the current frame address.
		:return: An array of all the words at the specified address
		"""
		return self.fradStructure[self.type][self.topBottom][self.row][self.column][self.minor]

	def get_num_frads(self):
		"""
		This function returns the number of frame addresses in the device
		:return: The number of frame addresses in the device
		"""
		return self.numFrads
		

	def get_current_frad(self):
		"""
		This returns the current frame address as a 32 bit value

		:return: 32 bit value representing frame address that FradStructure object is currently pointing to
		"""
		return ((self.type << self.typeShift) | (self.topBottom << self.topBottomShift) | (self.row << self.rowShift)
		       | (self.column << self.columnShift) | (self.column << self.columnShift) | self.minor)
		# return self.fradStructure[self.type][self.topBottom][self.row][self.column][self.minor]

	def get_type(self):
		"""
		:return: Current type pointed to by FradStructure
		"""
		return self.type

	def get_top_bottom(self):
		"""
		:return: Current half of device pointed to by FradStructure
		"""
		return self.topBottom

	def get_row(self):
		"""
		:return: Current row pointed to by FradStructure
		"""
		return self.row

	def get_column(self):
		"""
		:return: Current column pointed to by FradStructure
		"""
		return self.column

	def get_minor(self):
		"""
		:return: Current minor pointed to by FradStructure
		"""
		return self.minor

	def check_location(self, newType, newTopBottom, newRow, newColumn, newMinor):
		"""
		Helper function to check if location data points to a valid frame.
		:param newType: Type of frame address at desired location
		:param newTopBottom: Top/Bottom value of frame address at desired location
		:param newRow: Row of frame address at desired location
		:param newColumn: Column of frame address at desired location
		:param newMinor: Minor of frame address at desired location
		:return: FRAD_OK (0) if location is valid, FRAD_OUT_OF_BOUNDS (-1) if not		
		"""
		if((len(self.fradStructure) > newType) and (len(self.fradStructure[newType]) > newTopBottom) and 
			(len(self.fradStructure[newType][newTopBottom]) > newRow) and (len(self.fradStructure[newType][newTopBottom][newRow]) > newColumn) and
			(len(self.fradStructure[newType][newTopBottom][newRow][newColumn]) > newMinor)):
			return self.FRAD_OK
		else:
			return self.FRAD_OUT_OF_BOUNDS

	def set_current_location(self, newType, newTopBottom, newRow, newColumn, newMinor):
		"""
		Sets frame address that FradStructure points to using type, top/bottom, row, column, and minor values
		:param newType: Type of frame address at desired location
		:param newTopBottom: Top/Bottom value of frame address at desired location
		:param newRow: Row of frame address at desired location
		:param newColumn: Column of frame address at desired location
		:param newMinor: Minor of frame address at desired location
		:return: FRAD_OK (0) if location is valid, FRAD_OUT_OF_BOUNDS (-1) if not
		"""
		# check if FRAD is valid
		if(self.check_location(newType, newTopBottom, newRow, newColumn, newMinor) == self.FRAD_OK):
			self.type = newType
			self.topBottom = newTopBottom
			self.row = newRow
			self.column = newColumn
			self.minor = newMinor
			return self.FRAD_OK
		else:
			return self.FRAD_OUT_OF_BOUNDS

	def set_current_frad(self, frad):
		"""
		Sets frame address that FradStructure points to based on 32 bit representation of address
		:param frad: 32 representation of desired frame address
		:return: FRAD_OK (0) if location is valid, FRAD_OUT_OF_BOUNDS (-1) if not
		"""
		# check if frad is out of bounds
		if(frad & (~(self.typeMask | self.topBottomMask | self.rowMask | self.columnMask | self.minorMask))):
			return self.FRAD_OUT_OF_BOUNDS
		curType = (frad & self.typeMask) >> self.typeShift
		curTopBottom = 0 if (self.series == 8) else (frad & self.topBottomMask) >> self.topBottomShift
		curRow = (frad & self.rowMask) >> self.rowShift
		curColumn = (frad & self.columnMask) >> self.columnShift
		curMinor = frad & self.minorMask
		return self.set_current_location(curType, curTopBottom, curRow, curColumn, curMinor)

	# row functions

	def move_row_up(self):
		"""
		Moves to the row above the current row as they are physically laid out on the device (layout varies by series)
		:return: FRAD_OK (0) if row was moved up, FRAD_OUT_OF_BOUNDS (-1) if the row was already at the top value
		"""
		if self.series == 5:
			if(self.row < len(fradStructure[self.type][self.topBottom]) - 1): #Increment if there is a row above
				self.row += 1
			elif(self.topBottom == 1):# 1 indicates bottom half rows. Move to top
				self.topBottom = 0
				self.row = 0
			else:
				return self.FRAD_OUT_OF_BOUNDS
		elif self.series == 6 or self.series == 7:
			if(self.row < len(fradStructure[self.type][self.topBottom]) - 1 and self.topBottom == 0):
				self.row += 1
			elif(self.row > 0 and self.topBottom == 1):# Move from bottom toward center
				self.row -= 1
			elif(self.row == 0 and self.topBottom == 1):# Switch from bottom to top
				self.topBottom = 0
				self.row = 0
			else:
				return self.FRAD_OUT_OF_BOUNDS	
		elif self.series == 8:
			if(self.row < len(fradStructure[self.type][self.topBottom]) - 1):
				self.row += 1
			else:
				return self.FRAD_OUT_OF_BOUNDS	

		self.go_to_column(self.column)
		self.go_to_minor(self.minor)
		return self.FRAD_OK							

	def move_row_down(self):
		"""
		Moves to the row below the current row as they are physically laid out on the device (layout varies by series)
		:return: FRAD_OK (0) if row was moved down, FRAD_OUT_OF_BOUNDS (-1) if the row was already at the bottom value
		"""
		if self.series == 5:
			if(self.row > 0):# Decrement if there is a row below
				self.row -= 1
			elif(self.topBottom == 0):# 0 indicates top half rows. Move to bottom
				self.topBottom = 1
				self.row = len(fradStructure[self.type][self.topBottom]) - 1
			else:
				return self.FRAD_OUT_OF_BOUNDS
		elif self.series == 6 or self.series == 7:
			if(self.row > 0 and self.topBottom == 0):
				self.row -= 1
			elif(self.row == 0 and self.topBottom == 0):# Move to bottom half
				self.topBottom = 1
				self.row = 0
			elif(self.row < len(fradStructure[self.type][self.topBottom]) - 1 and self.topBottom == 1):# Increment row if on bottom half
				self.row += 1
			else:
				return self.FRAD_OUT_OF_BOUNDS
		elif self.series == 8:
			if(self.row > 0):
				self.row -= 1
			else:
				return self.FRAD_OUT_OF_BOUNDS

		self.go_to_column(self.column)
		self.go_to_minor(self.minor)
		return self.FRAD_OK

	def go_to_row(self, row):
		"""
		Move to the specified row. Column and minor are also moved if current column and minor values do not exist on new row.
		:param row: New row to point to
		:return: FRAD_OK (0) if specified row is valid, FRAD_OUT_OF_BOUNDS (-1) if not
		"""
		if(row < len(self.fradStructure[self.type][self.topBottom])):
			self.row = row
			self.go_to_column(self.column)
			self.go_to_minor(self.minor)
			return self.FRAD_OK
		else:
			return self.FRAD_OUT_OF_BOUNDS

	# column functions

	def move_column_left(self):
		"""
		Moves to the column left of the current column as they are physically laid out on the device
		:return: FRAD_OK (0) if column was moved left, FRAD_OUT_OF_BOUNDS (-1) if the row was already at the leftmost value
		"""		
		if self.column == 0:
			return self.FRAD_OUT_OF_BOUNDS
		else:
			self.column -= 1
			self.go_to_minor(self.minor)
			return self.FRAD_OK

	def move_column_right(self):
		"""
		Moves to the column right of the current column as they are physically laid out on the device
		:return: FRAD_OK (0) if column was moved right, FRAD_OUT_OF_BOUNDS (-1) if the row was already at the leftmost value
		"""	
		if self.column == len(self.fradStructure[self.type][self.topBottom][self.row]) - 1:
			return self.FRAD_OUT_OF_BOUNDS
		else:
			self.column += 1
			self.go_to_minor(self.minor)
			return self.FRAD_OK

	def go_to_column(self, column):
		"""
		Move to the specified column. Minor is also moved if current minor value does not exist on new column.
		:param column: New column to point to
		:return: FRAD_OK (0) if specified column is valid, FRAD_OUT_OF_BOUNDS (-1) if not
		"""
		if(column < len(self.fradStructure[self.type][self.topBottom][self.row])):
			self.column = column
			self.go_to_minor(self.minor)
			return self.FRAD_OK
		else:
			return self.FRAD_OUT_OF_BOUNDS

	def step_forward(self):
		"""
		Step frame address forward to next valid minor. Loops back to beginning when end is reached.
		:return: New frame address after stepping forward
		"""
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

	def step_backward(self):
		"""
		Step frame address backward to next valid minor. Loops back to end when zero is reached.
		:return: New frame address after stepping backward
		"""
		# decrement minor. If end of column is reached, set minor to size of column - 1
		if(self.minor > 0):
			self.minor -= 1
			return self.get_current_frad()
		
		
		# decrement column if minor reaches end of column. If end of row is reached, set column to size of row - 1
		if(self.column > 0):
			self.column -= 1
			self.minor = len(self.fradStructure[self.type][self.topBottom][self.row][self.column]) - 1
			return self.get_current_frad()
		
		
		# increment row if last column is reached. Set row to 0 if switching from top to bottom is necessary
		if(self.row > 0):
			self.row -= 1
			self.column = len(self.fradStructure[self.type][self.topBottom][self.row]) - 1
			self.minor = len(self.fradStructure[self.type][self.topBottom][self.row][self.column]) - 1	
			return self.get_current_frad()
		
		
		# change topBottom if last row on half is reached. Not applicable for ultrascale
		if(self.series != 8):
			if(self.topBottom == 1):
				self.topBottom = 0
				self.row = len(self.fradStructure[self.type][self.topBottom]) - 1
				self.column = len(self.fradStructure[self.type][self.topBottom][self.row]) - 1
				self.minor = len(self.fradStructure[self.type][self.topBottom][self.row][self.column]) - 1
				return self.get_current_frad()
			
			else:
				self.topBottom = len(self.fradStructure[self.type])-1
			
		
		
		# change type if end of type is reached. Return to type 0 if end of configuration is reached
		if(self.type > 0):
			self.type -= 1
			self.topBottom = len(self.fradStructure[self.type])-1
			self.row = len(self.fradStructure[self.type][self.topBottom]) - 1
			self.column = len(self.fradStructure[self.type][self.topBottom][self.row]) - 1
			self.minor = len(self.fradStructure[self.type][self.topBottom][self.row][self.column]) - 1
			return self.get_current_frad()
		
		self.type = len(self.fradStructure) - 1
		self.topBottom = len(self.fradStructure[self.type])-1
		self.row = len(self.fradStructure[self.type][self.topBottom]) - 1
		self.column = len(self.fradStructure[self.type][self.topBottom][self.row]) - 1
		self.minor = len(self.fradStructure[self.type][self.topBottom][self.row][self.column]) - 1
		return self.get_current_frad()

	def go_to_minor(self, minor):
		"""
		Move to the specified minor
		:param minor: New minor to point to
		:return: FRAD_OK (0) if specified minor is valid, FRAD_OUT_OF_BOUNDS (-1) if not
		"""

		if(minor < len(self.fradStructure[self.type][self.topBottom][self.row][self.column])):
			self.minor = minor
			return self.FRAD_OK
		else:
			return self.FRAD_OUT_OF_BOUNDS

	def print_current_frame(self):
		"""
		Helper function which prints out the current frame address followed by all the words in the frame.
		:return: returns nothing
		"""
		
		wordCount = 0
		print "Frame: " + hex(self.get_current_frad())
		print "Words:"
		for word in self.fradStructure[self.type][self.topBottom][self.row][self.column][self.minor]:
			print str(wordCount) + ": " + hex(word)
			wordCount += 1

if __name__ == '__main__':
	frads = FradStructure(7)
	frads.load_frads('./frads/xc7k325t_frads.txt')
	frads.set_current_frad(0)
	print "Logic: " + str(frads.numLogicFrames)
	print "BRAM: " + str(frads.numBramFrames)
	print "Type 2: " + str(frads.numType2Frames)
	print "Type 3: " + str(frads.numType3Frames)
	print "Type 4: " + str(frads.numType4Frames)
	print "Total: " + str(frads.numFrads)
	# for i in range(frads.numFrads):
	# 	print str(hex(frads.get_current_frad()))
	# 	frads.step_forward()