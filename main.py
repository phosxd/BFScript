# ------------------
# BFSC version 1.0.0
# ------------------

from pathlib import Path
import shutil
import random
import time
from lang import lang

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'

#Get config details
configDetails = {}
try:
  f = open('bfsc-config.txt','r')
  fileText = f.read().split('\n')
  for line in fileText:
    line = line.split(':')
    if line[0] == 'askToClearGen':
      if line[1] == '1': configDetails[line[0]] = 1
      elif line[1] == '0': configDetails[line[0]] = 0
      else: x = int('f')
    elif line[0] == 'indentationChar':
      configDetails[line[0]] = line[1]
    elif line[0] == 'indentationSize':
      configDetails[line[0]] = int(line[1])
    elif line[0] == 'defaultFuncFile':
      configDetails[line[0]] = line[1]
    elif line[0] == 'defaultBFScriptFile':
      configDetails[line[0]] = line[1]
  f.close()
except:
  print(f'{RED}Config file missing or malformed, generated new.{RESET}')
  f = open('bfsc-config','w')
  f.write("askToClearGen:1\nindentationChar: \nindentationSize:2\ndefaultFuncFile:base\ndefaultBFScriptFile:?")
  configDetails = {'askToClearGen':1,'indentationChar': ' ','indentationSize':2,'defaultFuncFile':'base','defaultBFScriptFile':'?'}

IndentationSize = configDetails['indentationSize']
Home = 'BFSC Generated'
Numbers = [*'1234567890']
stickyLines = []

#Utility functions
def isNumber(string):
  try: x = int(string)
  except: return False
  return True

def sandwich(var, start, end):
  var = 'a'+var.replace(start,'%-#â¡#-%',1).replace(end,'%-#â¡#-%',1)
  var = var.split('%-#â¡#-%')
  if len(var) > 1:
    substr = var[1]
    return substr
  else: return None

#Deletes the directory "BFSC Generated" to clear any leftover files then creates a new folder with the same name.
if configDetails['askToClearGen'] == 1: input(f'{RED}Wait! {YELLOW}proceeding will wipe any previously compiled files from the folder "BFSC Generated". Backup any important files there before continuing.{RESET}')
Path(Home).mkdir(parents=False,exist_ok=True)
shutil.rmtree(Home)
Path(Home).mkdir(parents=False,exist_ok=False)

#Create new line on a file
def newLine(file,command,stickToEnd=False):
  if stickToEnd: stickyLines.append([file,command])
  else:
    with open(f'{Home}/{file}.mcfunction', 'a') as f:
      f.write(f'\n{command}')


# ------------------------------------
# Define Compiling & Parsing Functions
# ------------------------------------
def returnParams(string):
  string = string+' '
  params = []
  inString = False
  ignoreNext = False
  current = ''
  for ch in string:
    if ch == "'" and inString == False:
      ignoreNext = False
      inString = True
    elif ch == "'" and inString:
      if ignoreNext:
        ignoreNext = False
        current += ch
      else:
        params.append({'t':'str','v':current})
        current = ''
        inString = False
    elif ch == '\\' and inString:
      ignoreNext = True
    elif ch == ' ' and inString == False:
      ignoreNext = False
      if current != '': params.append({'t':'any','v':current})
      current = ''
    else:
      current += ch
      ignoreNext = False
  return params


def compileST(ST,IN,meta):
  defVars = meta['defVars']
  defFuncs = meta['defFuncs']
  mods = meta['mods']
  ST = ST.lstrip('\n')
  ST2 = ST.lstrip(configDetails['indentationChar'])
  indent = int((len([*ST])-len([*ST2]))/IndentationSize)
  for i in range(0,len(mods)):
    if len(mods) > indent: mods.pop(-1)
  modCount = len(mods)
  def comp():
    try:
      #Split statement into list - STP = Statement Parameters
      STP = returnParams(ST2)
      lenSTP = len(STP)
      if lenSTP == 0: return 'skip'
      Keyword = STP[0]['v']

      #Recognize comment (#) statement
      if ST2.startswith('#'): pass
      #Recognize & execute log statement
      elif Keyword == 'log':
        if lenSTP != 2: return f'{RED}At statement {IN+1}: "log" statement takes 1 parameter.'
        input = STP[1]
        if input['t'] == 'str': print(input['v'])
        else:
          var = defVars.get(input['v'])
          if var == None: print(f'<{input["v"]}: Undefined>')
          else: print(f'<{input["v"]}: Defined>')

      #Compile var statement
      elif Keyword == 'var':
        if lenSTP != 4 and lenSTP != 5: return f'{RED}At statement {IN+1}: "var" statement takes 3 or 4 parameters.'
        name = STP[1]
        operator = STP[2]
        value = STP[3]
        value2 = None
        if lenSTP == 5: value2 = STP[4]
        if name['t'] != 'any': return f'{RED}At statement {IN+1}: "var" statement, parameter 1 can\'t be a string.'
        if operator['t'] != 'any': return f'{RED}At statement {IN+1}: "var" statement, parameter 2 can\'t be a string.'
        if value['t'] != 'any': return f'{RED}At statement {IN+1}: "var" statement, parameter 3 can\'t be a string.'
        if value2 != None:
          if value2['t'] != 'any': return f'{RED}At statement {IN+1}: "var" statement, parameter 4 can\'t be a string.'
        name = name['v']
        operator = operator['v']
        value = value['v']
        if value2 != None: value2 = value2['v']

        if operator == '=':
          if isNumber(value): construct = f'scoreboard players set {name} bfsGlobals {value}'
          else:
            if defVars.get(value) == None: return f'{RED}At statement {IN+1}: var "{value}" is not defined.'
            construct = f'scoreboard players operation {name} bfsGlobals = {value} bfsGlobals'
          defVars[name] = True
        elif operator == '+=':
          if isNumber(value): construct = f'scoreboard players add {name} bfsGlobals {value}'
          else:
            if defVars.get(value) == None: return f'{RED}At statement {IN+1}: var "{value}" is not defined.'
            if defVars.get(name) == None: return f'{RED}At statement {IN+1}: var "{name}" is not defined.'
            construct = f'scoreboard players operation {name} bfsGlobals += {value} bfsGlobals'
          defVars[name] = True
        elif operator == '-=':
          if isNumber(value): construct = f'scoreboard players remove {name} bfsGlobals {value}'
          else:
            if defVars.get(value) == None: return f'{RED}At statement {IN+1}: var "{value}" is not defined.'
            if defVars.get(name) == None: return f'{RED}At statement {IN+1}: var "{name}" is not defined.'
            construct = f'scoreboard players operation {name} bfsGlobals -= {value} bfsGlobals'
          defVars[name] = True
        elif operator == '/=':
          if isNumber(value): return f'{RED}At statement {IN+1}: Var to int division is not supported. Supported Usage Example: "var x /= y".'
          else:
            if defVars.get(value) == None: return f'{RED}At statement {IN+1}: var "{value}" is not defined.'
            if defVars.get(name) == None: return f'{RED}At statement {IN+1}: var "{name}" is not defined.'
            construct = f'scoreboard players operation {name} bfsGlobals /= {value} bfsGlobals'
          defVars[name] = True
        elif operator == '*=' or operator == 'x=':
          if isNumber(value): return f'{RED}At statement {IN+1}: Var to int multiplication is not supported. Supported Usage Example: "var x *= y" or "var x x= y".'
          else:
            if defVars.get(value) == None: return f'{RED}At statement {IN+1}: var "{value}" is not defined.'
            if defVars.get(name) == None: return f'{RED}At statement {IN+1}: var "{name}" is not defined.'
            construct = f'scoreboard players operation {name} bfsGlobals *= {value} bfsGlobals'
          defVars[name] = True
        elif operator == '?=':
          if isNumber(value) & isNumber(value2): construct = f'scoreboard players random {name} bfsGlobals {value} {value2}'
          else: return f'{RED}At statement {IN+1}: Variables cannot be used as parameters for random number generation.'
          defVars[name] = True
        else: return f'{RED}At statement {IN+1}: Operator "{operator}" does not exist.'
        modsToAdd = ''
        functionMod = configDetails['defaultFuncFile']
        for i in range(0,indent):
          if modCount < i+1: return f'{RED}At statement {IN+1}: Unexpected indent.'
          if mods[i].startswith('functionMod:'): functionMod = mods[i].split(':')[1]
          elif mods[i].startswith('loopFunctionMod:'): functionMod = mods[i].split(':')[1]
          else: modsToAdd = f'{modsToAdd}{mods[i]}'
        construct = f'{modsToAdd}{construct}'
        newLine(functionMod,construct)

      #Compile del statement
      elif Keyword == 'del':
        if lenSTP != 2: return f'{RED}At statement {IN+1}: "del" statement takes 1 parameter.'
        name = STP[1]
        if name['t'] != 'any': return f'{RED}At statement {IN+1}: "del" statement, parameter 1 can\'t be a string.'
        name = name['v']
        modsToAdd = ''
        functionMod = configDetails['defaultFuncFile']
        for i in range(0,indent):
          if modCount < i+1: return f'{RED}At statement {IN+1}: Unexpected indent.'
          if mods[i].startswith('functionMod:'): functionMod = mods[i].split(':')[1]
          elif mods[i].startswith('loopFunctionMod:'): functionMod = mods[i].split(':')[1]
          else: modsToAdd = f'{modsToAdd}{mods[i]}'
        construct = f'{modsToAdd}scoreboard players reset {name} bfsGlobals'
        newLine(functionMod,construct)
        del defVars[name]

      #Compile if statement
      elif Keyword == 'if':
        if lenSTP != 4: return f'{RED}At statement {IN+1}: "if" statement takes 4 parameters.'
        value1 = STP[1]
        operator = STP[2]
        value2 = STP[3]
        if value1['t'] != 'any': return f'{RED}At statement {IN+1}: "if" statement, parameter 1 can\'t be a string.'
        if operator['t'] != 'any': return f'{RED}At statement {IN+1}: "if" statement, parameter 2 can\'t be a string.'
        if value2['t'] != 'any': return f'{RED}At statement {IN+1}: "if" statement, parameter 3 can\'t be a string.'
        value1 = value1['v']
        operator = operator['v']
        value2 = value2['v']
        conditionMode = 'if'
        if operator.startswith('!'):
          operator = operator.replace('!','',1)
          conditionMode = 'unless'

        if operator == '==' or operator == '=' or operator == 'is':
          if isNumber(value2):
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            mods.append(f'execute if score {value1} bfsGlobals matches {value2} run ')
          elif isNumber(value1): return f'{RED}At statement {IN+1}: {lang.error.st.cond.diti}'
          else:
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            if defVars.get(value2) == None: return f'{RED}At statement {IN+1}: var "{value2}" is not defined.'
            mods.append(f'execute if score {value1} bfsGlobals = {value2} bfsGlobals run ')
        elif operator == '!=' or operator == 'isnt':
          if isNumber(value2):
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            mods.append(f'execute unless score {value1} bfsGlobals matches {value2} run ')
          elif isNumber(value1): return f'{RED}At statement {IN+1}: {lang.error.st.cond.diti}'
          else:
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            if defVars.get(value2) == None: return f'{RED}At statement {IN+1}: var "{value2}" is not defined.'
            mods.append(f'execute unless score {value1} bfsGlobals = {value2} bfsGlobals run ')
        elif operator == '>':
          if isNumber(value2):
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            return f'{RED}At statement {IN+1}: Comparing a var to an int using ">" is not supported. Use ">=" instead.'
          elif isNumber(value1): return f'{RED}At statement {IN+1}: {lang.error.st.cond.diti}'
          else:
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            if defVars.get(value2) == None: return f'{RED}At statement {IN+1}: var "{value2}" is not defined.'
            mods.append(f'execute {conditionMode} score {value1} bfsGlobals > {value2} bfsGlobals run ')
        elif operator == '>=':
          if isNumber(value2):
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            mods.append(f'execute {conditionMode} score {value1} bfsGlobals matches {value2}.. run ')
          elif isNumber(value1): return f'{RED}At statement {IN+1}: {lang.error.st.cond.diti}'
          else:
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            if defVars.get(value2) == None: return f'{RED}At statement {IN+1}: var "{value2}" is not defined.'
            mods.append(f'execute {conditionMode} score {value1} bfsGlobals >= {value2} bfsGlobals run ')
        elif operator == '<':
          if isNumber(value2):
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            return f'{RED}At statement {IN+1}: Comparing a var to an int using "<" is not supported. Use "<=" instead.'
          elif isNumber(value1): return f'{RED}At statement {IN+1}: {lang.error.st.cond.diti}'
          else:
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            if defVars.get(value2) == None: return f'{RED}At statement {IN+1}: var "{value2}" is not defined.'
            mods.append(f'execute {conditionMode} score {value1} bfsGlobals < {value2} bfsGlobals run ')
        elif operator == '<=':
          if isNumber(value2):
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            mods.append(f'execute {conditionMode} score {value1} bfsGlobals matches ..{value2} run ')
          elif isNumber(value1): return f'{RED}At statement {IN+1}: {lang.error.st.cond.diti}'
          else:
            if defVars.get(value1) == None: return f'{RED}At statement {IN+1}: var "{value1}" is not defined.'
            if defVars.get(value2) == None: return f'{RED}At statement {IN+1}: var "{value2}" is not defined.'
            mods.append(f'execute {conditionMode} score {value1} bfsGlobals <= {value2} bfsGlobals run ')
        else: return f'{RED}At statement {IN+1}: Operator "{operator}" does not exist.'

      #Compile loop statement
      elif Keyword == 'loop':
        if lenSTP != 2: return f'{RED}At statement {IN+1}: "loop" statement takes 1 parameter.'
        loopName = STP[1]
        if loopName['t'] != 'any': return f'{RED}At statement {IN+1}: "loop" statement, parameter 1 can\'t be a string.'
        loopName = loopName['v']

        if loopName in defFuncs: return f'{RED}At statement {IN+1}: Loop/Function name "{loopName}" already used.'
        modsToAdd = ''
        functionMod = configDetails['defaultFuncFile']
        for i in range(0,indent):
          if modCount < i+1: return f'{RED}At statement {IN+1}: Unexpected indent.'
          if mods[i].startswith('functionMod:'): functionMod = mods[i].split(':')[1]
          elif mods[i].startswith('loopFunctionMod:'): functionMod = mods[i].split(':')[1]
          else: modsToAdd = f'{modsToAdd}{mods[i]}'
        newLine(functionMod,f'{modsToAdd}scoreboard players set {loopName} bfsLoops 0')
        newLine(functionMod,f'{modsToAdd}function {loopName}')
        newLine(loopName,f'execute if score {loopName} bfsLoops matches 0 run function {loopName}',stickToEnd=True)
        mods.append(f'loopFunctionMod:{loopName}')
        defFuncs.append(loopName)

      #Compile break statement
      elif Keyword == 'break':
        loopName = None
        modsToAdd = ''
        functionMod = configDetails['defaultFuncFile']
        for i in range(0,indent):
          if modCount < i+1: return f'{RED}At statement {IN+1}: Unexpected indent.'
          if mods[i].startswith('functionMod:'):
            functionMod = mods[i].split(':')[1]
          elif mods[i].startswith('loopFunctionMod:'): loopName = mods[i].split(':')[1]
          else: modsToAdd = f'{modsToAdd}{mods[i]}'
        if loopName == None: return f'{RED}At statement {IN+1}: "break" statement cannot be used outside of a loop.'
        construct = f'{modsToAdd}scoreboard players set {loopName} bfsLoops 1'
        newLine(loopName,construct)

      #Compile reloop statement
      elif Keyword == 'reloop':
        if lenSTP != 2: return f'{RED}At statement {IN+1}: "reloop" statement takes 1 parameter.'
        name = STP[1]
        if name['t'] != 'any': return f'{RED}At statement {IN+1}: "reloop" statement, parameter 1 can\'t be a string.'
        name = name['v']
        modsToAdd = ''
        functionMod = configDetails['defaultFuncFile']
        for i in range(0,indent):
          if modCount < i+1: return f'{RED}At statement {IN+1}: Unexpected indent.'
          if mods[i].startswith('functionMod:'): functionMod = mods[i].split(':')[1]
          elif mods[i].startswith('loopFunctionMod:'): functionMod = mods[i].split(':')[1]
          else: modsToAdd = f'{modsToAdd}{mods[i]}'
        newLine(functionMod,f'{modsToAdd}scoreboard players set {name} bfsLoops 0')
        newLine(functionMod,f'{modsToAdd}function {name}')


      #Compile cmd statement
      elif Keyword == 'cmd':
        if lenSTP != 2: return f'{RED}At statement {IN+1}: "cmd" statement takes 1 parameter.'
        cmdText = STP[1]
        if cmdText['t'] != 'str': return f'{RED}At statement {IN+1}: "cmd" statement, parameter 1 must be a string.'
        cmdText = cmdText['v']
        modsToAdd = ''
        functionMod = configDetails['defaultFuncFile']
        for i in range(0,indent):
          if modCount < i+1: return f'{RED}At statement {IN+1}: Unexpected indent.'
          if mods[i].startswith('functionMod:'): functionMod = mods[i].split(':')[1]
          elif mods[i].startswith('loopFunctionMod:'): functionMod = mods[i].split(':')[1]
          else: modsToAdd = f'{modsToAdd}{mods[i]}'
        construct = f'{modsToAdd}{cmdText}'
        newLine(functionMod,construct)

      #Compile stm statement
      elif Keyword == 'stm':
        if lenSTP != 2: return f'{RED}At statement {IN+1}: "stm" statement takes 1 parameter.'
        modText = STP[1]
        if modText['t'] != 'str': return f'{RED}At statement {IN+1}: "stm" statement, parameter 1 must be a string.'
        modText = modText['v']
        modsToAdd = ''
        functionMod = configDetails['defaultFuncFile']
        for i in range(0,indent):
          if modCount < i+1: return f'{RED}At statement {IN+1}: Unexpected indent.'
          if mods[i].startswith('functionMod:'): functionMod = mods[i].split(':')[1]
          elif mods[i].startswith('loopFunctionMod:'): functionMod = mods[i].split(':')[1]
          else: modsToAdd = f'{modsToAdd}{mods[i]}'
        construct = f'{modsToAdd}execute {modText} run '
        mods.append(construct)

      #Compile func statement
      elif Keyword == 'func':
        if lenSTP != 2: return f'{RED}At statement {IN+1}: "func" statement takes 1 parameter.'
        name = STP[1]
        if name['t'] != 'any': return f'{RED}At statement {IN+1}: "func" statement, parameter 1 can\'t be string'
        name = name['v']
        if name in defFuncs: return f'{RED}At statement {IN+1}: Loop/Function name "{name}" already used.'
        mods.append(f'functionMod:{name}')
        defFuncs.append(name)

      else:
        if ST2.replace(' ','') != '': return f'{RED}At statement {IN+1}: Statement "{ST2}" is not recognized.'
      return None
    except: return f'{RED}At statement {IN+1}: Invalid syntax. {e}'
  result2 = comp()
  result = {'error':None,'meta':{'defVars':defVars,'defFuncs':defFuncs,'mods':mods}}
  if result2 != None and result2 != 'skip': result['error'] = result2
  return result


# ------------------------
# Actually Compile Scripts
# ------------------------
def compile():
  if configDetails['defaultBFScriptFile'] == '?': scriptPath = input(f'{BLUE}File to compile (Input Filepath): {RESET}')
  else: scriptPath = configDetails['defaultBFScriptFile']
  if scriptPath.endswith('.bfs') == False:
    print(f'{RED}"{scriptPath}" is not a BFScript file. Example: "main.bfscript".{RESET}')
    return
  if Path(scriptPath).exists() == False:
    print(f'{RED}"{scriptPath}" does not exist.')
    return
  print(f'{GREEN}Alright, I\'m compiling your script right now..{RESET}')
  startTime = time.time()
  rawscript = open(scriptPath).read()
  script = rawscript.split(';')
  meta = {'defVars':{},'defFuncs':[],'mods':[]}
  newLine(configDetails['defaultFuncFile'],f'scoreboard objectives add bfsGlobals dummy')
  # ST = Statement, IN = List index
  for IN,ST in enumerate(script):
    result = compileST(ST,IN,meta)
    if result == 'skip': continue
    if result['error'] != None:
      print(result['error'])
      break
    meta['defVars'] = result['meta']['defVars']
    meta['defFuncs'] = result['meta']['defFuncs']
    meta['mods'] = result['meta']['mods']
  for item in stickyLines:
    newLine(item[0],item[1])
  print(f'{MAGENTA}Finsihed in: {time.time()-startTime} seconds.{RESET}')
  print(f'{GREEN}All finished! You can find your function files in the "BFSC Generated" folder.')
compile()