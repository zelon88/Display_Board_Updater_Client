# --------------------------------------------------
# Display_Board_Updater_Client.py
# v2.5.5 - 2/12/2020

# Justin Grimes (@zelon88)
#   https://www.HonestRepair.net
# Made on Windows 7 with Python 2.7

# This program is for preparing & displaying PDF reports in fullscreen on unattended workstations. 
# For example, you can use this program to create an up-to-date dashboard that rotates slides automatically.

# --------------------------------------------------

# --------------------------------------------------
# VALID ARGUMENTS / PARAMETERS / SWITCHES
# If you combine multiple verbosity or log levels the last specified will be used.

#  h - Display help text. 1st argument.
#  help - Display help text. 1st argument.

#  <path to document folder> - 1st argument.

#  <time in seconds to display each document> - 2nd argument.

#  <time in seconds before old reports are deleted> - 3rd argument.

#  s - Split multi-page PDFs into separate files & display each file separately. 4th-7th argument.
#  split - Split multi-page PDFs into separate files & display each file separately. 4th-7th argument.

#  v0 - Verbosity 0. Optional. Disable output. 4th-7th argument.
#  v1 - Verbosity 1. Optional. Only errors are output. 4th-7th argument.
#  v2 - Verbosity 2. Optional. Everything is output. 4th-7th argument.

#  l0 - Log level 0. Optional. Disable logging. 4th-7th argument.
#  l1 - Log level 1. Optional. Only errors logged. 4th-7th argument.
#  l2 - Log level 2. Optional. Everything is logged. 4th-7th argument.
# --------------------------------------------------

# --------------------------------------------------
# EXAMPLE COMMANDS

# Display help text.
#     Display_Board_Updater_Client.py h

# Prepare the documents in C:\Path-To-Files and display each one for 12s. Delete old reports after 1 hour. 
# Full logging & console output.
#     Display_Board_Updater_Client.py "C:\Path-To-Files" 12 3600 v2 l2

# Prepare the documents in C:\Path-To-Files and display each one for 30s. Delete old reports after 2 hours. 
# Split multiple pages into files. No logging or console output.
#     Display_Board_Updater_Client.py "C:\Path-To-Files" 30 7200 s v0 l0
# --------------------------------------------------

# --------------------------------------------------
# Load required modules and set global variables.
import sys, getopt, time, datetime, os, shutil, errno, struct, ctypes

# -----DEFAULT CONFIGURATION SETTINGS----- # 
# The filename of this application.
progFileName = "Display_Board_Updater_Client.py"
# The full name of this application.
progName = "Display_Board_Updater_Client"
# The current version of this application.
progVers = "v2.5.5"
# A concise description of this application.
progDesc = 'This program prepares the data created by Display_Board_Updater_Server and displays it in full screen for shop floor dashboards.'
# The following value controls the characters to use for padding before writing console output.
# If centerConsoleOutput is set to true, this would probably look best if left as a blank string.
# Mainly useful for getting the start of console output away from the side of the screen. Otherwise in fullscreen it's very close.
consolePadding = ''
# Prefix standard log entries with the following string.
logPrefix = consolePadding+'OP-Act: '
# In the absence of the "s" argument, the following default value will be used to enable/disable splitting pages into files.
autoSplit = False
# The following boolean value will enable or disable output from dependencies such as Adobe Reader DC & taskkill.exe.
silenceDependencyOutput = True
# In the absence of a "refresh time" argument, the following default value will be used for display duration.
refreshTime = 60
# In the absence of a "logging" argument, the following default value defines the log level that will be used.
logging = 1
# In the absence of a "verbosity" argument, the following default value defines the verbosity level that will be used.
verbosity = 2
# A short delay in seconds to wait between the start of this program and the first scan on the target.
startupDelay = 10
# In the absence of an "expiration time", the following default value defines the number of seconds to store reports before deleting them.
expirationDuration = float(time.time()) - (60 * 60)  # 60sec x 60min = 1hour
# The following integer determines an upper boundary for the main loop of this program.
# If defined, the main loop of this program will execute this many times before stopping.
# Set to 0 to enable non-stop execution.
executionLimit = 0
# The wait time is the number of seconds to wait for file locks and other time sensitive operations.
# If you encounter errors with file locks, starting, or killing processes try increasing this value.
waitTime = 2
# The following boolean controls whether or not console output is centered in the command prompt window.
# Due to unconrollable circumstances in the pyinstaller module, this feature does not work in compiled .exe versions.
# If you compile this program to an executable and set the centerConsoleOutput varialble to True, no changes will take effect.
# This application can detect when the detected width & height of a console window is incorrect. 
# This application will ignore the following configuration entry when needed to avoid an unrecoverable error.
centerConsoleOutput = True
# The following equation should equal the number of seconds after start of program execution before the logo is redisplayed.
# Set to 0 to never redisplay the logo. 
logoRedisplayTimeLimit = 60 * 10 # 60sec x 10min = 10min 
# The installation directory where this application is installed.
# This configuration entry shold be considered a "hard-coded" installation path.
# This is the preferred method of defining the installation path for this application.
currentPath = "C:\Display_Board_Updater_Client"
# The installation directory where this application is installed.
# It's best to hard-code paths with the configuration entry below.
# If you need to specify this configuration entry uncomment, de-space, and populate the line below with the path. 
# Uncommenting and de-spacing (removing the 2 whicespace characters from) the line below will make this application detect the path
 # that is is installed into and use that instead of the currentPath specified above. 
# If this configuration entry is uncommented and de-spaced the configuration entry above will be overwritten and no longer apply.
  #currentPath = os.path.dirname(__file__)
# The Adobe path is a string with escaped directory separators that resolves to the AcroRd32.exe executable for Adobe Acrobat Reader DC.
# This path needs to have extra escaped directory separators because it is used directly in a command which is executed.
adobePath = '"C:\\Program Files (x86)\\Adobe\\Acrobat Reader DC\\Reader\\AcroRd32.exe"'
# The following string must be a valid absolute path to a place where this application can create & append to a log file.
logFile = os.path.join(currentPath, 'Display_Board_Updater_Client.log')
# -----END DEFAULT CONFIGURATION SETTINGS----- # 

# Set default variables for the session.
logoRedisplayTimer = float(time.time()) + float(logoRedisplayTimeLimit)
error = inputFile = inputPath = preparedDir = pageDir = ''
errorCounter = loopCounter = actionCounter = 0
# --------------------------------------------------

# --------------------------------------------------
# A function to set the time. Call this function at the start of each main loop iteration.
# Returns the current date and time in a human readable format. Perfect for logs & console output.
def setTime():
  # Get the time in seconds, machine time.
  now = datetime.datetime.now()
  # Turn the machine time into human-readable time.
  realtime = now.strftime("%B %d, %Y, %H:%M")
  return realtime
# --------------------------------------------------

# --------------------------------------------------
# A function to print output to the console in a consistent manner.
# Always returns 1.
def printGracefully(logPrefix, message, realtime, centerConsoleOutput):
  # Detect if the centerConsoleOutput configuration variable is set.
  if centerConsoleOutput == True: 
    # Call the getTermSize() function to detect the console width in number of characters.
    termWidth, termHeight, centerConsoleOutput = getTermSize(centerConsoleOutput)
    # Print console output in the center of the console window.
    print (consolePadding+logPrefix+message+' on '+str(realtime)+'.'+"\n").center(termWidth)
  # If centerConsoleOutput is False print the output at the start of the console window.
  else: print (consolePadding+logPrefix+message+' on '+str(realtime)+'.'+"\n")
  return 1
# --------------------------------------------------

# --------------------------------------------------
# A function to kill the program gracefully during unrecoverable error.
# The errorMessage will be displayed to the user in the console.
# Note this uses sys.exit(), which not only kills this script but the entire interpreter.
# Should never return anything because the interpreter should be dead before the return line.
def dieGracefully(errorMessage, errorNumber, errorCounter, realtime, centerConsoleOutput):
  # Detect if the centerConsoleOutput configuration variable is set.
  if centerConsoleOutput == True:
    # Call the getTermSize() function to detect the console width in number of characters.
    termWidth, termHeight, centerConsoleOutput = getTermSize(centerConsoleOutput)
    # Print console output in the center of the console window.
    print (consolePadding+'ERROR-'+str(errorCounter)+'!!! '+str(progName)+str(errorNumber)+': '+str(errorMessage)+' on '+str(realtime)+'!'+"\n").center(termWidth)
  # If centerConsoleOutput is False print the output at the start of the console window.
  else: print (consolePadding+'ERROR-'+str(errorCounter)+'!!! '+str(progName)+str(errorNumber)+': '+str(errorMessage)+' on '+str(realtime)+'!'+"\n")
  # Kill the interpreter that is interpreting this program, thus killing this program.
  sys.exit()
  return 1
# --------------------------------------------------

# --------------------------------------------------
# A function to write an entry to the logFile. 
# Do not punctuate your log entries with punctuation, or it will look strange.
# Set the errorNumber to 0 for regular prefix (default is "OP-Act").
# If the entry is an error message, set errorNumber to an int greater than 0.
# Always returns 1.
def writeLog(logPrefix, logFile, logEntry, realtime, errorNumber, errorCounter):
  # If a logFile already exists, set the file mode to append.
  if os.path.isfile(logFile): append = "ab"
  # If the logFile does not already exist, set the file mode to force create.
  else: append = "wb+"
  # If the errorNumber is greater than 1, set an ERROR prefix with the number of errors and the specific error number.
  if errorNumber > 0: entryPrefix = 'ERROR-'+str(errorCounter)+'!!! '+str(progName)+str(errorNumber)+': '
  # If the errorNumber is 0, set the prefix for this log entry to whatever the logPrefix configuration entry is.
  else:  entryPrefix = logPrefix
  entrySufix = ' on '+str(realtime)+'.'
  # Open the logFile in the defined file mode and write the specified data to it.
  with open(logFile, append) as logData:
    logData.write(entryPrefix+logEntry+entrySufix+"\n")
    logData.close
  # Clear unneeded memory.
  logEntry = logData = ''
  return 1
# --------------------------------------------------

# --------------------------------------------------
# A function to process user supplied arguments/parameters/switches.
# Returns populated variables: autoSplit, logging, verbosity, inputFile, inputPath, refreshTime, preparedDir, pageDir, expirationDuration
def parseArgs(logPrefix, logging, verbosity, argv, errorCounter, realtime, centerConsoleOutput):
  autoSplit = False
  # Check if any arguments were passed.
  try: opts, args = getopt.getopt(argv,"h")
  # If no arguments were passed, inform the user about the "help" argument.
  if len(sys.argv) <= 1:
    print ('\nType "'+str(progFileName)+' help" to display '+str(progName)+' usage & version information.\n')
    # Kill the interpreter. 
    sys.exit(2)
  # Print the help text if the "h" argument is passed.
  if sys.argv[1] == 'h' or sys.argv[1] == 'help':
    print ('\n'+str(progName)+' '+str(progVers)+', by Justin Grimes (@zelon88) - https://www.HonestRepair.net\n')
    print ('\n'+str(progDesc)+'\n\n'+str(progFileName)+' <path to folder> <time in seconds to display each report> <time in seconds before old reports are deleted> <options>\n')
    print (' Options: ')
    print ('----------')
    print ('  h = Display Help & Version Information')
    print ('  help = Display Help & Version Information')
    print ('----------')
    print ('  s = Split pages into separate files')
    print ('  split = Split pages into separate files')
    print (' ---------')
    print ('  v0 = Display No Messages')
    print ('  v1 = Display Warning Messages Only') 
    print ('  v2 = Display All Messages')
    print (' ---------')
    print ('  l0 = Record No Logs')
    print ('  l1 = Record Warning Logs Only') 
    print ('  l2 = Record All Logs')
    # Kill the interpreter.
    sys.exit(2)
  if len(sys.argv) > 4:
    # Set the logging level from argument 4.
    if sys.argv[4] == 'l0': logging = 0
    if sys.argv[4] == 'l1': logging = 1
    if sys.argv[4] == 'l2': logging = 2
    # Set the verbosity level from argument 4.
    if sys.argv[4] == 'v0': verbosity = 0
    if sys.argv[4] == 'v1': verbosity = 1
    if sys.argv[4] == 'v2': verbosity = 2
    # Set autoSplit overwrite from argument 4.
    if sys.argv[4] == 's' or 'split' in sys.argv[4]: autoSplit = True
  if len(sys.argv) > 5:
    # Set the logging level from argument 5.
    if sys.argv[5] == 'l0': logging = 0
    if sys.argv[5] == 'l1': logging = 1
    if sys.argv[5] == 'l2': logging = 2
    # Set the verbosity level from argument 5.
    if sys.argv[5] == 'v0': verbosity = 0
    if sys.argv[5] == 'v1': verbosity = 1
    if sys.argv[5] == 'v2': verbosity = 2
    # Set autoSplit overwrite from argument 5.
    if sys.argv[5] == 's' or 'split' in sys.argv[5]: autoSplit = True
  if len(sys.argv) > 6:
    # Set the logging level from argument 6.
    if sys.argv[6] == 'l0': logging = 0
    if sys.argv[6] == 'l1': logging = 1
    if sys.argv[6] == 'l2': logging = 2
    # Set the verbosity level from argument 6.
    if sys.argv[6] == 'v0': verbosity = 0
    if sys.argv[6] == 'v1': verbosity = 1
    if sys.argv[6] == 'v2': verbosity = 2
    # Set autoSplit overwrite from argument 6.
    if sys.argv[6] == 's' or 'split' in sys.argv[6]: autoSplit = True
  # Check to see if a folder path was supplied.
  try: sys.argv[1]
  except IndexError:
    errorCounter += 1
    message = 'No folder path was specified'
    if logging > 0: writeLog(logPrefix, logFile, message, realtime, 1, errorCounter)
    if verbosity > 0: dieGracefully(message, 1, errorCounter, realtime, centerConsoleOutput)
    else: sys.exit()
  # Check to see if an output delimeter was supplied.
  try: sys.argv[2]
  except IndexError:
    errorCounter += 1
    message = 'No refresh time was specified'
    if logging > 0: writeLog(logPrefix, logFile, message, realtime, 2, errorCounter)
    if verbosity > 0: dieGracefully(message, 2, errorCounter, realtime, centerConsoleOutput)
    else: sys.exit()
  # Check to see if an output delimeter was supplied.
  try: sys.argv[3]
  except IndexError:
    errorCounter += 1
    message = 'No expiration time was specified'
    if logging > 0: writeLog(logPrefix, logFile, message, realtime, 3, errorCounter)
    if verbosity > 0: dieGracefully(message, 3, errorCounter, realtime, centerConsoleOutput)
    else: sys.exit()
  else: 
    # Define the first argument & set associated file & directory variables.
    inputFile = sys.argv[1]
    inputPath = inputFile
    preparedDir = os.path.join(inputPath, "Prepared")
    pageDir = os.path.join(preparedDir, "Pages")
    # Define the second argument & set associated time related variables.
    refreshTime = int(sys.argv[2])
    expirationDuration = float(time.time()) - float(sys.argv[3])
    # Check to see that required directories exist & create them where required.
    if not os.path.exists(inputPath):
      # "ERROR-<#>!!! Display_Board_Updater_Client109, The output file specified relies on an invalid directory on <time>."
      errorCounter += 1
      message = 'The folder path specified relies on an invalid directory'
      if logging > 0: writeLog(logPrefix, logFile, message, realtime, 4, errorCounter)
      if verbosity > 0: dieGracefully(message, 4, errorCounter, realtime, centerConsoleOutput)
      # Kill the interpreter.
      else: sys.exit()
  # Clear unneeded memory.
  message = ''
  return autoSplit, logging, verbosity, inputFile, inputPath, refreshTime, preparedDir, pageDir, expirationDuration
# --------------------------------------------------

# --------------------------------------------------
# A function to verify that required directories exist and create them when needed.
# Returns 0 on error. Returns 1 if all files exist.
def verifyDirs(logPrefix, inputPath, preparedDir, pageDir, realtime, centerConsoleOutput):
  # Check for the existence of the inputPath.
  if not os.path.exists(inputPath): 
    message = 'Creating '+str(inputPath)
    if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
    if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
    os.mkdir(inputPath)\
  # Check for the existence of the preparedDir.
  if not os.path.exists(preparedDir):
    message = 'Creating '+str(preparedDir)
    if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
    if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
    os.mkdir(preparedDir)
  # Check for the existence of the pageDir.
  if not os.path.exists(pageDir):
    message = 'Creating '+str(pageDir)
    if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
    if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
    os.mkdir(pageDir)
    # Clear unneeded memory.
  message = ''
  # Double-check that the files searched for earlier were created by this function.
  # If this check fails, the entire function fails and returns 0.
  # Looks for the existence of inputPath, preparedDir, & pageDir. These should have been created above.
  if not os.path.exists(inputPath) or not os.path.exists(preparedDir) or not os.path.exists(pageDir):
    return 0
  else: return 1
# --------------------------------------------------

# --------------------------------------------------
# A function to scan the specified input folder. 
# Returns a list of files contained in the specified folder.
def scanFolder(logPrefix, scanPath, realtime, centerConsoleOutput):
  message = 'Scanning '+str(scanPath)+' for file objects'
  if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
  if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
  # Use the os module to scan the supplied directory.
  return os.listdir(scanPath)
# --------------------------------------------------

# --------------------------------------------------
# A function to detect when an input file is locked and pause until it becomes available.
# Does not return until the input file is unlocked and ready.
def waitForLockedFile(logPrefix, testFile, realtime, centerConsoleOutput):
  # Reset the current time.
  realTime = setTime()
  # Attempt to open the specified file.
  try:
    with open(testFile, 'r') as f: pass
  # Catch the result of the above operation.
  except IOError as x:
    # Check if any errors were caught during the file operation above.
    if x.errno == errno.EACCES:
      message = 'File '+str(testFile)+' is locked. Waiting'
      if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
      if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
      # If errirs were encountered trying to open the specified file, sleep for waitTime duration.
      time.sleep(float(waitTime))
      # Reset current time & re-exdcute this function.
      realtime = waitForLockedFile(logPrefix, testFile, realtime, centerConsoleOutput)
    # Clear un-needed memory.
    testFile = message = f = x = ''
  return realtime
# --------------------------------------------------

# --------------------------------------------------
# A function to prepare the raw reports found in the inputPath.
# This function will execute pdfsplit on the inputPath and store individual pages in the pageDir.
# Pages are then copied to the preparedDir when ready and deleted from PageDir.
# Always returns 1.
def prepareReports(logPrefix, currentPath, inputPath, preparedDir, pageDir, expirationDuration, realtime, centerConsoleOutput):
  os.chdir(inputPath)
  pdfSplitPath = os.path.join(currentPath, 'pdfsplit.py')
  inputFiles = scanFolder(logPrefix, inputPath, realtime, centerConsoleOutput)
  for iFile in inputFiles:
    if ".pdf" in iFile:
      pageNumber = commandResult = 0
      while commandResult == 0:
        pageNumber += 1
        iFilePath = os.path.join(inputPath, iFile)
        oFilePath = os.path.join(pageDir, iFile)+'page-'+str(pageNumber)    
        commandResult = os.system(pdfSplitPath+' '+iFilePath+' '+oFilePath+' '+str(pageNumber))
  pageFiles = scanFolder(logPrefix, pageDir, realtime, centerConsoleOutput)
  for pFile in pageFiles:
    pFilePath = os.path.join(pageDir, pFile)
    prepFilePath = os.path.join(preparedDir, pFile)
    if os.path.exists(prepFilePath):
        message = 'Deleting '+str(prepFilePath)
        if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
        if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
        realtime = waitForLockedFile(logPrefix, prepFilePath, realtime, centerConsoleOutput)
        os.remove(prepFilePath)
        time.sleep(float(waitTime))
    message = 'Copying '+str(pFilePath)+' to '+str(prepFilePath)
    if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
    if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
    realtime = waitForLockedFile(logPrefix, prepFilePath, realtime, centerConsoleOutput)
    shutil.copyfile(pFilePath, prepFilePath)
    if os.path.getmtime(os.path.join(pageDir, pFile)) < expirationDuration:
      message = 'Deleting '+str(os.path.join(pageDir, pFile))
      if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
      if verbosity > 1: printGracefully(logPrefix, message, realtime)
      realtime = waitForLockedFile(logPrefix, os.path.join(pageDir, pFile), realtime, centerConsoleOutput)
      os.remove(os.path.join(pageDir, pFile))
  for iFile2 in inputFiles:
    if ".pdf" in iFile2:
      inputFilePath = os.path.join(inputPath, iFile2)
      if os.path.getmtime(inputFilePath) < expirationDuration:
        message = 'Deleting '+str(inputFilePath)
        if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
        if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
        realtime = waitForLockedFile(logPrefix, inputFilePath, realtime, centerConsoleOutput)
        os.remove(inputFilePath)
  pageNumber = pdfSplitPath = commandResult = inputFiles = pageFiles = iFilePath = oFilePath = iFile = pFilePath = pFile = prepFilePath = inputFilePath = iFile2 = message = ''
  return realtime
# --------------------------------------------------

# --------------------------------------------------
# A function to copy the raw reports found in the inputPath.
# This function will simply copy the files found at the inputPath to the preparedDir.
# Originals are deleted from the inputDir. This way file locks don't interfre with new report generation.
# Always returns 1.
def copyReports(inputPath, preparedDir, realtime, centerConsoleOutput):
  os.chdir(inputPath)
  inputFiles = scanFolder(logPrefix, inputPath, realtime, centerConsoleOutput)
  for iFile in inputFiles:
    realtime = setTime()
    if ".pdf" in iFile:
      iFilePath = os.path.join(inputPath, iFile)
      prepFilePath = os.path.join(preparedDir, iFile)
      if os.path.exists(prepFilePath):
        message = 'Deleting '+str(prepFilePath)
        if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
        if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
        realtime = waitForLockedFile(logPrefix, prepFilePath, realtime, centerConsoleOutput)
        os.remove(prepFilePath)
        time.sleep(float(waitTime))
      message = 'Copying '+str(os.path.join(inputPath, iFile))+' to '+str(os.path.join(preparedDir, iFile))
      if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
      if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
      realtime = waitForLockedFile(logPrefix, prepFilePath, realtime, centerConsoleOutput)
      shutil.copyfile(iFilePath, prepFilePath)
      message = 'Deleting '+str(os.path.join(inputPath, iFile))
      if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
      if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
      realtime = waitForLockedFile(logPrefix, os.path.join(inputPath, iFile), realtime, centerConsoleOutput)
      os.remove(os.path.join(inputPath, iFile))
  inputFiles = iFilePath = iFile = pFilePath = prepFilePath = message = ''
  return realtime
# --------------------------------------------------

# --------------------------------------------------
# Display a prepared report for the desired duration.
# Uses Adobe Acrobat Reader DC to display PDF's in fullscreen mode.
# Kill Adobe Acrobat once the report has been displayed for refreshTime number of seconds.
# Once the report is done being displayed it is deleted so it cannot be displayed again.
# Always returns 1.
def displayReport(logPrefix, displayDir, realtime, centerConsoleOutput):
  displayFiles = scanFolder(logPrefix, displayDir, realtime, centerConsoleOutput)
  verbOutput = " >nul 2>&1"
  if verbosity > 1 and silenceDependencyOutput == False: verbOutput = ''
  for displayFile in displayFiles:
    realtime = setTime()
    displayFilePath = os.path.join(displayDir, displayFile)
    if ".pdf" in displayFilePath: 
      realtime = waitForLockedFile(logPrefix, displayFilePath, realtime, centerConsoleOutput)
      message = 'Opening '+str(displayFilePath)
      if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
      if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
      os.chdir(currentPath)
      displayCommandResult = os.system('start "" /max '+adobePath+' /A "pagemode=FullScreen" "'+displayFilePath+'"'+verbOutput)
      time.sleep(float(refreshTime))
      message = 'Closing '+str(displayFilePath)
      if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
      if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
      os.system("taskkill /im AcroRd32.exe"+verbOutput)
      time.sleep(float(waitTime*2))
      realtime = waitForLockedFile(logPrefix, displayFilePath, realtime, centerConsoleOutput)
      if os.path.getmtime(displayFilePath) < expirationDuration:
        message = 'Deleting '+str(displayFilePath)
        if logging > 1: writeLog(logPrefix, logFile, message, realtime, 0, 0)
        if verbosity > 1: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
        realtime = waitForLockedFile(logPrefix, displayFilePath, realtime, centerConsoleOutput)
        os.remove(displayFilePath)
  displayFiles = verbOutput = displayFilePath = message = displaycommandResult = ''
  return realtime
# --------------------------------------------------

# --------------------------------------------------
# A function to display some text to kick things off.
# Known as the welcome message.
# Always returns 1.
def printWelcome(logPrefix, logging, verbosity, realtime, centerConsoleOutput):
  print ('\n')
  message = 'Starting '+str(progName)
  if logging > 0: writeLog(logPrefix, logFile, message, realtime, 0, 0)
  if verbosity > 0: printGracefully(logPrefix, message, realtime, centerConsoleOutput)
  message = ''
  return 1
# --------------------------------------------------

# --------------------------------------------------
# A function to display some text to round things out.
# Known as the goodbye message.
# Always returns 1.
def printGoodbye(logPrefix, logging, verbosity, realtime, centerConsoleOutput):
  message = 'Operation complete'
  if logging > 0: writeLog(logPrefix, logFile, message, realtime, 0, 0)
  if verbosity > 0:
    printGracefully(logPrefix, '', message, realtime, centerConsoleOutput)
    print("\n")
  message = ''
  return 1
# --------------------------------------------------


# --------------------------------------------------
# A function to get the current buffer size of a Windows Command Prompt window.
# Used later to center text in the console window.
def getTermSize(centerConsoleOutput):
  h = ctypes.windll.kernel32.GetStdHandle(-12)
  csbi = ctypes.create_string_buffer(22)
  k32 = ctypes.windll.LoadLibrary('C:\Windows\System32\kernel32.dll')
  res = k32.GetConsoleScreenBufferInfo(h, csbi)
  bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy = struct.unpack("hhhhHhhhhhh", csbi.raw)
  sizex = right - left + 1
  sizey = bottom - top + 1
  if sizex < 3 or sizex < 3: centerConsoleOutput = False
  return sizex, sizey, centerConsoleOutput
# --------------------------------------------------

# --------------------------------------------------
# A function to print a fancy Truform logo in between iterations.
def printLogo(verbosity, centerConsoleOutput):
  if verbosity > 0:
    os.system("cls")
    if centerConsoleOutput == True:
      print ('  ___________ _   _______ ______________  ___').center(termWidth)
      print (' |_   _| ___ \ | | |  ___|  _  | ___ \  \/  |').center(termWidth)
      print ('   | | | |_/ / | | | |_  | | | | |_/ / .  . |').center(termWidth)
      print ('   | | |    /| | | |  _| | | | |    /| |\/| |').center(termWidth)
      print ('   | | | |\ \| |_| | |   \ \_/ / |\ \| |  | |').center(termWidth)
      print ('   \_/ \_| \_|\___/\_|    \___/\_| \_\_|  |_/').center(termWidth)
      print ('  _____  ___________ _____ _    _  ___  ______ _____ ').center(termWidth)
      print (' /  ___||  _  |  ___|_   _| |  | |/ _ \ | ___ \  ___|').center(termWidth)
      print (' \ `--. | | | | |_    | | | |  | / /_\ \| |_/ / |__  ').center(termWidth)
      print ('  `--. \| | | |  _|   | | | |/\| |  _  ||    /|  __| ').center(termWidth)
      print (' /\__/ /\ \_/ / |     | | \  /\  / | | || |\ \| |___ ').center(termWidth)
      print (' \____/  \___/\_|     \_/  \/  \/\_| |_/\_| \_\____/ ').center(termWidth)
      print ('-------- '+progName+' | '+progVers+' --------').center(termWidth)
    else:
      print ('     ___________ _   _______ ______________  ___')
      print ('    |_   _| ___ \ | | |  ___|  _  | ___ \  \/  |')
      print ('      | | | |_/ / | | | |_  | | | | |_/ / .  . |')
      print ('      | | |    /| | | |  _| | | | |    /| |\/| |')
      print ('      | | | |\ \| |_| | |   \ \_/ / |\ \| |  | |')
      print ('      \_/ \_| \_|\___/\_|    \___/\_| \_\_|  |_/')
      print ('  _____  ___________ _____ _    _  ___  ______ _____ ')
      print (' /  ___||  _  |  ___|_   _| |  | |/ _ \ | ___ \  ___|')
      print (' \ `--. | | | | |_    | | | |  | / /_\ \| |_/ / |__  ')
      print ('  `--. \| | | |  _|   | | | |/\| |  _  ||    /|  __| ')
      print (' /\__/ /\ \_/ / |     | | \  /\  / | | || |\ \| |___ ')
      print (' \____/  \___/\_|     \_/  \/  \/\_| |_/\_| \_\____/ ')
      print ('-------- '+progName+' | '+progVers+' --------')
    print ('\n')
    return 1
# --------------------------------------------------

# --------------------------------------------------
# The main portion of the program which makes use of the functions above.
realtime = setTime()
termWidth, termHeight, centerConsoleOutput = getTermSize(centerConsoleOutput)
autoSplit, logging, verbosity, inputFile, inputPath, refreshTime, preparedDir, pageDir, expirationDuration = parseArgs(logPrefix, logging, verbosity, sys.argv[1:], errorCounter, realtime, centerConsoleOutput) 
printLogo(verbosity, centerConsoleOutput)
printWelcome(logPrefix, logging, verbosity, realtime, centerConsoleOutput)

time.sleep(float(startupDelay))

while loopCounter <= executionLimit or executionLimit == 0:
  realtime = setTime()
  termWidth, termHeight, centerConsoleOutput = getTermSize(centerConsoleOutput)
  if float(time.time()) >= logoRedisplayTimer and logoRedisplayTimeLimit > 0 and verbosity > 0:
    logoRedisplayTimer = float(time.time()) + float(logoRedisplayTimeLimit)
    printLogo(verbosity, centerConsoleOutput)
  loopCounter += 1
  if verifyDirs(logPrefix, inputPath, preparedDir, pageDir, realtime, centerConsoleOutput) > 0:
    if autoSplit == True:
      realtime = prepareReports(logPrefix, currentPath, inputPath, preparedDir, pageDir, expirationDuration, realtime, centerConsoleOutput)
      realtime = displayReport(logPrefix, preparedDir, realtime, centerConsoleOutput)     
    else:
      realtime = copyReports(logPrefix, inputPath, preparedDir, realtime, centerConsoleOutput)
      realtime = displayReport(logPrefix, preparedDir, realtime, centerConsoleOutput)
  else:
      message = 'Could not verify required directories'
      if logging > 0: writeLog(logPrefix, logFile, message, realtime, 5, errorCounter)
      if verbosity > 0: dieGracefully(message, 5, errorCounter, realtime, centerConsoleOutput)
      else: sys.exit()

printGoodbye(logPrefix, logging, verbosity, realtime, centerConsoleOutput)
# --------------------------------------------------