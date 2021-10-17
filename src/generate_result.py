# generate_result.py
# USTChorusWeb2021
# By HurryPeng & WhitieKitty

import json

class ResultGen:
    def __init__(self) -> None:
        self.result_template_file = open("./template/result_template.pythtml", "r")
        self.result_template = self.result_template_file.read()
        self.result_template_file.close()

        self.term_template_file = open("./template/term_template.pythtml", "r")
        self.term_template = self.term_template_file.read()
        self.term_template_file.close()

    def generate(self, query: str, elapse: float, results: list) -> str:
        show_count = len(results)
        if show_count > 20:
            show_count = 20
        show_stride = 1
        if show_count != 0:
            show_stride = len(results) // show_count
        
        terms = ""
        for i in range(0, show_stride * show_count, show_stride):
            article_name = results[i]
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
            terms += self.term_template.format(url, title, article_name, url_short, date, text)

        return self.result_template.format(query, len(results), elapse, show_count, terms, results)

class ImageResultGen:
    def __init__(self) -> None:
        self.result_template_file = open("./template/image_result_template.pythtml", "r")
        self.result_template = self.result_template_file.read()
        self.result_template_file.close()

        self.term_template = '<td><a href="{0}"><img src="{1}" width="256" height="128" title="source: {2} relevance: {3}"></a></td>'

    def generate(self, query: str, elapse: float, results: list) -> str:
        terms = []
        for i in range(0, len(results)):
            article_name = results[i][1]
            relevance = results[i][0]
            article_path = "../dataset/US_Financial_News_Articles/" + article_name.replace("1/b", "2018_01/blogs_00") + ".json"
            json_file = open(article_path, "r", encoding='utf-8')
            article = json.load(json_file)
            json_file.close()
            url = article["url"]
            image_path = "../output/images/" + article_name.replace("/", "_") + ".jpg"
            terms.append(self.term_template.format(url, image_path, article_name.replace("1/b", "2018_01/blogs_00"), relevance))

        terms_str = "<tr>\n"
        for i in range(0, len(terms)):
            if i % 4 == 0 and i != 0 and i != len(terms) - 1:
                terms_str += "</tr>\n<tr>"
            terms_str += terms[i] + '\n'
        terms_str += "</tr>"

        return self.result_template.format(query, elapse, terms_str)
