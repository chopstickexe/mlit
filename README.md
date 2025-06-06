# mlit
国土交通省 自動車不具合情報クローラー

**取得したデータは[利用規約](https://www.mlit.go.jp/jidosha/carinf/rcl/announce.html)を守ってご利用ください**

## 外為法該非判定 / Foreign Exchange Law Compliance
このプロジェクトは外為法に基づく該非判定を実施済みです。詳細は[FOREIGN_EXCHANGE_COMPLIANCE.md](FOREIGN_EXCHANGE_COMPLIANCE.md)をご確認ください。

**判定結果**: 非該当（規制対象外）
- 公開されている自動車安全情報の取得のため
- 軍事転用可能性がない消費者向け情報
- 自動コンプライアンスチェック機能搭載

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


