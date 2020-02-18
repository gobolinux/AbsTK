#!/usr/bin/env python3

from wizard import *
import sys
from PyQt4 import QtCore
from PyQt4 import QtGui

class NewQWizard(QtGui.QWizard):
	def __init__(self, qabswizard):
		QtGui.QWizard.__init__(self)
		self.qabswizard = qabswizard
		self.returnCode = 0
		self.button(QtGui.QWizard.NextButton).clicked.connect(self.__next__)
		self.button(QtGui.QWizard.FinishButton).clicked.connect(self.finish)

	def currentScreen(self):
		i = self.currentId()
		return self.qabswizard.screens[i]

	def __next__(self):
		screen = self.currentScreen()

	def finish(self):
		screen = self.currentScreen()
		self.returnCode = 1
		

class AbsQtWizard(AbsWizard):
	def __init__(self, name):
		AbsWizard.__init__(self, name)
		self.app = QtGui.QApplication([])
		self.qwizard = NewQWizard(self)
		self.qwizard.setWindowTitle(name)
		self.lastScreen = None
		self.qwizard.setGeometry(QtCore.QRect(50, 50, 600, 600))
		self.messageBoxPending = 0

	def showMessageBox(self, message, buttons = ['Ok', 'Cancel']):
		if self.messageBoxPending:
			return ''
		self.messageBoxPending = 1
		if len(buttons) == 1:
			i = QtGui.QMessageBox.warning(self.qwizard, str(self.qwizard.windowTitle())+' warning', message, buttons[0])
		elif len(buttons) == 2:
			i = QtGui.QMessageBox.warning(self.qwizard, str(self.qwizard.windowTitle())+' warning', message, buttons[0], buttons[1])
		if len(buttons) >= 3:
			i = QtGui.QMessageBox.warning(self.qwizard, str(self.qwizard.windowTitle())+' warning', message, buttons[0], buttons[1], buttons[2])
		self.messageBoxPending = 0
		return buttons[i]

	def start(self):
		#self.app.setMainWidget(self.qwizard)
		self.qwizard.show()
		self.app.exec_()
		return self.qwizard.returnCode

	def addScreen(self, absQtScreen, pos=0):
		# Add the screen at the end
		if pos == 0:
			self.screens.append(absQtScreen)
			self.qwizard.addPage(absQtScreen.widget)
			self.lastScreen = absQtScreen
		# Add the screen right after the current one
		elif pos == -1:
			pos = self.qwizard.currentId() + 1
			self.screens.insert(pos, absQtScreen)
			self.qwizard.insertPage(absQtScreen.widget, absQtScreen.widget.windowTitle(), pos)
		# Add the screen at a specific possition
		else:
			self.screens.insert(pos,absQtScreen)
			self.qwizard.insertPage(absQtScreen.widget, absQtScreen.widget.windowTitle(),pos)

	def removeScreen(self, absQtScreen):
		self.screens.remove(absQtScreen)
		self.qwizard.removePage(absQtScreen.widget)

	def clear(self, newName = ''):
		lastName = self.qwizard.windowTitle()
		if not newName:
			newName = lastName
		self.qwizard = QWizard()
		self.qwizard.setWindowTitle(newName)
		self.lastScreen = None
		self.screens = []
		self.qwizard.setGeometry(QtCore.QRect(50, 50, 480, 400))

class NewQWizardPage(QtGui.QWizardPage):
	def __init__(self):
		QtGui.QWizardPage.__init__(self)
		self.validator = None

	def validatePage(self):
		ret = True
		if self.validator:
			ret = self.validator()
		return ret


class AbsQtScreen(AbsScreen):
	def __init__(self, title = "I DON'T HAVE A NAME"):
		AbsScreen.__init__(self)
		self.widget = NewQWizardPage()

		self.pageLayout = QtGui.QGridLayout(self.widget)
		self.pageLayout.setAlignment(QtCore.Qt.AlignTop)
		spacer = QtGui.QSpacerItem(2, 2, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.pageLayout.addItem(spacer, 10, 0)
		self.rowsCount = 0
		self.setTitle(title)
		self.fieldsTypes = {}
		self.fieldsContainer = {}

		self.widget.setTitle(title)

		self.nextCB = None

	def __registerField(self, name, widget, fieldType, container=None):
		self.fields[name] = widget
		self.fieldsTypes[name] = fieldType
		self.fieldsContainer[name] = container

	def __unregisterField(self, name):
		container = None
		if name and name in self.fields:
			container = self.fieldsContainer[name]
			del self.fields[name]
			del self.fieldsTypes[name]
			del self.fieldsContainer[name]
		return container

	def onValidate(self, nextCB):
		self.nextCB = nextCB
		self.widget.validator = nextCB

	def addImage(self, fileName):
		p = QtGui.QPixmap()
		p.load(fileName)
		w = QtGui.QLabel(self.widget)
		w.setPixmap(p)
		self.__addWidget(w)

	def setEnabled(self, fieldName, newValue):
		if fieldName in self.fields:
			field = self.fields[fieldName]
			fieldType = self.fieldsTypes[fieldName]

			if fieldType == 'QButtonGroup':
				for button in field.buttons():
					button.setEnabled(newValue)
			else:
				field.setEnabled(newValue)

	def setValue(self, fieldName, newValue):
		if fieldName in self.fields:
			field = self.fields[fieldName]
			fieldType = self.fieldsTypes[fieldName]

			if fieldType == 'QCheckBox':
				field.setChecked(newValue)
			elif fieldType == 'QButtonGroup':
				pass
			elif fieldType == 'QDropList':
				field.setCurrentText(newValue)
			elif fieldType == 'QLineEdit':
				field.setText(newValue)
			elif fieldType == 'QLabel':
				field.setText(newValue)
			if fieldType == 'QTableWidget' or fieldType == 'QListBox':
				import types
				
				if type(newValue) == list:
					for i in range(field.rowCount()):
						field.item(i, 0).setCheckState(str(field.item(i, 0).text()) in newValue)
				
				elif len(newValue) == 1:
					defaultValue = newValue[0]
					items = self.getValue(fieldName)[0]
					for i in range(field.rowCount()):
						if fieldType == 'QListBox':
							field.item(i, 0).setSelected(str(field.item(i, 0).text()) in newValue)
						else:
							field.item(i, 0).setCheckState(str(field.item(i, 0).text()) in newValue)
				else:
					items, defaultValue = newValue
					field.setRowCount(len(items))
					j = 0
					for item in items:
						c = QtGui.QTableWidgetItem(item)
						if fieldType == 'QListBox':
							c.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
							c.setSelected(item == defaultValue)
						else:
							#c.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
							if item in defaultValue:
								c.setCheckState(2)
							else:
								c.setCheckState(0)
						field.setItem(j, 0, c)
						j = j + 1
			else:
				return 0
			return 1
		else:
			return 0

	def getValue(self, fieldName):
		if fieldName in self.fields:
			field = self.fields[fieldName]
			fieldType = self.fieldsTypes[fieldName]

			if fieldType == 'QCheckBox':
				return int(field.isChecked())
			
			elif fieldType == 'QDropList':
				return str(field.currentText())

			elif fieldType == 'QButtonGroup':
				ret = []
				for button in field.buttons():
					ret.append(str(button.text()))
				
				checkedButton = field.checkedButton()
				if checkedButton == None:
					selected = ''
				else:
					selected = str(checkedButton.text())
				
				return (ret, selected)
			
			elif fieldType == 'QLineEdit':
				return str(field.text())
			
			elif fieldType == 'QTableWidget' or fieldType == 'QListBox':
				ret1 = []
				if fieldType == 'QListBox':
					ret2 = ''
				else:
					ret2 = []
				for i in range(field.rowCount()):
					fieldItem = field.item(i, 0)
					if fieldItem == None:
						continue
					ret1.append(str(fieldItem.text()))
					if fieldType == 'QListBox':
						if fieldItem.isSelected():
							ret2 = str(fieldItem.text())
					else:
						if fieldItem.checkState():
							ret2.append(str(fieldItem.text()))
				return (ret1,ret2)
			
			else:
				return None

		else:
			#!has_key...
			return None


	def __addLayout(self, widget, row=-1, column=-1):
		if row  == -1 or column == -1:
			row = self.rowsCount
			column = 0
		self.pageLayout.addLayout(widget, row, column)

		if row >= self.rowsCount:
			self.rowsCount = row + 1


	def __addWidget(self, widget, row=-1, column=-1):
		if row  == -1:
			row = self.rowsCount

		if column == -1:
			column = 0

		self.pageLayout.addWidget(widget, row, column)

		if row >= self.rowsCount:
			self.rowsCount = row + 1

	def delWidget(self, fieldName):
		# Not supported on every QtWidget
		container = self.__unregisterField(fieldName)
		if container:
			self.pageLayout.removeWidget(container)

	def setTitle(self,title):
		self.widget.setWindowTitle(title)

	def addBoolean(self, fieldName, label='', defaultValue=0, toolTip='', callBack=None):
		w = QtGui.QCheckBox(self.widget)
		w.setText(label)
		w.setChecked(defaultValue)
		if toolTip:
			w.setToolTip(toolTip)
		if fieldName:
			self.__registerField(fieldName, w, 'QCheckBox')
		if callBack:
			w.stateChanged.connect(callBack)
		w.stateChanged.connect(self.widget.completeChanged)

		self.__addWidget(w)

	def __addLineEditGeneric(self, fieldName, label, defaultValue, toolTip, callBack, isPasswd):
		w = QtGui.QLineEdit(self.widget)
		w.setText(defaultValue)
		if isPasswd:
			w.setEchoMode(QtGui.QLineEdit.Password)

		if callBack:
			if isPasswd:
				w.lostFocus.connect(callBack)
			else:
				w.textChanged.connect(callBack)

		if isPasswd:
			w.lostFocus.connect(self.widget.completeChanged)
		else:
			w.textChanged.connect(self.widget.completeChanged)

		if toolTip:
			w.setToolTip(toolTip)

		if fieldName:
			self.__registerField(fieldName, w, 'QLineEdit')

		if label:
			layout = QtGui.QHBoxLayout()

			l = QtGui.QLabel(self.widget)
			l.setText(label)
			layout.addWidget(l)
			layout.addWidget(w)

			self.__addLayout(layout)
		else:
			self.__addWidget(w)
	
	def addPassword(self, fieldName, label='', defaultValue='', toolTip='', callBack=None):
		self.__addLineEditGeneric(fieldName, label, defaultValue, toolTip, callBack, True)


	def addLineEdit(self, fieldName, label='', defaultValue='', toolTip='', callBack=None):
		self.__addLineEditGeneric(fieldName, label, defaultValue, toolTip, callBack, False)


	def addMultiLineEdit(self, fieldName='', label='', defaultValue='', toolTip='', callBack=None):
		w = QtGui.QGroupBox(self.widget)
		w.setTitle(label)

		gbLayout = QtGui.QVBoxLayout(w)

		mle = QtGui.QTextEdit(w)
		mle.setText(defaultValue)
		mle.setReadOnly(not fieldName)

		gbLayout.addWidget(mle)

		if callBack:
			mle.textChanged.connect(callBack)
		mle.textChanged.connect(self.widget.completeChanged)

		if toolTip:
			w.setToolTip(toolTip)
		if fieldName:
			self.__registerField(fieldName, mle, 'QMultiLineEdit')

		self.__addWidget(w)
		return


	def addLabel(self, fieldName, label='', defaultValue='', toolTip=''):
		w = QtGui.QLabel(self.widget)
		w.setText(label)
		if toolTip:
			w.setToolTip(toolTip)
		if fieldName:
			self.__registerField(fieldName, w, 'QLabel')
		self.__addWidget(w)

	def addButton(self, fieldName, label='', defaultValue='', toolTip='', callBack=None):
		w = QtGui.QPushButton(self.widget)
		w.setText(label)
		w.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		if toolTip:
			w.setToolTip(toolTip)
		if callBack:
			w.released.connect(callBack)
		w.released.connect(self.widget.completeChanged)

		self.__addWidget(w)

	def addList(self, fieldName, label='', defaultValueTuple=([],''), toolTip='', callBack=None):
		items, defaultValue = defaultValueTuple
		if len(items)<= 5 and len(items) != 0:
			self.addRadioList(fieldName, label, defaultValueTuple, toolTip, callBack)
		else:
			self.addBoxList(fieldName, label, defaultValueTuple, toolTip, callBack)


	def addBoxList(self, fieldName, label='', defaultValueTuple=([],''), toolTip='', callBack=None):
		items, defaultValue = defaultValueTuple
		w = QtGui.QGroupBox(self.widget)
		w.setTitle(label)
		
		gridLayout = QtGui.QGridLayout(w)
		tableView = QtGui.QTableWidget(w)
		gridLayout.addWidget(tableView, 0, 0, 1, 1)
		
		tableView.verticalHeader().hide()
		tableView.horizontalHeader().hide()
		tableView.setShowGrid(False)
		tableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		tableView.setColumnCount(0)
		
		if toolTip:
			w.setToolTip(toolTip)
		if callBack:
			tableView.currentCellChanged.connect(callBack)
		tableView.currentCellChanged.connect(self.widget.completeChanged)
		
		i = 0
		tableView.insertColumn(0)
		for item in items:
			tableView.insertRow(i)
			widgetItem = QtGui.QTableWidgetItem(item)
			widgetItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
			tableView.setItem(i, 0, widgetItem)
			i += 1
			
		try:
			selectedIndex = items.index(defaultValue)
		except:
			selectedIndex = 0

		tableView.setColumnWidth(0, 700)
		
		if tableView.item(selectedIndex, 0):
			tableView.item(selectedIndex, 0).setSelected(True)
		
		if fieldName:
			self.__registerField(fieldName, tableView, 'QListBox', w)

		self.__addWidget(w)


	def addDropList(self, fieldName, label='', defaultValueTuple=([],''), toolTip='', callBack=None):
		items, defaultValue = defaultValueTuple
		w = QtGui.QComboBox(self.widget)
		w.setEditable(0)
		if toolTip:
			w.setToolTip(toolTip)

		i = 0
		for item in items :
			w.insertItem(i, item)
			i += 1
		if defaultValue and defaultValue in items:
			w.setCurrentIndex(items.index(defaultValue))
		if fieldName :
			self.__registerField(fieldName, w, 'QDropList')
		if callBack :
			w.currentIndexChanged.connect(callBack)
		w.currentIndexChanged.connect(self.widget.completeChanged)

		self.__addWidget(w)

	def addRadioList(self, fieldName, label='', defaultValueTuple=([],''), toolTip='', callBack=None):
		items, defaultValue = defaultValueTuple
		
		buttonGroup = QtGui.QButtonGroup(self.widget)
		w = QtGui.QGroupBox(self.widget)
		w.setTitle(label)
		gridLayout = QtGui.QGridLayout(w)
		
		if toolTip:
			w.setToolTip(toolTip)

		try:
			selectedIndex = items.index(defaultValue)
		except:
			selectedIndex = 0
		i=0
		for item in items:
			radioButton = QtGui.QRadioButton(w)
			gridLayout.addWidget(radioButton, i, 0, 1, 1)
			buttonGroup.addButton(radioButton)
			if i == selectedIndex:
				radioButton.setChecked(1)
			radioButton.setText(item)
			i += 1
		if callBack:
			# did not find a QGroupBox signal. Not tried hard though
			buttonGroup.buttonReleased.connect(callBack)
		buttonGroup.buttonReleased.connect(self.widget.completeChanged)

		if fieldName:
			self.__registerField(fieldName, buttonGroup, 'QButtonGroup', w)

		self.__addWidget(w)

	def __createGroupBoxAndLayout(self, label):
		gb = QtGui.QGroupBox(self.widget)
		gb.setTitle(label)
		gbLayout = QtGui.QGridLayout(gb.layout())
		gbLayout.setAlignment(QtCore.Qt.AlignTop)
		return gb, gbLayout

	def addCheckList(self,fieldName, label, defaultValueTuple=([],[]), toolTip='', callBack=None):
		items, defaultValue = defaultValueTuple
		w = QtGui.QGroupBox(self.widget)
		w.setTitle(label)

		gridLayout = QtGui.QGridLayout(w)
		tableView = AbsQtQTable(w, callBack)
		gridLayout.addWidget(tableView, 0, 0, 1, 1)
		
		tableView.verticalHeader().hide()
		tableView.horizontalHeader().hide()
		tableView.setShowGrid(False)
		tableView.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
		tableView.setColumnCount(1)
		tableView.setColumnWidth(0, 800)
		
		if callBack:
			tableView.currentItemChanged.connect(callBack)
		tableView.currentItemChanged.connect(self.widget.completeChanged)

		if toolTip:
			w.setToolTip(toolTip)

		i = 0
		for item in items:
			tableView.insertRow(i)
			widgetItem = QtGui.QTableWidgetItem(item)
			widgetItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
			if item in defaultValue:
				widgetItem.setCheckState(2)
			else:
				widgetItem.setCheckState(0)

			tableView.setItem(i, 0, widgetItem)
			i += 1

		if fieldName:
			self.__registerField(fieldName, tableView, 'QTableWidget')

		self.__addWidget(w)

#in the soon future, maybe all widgets will be extended
class AbsQtQTable(QtGui.QTableWidget):
	def __init__(self, w, callBack):
		QtGui.QTableWidget.__init__(self, w)
		self.callBack = callBack

	def mouseReleaseEvent(self, e):
		QtGui.QTableWidget.mouseReleaseEvent(self, e)
		if self.callBack:
			self.callBack()

	def keyPressEvent(self, e):
		QtGui.QTableWidget.keyPressEvent(self, e)
		if self.callBack:
			self.callBack()
