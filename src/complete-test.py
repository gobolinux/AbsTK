#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#
# A more complete API test, used during migration to PyQt4
#

import sys

if len(sys.argv) == 1 :
	print 'Syntax: %s <curses|qt|gtk>' %sys.argv[0]
	sys.exit(1)

mode = sys.argv[1]
if mode == 'curses' :
	from cwizard import *
	Wizard = AbsCursesWizard
	Screen = AbsCursesScreen
elif mode == 'qt' :
	from qtwizard import *
	Wizard = AbsQtWizard
	Screen = AbsQtScreen
elif mode == 'gtk' :
	from gtkwizard import *
	Wizard = AbsGtkWizard
	Screen = AbsGtkScreen
else :
	print 'Syntax: %s <curses|qt|gtk>' %sys.argv[0]
	sys.exit(1)


def TestBooleanCallback(param):
	print 'callback ', param
	

def TestPasswordCallback():
	print 'pwd callback '

def TestLineEditCallback(param):
	print 'lineedit callback ', param

def TestMultiLineEditCallback():
	print 'lineedit callback '

def TestButtonCallback():
	print 'button callback '

def TestBoxListCallback():
	print 'TestBoxListCallback callback '



w = Wizard('AbsTk Complete Test')

scr = Screen('Screen')

scr.addRadioList('TestRadioList', 'Testing Radio List', (['aaaa', 'bbbb'], 'aaaa'), 'Tooltip', TestBoxListCallback)

scr.addCheckList('TestCheckList', 'Testing Check List', (['aaaa', 'bbbb'], ['aaaa']), 'Tooltip', TestBoxListCallback)
scr.setValue('TestCheckList', (['000', 'aaaa', 'item', 'dddd'], [ 'aaaa', 'dddd'] ))

w.addScreen(scr)


scr = Screen('Screen')
scr.addBoxList('TestBoxList', 'Testing List', (['aaaa', 'item', 'cccc'], 'item'), 'Tooltip', TestBoxListCallback)
scr.setValue('TestBoxList', (['000', 'aaaa', 'item', 'dddd'], 'aaaa'))
w.addScreen(scr)

scr = Screen('Screen')
#scr.addImage('IMG_1607.jpg')
w.addScreen(scr)



scr = Screen('Screen')
scr.addBoolean('TestBoolean', 'Testing Boolean', 1, 'Test Tooltip Boolean', TestBooleanCallback)
scr.addPassword('TestPassword', 'Testing Password', 'xxx', 'Tooltip', TestPasswordCallback)
scr.addLineEdit('TestLineEdit', 'Testing LineEdit', 'xxxyyy', 'Tooltip', TestLineEditCallback)
scr.addMultiLineEdit('TestMultiLineEdit', 'Testing MultiLineEdit', 'xxxyyy jdsfklj dhjslf', 'Tooltip', TestMultiLineEditCallback)

w.addScreen(scr)

scr = Screen('Screen')
scr.addButton('TestButton', 'Testing Button', 1, 'Tooltip button', TestButtonCallback)
scr.addDropList('TestDropList', 'Testing List', (['aaaa', 'bbbb', 'cccc'], 'bbbb'), 'Tooltip', TestBoxListCallback)
w.addScreen(scr)


scr = Screen('Last Screen')
scr.addLabel('Parameter1', '1234')
scr.addLabel('Parameter2', 'abcd')
scr.addLabel('Parameter3', 'xyz')

w.addScreen(scr)


w.start()

for FieldName in [ 'TestBoolean', 'TestPassword', 'TestMultiLineEdit', 'TestBoxList', 'TestCheckList', 'TestRadioList']:
	print FieldName, '=', w.getValue(FieldName)


