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


# "loadNFAFromFile": function that uses the "getSection" function, to load the sections of an NFA config file
# and return them in lists, together with an error code if the file is not valid
def loadNFAFromFile(fileName):
    lGen = []
    errorCode = 0

    file = open(fileName)

    for line in file:
        line = line.strip().lower()
        if len(line) > 0 and line[0] != "#":  # we create a list from the input file only with the
            lGen.append(line)                 # lines that are different from comments
                                              # so we can pass it to the "getSection" function

    states = list(getSection("states", lGen))  # getting the states of the NFA from the config file
    sigma = list(getSection("sigma", lGen))  # getting the alphabet of the NFA from the config file
    transitions = list(getSection("transitions", lGen))  # getting the transitions of the NFA from the config file

    # if the NFA config file does not contain at least one state, we return an error code
    if len(states) == 0:
        errorCode = 1
        return errorCode, states, sigma, transitions
    else:
        numberOfStartStates = 0  # we keep track of how many start states are in the config file
        numberOfFinalStates = 0  # we keep track of how many accept states are in the config file
        for state in states:
            state = state.replace(",", " ").split()
            if len(state) > 3:  # if a line from the "states" section of the config file has more than three elements (the state, and
                errorCode = 1   # two letters that indicate if the state is a start state and/or a final state), we return an error code
                return errorCode, states, sigma, transitions
            elif len(state) == 2:
                if state[1] != "s" and state[1] != "f":  # if a line from the "states" section has exactly two elements, then those elements must be the state, and the letter "s" (start state) or "f" (accept state)
                    errorCode = 1
                    return errorCode, states, sigma, transitions
                elif state[1] == "s":
                    numberOfStartStates += 1
                else:
                    numberOfFinalStates += 1
            elif len(state) == 3:
                if state[1] != "s" or state[2] != "f":  # if a line from the "states" section has exactly three elements, then those elements must be the state, the letter "s" (start state) and "f" (accept state)
                    errorCode = 1
                    return errorCode, states, sigma, transitions
                else:
                    numberOfStartStates += 1
                    numberOfFinalStates += 1

        if numberOfStartStates != 1:  # if we have encountered more than one start state, we return an error code
            errorCode = 1
            return errorCode, states, sigma, transitions

        if numberOfFinalStates == 0:  # if we have not encountered any accept state, we return an error code
            errorCode = 1
            return errorCode, states, sigma, transitions

    # if the NFA config file does not contain at least one symbol, we return an error code
    if len(sigma) == 0:
        errorCode = 2
        return errorCode, states, sigma, transitions

    statesAux = [state.replace(",", " ").split()[0] for state in states]

    # if the NFA config file does not contain at least one transition, we return an error code
    if len(transitions) == 0:
        errorCode = 3
        return errorCode, states, sigma, transitions
    else:
        for transition in transitions:
            transition = transition.replace(",", " ").split()
            if len(transition) != 3:  # if a transition does not contain exactly three elements (a state,
                errorCode = 3         # a symbol, and another state), we return an error code
                return errorCode, states, sigma, transitions
            else:
                if transition[0] not in statesAux or \
                   transition[1] not in sigma and \
                   transition[1] != "e" or \
                   transition[2] not in statesAux:  # if neither element of a transition is recognized by the NFA, we return an error code
                    errorCode = 3
                    return errorCode, states, sigma, transitions

    file.close()

    # if the NFA config file is valid, we do not return any error code
    return errorCode, states, sigma, transitions


DFAStartState = []  # list that contains the states included in the start state of the DFA
# "generateDFAStartState": function that helps us generate the start state of the DFA
def generateDFAStartState(NFATransitions, position):
    global DFAStartState

    if position < len(DFAStartState):  # we check if we have found all the states included in the start state of the DFA
        for transition in NFATransitions:
            transition = transition.replace(",", " ").split()
            if transition[0] == DFAStartState[position] and \
               transition[1] == "e" and \
               transition[2] not in DFAStartState:  # we check if we have encountered a state that has not already been added to the start state of the DFA
                DFAStartState.append(transition[2])  # we add a state of the NFA to the start state of the DFA

        generateDFAStartState(NFATransitions, position + 1)


# "generateDFAStates": function that helps us generate the states of the DFA
def generateDFAStates(NFAStates, NFATransitions):
    # "statesAux": list that contains the states of the NFA, which helps us generate the states of the DFA
    statesAux = [state.replace(",", " ").split()[0] for state in NFAStates]

    DFAStates = []
    n = len(statesAux)
    nr = 1 << n
    x = 0
    while x < nr:  # while loop that generates the states of the DFA, with the help of "statesAux", using bit manipulation
        position = 1
        cx = x
        DFAState = []
        while cx:
            if cx & 1:
                DFAState.append(statesAux[position - 1])
            position += 1
            cx = cx >> 1
        x += 1
        DFAStates.append(DFAState)
    DFAStates.sort()  # we want to memorize the states of the DFA in an organized order

    NFAstartState = None
    for state in NFAStates:  # we want to get the start state of the NFA
        state = state.replace(",", " ").split()
        if len(state) >= 2 and state[1] == "s":
            NFAstartState = state[0]
            break

    DFAStartState.append(NFAstartState)
    generateDFAStartState(NFATransitions, 0)
    DFAStartState.sort()  # we want to memorize the states included in the start state of the DFA in an organized order

    DFAAcceptStates = []
    for state in DFAStates:
        if len(state) != 0 and state[0] == NFAstartState:  # the accept states of the DFA are the states that contain the start state of the NFA
            DFAAcceptStates.append(state)

    return DFAStates, DFAStartState, DFAAcceptStates


# "convertNFAToDFA": function that helps us make the actual conversion from an NFA to its equivalent DFA
def convertNFAToDFA(NFAStates, sigma, NFATransitions, convertedDFAConfigFile):
    file = open(convertedDFAConfigFile, "w")

    DFAStates, DFAStartState, DFAAcceptStates = generateDFAStates(NFAStates, NFATransitions)

    # we write the alphabet of the DFA to a file
    file.write("Sigma:\n")

    for symbol in sigma:
        file.write("\t"+symbol+"\n")

    file.write("End\n")

    # we write the states of the DFA to a file
    file.write("States:\n")

    # we first write the start state of the DFA
    file.write("\t{")
    for pos in range(len(DFAStartState) - 1):
        file.write(DFAStartState[pos] + ", ")
    file.write(DFAStartState[-1] + "}, s")
    if DFAStartState in DFAAcceptStates:
        file.write(", f")
    file.write("\n")

    # then we write the rest of the states
    for DFAState in DFAStates:
        if DFAState != DFAStartState:
            file.write("\t{")
            if DFAState != []:
                for pos in range(len(DFAState) - 1):
                    file.write(DFAState[pos] + ", ")
                file.write(DFAState[-1] + "}")
                if DFAState in DFAAcceptStates:
                    file.write(", f")
                file.write("\n")
            else:
                file.write("}\n")

    file.write("End\n")

    # we generate and write the transitions of the DFA to a file
    file.write("Transitions:\n")

    # we transform the strings from "NFATransitions" into lists of three
    # elements, each one representing an element of a transition of the NFA,
    # to help us determine the transitions of the DFA
    for pos in range(len(NFATransitions)):
        transitions[pos] = transitions[pos].replace(",", " ").split()

    # we generate the transitions of the DFA
    for DFAState in DFAStates:
        statePrintedToFile = "{"
        if DFAState != []:  # we write the transitions for the DFA states that are different from the empty set
            # we write the beginning of a transition of the DFA to a file
            for pos in range(len(DFAState) - 1):
                statePrintedToFile = statePrintedToFile + DFAState[pos] + ", "
            statePrintedToFile = statePrintedToFile + DFAState[-1] + "}"

            # we get the rest of a transition of the DFA
            for symbol in sigma:
                # "commonStates": list that contains all of the states of the DFA that can be directly
                # accessed from a certain state of the DFA, by reading the symbol "symbol"
                commonStates = []
                for state in DFAState:
                    for transition in NFATransitions:
                        if transition[0] == state and \
                           transition[1] == symbol and \
                           transition[2] not in commonStates:   # if we have encountered a state that has not already
                            commonStates.append(transition[2])  # been added to "commonStates", then we add it to the list
                        elif transition[2] == state and transition[1] == "e":  # we treat the case where we have epsilon on a transition of the NFA
                            for transitionForEpsilon in NFATransitions:
                                if transitionForEpsilon[0] == transition[2] and \
                                   transitionForEpsilon[1] == symbol and \
                                   transitionForEpsilon[2] == transition[0] and \
                                   transition[2] not in commonStates:   # if we have encountered a state that has not already
                                    commonStates.append(transition[2])  # been added to "commonStates", then we add it to the list
                                    break

                commonStates.sort()  # we want to memorize the states from "commonStates" in an organized order

                # we write the rest of a transition of the DFA to a file
                file.write("\t" + statePrintedToFile)
                file.write(", " + symbol + ", {")
                for pos in range(len(commonStates) - 1):
                    file.write(commonStates[pos] + ", ")
                if len(commonStates) != 0:
                    file.write(commonStates[-1])
                file.write("}\n")

        else:  # we write the transitions for the DFA state that is the empty set
            statePrintedToFile += "}"

            for symbol in sigma:
                file.write("\t" + statePrintedToFile + ", " + symbol + "\n")

    file.write("End")

    file.close()


try:
    errorCode, states, sigma, transitions = loadNFAFromFile(sys.argv[1])

    print()
    if errorCode == 1:
        print(f"The \"states\" section of the config file \"{sys.argv[1]}\" is not valid.", end=" ")
        print(f"The NFA from \"{sys.argv[1]}\" cannot be converted to a DFA.")
    elif errorCode == 2:
        print(f"The \"sigma\" section of the config file \"{sys.argv[1]}\" is not valid.", end=" ")
        print(f"The NFA from \"{sys.argv[1]}\" cannot be converted to a DFA.")
    elif errorCode == 3:
        print(f"The \"transitions\" section of the config file \"{sys.argv[1]}\" is not valid.", end=" ")
        print(f"The NFA from \"{sys.argv[1]}\" cannot be converted to a DFA.")
    else:
        print(f"The config file \"{sys.argv[1]}\" is valid.", end=" ")
        print(f"The NFA from \"{sys.argv[1]}\" has been converted to a DFA!")

        convertNFAToDFA(states, sigma, transitions, sys.argv[2])
except:
    print("The requested file does not exist, or something else went wrong.")
