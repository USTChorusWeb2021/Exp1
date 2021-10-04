# bool_search.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

def printWelcomeMsg():
    print("Welcome to USTChorusWeb2021 bool search console.")
    print("Enter \"help\" for help.")

def printHelpMsg():
    print("help: print help message")

def importIndex(path: str):
    print("Importing index file from \"{}\"".format(path))

def boolSearch(query: str):
    print("Received query string \"{}\"".format(query))
    

def main() -> int:
    printWelcomeMsg()

    while (True):
        rawCommand = input(">> ")
        commands = rawCommand.split(' ')

        if (len(commands) == 1 and (commands[0] == "exit" or commands[0] == "bye")):
            print("bye!")
            return 0
        elif (len(commands) == 1 and commands[0] == "help"):
            printHelpMsg()
        elif (len(commands) > 1 and commands[0] == "import"):
            importIndex(rawCommand[len(commands[0]) + 1:])
        elif (len(commands) > 1 and commands[0] == "search"):
            boolSearch(rawCommand[len(commands[0]) + 1:])
        else:
            print("Unknown command. Enter \"help\" for help.")
        
if __name__ == "__main__":
    main()
