# bool_search.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

from typing import runtime_checkable


def printWelcomeMsg():
    print("Welcome to USTChorusWeb2021 bool search console.")
    print("Enter \"help\" for help.")

def printHelpMsg():
    print("help: print help message")
    print("search [boolean expression]: do bool search with boolean expression")
    print("    e.g. >> search a OR b AND (NOT c OR d AND e) AND (NOT f OR NOT g)")

def importIndex(path: str):
    print("Importing index file from \"{}\"".format(path))

def boolSearch(query: str):
    print("Received query string \"{}\"".format(query))

    # Scan tokens
    query = query.replace("(", " ( ").replace(")", " ) ")
    tokens = query.split()
    tokens.append(" ") # Terminator token
    #print(tokens)
    tokens.reverse() # Use as stack

    class Exp:
        def __init__(self, syntax: str, type: str):
            self.syntax = syntax
            self.type = type
            self.lhs = None
            self.rhs = None
        
        def print(self):
            if self.type == "AND" or self.type == "OR":
                print("(", end="")
                if self.lhs != None:
                    self.lhs.print()
                else:
                    print("NONE", end="")
                print(" " + self.type + " ", end="")
                if self.rhs != None:
                    self.rhs.print()
                else:
                    print("NONE", end="")
                print(")", end="")
            elif self.type == "NOT":
                print("(NOT ", end="")
                self.lhs.print()
                print(")", end="")
            elif self.type == "BRACE":
                self.lhs.print()
            else: # id
                print(self.lhs, end="")

        def reduce(self):
            if self.type == "AND" or self.type == "OR":
                if self.lhs != None:
                    self.lhs.reduce()
                    if (self.lhs.type == "AND" or self.lhs.type == "OR") and self.lhs.rhs == None:
                        self.lhs = self.lhs.lhs
                if self.rhs != None:
                    self.rhs.reduce()
                    if (self.rhs.type == "AND" or self.rhs.type == "OR") and self.rhs.rhs == None:
                        self.rhs = self.rhs.lhs
            elif self.type == "BRACE" or self.type == "NOT":
                self.lhs.reduce()
                if (self.lhs.type == "AND" or self.lhs.type == "OR") and self.lhs.rhs == None:
                    self.lhs = self.lhs.lhs

    # Build AST (Abstract Syntax Tree) with LL(0) Syntax
    def isId(token: str) -> bool:
        if token == "AND" or token == "OR" or token == "(" or token == ")" or token == "NOT" or token == " ":
            return False
        return True
    
    root = Exp("OrExp", "OR")
    stack = [root]
    
    try:
        while len(stack) != 0:
            #print(tokens)
            if stack[-1].syntax == "OrExp":
                #print("Parsing OrExp")
                if tokens[-1] == "(" or tokens[-1] == "NOT" or isId(tokens[-1]):
                    lhs = stack[-1].lhs = Exp("AndExp", "AND")
                    rhs = stack[-1].rhs = Exp("OrTailExp", "OR")
                    stack.pop()
                    stack.append(rhs)
                    stack.append(lhs)
                else:
                    raise SyntaxError()
            elif stack[-1].syntax == "OrTailExp":
                #print("Parsing OrTailExp")
                if tokens[-1] == "OR":
                    tokens.pop()
                    lhs = stack[-1].lhs = Exp("AndExp", "AND")
                    rhs = stack[-1].rhs = Exp("OrTailExp", "OR")
                    stack.pop()
                    stack.append(rhs)
                    stack.append(lhs)
                elif tokens[-1] == ")" or tokens[-1]== " ":
                    stack[-1].lhs = None
                    stack[-1].rhs = None
                    stack.pop()
                else:
                    raise SyntaxError()
            elif stack[-1].syntax == "AndExp":
                #print("Parsing AndExp")
                if tokens[-1] == "(" or tokens[-1] == "NOT" or isId(tokens[-1]):
                    lhs = stack[-1].lhs = Exp("UnaryExp", "")
                    rhs = stack[-1].rhs = Exp("AndTailExp", "AND")
                    stack.pop()
                    stack.append(rhs)
                    stack.append(lhs)
                else:
                    raise SyntaxError()
            elif stack[-1].syntax == "AndTailExp":
                #print("Parsing AndTailExp")
                if tokens[-1] == "AND":
                    tokens.pop()
                    lhs = stack[-1].lhs = Exp("UnaryExp", "")
                    rhs = stack[-1].rhs = Exp("AndTailExp", "AND")
                    stack.pop()
                    stack.append(rhs)
                    stack.append(lhs)
                elif tokens[-1] == "OR" or tokens[-1] == ")" or tokens[-1]== " ":
                    stack[-1].lhs = None
                    stack[-1].rhs = None
                    stack.pop()
                else:
                    raise SyntaxError()
            elif stack[-1].syntax == "UnaryExp":
                #print("Parsing UnaryExp")
                if tokens[-1] == "(":
                    tokens.pop()
                    stack[-1].type = "BRACE"
                    lhs = stack[-1].lhs = Exp("OrExp", "OR")
                    stack.pop()
                    stack.append(Exp("RbracePlaceholder", ""))
                    stack.append(lhs)
                elif tokens[-1] == "NOT":
                    tokens.pop()
                    stack[-1].type = "NOT"
                    lhs = stack[-1].lhs = Exp("UnaryExp", "")
                    stack.pop()
                    stack.append(lhs)
                elif isId(tokens[-1]):
                    stack[-1].lhs = tokens[-1]
                    tokens.pop()
                    stack.pop()
                else:
                    raise SyntaxError()
            elif stack[-1].syntax == "RbracePlaceholder":
                if tokens[-1] == ")":
                    stack.pop()
                    tokens.pop()
                else:
                    raise SyntaxError()

        # Reduce root
        root.reduce()
        while (root.type == "OR" or root.type == "AND") and root.rhs == None:
            root = root.lhs

        print("Resolved boolean expression: ")
        root.print()
        print("")
                    
    except SyntaxError:
        print("Syntax Error! (Or my fault)")

def main() -> int:
    printWelcomeMsg()

    while (True):
        rawCommand = input(">> ")
        commands = rawCommand.split()

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