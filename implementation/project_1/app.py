from typing import final
from flask import Flask, render_template, request, g
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import requests

app = Flask(__name__)

## returns the news content from the article
def news_extract(heading, url):

    def india_today_get_content(url):
        ar      = requests.get(url)
        article = BeautifulSoup(ar.text,"lxml")
        if (article.find('div',{"class":"description"}) == None):
            return None
        else:
            content = ""
            for para in article.find(class_ = "description").find_all("p")[:-3]:
                content+=para.get_text()
            return content

    def indian_express_get_content(url):
        ar = requests.get(url)
        article = BeautifulSoup(ar.text,"lxml")
        if article.find(id="pcl-full-content") == None:
            return None
        else:
            content = ""
            for para in article.find('div', id = "pcl-full-content").find_all("p"):
                content+=para.get_text()
            return content
    
    def hindu_get_content(url):
        html    = requests.get(url)
        article = BeautifulSoup(html.text,"lxml")
        content = ""
        paras = article.find_all("p")[1:-5]
        for para in paras:
            content+=para.get_text()
        return content

    def ndtv_get_content(url):
        ar = requests.get(url)
        article = BeautifulSoup(ar.text,"lxml")
        if article.find('div',{'id':"ins_storybody"}) == None:
            return None, None
        else:
            content = ""
            for para in article.find('div',{'id':"ins_storybody"}).find_all("p"):
                content+=para.get_text()
            return content
    
    def toi_get_content(url):
        data = requests.get(url).content
        soup = BeautifulSoup(data,"lxml")
        div = soup.find("div", class_= "_3YYSt clearfix ")
        if div is None:
            div = soup.find("div", class_= "_3YYSt clearfix")
        if div is not None:
            time = soup.find("div", class_="yYIu- byline").find("span").text
            time = re.sub("Updated:|IST|AM|PM", "", time, flags=re.IGNORECASE).strip()
            # time = datetime.strptime(time, "%b %d, %Y, %H:%M")
            return "".join(list(div.strings))
        return None

    if (heading == 'India_Today'): return india_today_get_content(url)
    if (heading == 'The_Indian_Express'): return indian_express_get_content(url)
    if (heading == 'The_Hindu'): return hindu_get_content(url)
    if (heading == 'NDTV'): return ndtv_get_content(url)
    if (heading == 'Times_of_India'): return toi_get_content(url)


 
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/plain_news', methods=['GET', 'POST'])
def plain_news():
    plain_text        = request.form['text_id']
    return render_template("output.html", plain_news = plain_text)

@app.route('/news_article_link',  methods=['GET', 'POST'])
def link_to_content():
    url                      = request.form['article_id']
    news_company = request.form['news_company']
    plain_text           = news_extract(news_company, url)
    print("in App.py : ",plain_text)
    return render_template("output.html", plain_news = plain_text)

@app.route('/translate_news', methods=['GET', 'POST'])
def translate():
    text                     = request.form['translate_text_id']
    language            = request.form['destination_language_id']
    translated_text   = GoogleTranslator(source='auto', target=language).translate(text)
    setattr(g, '_translated_text', translated_text)
    return render_template("output.html", translated_news = translated_text)

@app.route('/summarize_news', methods=['GET', 'POST'])
def summarize_news():
    if (request.form.get('summarize_button')):
        summarized_text = request.form['summarize_button']
        print(summarized_text)
        return  
    return render_template("page_1.html", ready_text = summarized_text)

@app.route('/categorize_news', methods=['GET', 'POST'])
def categorize_news():
    if(request.form['categorize_id']):
        categorized_text = request.form['categorize_id']
        print(categorized_text)
    return render_template("page_1.html", ready_text = categorized_text)


if __name__ == '__main__':
	app.run(debug=True)
