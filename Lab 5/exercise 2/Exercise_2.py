import sys


# "getSection": function that returns the lines of a specific section in the input file
# it is used to separate sections (states, sigma, gamma, transitions, start state, accept state, reject state)
def getSection(name, lGen):
    flag = False
    lRet = []

    for line in lGen:
        if line == name + ":":  # the beginning of the section
            flag = True
            continue
        if line == "end":  # the end of the section
            flag = False
        if flag == True and line not in lRet:  # if we have not reached the end of the section, we append the line of the file to the list
            lRet.append(line)

    return lRet


# "loadTMFromFile": function that uses the "getSection" function, to load the sections of a TM config file
# and return them in lists, together with an error code if the file is not valid
def loadTMFromFile(fileName):
    lGen = []
    errorCode = 0

    file = open(fileName)

    for line in file:
        line = line.strip().lower()
        if len(line) > 0 and line[0] != "#":  # we create a list from the input file only with the
            lGen.append(line)                 # lines that are different from comments
                                              # so we can pass it to the "getSection" function

    states = list(getSection("states", lGen))  # getting the states of the TM from the config file
    sigma = list(getSection("sigma", lGen))  # getting the input alphabet of the TM from the config file
    gamma = list(getSection("gamma", lGen))  # getting the tape alphabet of the TM from the config file
    transitions = list(getSection("transitions", lGen))  # getting the transitions of the TM from the config file
    startState = list(getSection("start state", lGen))  # getting the start state of the TM from the config file
    acceptState = list(getSection("accept state", lGen))  # getting the accept state of the TM from the config file
    rejectState = list(getSection("reject state", lGen))  # getting the reject state of the TM from the config file

    # if the TM config file does not contain exactly one start state, we return an error code
    if len(startState) != 1:
        errorCode = 5
        return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState

    # if the TM config file does not contain exactly one accept state, we return an error code
    if len(acceptState) != 1:
        errorCode = 6
        return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState

    # if the TM config file does not contain exactly one reject state, we return an error code
    if len(rejectState) != 1:
        errorCode = 7
        return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState

    # if the TM config file does not contain at least three states, including the start state, accept state, and
    # reject state, we return an error code
    if len(states) < 3:
        errorCode = 1
        return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState
    elif startState[0] not in states or acceptState[0] not in states or rejectState[0] not in states:
        errorCode = 1
        return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState

    # if the TM config file contains the blank symbol ("_") in the input alphabet, or if the input alphabet
    # is empty, we return an error code
    if "_" in sigma or len(sigma) == 0:
        errorCode = 2
        return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState

    # if the TM config file does not contain the blank symbol ("_") in the tape alphabet, or if the input alphabet
    # is not included in the tape alphabet, or if the tape alphabet is empty, we return an error code
    if "_" not in gamma or len(set(gamma)) != len(set(gamma)|set(sigma)) or len(gamma) == 0:
        errorCode = 3
        return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState

    # if the TM config file does not contain any transition, we return an error code
    if len(transitions) == 0:
        errorCode = 4
        return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState
    else:
        for transition in transitions:
            transition = transition.split()
            if len(transition) != 5:  # if a transition does not contain exactly 5 elements, we return an error code
                errorCode = 4
                return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState
            elif transition[0] not in states or transition[1] not in states:  # if the first two elements of a transition are not states from the TM config file, we return an error code
                errorCode = 4
                return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState
            elif transition[0] == acceptState[0] or transition[0] == rejectState[0]:  # if the first state of a transition is either the accept state or the reject state, we return an error code
                errorCode = 4
                return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState
            elif transition[2] not in gamma:  # if the third element of a transition is not a symbol from the tape alphabet, we return an error code
                errorCode = 4
                return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState
            elif transition[3] not in gamma and transition[3] != "e":  # if the fourth element of a transition is not a symbol from the tape alphabet (excluding epsilon), we return an error code
                errorCode = 4
                return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState
            elif transition[4] != "l" and transition[4] != "r":  # if the direction in which the head will move next is neither left, nor right, we return an error code
                errorCode = 4
                return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState

    file.close()

    # if the TM config file is valid, we do not return any error code
    return errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState


try:
    errorCode, states, sigma, gamma, transitions, startState, acceptState, rejectState = loadTMFromFile(sys.argv[1])

    print()
    if errorCode == 1:
        print(f"The \"states\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 2:
        print(f"The \"sigma\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 3:
        print(f"The \"gamma\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 4:
        print(f"The \"transitions\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 5:
        print(f"The \"start state\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 6:
        print(f"The \"accept state\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 7:
        print(f"The \"reject state\" section of the config file \"{sys.argv[1]}\" is not valid.")
    else:
        print(f"The config file \"{sys.argv[1]}\" is valid!")
        print()

        inputTM = open("input_tm.txt")

        print("Validating the input strings from \"input_tm.txt\":")
        print("----------------------------------")
        for string in inputTM:
            copyString = list(string.rstrip("\n"))
            copyString[0:0] = [startState[0]]

            position = 0  # we keep track of the position of the current state, on the tape
            flag = 1  # we use a flag to know when to stop a string validation

            while flag == 1:  # we continue the string validation, as long as we have not reached an end point
                flag = 0  # we tell the program that no transition has occurred yet

                for transition in transitions:  # we search for the transition that starts with the current state and reads the first symbol situated to the right of the current state
                    transition = transition.split()
                    if transition[0] == copyString[position] and transition[2] == copyString[position+1]:
                        if transition[4] == "l":  # the head should go to the left
                            if position == 0:  # we have already reached the left-hand end of the tape, meaning we can't go left anymore
                                flag = 2       # thus, we tell the program to end the string validation, as we will not be able to get past the leftmost square of the tape
                                break
                            else:
                                if transition[3] != "e":  # besides interchanging the current state with a symbol, we are also replacing the value of the symbol with a different one
                                    copyString[position-1] = transition[1]
                                    copyString[position] = transition[3]
                                else:  # we are interchanging the current state with a symbol, without replacing the value of the symbol
                                    symbolAux = copyString[position-1]
                                    copyString[position-1] = transition[1]
                                    copyString[position] = symbolAux
                                position -= 1
                            flag = 1  # we tell the program that a transition has occurred
                        else:  # the head should go to the right
                            if position == (len(copyString) - 2):  # if we have reached the square before the rightmost square of the tape, we add a blank symbol to the tape
                                copyString.append("_")
                            if transition[3] != "e":  # besides interchanging the current state with a symbol, we also replace the latter symbol with a different symbol
                                copyString[position + 1] = transition[1]
                                copyString[position] = transition[3]
                            else:  # we are interchanging the current state with a symbol, without replacing the value of the symbol
                                symbolAux = copyString[position + 1]
                                copyString[position + 1] = transition[1]
                                copyString[position] = symbolAux
                            position += 1
                            flag = 1  # we tell the program that a transition has occurred

                if copyString[position] == acceptState[0]:
                    flag = 3  # we have reached the accepting state, and thus we end the string validation
                elif copyString[position] == rejectState[0]:
                    flag = 4  # we have reached the rejecting state, and thus we end the string validation

            string = string.strip("\n")
            if flag != 3:
                print(f"The string \"{string}\" from \"input_tm.txt\" is not accepted by the turing machine.")
            else:
                print(f"The string \"{string}\" from \"input_tm.txt\" is accepted by the turing machine!")

            print("----------------------------------")

        inputTM.close()
except:
    print("The requested file does not exist, or something else went wrong.")
