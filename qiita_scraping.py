import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from openai import OpenAI
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import re



# DB認証（初期化済みかを判定する）
if not firebase_admin._apps:
    # 初期済みでない場合は初期化処理を行う
    cred = credentials.Certificate("admin.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
    

def scraping():
    URL ="https://qiita.com/"
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")
    elems = soup.find_all("div", class_="style-1p44k52")
    articles = elems[0].find_all("article", class_="style-1w7apwp")

    scraping_data = []
    for article in articles:
        article_data = []
        article_data.append(article.h2.a.text)
        article_data.append(str(article.h2.a["href"]))
        scraping_data.append(article_data)

    return scraping_data


def get_sentence_list(url_list):  
    sentence_list = []
    for url in url_list:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.find_all("div", class_="mdContent-inner") 
        article = articles[0].find_all("p")
        art_str = ""
        for art in article:
            art_str += art.text
        sentence_list.append(art_str)
    
    return sentence_list


def summarize_sentence(sentence):
    if len(sentence) <= 2000:
        client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an excellent software engineer."},
                {
                    "role": "user",
                    "content": f"Please summarize the following sentence. {sentence}  Please write your answer in Japanese." 
                }
            ],
            max_completion_tokens = 1000
        )
        
        return completion.choices[0].message.content

    else:
        error_message = "入力文字数が制限文字数2000文字を超えたので要約できませんでした。"

        return error_message
        

def register_db(index, title, url, summary):
    date = datetime.today().strftime("%Y%m%d")
    doc_ref = db.collection("scraping").document(f"{date}-{index}")
    doc_ref.set({"DATE": f"{date}", "TITLE": f"{title}", "URL": f"{url}","summary": f"{summary}"})
    


st.title("Qiita_scraping")
st.write("要約を希望する記事をチェックボックスで選択してください。")

scraping_data = scraping()

df = pd.DataFrame(scraping_data, columns=["TITLE", "URL"])
df[["CHECK"]] = False
df = df[["CHECK", "TITLE", "URL"]]
df = st.data_editor(df)

# "CHECK"カラムにチェックが入ったものだけを再表示
if len(df[df["CHECK"] == True]) != 0:
    df = df[df["CHECK"] == True]
    st.write("以下の記事を要約します。よろしければ下の実行ボタンを押してください。")
    df_view = st.dataframe(df, width=800, height=50 + len(df[df["CHECK"] == True]) * 50)

title_list = df["TITLE"].tolist()
url_list = df["URL"].tolist()
sentence_list = get_sentence_list(url_list)
exec_button = st.button("実行")

if exec_button:
    for index, title, url, sentence in zip(range(len(title_list)), title_list, url_list, sentence_list):
        st.write(f"タイトル：{title}")
        st.write(f"URL：{url}")
        st.write(f"本文：{sentence}")
        summary = summarize_sentence(sentence)
        st.write(f"要約文：{summary}")
        index += 1
        register_db(index, title, url, summary)
    st.write("データ登録完了しました。")




st.sidebar.title("データベース検索")

keyword = st.sidebar.text_input("検索ワードを入力してください。タイトル、要約に含まれるものを抽出します。\n"
                                "日付（例：20240930）でも検索できます。"
                                )

if keyword:
    doc_ref = db.collection("scraping")
    docs = doc_ref.stream()
    no_keyword = True
    for doc in docs:
        doc_data = doc.to_dict()
        serch_title = doc_data["TITLE"]
        serch_url= doc_data["URL"]
        serch_summary = doc_data["summary"]
        # keywordが日付（doc.id）、タイトル、要約の中に含まれるかを調べる
        s_i = re.search(keyword, doc.id)
        s_t = re.search(keyword, serch_title)
        s_s = re.search(keyword, serch_summary)
        # 日付、タイトル、要約の中にkeywordが一つでも含まれていれば、その記事のタイトル、URL、要約を表示する
        if s_i != None or s_t != None or s_s != None: 
            st.sidebar.write(f"**タイトル：{serch_title}**")
            st.sidebar.write(f"URL:{serch_url}")
            st.sidebar.write(f"要約：{serch_summary}")
            no_keyword = False
    if no_keyword:    
        st.sidebar.write("情報が見つかりませんでした。")
    





   
