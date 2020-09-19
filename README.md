# mlit
国土交通省 自動車不具合情報クローラー

**取得したデータは[利用規約](https://www.mlit.go.jp/jidosha/carinf/rcl/announce.html)を守ってご利用ください**

# usage

事前にPython 3.7を用意してください。

```
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ python mlit/crawler.py path/to/csv
```

デフォルトでは10秒おきに検索結果の1ページをクロールします。
変更したい場合は
```
(.venv) $ python mlit/crawler.py path/to/csv -i (秒数)
```
で変更してください。


