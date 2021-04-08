# flake8: noqa
template_html = """
<!DOCTYPE html>
<html lang="ja">
  <head>
    <title>Problem Statement</title>
    <meta charset="utf-8">
    <style type="text/css">
      html {
          color: #222222;
          font-family: 'Times New Roman', 'ヒラギノ角ゴ Pro W3', 'Hiragino Kaku Gothic Pro', 'メイリオ', meiryo, Verdana, "lr oSVbN";
      }

      h1{
          font-size:16pt;
          border-bottom: solid 2px #e0e0e0;
          margin-bottom:20px;
      }

      h2{
          font-size:14pt;
          border-bottom: solid 2px #e0e0e0;
          margin-bottom:20px;
          margin-top:20px;
      }

      h3{
          font-size:14pt;
          border-bottom: solid 2px #e0e0e0;
          margin-bottom:20px;
          margin-top:20px;
      }

      h4{
          font-size:13pt;
          margin-bottom:20px;
          margin-top:20px;
      }

      h5{
          font-size:12pt;
          margin-bottom:20px;
          margin-top:20px;
      }

      b{
          font-weight:bold;
      }

      p{
          font-size:12pt;
          font-family: 'Times New Roman', 'ヒラギノ角ゴ Pro W3', 'Hiragino Kaku Gothic Pro', 'メイリオ', meiryo, Verdana, "lr oSVbN"; 
      }

      li{
          font-size:12pt;
          font-family: 'Times New Roman', 'ヒラギノ角ゴ Pro W3', 'Hiragino Kaku Gothic Pro', 'メイリオ', meiryo, Verdana, "lr oSVbN"; 
      }

      pre {
          font-size:11pt;
          padding: 8px;
          border: solid 1px #e0e0e0;
          border-radius: 4px;
      }

      pre > code {
          color: #222222;
      }

      .testcase_pre{
          font-size:11pt;
          padding: 8px;
          border: solid 1px #e0e0e0;
          border-radius: 4px;
          overflow:auto;
          max-width:480;
          max-height:340;
      }

      .error_pre{
          font-size:11pt;
          padding: 8px;
          border: solid 1px #f0e0e0;
          border-radius: 4px;
          overflow:auto;
          max-height:340;
          background-color:#ffeeee;
      }

      .table tbody > tr > td.vert-aligned {
          vertical-align: middle;
      }

      code {
        font-size: 87.5%;
        color: #e83e8c;
        word-break: break-word;
      }
    </style>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {
                inlineMath: [["$", "$"]],
                processEscapes: true,
                processClass: 'input-format|language-input-format'
            }
        });
    </script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-AMS_CHTML">
    </script>
  </head>
  <body>
    {@task.statements}
  </body>
</html>
"""

template_pdf_options = {
    "page-size": "A4",
    "margin-top": 24,
    "margin-right": 16,
    "margin-bottom": 16,
    "margin-left": 16,
    "encoding": "UTF-8",
    "javascript-delay": "3000",
    # "header-center": "hoge",
    # "header-font-size": 10,
    # "header-spacing": 12,
    # "footer-center": "[page] / [toPage]",
    # "footer-font-size": 8,
    # "footer-spacing": 8,
    "enable-local-file-access": None,
}
