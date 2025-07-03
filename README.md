# qiita_scrapingとは

Qiitaのトレンド記事のタイトルとURLをスクレイピングして30件表示させたのちに、自分が気になる記事にチェックを入れて実行ボタンを押します。
そうすると自分がチェックを入れた記事の本文とそれをchat-gptが要約した文章が表示されます。また、同時にDBにタイトル、URL、要約文が保存されます。
過去に保存した記事のタイトル、URL、要約文を検索することもできます。
（ただし、経済的理由で2000文字を超えると要約できない仕様にしています。）

# URL

https://qiita-scraping.onrender.com

# 使用技術

Python 3.9.13

Streamlit 1.27.2

BeautifulSoup 4.12.2

pandas  2.1.1

openai 

firebase

# 機能一覧


スクレイピング機能(BeautifulSoup)

要約機能(Web-api)

保存機能（firebase）

検索機能

