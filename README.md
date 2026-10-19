# 親と実家の相談室

親の介護、実家の片づけ、遺品整理など、家族のこれからについての基礎知識サイト。GitHub Pagesで公開する静的HTML。

公開URL: https://g-monotukun.github.io/parents-consultation/

## 編集ルール
- 資料請求・無料見積もり・無料査定など、ユーザーの負担がない入口を中心に紹介する
- 「最安」「No.1」「必ず」など、比較優良・断定の表現を使わない
- 制度・料金・条件は断定せず、自治体や公式サイトでの確認を促す
- 親本人の意思を尊重する書き方にする（不安をあおらない）

## ページの更新方法
- 記事の原稿は `src/articles/`、固定ページは `src/` に置き、`python3 build.py` で全ページを生成する
- 広告リンクは `links.js` に、商品紹介は `build.py` の `PRODUCTS` に登録する

## Threads
Threads アカウントは全サイト共通。投稿は claude-affiliate リポジトリの `threads/queue.json` で管理する。
