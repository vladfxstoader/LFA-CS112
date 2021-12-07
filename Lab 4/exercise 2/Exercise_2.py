import sys
import copy


results = []  # list that contains the strings resulted from deriving a string from the "input_cfg.txt" file, by using the function "derive"
# "derive": recursive function that helps us derive the strings from "input_cfg.txt"
def derive(string, rulesLeft, rulesRight):
    global derivationNr
    flag = True  # we use a flag to know when we have reached a string that can no longer be derived

    if derivationNr <= 100000:  # we derive all of the strings a maximum of 100000 times (by doing this, we make sure that the program stops for any given string)
        for positionString in range(len(string)):  # we check for parts of our string which can be derived
            if string[positionString] in rulesLeft:         # if a variable of our string is found on the left side of a rule,
                for positionRule in range(len(rulesLeft)):  # we search for every rule which has that variable on the left side
                    if rulesLeft[positionRule] == string[positionString]:
                        stringCopy = copy.copy(string)  # we create a copy of the string that we are currently deriving, so that we do not modify the actual string
                        derivationNr = derivationNr + 1
                        if rulesRight[positionRule] != "e":  # the rule that we have found tells us we must replace a variable from our string with a string of variables and terminals
                            if len(rulesRight[positionRule]) > 1: # we check whether the rule that we have found, tells us to replace a variable with a string of more than one character
                                if len(string) < 20:  # we do not want to obtain strings that have a length of over 20 characters
                                    flag = False
                                    stringCopy[positionString:positionString+1] = rulesRight[positionRule]
                                    derive(stringCopy, rulesLeft, rulesRight)
                            else:  # the rule that we have found tells us to replace a variable with a single character
                                flag = False
                                stringCopy[positionString:positionString + 1] = rulesRight[positionRule]
                                derive(stringCopy, rulesLeft, rulesRight)
                        else:  # the rule that we have found tells us we must remove a variable from our string
                            flag = False
                            stringCopy[positionString:positionString + 1] = ""
                            derive(stringCopy, rulesLeft, rulesRight)

        if flag:  # if the flag has the value "True", we have reached a string that can no longer be derived, otherwise, the current string, "string", can still be derived
            if "".join(string) not in results:  # we check if the current (derived) string has not already been reached
                results.append("".join(string))
                print("".join(string))

# "getSection": function that returns the lines of a specific section in the input file
# it is used to separate sections (variables, sigma, rules, start variable)
def getSection(name, lGen):
    flag = False
    lRet = []

    for line in lGen:
        if line.lower() == name + ":":  # the beginning of the section
            flag = True
            continue
        if line.lower() == "end":  # the end of the section
            flag = False
        if flag == True and line not in lRet:  # if we have not reached the end of the section, we append the line of the file to the list
            lRet.append(line)

    return lRet


# "loadCFGFromFile": function that uses the "getSection" function, to load the sections of a CFG config file
# and return them in lists, together with an error code if the file is not valid
def loadCFGFromFile(fileName):
    lGen = []
    errorCode = 0

    file = open(fileName)

    for line in file:
        line = line.strip()
        if len(line) > 0 and line[0] != "/":  # we create a list from the input file only with the
            lGen.append(line)                 # lines that are different from comments
                                              # so we can pass it to the "getSection" function

    variables = list(getSection("variables", lGen))  # getting the variables of the CFG from the config file
    sigma = list(getSection("sigma", lGen))  # getting the terminals of the CFG from the config file
    rules = list(getSection("rules", lGen))  # getting the rules of the CFG from the config file
    startVariable = list(getSection("start variable", lGen))  # getting the start variable of the CFG from the config file

    # if the CFG config file does not contain exactly one start variable, we return an error code
    if len(startVariable) != 1:
        errorCode = 4
        return errorCode, variables, sigma, rules, startVariable
    elif len(startVariable[0]) != 1:  # if the start variable does not have a length of 1, we return an error code
        errorCode = 4
        return errorCode, variables, sigma, rules, startVariable

    # if the CFG config file does not contain at least one variable, including the start variable, we return an error code
    if len(variables) == 0 or startVariable[0] not in variables:
        errorCode = 1
        return errorCode, variables, sigma, rules, startVariable
    else:  # if the variables within the CFG config file are not uppercase, or do not have a length of 1, we return an error code
        for variable in variables:
            if variable.upper() != variable or len(variable) != 1:
                errorCode = 1
                return errorCode, variables, sigma, rules, startVariable

    # if the CFG config file does not contain at least one terminal, we return an error code
    if len(sigma) == 0:
        errorCode = 2
        return errorCode, variables, sigma, rules, startVariable
    else:  # if the terminals within the CFG config file are not lowercase, or do not have a length of 1, we return an error code
        for terminal in sigma:
            if terminal.lower() != terminal or len(terminal) != 1:
                errorCode = 2
                return errorCode, variables, sigma, rules, startVariable

    # if the CFG config file does not contain any rules, we return an error code
    if len(rules) == 0:
        errorCode = 3
        return errorCode, variables, sigma, rules, startVariable
    elif startVariable[0] not in rules[0].replace(",", " ").split()[0]:  # if the left side of the first rule does not contain the start variable, we return an error code
        errorCode = 3
        return errorCode, variables, sigma, rules, startVariable
    else:
        for rule in rules:
            rule = rule.replace(",", " ").split()
            if len(rule) != 2:  # if a rule does not have exactly two sides, we return an error code
                errorCode = 3
                return errorCode, variables, sigma, rules, startVariable
            elif rule[0] not in variables:  # if the variable from the left side is not recognized by the CFG, we return an error code
                errorCode = 3
                return errorCode, variables, sigma, rules, startVariable
            else:
                for character in rule[1]:  # if either a variable or a terminal from the right side is not recognized by the CFG, we return an error code
                    if character not in variables and character not in sigma and character != "e":
                        errorCode = 3
                        return errorCode, variables, sigma, rules, startVariable

    file.close()

    # if the CFG config file is valid, we do not return any error code
    return errorCode, variables, sigma, rules, startVariable


try:
    errorCode, variables, sigma, rules, startVariable = loadCFGFromFile(sys.argv[1])

    print()
    if errorCode == 1:
        print(f"The \"variables\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 2:
        print(f"The \"sigma\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 3:
        print(f"The \"rules\" section of the config file \"{sys.argv[1]}\" is not valid.")
    elif errorCode == 4:
        print(f"The \"start variable\" section of the config file \"{sys.argv[1]}\" is not valid.")
    else:
        print(f"The config file \"{sys.argv[1]}\" is valid!")
        print()

        inputCFG = open("input_cfg.txt")

        rulesLeft = [rule[0] for rule in rules]            # we separate the left side of rules
        rulesRight = [rule[2:].strip() for rule in rules]  # from the right side of rules, to help us in the process of deriving strings

        print("Deriving the strings from \"input_cfg.txt\":")
        print("----------------------------------")

        for string in inputCFG:  # we derive the strings from "input_cfg.txt"
            derivationNr = 0
            results = []

            string = string.rstrip("\n")
            print(f"The strings resulted from deriving \"{string}\" are:")
            print()
            derive(list(string), rulesLeft, rulesRight)  # recursive function that helps us derive the strings from "input_cfg.txt"
            print("----------------------------------")

        inputCFG.close()
except:
    print("The requested file does not exist, or something else went wrong.")
