// 広告リンクの置き場所。ASPの管理画面でコピーしたリンクのHTMLを、キーごとに貼り付ける。
// 空のままのキーは、記事上に何も表示されない（提携承認前でもページは壊れない）。
const AFF_LINKS = {
  poimitsu: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEK9E+40OEBM+5Y1K+5ZEMP" rel="nofollow">
<img border="0" width="300" height="250" alt="" src="https://www27.a8.net/svt/bgt?aid=261019922243&wid=003&eno=01&mid=s00000027740001005000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4BEK9E+40OEBM+5Y1K+5ZEMP" alt="">`, // ぽいみつ 不用品回収の無料一括見積もり（A8.net）
  poimitsu_text: ``,
  otakiage: `<a href="https://t.afi-b.com/visit.php?a=310103a-x340547m&p=n997772N" rel="nofollow"><img src="https://www.afi-b.com/upload_image/10103-1533815792-3.jpg" width="300" height="250" style="border:none;" alt="みんなのお焚き上げ" /></a><img src="https://t.afi-b.com/lead/310103a/n997772N/x340547m" width="1" height="1" style="border:none;" />`, // みんなのお焚き上げ（afb）※社名・商標でのリスティング出稿NG
  otakiage_text: ``,
};

document.querySelectorAll("[data-aff]").forEach((el) => {
  const html = AFF_LINKS[el.dataset.aff];
  if (html) el.innerHTML = html;
  else el.remove();
});
