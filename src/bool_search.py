# bool_search.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json
import time
from nltk.stem import PorterStemmer
import webbrowser
import os
import struct

from generate_result import ResultGen

all_articles_list = None
posting_list = None
porter_stemmer = PorterStemmer()

class ArticleSet:
    def __init__(self, articles: list = [], is_not: bool = False) -> None:
        self.articles = articles
        self.is_not = is_not

    def clone(self):
        return ArticleSet(self.articles.copy(), self.is_not)

    @staticmethod
    def basicAnd(lhs, rhs): # lhs AND rhs, inheriting lhs's is_not flag
        ret = ArticleSet([], lhs.is_not)
        i = 0
        j = 0
        while i < len(lhs.articles) and j < len(rhs.articles):
            if lhs.articles[i] < rhs.articles[j]:
                i += 1
            elif lhs.articles[i] > rhs.articles[j]:
                j += 1
            else:
                ret.articles.append(lhs.articles[i])
                i += 1
                j += 1
        return ret

    @staticmethod
    def basicOr(lhs, rhs): # lhs OR rhs, inheriting lhs's is_not flag
        ret = ArticleSet([], lhs.is_not)
        i = 0
        j = 0
        while i < len(lhs.articles) and j < len(rhs.articles):
            if lhs.articles[i] < rhs.articles[j]:
                ret.articles.append(lhs.articles[i])
                i += 1
            elif lhs.articles[i] > rhs.articles[j]:
                ret.articles.append(rhs.articles[j])
                j += 1
            else:
                ret.articles.append(lhs.articles[i])
                i += 1
                j += 1
        ret.articles.extend(lhs.articles[i:])
        ret.articles.extend(rhs.articles[j:])
        return ret

    @staticmethod
    def basicErase(lhs, rhs): # lhs - rhs, inheriting lhs's is_not flag
        ret = ArticleSet([], lhs.is_not)
        i = 0
        j = 0
        while i < len(lhs.articles) and j < len(rhs.articles):
            if lhs.articles[i] < rhs.articles[j]:
                ret.articles.append(lhs.articles[i])
                i += 1
            elif lhs.articles[i] > rhs.articles[j]:
                j += 1
            else:
                i += 1
                j += 1
        ret.articles.extend(lhs.articles[i:])
        return ret
    
    def __and__(self, rhs):
        if self.is_not == False and rhs.is_not == False:
            return ArticleSet.basicAnd(self, rhs)
        elif self.is_not == False and rhs.is_not == True:
            return ArticleSet.basicErase(self, rhs)
        elif self.is_not == True and rhs.is_not == False:
            return ArticleSet.basicErase(rhs, self)
        else:
            return ArticleSet.basicOr(self, rhs)
    
    def __or__(self, rhs):
        if self.is_not == False and rhs.is_not == False:
            return ArticleSet.basicOr(self, rhs)
        elif self.is_not == False and rhs.is_not == True:
            return ArticleSet.basicErase(rhs, self)
        elif self.is_not == True and rhs.is_not == False:
            return ArticleSet.basicErase(self, rhs)
        else:
            return ArticleSet.basicAnd(self, rhs)
    
    def __invert__(self):
        ret = self.clone()
        ret.is_not = not self.is_not
        return ret

class Exp:
    def __init__(self, syntax: str, type: str) -> None:
        self.syntax = syntax
        self.type = type
        self.lhs = None
        self.rhs = None
    
    def __str__(self) -> str:
        ret = ""
        if self.type == "AND" or self.type == "OR":
            ret += "("
            if self.lhs != None:
                ret += "{}".format(self.lhs)
            else:
                ret += "NONE"
            ret += " {} ".format(self.type)
            if self.rhs != None:
                ret += "{}".format(self.rhs)
            else:
                ret += "NONE"
            ret += ")"
        elif self.type == "NOT":
            ret += "(NOT {})".format(self.lhs)
        elif self.type == "BRACE":
            ret += "({})".format(self.lhs)
        else: # ID
            ret += "{}".format(self.lhs)
        return ret

    def reduce(self) -> None:
        if self.type == "AND" or self.type == "OR":
            if self.lhs != None:
                self.lhs.reduce()
                if (self.lhs.type == "AND" or self.lhs.type == "OR") and self.lhs.rhs == None:
                    self.lhs = self.lhs.lhs
                elif self.lhs.type == "BRACE":
                    self.lhs = self.lhs.lhs
            if self.rhs != None:
                self.rhs.reduce()
                if (self.rhs.type == "AND" or self.rhs.type == "OR") and self.rhs.rhs == None:
                    self.rhs = self.rhs.lhs
                elif self.rhs.type == "BRACE":
                    self.rhs = self.rhs.lhs
        elif self.type == "BRACE" or self.type == "NOT":
            self.lhs.reduce()
            if (self.lhs.type == "AND" or self.lhs.type == "OR") and self.lhs.rhs == None:
                self.lhs = self.lhs.lhs
            elif self.lhs.type == "BRACE":
                self.lhs = self.lhs.lhs

    def eval(self) -> ArticleSet:
        if self.type == "AND":
            lhs_eval = ArticleSet([], True)
            if self.lhs != None:
                lhs_eval = self.lhs.eval()
            rhs_eval = ArticleSet([], True)
            if self.rhs != None:
                rhs_eval = self.rhs.eval()
            return lhs_eval & rhs_eval
        elif self.type == "OR":
            lhs_eval = ArticleSet([], False)
            if self.lhs != None:
                lhs_eval = self.lhs.eval()
            rhs_eval = ArticleSet([], False)
            if self.rhs != None:
                rhs_eval = self.rhs.eval()
            return lhs_eval | rhs_eval
        elif self.type == "NOT":
            lhs_eval = ArticleSet([], True)
            if self.lhs != None:
                lhs_eval = self.lhs.eval()
            return ~lhs_eval
        elif self.type == "BRACE":
            lhs_eval = ArticleSet([], True)
            if self.lhs != None:
                lhs_eval = self.lhs.eval()
            return lhs_eval
        else: # ID
            lhs_eval = ArticleSet([], False)
            if self.lhs != None:
                try:
                    lhs_eval = ArticleSet(posting_list[porter_stemmer.stem(self.lhs)])
                except Exception:
                    lhs_eval = ArticleSet([], False)
            return lhs_eval

def printWelcomeMsg() -> None:
    print("Welcome to USTChorusWeb2021 bool search console.")
    print("Enter \"help\" for help.")

def printHelpMsg() -> None:
    print("help: print help message")
    print("load [(optional) path]: load posting list, from default path if second parameter is ignored")
    print("search [boolean expression]: do bool search with boolean expression")
    print("    e.g. >> search war AND (iraq OR iran) AND (NOT (britain OR england) AND NOT (us OR usa OR america)) AND australia")
    print("exit: bye!")

def loadPostingList(path: str) -> None:
    if path == "":
        path = "../output/posting_list.bin"
    print("Loading posting list from \"{}\"".format(path))
    print("This may take about 20 seconds")

    posting_list_file = open(path, "rb")

    # Extract all articles list
    all_articles_list_temp = []
    while True:
        article = posting_list_file.read(3)
        article = struct.unpack("BBB", article)
        article: int = (article[0] << 16) | (article[1] << 8) | article[2]
        if article == 0:
            break
        all_articles_list_temp.append(article)
    globals()["all_articles_list"] = all_articles_list_temp

    # Extract posting list
    posting_list_temp = {}
    while True:
        word: str = ""
        char_buffer = posting_list_file.read(1)
        if len(char_buffer) == 0:
            break
        word += struct.unpack("s", char_buffer)[0].decode()
        
        while True:
            char_buffer = posting_list_file.read(1)
            if char_buffer[0] == 0:
                break
            word += struct.unpack("s", char_buffer)[0].decode()

        current_article_list_temp = []
        while True:
            article = posting_list_file.read(3)
            article = struct.unpack("BBB", article)
            article: int = (article[0] << 16) | (article[1] << 8) | article[2]
            break_flag = False
            if article & 0x800000 != 0:
                article &= 0x7fffff
                break_flag = True
            current_article_list_temp.append(article)
            if break_flag:
                break
        
        posting_list_temp[word] = current_article_list_temp

    globals()["posting_list"] = posting_list_temp
    
    posting_list_file.close()
    print("Load complete")

def boolSearch(query: str) -> None:
    if posting_list == None:
        print("Error: posting list is not loaded")
        return

    start_time = time.time()

    print("Received query string:")
    print(query)

    # Scan tokens
    query = query.replace("(", " ( ").replace(")", " ) ")
    tokens = query.split()
    tokens.append(" ") # Terminator token
    #print(tokens)
    tokens.reverse() # Use as stack

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
                    stack[-1].type = "ID"
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

        # print("Raw AST: ")
        # print(root)

        # Reduce root
        root.reduce()
        while (root.type == "OR" or root.type == "AND") and root.rhs == None:
            root = root.lhs

        print("Resolved boolean expression: ")
        print(root)

        result = root.eval()
        if result.is_not:
            result = ArticleSet.basicErase(ArticleSet(all_articles_list, False), result)
        elapse = time.time() - start_time
        print("Finished searching in {} seconds".format(elapse))
        print("Found {} matching result(s)".format(len(result.articles)))
        
        # articles = []
        # for article in result.articles:
        #     article = "2018_0" + article
        #     article = article.replace("b", "blogs_00")
        #     article = article.replace("n", "news_00")
        #     articles.append(article)

        articles = []
        for article in result.articles:
            article_str: str = "2018_0%1d/" % (article >> 17)
            if (article >> 16) & 0b1 != 0:
                article_str += "news_00%05d"
            else:
                article_str += "blogs_00%05d"
            article_str %= (article & 0xffff)
            articles.append(article_str)

        # print(result.articles)

        result_gen = ResultGen()
        result_gen.results = articles
        result_gen.query = root.__str__()
        result_gen.elapse = elapse

        result_file = open("../output/result.html", "w", encoding='utf-8')
        result_file.write(result_gen.generate())
        result_file.close()

        # webbrowser.open("file://" + os.getcwd() + "/../output/result.html")
        os.startfile(os.getcwd() + "/../output/result.html")

        print("Result page generated")
    
    except SyntaxError:
        print("Syntax Error! (or my fault)")

def main() -> int:
    printWelcomeMsg()

    while (True):
        raw_command = input(">> ")
        commands = raw_command.split()

        if (len(commands) == 1 and (commands[0] == "exit" or commands[0] == "bye")):
            print("bye!")
            return 0
        elif (len(commands) == 1 and commands[0] == "help"):
            printHelpMsg()
        elif (commands[0] == "load"):
            loadPostingList(raw_command[len(commands[0]) + 1:])
        elif (len(commands) > 1 and commands[0] == "search"):
            boolSearch(raw_command[len(commands[0]) + 1:])
        elif (commands[0] == "eval"):
            while True:
                try:
                    eval_command = input(">>> ")
                    if eval_command == "exit":
                        break
                    eval(eval_command)
                except Exception:
                    pass
        else:
            print("Unknown command. Enter \"help\" for help.")
        
if __name__ == "__main__":
    main()
