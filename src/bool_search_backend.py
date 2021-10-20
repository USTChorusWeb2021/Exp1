# bool_search_backend.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import time
from typing import Tuple
from nltk.stem import PorterStemmer
import struct

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

    def eval(self, posting_list, porter_stemmer) -> ArticleSet:
        if self.type == "AND":
            lhs_eval = ArticleSet([], True)
            if self.lhs != None:
                lhs_eval = self.lhs.eval(posting_list, porter_stemmer)
            rhs_eval = ArticleSet([], True)
            if self.rhs != None:
                rhs_eval = self.rhs.eval(posting_list, porter_stemmer)
            return lhs_eval & rhs_eval
        elif self.type == "OR":
            lhs_eval = ArticleSet([], False)
            if self.lhs != None:
                lhs_eval = self.lhs.eval(posting_list, porter_stemmer)
            rhs_eval = ArticleSet([], False)
            if self.rhs != None:
                rhs_eval = self.rhs.eval(posting_list, porter_stemmer)
            return lhs_eval | rhs_eval
        elif self.type == "NOT":
            lhs_eval = ArticleSet([], True)
            if self.lhs != None:
                lhs_eval = self.lhs.eval(posting_list, porter_stemmer)
            return ~lhs_eval
        elif self.type == "BRACE":
            lhs_eval = ArticleSet([], True)
            if self.lhs != None:
                lhs_eval = self.lhs.eval(posting_list, porter_stemmer)
            return lhs_eval
        else: # ID
            lhs_eval = ArticleSet([], False)
            if self.lhs != None:
                try:
                    lhs_eval = ArticleSet(posting_list[porter_stemmer.stem(self.lhs)])
                except Exception:
                    lhs_eval = ArticleSet([], False)
            return lhs_eval

class BoolSearcher:
    def __init__(self) -> None:
        self.all_articles_list = None
        self.posting_list = None
        self.porter_stemmer = PorterStemmer()

    def loadPostingList(self, path: str) -> None:
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
        self.all_articles_list = all_articles_list_temp

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

        self.posting_list = posting_list_temp
        posting_list_file.close()

    def buildAST(self, query: str) -> Exp:
        # Scan tokens
        query = query.replace("(", " ( ").replace(")", " ) ")
        tokens = query.split()
        tokens.append(" ") # Terminator token
        tokens.reverse() # Use as stack

        # Build AST (Abstract Syntax Tree) with LL(0) Syntax
        def isId(token: str) -> bool:
            if token == "AND" or token == "OR" or token == "(" or token == ")" or token == "NOT" or token == " ":
                return False
            return True
        
        root = Exp("OrExp", "OR")
        stack = [root]
        
        while len(stack) != 0:
            if stack[-1].syntax == "OrExp":
                if tokens[-1] == "(" or tokens[-1] == "NOT" or isId(tokens[-1]):
                    lhs = stack[-1].lhs = Exp("AndExp", "AND")
                    rhs = stack[-1].rhs = Exp("OrTailExp", "OR")
                    stack.pop()
                    stack.append(rhs)
                    stack.append(lhs)
                else:
                    raise SyntaxError()
            elif stack[-1].syntax == "OrTailExp":
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
                if tokens[-1] == "(" or tokens[-1] == "NOT" or isId(tokens[-1]):
                    lhs = stack[-1].lhs = Exp("UnaryExp", "")
                    rhs = stack[-1].rhs = Exp("AndTailExp", "AND")
                    stack.pop()
                    stack.append(rhs)
                    stack.append(lhs)
                else:
                    raise SyntaxError()
            elif stack[-1].syntax == "AndTailExp":
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

        return root

    def boolSearch(self, query: str) -> Tuple[str, list]:
        if self.posting_list == None:
            raise RuntimeError("Error: posting list is not loaded")

        root = self.buildAST(query)

        result = root.eval(self.posting_list, self.porter_stemmer)
        if result.is_not:
            result = ArticleSet.basicErase(ArticleSet(self.all_articles_list, False), result)

        articles = []
        for article in result.articles:
            article_str: str = "2018_0%1d/" % (article >> 17)
            if (article >> 16) & 0b1 != 0:
                article_str += "news_00%05d"
            else:
                article_str += "blogs_00%05d"
            article_str %= (article & 0xffff)
            articles.append(article_str)

        return root.__str__(), articles
