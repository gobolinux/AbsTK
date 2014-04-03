# -*- encoding iso-8859-1 -*-
#!/usr/bin/python

import curses, curses.textpad, traceback, string, time, textwrap, threading
from wizard import *

class keys :
   TAB = 9
   ENTER = 10
   ESC = 27
   SPACE = 32

class actions :
   PASSTHROUGH = 0
   HANDLED = -2
   PREVIOUS = -1
   NEXT = 1
   FOCUS_ON_BUTTONS = 10

class buttons :
   PREVIOUS = 0
   NEXT = 1
   QUIT = 2
   LAST = 2

def setColor(color, fg, bg):
   try : curses.init_pair(color, fg, bg)
   except : pass

def drawScrollBar(drawable, x, y, h, percent) :
   for i in range(h-1) :
      drawable.addstr(y + i, x, " ", widgetColor)
   pch = percent * (h - 2)
   drawable.addstr(y, x, "^", buttonColor)
   drawable.addstr(y+int(pch)+1, x, "*", buttonColor)
   drawable.addstr(y+h-1, x, "v", buttonColor)
      
def drawButton(drawable, x, y, buttonText, focus, hidden=False) :
   if hidden :
      drawable.addstr(y, x, " " * len(buttonText), defaultColor)
   else :
      drawable.addstr(y, x, buttonText, buttonColor)
   (left, right) = (" ", " ")
   if focus :
      (left, right) = (">", "<")
   drawable.addstr(y, x-1, left, titleColor)
   drawable.addstr(y, x+len(buttonText), right, titleColor)

def hideCursor() :
   stdscr.move(maxY-1,maxX-1)

def center(width, data) :
   if type(data) == type("string") :
      return (width / 2) - (len(data) / 2)
   else :
      return (width / 2) - (data / 2)

def debug(s):
   stdscr.addstr(0, 0, str(s))

class AbsCursesWizard(AbsWizard) :

   def __init__(self, name = '') :
      self.screens = []
      self.currentScreen = -1

   #detsch
   def clear(self, newName = '') :
      self.screens = []
      self.currentScreen = -1

   def start(self) :
      result = 0
      try :
         curses.noecho()
         curses.cbreak()
         stdscr.keypad(1)
         result = self.__main(stdscr)
         self.done()
      except :
         self.done()
         traceback.print_exc()
      return result

   def done(self):
      stdscr.keypad(0)
      curses.echo()
      curses.nocbreak()
      curses.endwin()
      
   def __movementHelp(self):
      stdscr.addstr(maxY-3, 1, " Tab: move focus   Enter: select ", defaultColor)
      
   def __drawButtons(self, focus) :
      if self.currentScreen == len(self.screens) - 1 :
         next = " -> Done "
      else :
         next = " -> Next "
      drawButton(stdscr, maxX-35, maxY-3, " Previous <- ", focus == buttons.PREVIOUS, self.currentScreen == 0)
      drawButton(stdscr, maxX-20, maxY-3, next, focus == buttons.NEXT, False)
      drawButton(stdscr, maxX-9, maxY-3, " Quit ", focus == buttons.QUIT, False)

   def __drawScreen(self) :
      # stdscr.clear()
      stdscr.subwin(maxY-1,maxX,0,0).box()
      self.__movementHelp()
      self.__drawButtons(None)
      self.screens[self.currentScreen].draw()
      stdscr.refresh()

   def showMessageBox(self, message, options=["Ok", "Cancel"], default=0) :
      global spinner
      if spinner != None:
         spinner.stop()
      x = 3
      y = maxY/2-4
      width = maxX - 6
      subwidth = width - 2
      message = message.replace("\n", " ")
      if len(message) < subwidth :
         lines = [ message ]
      else :
         lines = textwrap.wrap(message, subwidth - 2)

      height = 6 + len(lines)
      area = stdscr.subwin(height, width, y, x)
      area.attrset(widgetColor)
      area.clear()
      area.box()
      area.keypad(1)
      subarea = stdscr.subwin(height-2, subwidth, y + 1, x + 1)
      subarea.idlok(1)
      subarea.scrollok(1)

      i = 1
      for line in lines: 
         subarea.addstr(i, center(subwidth, line), line, titleColor)
         i = i + 1

      k = 0
      sel = default
      global forceRedraw
      while ( k != keys.ENTER and k != keys.SPACE ) :
         l = center(width, sum(map(lambda x : len(x) + 6, options)))
         for i in range(len(options)) :
            drawButton(area, 3 + l, height - 3, " "+options[i]+" ", i == sel)
            l = l + len(options[i]) + 4
         area.refresh()
         hideCursor()
         k = stdscr.getch()
         if k == curses.KEY_RIGHT or k == keys.TAB or k == curses.KEY_DOWN :
            sel = sel + 1
            if sel == len(options) :
               sel = 0
         elif k == curses.KEY_LEFT or k == curses.KEY_UP :
            sel = sel - 1
            if sel == - 1 :
               sel = len(options) - 1
         elif k == keys.ESC :
            forceRedraw = True
            return actions.HANDLED
      forceRedraw = True
      return options[sel]

   def __main(self, stdscr):
      global defaultColor, disabledColor, titleColor, buttonColor, widgetColor, widgetDisabledColor
      # Frame the interface area at fixed VT100 size
      if self.currentScreen == -1 :
         return
      k = 0
      self.__drawScreen()
      global forceRedraw
      forceRedraw = False
      while 1 :
         self.__drawButtons(None)
         screen = self.screens[self.currentScreen]
         screen.draw()
         hideCursor()
         if forceRedraw == True:
            k = 0
            forceRedraw = False
            stdscr.refresh()
         else :
            k = stdscr.getch()
         
         action = screen.processKey(k)
         if action == actions.FOCUS_ON_BUTTONS :
            screen.draw()
            if self.currentScreen != 0 :
               firstButton = buttons.PREVIOUS
            else :
               firstButton = buttons.NEXT
            if screen.focus == -1 :
               currButton = buttons.LAST
            else :
               currButton = firstButton
            while 1 :
               self.__drawButtons(currButton)
               hideCursor()
               bk = stdscr.getch()
               if bk == curses.KEY_LEFT or bk == curses.KEY_UP :
                  if currButton == firstButton :
                     lastActive = len(screen.focusWidgets) - 1
                     while screen.focusWidgets[lastActive].enabled == False :
                        lastActive = lastActive - 1
                     screen.setFocus(lastActive, -1)
                     break
                  else :
                     currButton = currButton - 1
               elif bk == curses.KEY_RIGHT or bk == keys.TAB or bk == curses.KEY_DOWN :
                  if currButton == buttons.LAST :
                     screen.setFocus(0, 1)
                     break
                  else :
                     currButton = currButton + 1
               elif bk == keys.ENTER :
                  screen.setFocus(0)
                  if currButton == buttons.PREVIOUS :
                     self.currentScreen = self.currentScreen - 1
                     self.screens[self.currentScreen].setFocus(0)
                     break
                  elif currButton == buttons.NEXT :
                     if not screen.nextCB or screen.nextCB():
                        if self.currentScreen < len(self.screens) - 1 :
                           self.currentScreen = self.currentScreen + 1
                           self.screens[self.currentScreen].setFocus(0)
                        else :
                           go = self.showMessageBox("Press Enter to proceed!")
                           if go == "Ok" :
                              return 1
                     break
                  elif currButton == buttons.QUIT :
                     go = self.showMessageBox("Are you sure you want to quit?", ["Yes", "No"], 1)
                     if go == "Yes" :
                        return 0
                     break
         elif action == actions.PASSTHROUGH :
            # Easter egg: MATRIX MODE :)
            if k == ord('9') :
               setColor(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
               setColor(2, curses.COLOR_RED, curses.COLOR_BLACK)
               setColor(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
               setColor(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
               setColor(5, curses.COLOR_BLUE, curses.COLOR_GREEN)
               setColor(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
               defaultColor = curses.color_pair(1)
               disabledColor = curses.color_pair(2) + curses.A_BOLD
               titleColor = curses.color_pair(3)
               buttonColor = curses.color_pair(4)
               widgetColor = curses.color_pair(5)
               widgetDisabledColor = curses.color_pair(5) + curses.A_BOLD
               currentColor = curses.color_pair(6) + curses.A_BOLD
               stdscr.clear()
               stdscr.addstr(0,0,"Knock, knock.")
               stdscr.getch()
               self.__drawScreen()
            elif k == ord('0') :
               setColor(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
               setColor(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
               setColor(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)
               setColor(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
               setColor(5, curses.COLOR_BLACK, curses.COLOR_CYAN)
               setColor(6, curses.COLOR_CYAN, curses.COLOR_BLUE)
               defaultColor = curses.color_pair(1)
               disabledColor = curses.color_pair(2) + curses.A_BOLD
               titleColor = curses.color_pair(3)
               buttonColor = curses.color_pair(4)
               widgetColor = curses.color_pair(5)
               widgetDisabledColor = curses.color_pair(5) + curses.A_BOLD
               currentColor = curses.color_pair(6) + curses.A_BOLD

   def addScreen(self, screen, pos = 0) :
      # Add the screen at the end
      if pos == 0 :
         self.screens.append(screen)
      # Add the screen right after the current one
      elif pos == -1 :
         self.screens.insert(self.currentScreen + 1, screen)
      # Add the screen at a specific possition
      else :
         self.screens.insert(pos,screen)
      if self.currentScreen == -1 :
         self.currentScreen = 0

   def removeScreen(self, screen) :
      self.screens.remove(screen)

class Spinner(threading.Thread) :
   def __init__(self):
      threading.Thread.__init__(self)
      self.stopped = False
   
   def stop(self):
      self.stopped = True
   
   def run(self):
      spin = ['-','\\','|','/']
      step = 0
      while not self.stopped:
         stdscr.addstr(maxY/2, maxX/2, "("+spin[step]+")")
         stdscr.refresh()
         step = step + 1
         if step == len(spin):
            step = 0
         time.sleep(0.1)

class CursesWidget :

   def __init__() :
      self.height = 1
      self.tooltip = "I DON'T HAVE A TOOLTIP"
      self.enabled = True

   def setEnabled(self, enabled) :
      self.enabled = enabled
      if not enabled :
         self.inside = False

   def getHeight(self) :
      return self.height

   def isEnabled(self) :
      return self.enabled

   def getTooltip(self) :
      return self.tooltip

   def draw(self, drawable, x, y) :
      pass

   def runCallback(self):
      global forceRedraw
      global spinner
      if self.callBack != None :
         spinner = Spinner()
         spinner.start()
         self.callBack()
         forceRedraw = True
         spinner.stop()
         spinner = None

   def makeAttr(self, inside, enabled, off, on, usein=None) :
      if not enabled :
         return off
      else :
         if inside and usein:
            return usein
         return on

class CursesLabel(CursesWidget) :
   def __init__(self, label) :
      self.height = 1
      #detsch:
      self.label = label

   #detsch:
   def setValue(self, newlabel) :
      self.label = newlabel

   #detsch:
   def getValue(self) :
      return self.label

   def draw(self, drawable, x, y) :
      attr = self.makeAttr(0, 1, disabledColor, defaultColor, defaultColor + curses.A_BOLD)
      drawable.addstr(y, x, " " * (maxX - 10), attr)
      drawable.addstr(y, x, self.label, attr)

class CursesAbstractList(CursesWidget):

   def __init__(self, label, items, defaultValue, callBack, tooltip) :
      if maxY <= 25 :
         limit = 5
      else :
         limit = maxY / 3
      if len(items) < limit and len(items) > 0 :
         self.height = len(items)+1
         self.isCompact = True
      else :
         self.height = limit + 3
         self.isCompact = False
      self.width = maxX - 10
      self.first = 0
      self.items = items
      self.value = defaultValue
      self.current = 0
      self.inside = False
      self.enabled = True
      self.label = label
      self.callBack = callBack
      self.tooltip = tooltip
      self.scrollH = 0
      self.on = "[x]"
      self.off = "[ ]"

   def isSet(self, i) :
      return 0
      
   def set(self, i) :
      pass

   def draw(self, drawable, x, y) :
      attrdefault = self.makeAttr(self.inside, self.enabled, disabledColor, defaultColor, defaultColor + curses.A_BOLD)
      attrlist = attrdefault
      attritem = self.makeAttr(self.inside, self.enabled, disabledColor, defaultColor, currentColor)
      drawable.addstr(y, x, self.label, attrlist)
      curr = self.current
      first = self.first
      last = min(first+(self.height-3), len(self.items))
      if self.isCompact :
         ypos = y+1
         xpos = x
         last = len(self.items)
      else :
         attrlist = self.makeAttr(self.inside, self.enabled, widgetDisabledColor, widgetColor)
         attritem = self.makeAttr(self.inside, self.enabled, widgetDisabledColor, widgetColor, widgetColor + curses.A_STANDOUT)
         w = drawable.subwin(self.height-1, self.width, y+1, x)
         w.attrset(attrdefault)
         w.clear()
         w.border()
         pc = max(((curr+0.0)/max(len(self.items),1)), 0)
         drawScrollBar(drawable, x+self.width-1, y+2, self.height - 3, pc)
         ypos = y+2
         xpos = x+1
      if len(self.items) == 0 :
         return
      for i in range(first, last) :
         item = self.items[i]
         value = self.isSet(i)
         cropItem = item[self.scrollH:self.width-6+self.scrollH].ljust(self.width-6)
         if i == self.current :
            at = attritem
         else :
            at = attrlist
         if value:
            drawable.addstr(ypos, xpos, self.on + " " + cropItem, at)
         else :
            drawable.addstr(ypos, xpos, self.off + " " + cropItem, at)
         ypos = ypos + 1

   def processKey(self, key) :
      c = self.current
      if key == keys.TAB :
         return actions.NEXT
      if key == keys.SPACE or key == keys.ENTER :
         self.set(c)
         self.runCallback()
         return actions.HANDLED
      elif (key >= ord('a') and key <= ord('z')) or (key >= ord('A') and key <= ord('Z')):
         for i in range(len(self.items)) :
            if self.items[i][0].lower() == chr(key).lower() :
               c = i
               break
      elif key == curses.KEY_UP :
         c = c - 1
      elif key == curses.KEY_DOWN :
         c = c + 1
      elif key == curses.KEY_PPAGE :
         c = c - (self.height - 3)
      elif key == curses.KEY_NPAGE :
         c = c + (self.height - 3)
      elif key == curses.KEY_HOME :
         c = 0
      elif key == curses.KEY_END :
         c = len(self.items) - 1
      elif key == curses.KEY_RIGHT:
         if self.isCompact :
            return actions.FOCUS_ON_BUTTONS
         self.scrollH = self.scrollH + 10
         return actions.HANDLED
      elif key == curses.KEY_LEFT:
         if self.isCompact :
            return actions.FOCUS_ON_BUTTONS
         if self.scrollH > 0:
            self.scrollH = self.scrollH - 10
         return actions.HANDLED
      action = actions.PASSTHROUGH
      if c != self.current :
         action = actions.HANDLED
      if c < 0 :
         c = 0
         action = actions.PREVIOUS
      elif c >= len(self.items) :
         c = len(self.items) - 1
         action = actions.NEXT
      self.current = c
      if not self.isCompact :
         if c < self.first :
            self.first = c
         if c >= self.first+(self.height-3) :
            self.first = c-((self.height-3)-1)
      return action

class CursesList(CursesAbstractList) :

   def __init__(self, label, items, defaultValue, callBack, tooltip) :
      CursesAbstractList.__init__(self, label, items, defaultValue, callBack, tooltip)
      self.value = 0
      if defaultValue :
         for i in range(len(items)) :
            if items[i] == defaultValue :
               self.value = i
               self.current = i
               break
      if self.value >= self.first + self.height:
         self.first = self.value
      self.on = "(*)"
      self.off = "( )"

   def isSet(self, i) :
      return self.value == i
      
   def set(self, i) :
      self.value = i

   def setValue(self, valueTuple) :
      self.items = valueTuple[0][:]
      try :
         self.value = self.items.find(valueTuple[1])
      except :
         self.value = 0
      self.first = 0
      self.current = 0

   def getValue(self) :
      if self.value >= 0 and len(self.items) > self.value:
         v = self.items[self.value]
      else :
         v = 0
      #detsch ([:] to copy the list, instead of passing a reference)
      return (self.items[:], v)


class CursesCheckList(CursesAbstractList) :

   def __init__(self, label, items, defaultValue, callBack, tooltip) :
      CursesAbstractList.__init__(self, label, items, defaultValue, callBack, tooltip)
      self.value = defaultValue

   def setValue(self, valueTuple) :
      self.items = valueTuple[0][:]
      self.value = map(lambda item : item in valueTuple[1], self.items)
      self.first = 0
      self.current = 0
      
   def getValue(self):
      result = []
      for (value, item) in zip(self.value, self.items) :
         if value == True :
            result.append(item)
      #detsch ([:] to copy the list, instead of passing a reference)
      return (self.items[:], result)

   def isSet(self, i):
      return self.value[i]

   def set(self, i) :
      if self.value[i] == False :
         self.value[i] = True
      else :
         self.value[i] = False

class CursesTextBox(CursesWidget) :

   def __init__(self, label, defaultValue, callBack, tooltip) :
      self.height = maxY - 10
      self.width = maxX - 10
      self.first = 0
      self.label = label
      self.value = defaultValue.split("\n")
      self.textWidth = max([len(l) for l in self.value])
      self.inside = False
      self.enabled = True
      self.callBack = callBack
      self.tooltip = tooltip
      self.scrollH = 0

   def setValue(self, value) :
      self.value = value.split("\n")

   def getValue(self):
      return string.join(self.value, "\n")

   def draw(self, drawable, x, y) :
      attrtitle = self.makeAttr(self.inside, self.enabled, disabledColor, defaultColor, currentColor)
      attrtext = self.makeAttr(self.inside, self.enabled, disabledColor, defaultColor)
      drawable.addstr(y, x, self.label, attrtitle)
      w = drawable.subwin(self.height-1, self.width, y+1, x)
      w.clear()
      w.border()
      f = self.first
      if len(self.value) > self.height - 2:
         pc = (self.first+0.0)/len(self.value)
         drawScrollBar(drawable, x+self.width-1, y+2, self.height - 3, pc)
      ypos = y+2
      for item in self.value[f:f+self.height-3] :
         cropItem = item[self.scrollH:self.width-2+self.scrollH].ljust(self.width-2)
         drawable.addstr(ypos, x+1, cropItem, attrtext)
         f = f + 1
         ypos = ypos + 1

   def processKey(self, key) :
      if self.inside :
         f = self.first
         if key == keys.TAB :
            self.inside = False
            self.runCallback()
            return actions.NEXT
         elif key == curses.KEY_UP :
            if len(self.value) > self.height - 2 :
               f = f - 1
            else :
               return actions.PREVIOUS
         elif key == curses.KEY_DOWN :
            if len(self.value) > self.height - 2 :
               f = f + 1
            else :
               return actions.NEXT
         elif key == curses.KEY_PPAGE :
            if len(self.value) > self.height - 2 :
               f = f - (self.height - 3)
         elif key == curses.KEY_NPAGE :
            if len(self.value) > self.height - 2 :
               f = f + (self.height - 3)
         elif key == curses.KEY_RIGHT:
            if self.textWidth > self.width - 2 :
               self.scrollH = self.scrollH + 10
               return actions.HANDLED
         elif key == curses.KEY_LEFT:
            if self.textWidth > self.width - 2 :
               if self.scrollH > 0:
                  self.scrollH = self.scrollH - 10
                  return actions.HANDLED
         if f < 0 :
            f = 0
         if f >= len(self.value) :
            f = len(self.value) - 1
         self.first = f
      else :
         if key == keys.ENTER and self.enabled :
            self.inside = True
         elif key == keys.TAB :
            return actions.NEXT
      return 0

class CursesBoolean(CursesWidget) :

   def __init__(self, label, value, callBack, tooltip) :
      self.callBack = callBack
      self.height = 1
      self.inside = False
      self.label = label
      if value == 0 or value == False:
         self.value = False
      else:
         self.value = True
      self.enabled = True
      self.tooltip = tooltip

   def setValue(self, value) :
      self.value = value

   def getValue(self):
      return self.value

   def draw(self, drawable, x, y) :
      attr = self.makeAttr(self.inside, self.enabled, disabledColor, defaultColor, currentColor)
      if self.value == 1 :
         drawable.addstr(y, x, "[x] " + self.label, attr)
      else :
         drawable.addstr(y, x, "[ ] " + self.label, attr)

   def processKey(self, key) :
      if ( key == keys.ENTER or key == keys.SPACE ) and self.enabled :
         if self.value == False :
            self.value = True
         else :
            self.value = False
         self.runCallback()
         return actions.HANDLED
      elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT :
         return actions.FOCUS_ON_BUTTONS
      elif key == curses.KEY_UP :
         return actions.PREVIOUS
      elif key == curses.KEY_DOWN or key == keys.TAB :
         return actions.NEXT
      return actions.PASSTHROUGH

class CursesButton(CursesWidget) :

   def __init__(self, label, value, callBack, tooltip) :
      self.height = 1
      self.inside = False
      self.label = label
      self.value = value
      self.enabled = True
      self.callBack = callBack
      self.tooltip = tooltip

   def setValue(self, value) :
      self.value = value

   def getValue(self):
      return self.value

   def draw(self, drawable, x, y) :
      drawButton(drawable, x+1, y, " "+self.label+" ", self.inside)

   def processKey(self, key) :
      if ( key == keys.ENTER or key == keys.SPACE ) and self.enabled :
         self.runCallback()
      elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT :
         return actions.FOCUS_ON_BUTTONS
      elif key == keys.TAB or key == curses.KEY_DOWN :
         return actions.NEXT
      elif key == curses.KEY_UP :
         return actions.PREVIOUS
      return actions.PASSTHROUGH

class CursesEntry(CursesWidget) :

   def __init__(self, label, value, callBack, tooltip) :
      self.height = 1
      self.width = maxX - 10 - len(label)
      self.label = label
      self.value = value
      self.inside = False
      self.cursor = len(value)
      self.enabled = True
      self.callBack = callBack
      self.tooltip = tooltip

   def setValue(self, value) :
      self.value = value
      self.cursor = len(value)

   def getValue(self):
      return self.value

   def draw(self, drawable, x, y) :
      attr = self.makeAttr(self.inside, self.enabled, disabledColor, defaultColor, currentColor)
      field = self.value[:self.width].ljust(self.width)
      cur = self.cursor
      label = self.label + " ["
      drawable.addstr(y, x, label, attr)
      drawable.addstr(y, x+len(label)+len(field), "]", attr)
      attr = self.makeAttr(self.inside, self.enabled, widgetDisabledColor, widgetColor)
      if self.inside:
         left = field[:cur]
         mid = field[cur:cur+1]
         right = field[cur+1:]
         drawable.addstr(y, x+len(label), left, attr)
         drawable.addstr(y, x+len(label)+len(left), mid, attr + curses.A_STANDOUT)
         drawable.addstr(y, x+len(label)+len(left)+1, right, attr)
      else:
         drawable.addstr(y, x+len(label), field, attr)

   def processKey(self, key) :
      if key == curses.KEY_UP :
         self.runCallback()
         return actions.PREVIOUS
      elif key == curses.KEY_DOWN or key == keys.TAB or key == curses.KEY_ENTER :
         self.runCallback()
         return actions.NEXT
      elif (key >= keys.SPACE and key <= 126) or (key >= 128 and key <= 255) :
         cur = self.cursor
         self.value = self.value[:cur] + chr(key) + self.value[cur:]
         self.cursor = cur + 1
         self.runCallback()
         return actions.HANDLED
      elif key == 127 or key == 263:
         cur = self.cursor
         if cur > 0 :
            self.value = self.value[:cur-1] + self.value[cur:]
            self.cursor = cur - 1
         return actions.HANDLED
      elif key == 330 :
         cur = self.cursor
         self.value = self.value[:cur] + self.value[cur+1:]
         return actions.HANDLED
      elif key == curses.KEY_LEFT :
         cur = self.cursor
         if cur > 0 :
            self.cursor = cur - 1
         return actions.HANDLED
      elif key == curses.KEY_RIGHT :
         cur = self.cursor
         if cur < len(self.value) :
            self.cursor = cur + 1
         return actions.HANDLED
      return actions.PASSTHROUGH

class CursesPassword(CursesEntry) :

   def draw(self, drawable, x, y) :
      saveField = self.value
      pw = ""
      for c in saveField :
         pw = pw + "*"
      self.value = pw
      CursesEntry.draw(self, drawable, x, y)
      self.value = saveField

class AbsCursesScreen(AbsScreen) :

   def __init__(self, title="WARNING: I DON'T HAVE A TITLE!") :
      self.fields = {}
      self.widgets = []
      self.focusWidgets = []
      self.pad = curses.newpad(maxX-2 + 100, maxY-4 + 100)
      self.pad.bkgd(" ",curses.color_pair(1))
      self.focus = -1
      self.vscroll = 0
      self.title = title
      self.nextCB = None

   def __setupFocusAndCurrent(self, delta) :
      widget = self.focusWidgets[self.focus]
      widget.inside = True
      if hasattr(widget, "items") :
         if delta == 1 :
            widget.current = 0
         else :
            widget.current = len(widget.items) - 1
      return widget

   def __moveFocusSkippingDisabled(self, delta) :
      widget = self.focusWidgets[self.focus]
      while 1 :
         widget.inside = False
         self.focus = self.focus + delta
         if self.focus == -1 or self.focus == len(self.focusWidgets) :
            return actions.FOCUS_ON_BUTTONS
         widget = self.__setupFocusAndCurrent(delta)
         if self.focusWidgets[self.focus].enabled :
            return actions.HANDLED

   def setFocus(self, idx, delta=1) :
      self.focus = idx
      if idx != -1 :
         if not self.focusWidgets[self.focus].enabled :
            return self.__moveFocusSkippingDisabled(delta)
         self.__setupFocusAndCurrent(delta)

   def draw(self) :
      self.pad.addstr(0, 0, self.title, titleColor)
      at = 2
      focusAt = 2
      focusHeight = 0
      if self.focus > -1 and self.focus < len(self.focusWidgets) :
         focused = self.focusWidgets[self.focus]
      else :
         focused = None
      vscroll = self.vscroll
      for widget in self.widgets :
         if widget == focused :
            self.pad.addstr(at, 1, ">", titleColor)
            focusAt = at
            focusHeight = widget.getHeight()
         else :
            self.pad.addstr(at, 1, " ", titleColor)
            if self.focus == len(self.focusWidgets) :
               focusAt = at
               focusHeight = widget.getHeight()
               
         widget.draw(self.pad, 3, at)
         at = at + widget.getHeight() + 1
      padheight = maxY - 5
      if (focusAt + focusHeight) >= (vscroll + padheight) :
         vscroll = vscroll + ((focusAt+focusHeight) - (vscroll+padheight))
         self.vscroll = vscroll
      if focusAt < vscroll :
         vscroll = focusAt
         if vscroll == 2 :
            vscroll = 0
         self.vscroll = vscroll
      if (at - 2) > padheight :
         drawScrollBar(self.pad, maxX - 3, vscroll, padheight, ((focusAt-2)+0.0)/(at-2))

      self.pad.refresh(vscroll, 0, 1, 1, padheight, maxX-2)
      if focused :
         stdscr.addstr(maxY - 1, 0, focused.getTooltip().ljust(maxX)[:maxX-1], widgetColor)

   def processKey(self, key) :
      if self.focus == -1 :
         return
      widget = self.focusWidgets[self.focus]
      motion = widget.processKey(key)
      if motion == actions.PASSTHROUGH or motion == actions.HANDLED :
         return motion
      elif motion == motion == actions.FOCUS_ON_BUTTONS :
         self.focus = len(self.focusWidgets)
         return motion
      assert motion == actions.PREVIOUS or motion == actions.NEXT, "Motion is " + str(motion)
      if motion == actions.PREVIOUS :
         delta = -1
      elif motion == actions.NEXT :
         delta = 1
      return self.__moveFocusSkippingDisabled(delta)

   def __registerField(self, name, widget) :
      self.fields[name] = widget

   def __registerFocus(self, widget) :
      self.focusWidgets.append(widget)
      if self.focus == -1 :
         self.focus = 0
         widget.inside = True

   def setTitle(self, title) :
      self.title = title

   def __addWidget(self, fieldName, w = None, focus = True):
      if fieldName :
         self.__registerField(fieldName, w)
      if focus :
         self.__registerFocus(w)
      self.widgets.append(w)

   def addLabel(self, fieldName, label, defaultValue = '', tooltip = "I DON'T HAVE A TOOLTIP", callBack = None) :
      w = CursesLabel(label)
      self.__addWidget(fieldName, w, False)

   def addList(self, fieldName, label, defaultValueTuple = ([],''), tooltip = "I DON'T HAVE A TOOLTIP", callBack = None) :
      w = CursesList(label, defaultValueTuple[0], defaultValueTuple[1], callBack, tooltip)
      self.__addWidget(fieldName, w)

   def addBoolean(self, fieldName, label, defaultValue = 0, tooltip = "I DON'T HAVE A TOOLTIP", callBack = None) :
      w = CursesBoolean(label, defaultValue, callBack, tooltip)
      self.__addWidget(fieldName, w)

   def addLineEdit(self, fieldName, label, defaultValue = '', tooltip = "I DON'T HAVE A TOOLTIP", callBack = None) :
      w = CursesEntry(label, defaultValue, callBack, tooltip)
      self.__addWidget(fieldName, w)

   def addPassword(self, fieldName, label, defaultValue = '', tooltip = "I DON'T HAVE A TOOLTIP", callBack = None) :
      w = CursesPassword(label, defaultValue, callBack, tooltip)
      self.__addWidget(fieldName, w)

   def addMultiLineEdit(self, fieldName, label, defaultValue = '', tooltip = "I DON'T HAVE A TOOLTIP", callBack = None) :
      w = CursesTextBox(label, defaultValue, callBack, tooltip)
      self.__addWidget(fieldName, w)

   def addCheckList(self, fieldName, label, defaultValueTuple = ([],[]), tooltip = "I DON'T HAVE A TOOLTIP", callBack = None) :
      defaultChecks = map(lambda item : item in defaultValueTuple[1], defaultValueTuple[0])
      w = CursesCheckList(label, defaultValueTuple[0], defaultChecks, callBack, tooltip)
      self.__addWidget(fieldName, w)

   def addButton(self, fieldName, label, defaultValue = '', tooltip = "I DON'T HAVE A TOOLTIP", callBack = None) :
      w = CursesButton(label, defaultValue, callBack, tooltip)
      self.__addWidget(fieldName, w)
   
   def addImage(self, fileName) :
      pass
   
   def onValidate(self, nextCB) :
      self.nextCB = nextCB

global stdscr
global defaultColor, disabledColor, titleColor, buttonColor, widgetColor, spinner
spinner = None
stdscr = curses.initscr()
global maxX, maxY
(maxY, maxX) = stdscr.getmaxyx()
maxX=min(maxX,127)
#maxY=min(maxY,24)
curses.start_color()
setColor(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
setColor(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
setColor(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)
setColor(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
setColor(5, curses.COLOR_BLACK, curses.COLOR_CYAN)
setColor(6, curses.COLOR_CYAN, curses.COLOR_BLUE)
defaultColor = curses.color_pair(1)
disabledColor = curses.color_pair(2) + curses.A_BOLD
titleColor = curses.color_pair(3) + curses.A_BOLD
buttonColor = curses.color_pair(4)
widgetColor = curses.color_pair(5)
widgetDisabledColor = curses.color_pair(5) + curses.A_BOLD
currentColor = curses.color_pair(6) + curses.A_BOLD

stdscr.bkgd(" ",curses.color_pair(1))
