# File: Assembler.py
# Author: Kelsey Jackson
# Date: 11/4/2021
# Section: 506 
# E-mail: jackson.kel1019@tamu.edu 
# Description: This file implements the Assembler
import os

# take input for file name and error check
nameInput = input()
fileName, fileExten = os.path.splitext(nameInput) # grab file extension for file checking

# if file is not .asm, prompt new input
while fileExten != ".asm":
    print("Error, file is not a .asm.") # output error
    nameInput = input("Enter the name of the file: ") # ask for new file
    print() # newline for formatting
    fileName, fileExten = os.path.splitext(nameInput) # grab file extension for file checking
    
# after confirming file, open file
asmFile = open(nameInput, 'r')

# Creating new lists and line number variable for asm code
asmStrings = [] # lines of code for later processing
asmSections = [] # names of sections since separate from normal registers
sectionVals = [] # values of defined sections
lineNum = 0 # line number incrementer for section values

# load code into asm code list
for line in asmFile:
    
    # check if line is/has a comment
    comment = line.find('//')
    
    # if comment exists, check whether comment is whole line or at end of line
    if comment != -1 and comment != 0:
        line = line[:comment] # remove comment from command
        comment = -1 # reset comment for next if statement
        
    # if line is not whitespace or comment, add to asm code list
    if line != "\n" and comment == -1:
        currLine = line.strip() # remove ending whitespace
        
        section = currLine.find('(')
        
        # if line is start of section, update asmSections and sectionVals lists
        if section != -1:
            
            # removes parentheses from section name
            currLine = currLine[1:len(currLine)-1]
            
            # check if section exists and add value
            
            # default section to not found
            foundSect = False
            
            # check whether section exists
            for sectCheck in range(len(asmSections)):
                
                # if exists, set bool to "true" and break
                if currLine == asmSections[sectCheck]:
                    foundSect = True # section was found from predefined
                    break;
                    
            # if not found, create new space
            if foundSect == False:
                asmSections += [currLine] # add name of section
                sectionVals += [lineNum] # add line number as value
            
        else:
            asmStrings += [currLine] # add code to list
            lineNum += 1 # increment line number for section values

# no longer need file, so close
asmFile.close()

# open to file to write to
newHack = fileName + ".hack" # use file name from before to create hack file
hackFile = open(newHack, 'w') # open file to write into

# set area for defined symbols and values
reservedRegNames = ["R0","R1","R2","R3","R4","R5","R6","R7","R8","R9","R10","R11","R12","R13","R14","R15","SCREEN","KBD","SP","LCL","ARG","THIS","THAT"]
reservedRegValues = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16384,24576,0,1,2,3,4]

# set area for custom symbols and values
customRegNames = []
customRegValues = []

# placeholder for displacement when adding new symbols
regVal = 0

# begin processing asm code
for asmIndex in range(len(asmStrings)):
    
    # create new binary output and load command from asm list
    binaryOutput = ""
    command = asmStrings[asmIndex]
    
    # check whether A- or C- instruction
    findAtSym = command.find('@')
    findParen = command.find('(')
    
    # if A instruction, either "create" new register or open old one
    if findAtSym != -1 or findParen != -1:
        
        # grab register name
        if findAtSym != -1:
            regNum = command[1:] # remove @ symbol
            
            # if register is not just a number, figure out register number
            if not(regNum.isdigit()):
                
                # default to not found
                foundReg = False
                
                # check whether predefined register exists
                for regCheck1 in range(len(reservedRegNames)):
                    
                    # if predefined, set regNum to value, set bool to "true", and break
                    if regNum == reservedRegNames[regCheck1]:
                        regNum = reservedRegValues[regCheck1]
                        foundReg = True
                        break;
                
                # check if custom register
                for regCheck2 in range(len(customRegNames)):
                    
                    # if custom, set regNum to value, set bool to "true", and break
                    if regNum == customRegNames[regCheck2]:
                        regNum = customRegValues[regCheck2]
                        foundReg = True
                        break;
                        
                # if not found, check sections then create new space if not found
                if foundReg == False:
    
                    # default to not found
                    foundSect = False
                    
                    # check whether section exists
                    for sectCheck in range(len(asmSections)):
                        
                        # if exists, set regNum to value, set bool to "true", and break
                        if regNum == asmSections[sectCheck]:
                            regNum = sectionVals[sectCheck]
                            foundSect = True
                            break;
                            
                    # if not found, create new space
                    if foundSect == False:
                        customRegNames += [regNum] # add name to custom registers
                        regNum = regVal + 16 # add 16 to displacement value
                        customRegValues += [regNum] # add value to custom registers
                        regVal += 1 # increment displacement for next new register
        
        # grab section name if not register
        elif findParen != -1:
            regNum = command[1:len(command)-1] # remove parentheses
            
            # find section in list from asmSections and break
            for regCheck in range(len(asmSections)):
                
                # when found, set regNum to value
                if regNum == asmSections[regCheck]:
                    regNum = sectionVals[regCheck]
                    break;            
            
        # create default binary output and edit as needed
        defaultBinary = list("0000000000000000")
        
        # edit default binary output based on register number
        regIndex = 15 # only 15/16 bits can be altered for register address
        regValue = int(regNum) # make sure regNum is an int for calculations
        
        # while index is greater than 0, continue dividing
        # go backwards when adding remainders to output so output is correct binary
        while regIndex > 0:
            defaultBinary[regIndex] = str(regValue % 2) # add remainder of modulo to binary output
            regValue = regValue // 2 # floor division by 2
            regIndex -= 1 # reduce index value
            
        # copy output from previous loop in reverse order
        for index in range(len(defaultBinary)):
            binaryOutput += str(defaultBinary[index])
            
        # write output to file with newline
        hackFile.write(binaryOutput)
        hackFile.write("\n")
        
    # if C instruction, convert operations to hack
    else:
        binaryOutput += "111" # add starting 111 for C-instruction
                
        # Determine jump value
        findJump = command.find(';') # if jump exists, must have semicolon
        jumpOut = "000" # default is null
        
        # if jump is listed, match phrase for binary
        if findJump != -1:
            jumpCommand = command[(findJump+1):] # grab jump command
            
            if jumpCommand == "JGT":
                jumpOut = "001"
                
            elif jumpCommand == "JEQ":
                jumpOut = "010"
                
            elif jumpCommand == "JGE":
                jumpOut = "011"
                
            elif jumpCommand == "JLT":
                jumpOut = "100"
                
            elif jumpCommand == "JNE":
                jumpOut = "101"
                
            elif jumpCommand == "JLE":
                jumpOut = "110"
                
            else:
                jumpOut = "111"
            
            # remove jump command from overall command
            command = command[:findJump]
            
        # determine destination value
        findDest = command.find('=') # if destination exists, must have equal sign
        destOut = "000" # default is null
        
        # if destination is included, match phrase for binary
        if findDest != -1:
            destCommand = command[:findDest] # grab destination command
            
            if destCommand == "M":
                destOut = "001"
                
            elif destCommand == "D":
                destOut = "010"
                
            elif destCommand == "MD":
                destOut = "011"
                
            elif destCommand == "A":
                destOut = "100"
                
            elif destCommand == "AM":
                destOut = "101"
                
            elif destCommand == "AD":
                destOut = "110"
                
            else:
                destOut = "111"
        
            # remove desination command from overall command
            command = command[(findDest + 1):]
        
        # Determine "a" value
        findM = command.find('M')
        if findM != -1:
            binaryOutput += "1"
        else:
            binaryOutput += "0"
            
        # Determine comp value
        findAndSym = command.find('&') # only one option for binary if found
        findSlash = command.find('|') # only one option for binary if found
        
        compOut = "101010" # default is "0"
        
        # if not "0", search for binary
        if findAndSym != -1:
            compOut = "000000"
            
        elif findSlash != -1:
            compOut = "010101"
            
        elif command == "1":
            compOut = "111111"
            
        elif command == "-1":
            compOut = "111010"
            
        elif command == "D":
            compOut = "001100"
        
        elif command == "A" or command == "M": # A and M have same c1-c6
            compOut = "110000"
            
        elif command == "!D":
            compOut = "001101"
            
        elif command == "!A" or command == "!M": # !A and !M have same c1-c6
            compOut = "110001"
            
        elif command == "-D":
            compOut = "001111"
            
        elif command == "-A" or command == "-M": # -A and -M have same c1-c6
            compOut = "110011"
            
        elif command == "D+1":
            compOut = "011111"
            
        elif command == "A+1" or command == "M+1": # A+1 and M+1 have same c1-c6
            compOut = "110111"
            
        elif command == "D-1":
            compOut = "001110"
            
        elif command == "A-1" or command == "M-1": # A-1 and M-1 have same c1-c6
            compOut = "110010"
        
        elif command == "D+A" or command == "D+M": # D+A and D+M have same c1-c6
            compOut = "000010"
        
        elif command == "D-A" or command == "D-M": # D-A and D-M have same c1-c6
            compOut = "010011"
            
        elif command == "A-D" or command == "M-D": # A-D and M-D have same c1-c6
            compOut = "000111"
        
        # combine all outputs for final binary output
        binaryOutput += compOut + destOut + jumpOut
        
        # write output to file and add newline
        hackFile.write(binaryOutput)
        hackFile.write("\n")

# close hack file
hackFile.close()