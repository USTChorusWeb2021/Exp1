# generate_result.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json
from typing import ForwardRef

result_template_file = open("./template/result_template.pythtml", "r")
result_template = result_template_file.read()
result_template_file.close()

term_template_file = open("./template/term_template.pythtml", "r")
term_template = term_template_file.read()
term_template_file.close()

class ResultGen:
    def __init__(self) -> None:
        self.query = str()
        self.elapse = 0.0
        self.results = []

    def generate(self) -> str:
        show_count = len(self.results)
        if show_count > 20:
            show_count = 20
        show_stride = 1
        if show_count != 0:
            show_stride = len(self.results) // show_count
        
        terms = ""
        for i in range(0, show_stride * show_count, show_stride):
            article_name = self.results[i]
            article_path = "../dataset/US_Financial_News_Articles/" + article_name + ".json"
            json_file = open(article_path, "r", encoding='utf-8')
            article = json.load(json_file)
            json_file.close()
            title = article["title"]
            url = article["url"]
            url_short = url
            if len(url) > 64:
                url_short = url[0:64] + "..."
            date = article["published"][0:10]
            text: str = article["text"]
            text = text.replace("\n", " ")
            text = text.replace("\t", " ")
            if len(text) > 512:
                text = text[0:512] + " ..."
            terms += term_template.format(url, title, article_name, url_short, date, text)

        return result_template.format(self.query, len(self.results), self.elapse, show_count, terms, self.results)

        

        
        
    