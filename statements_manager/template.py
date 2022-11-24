# flake8: noqa
default_template_html = """
<!DOCTYPE html>
<html lang="ja">

<head>
    <title>Problem Statement</title>
    <meta charset="utf-8">
    <link href='http://fonts.googleapis.com/css?family=Noto+Serif' rel='stylesheet' type='text/css'>
    <style type="text/css">
        html {
            color: #222222;
            font-family: "Noto Serif";
        }

        h1 {
            font-size: 16pt;
            border-bottom: solid 2px #e0e0e0;
            margin-bottom: 20px;
        }

        h2 {
            font-size: 14pt;
            border-bottom: solid 2px #e0e0e0;
            margin-bottom: 20px;
            margin-top: 20px;
        }

        h3 {
            font-size: 14pt;
            border-bottom: solid 2px #e0e0e0;
            margin-bottom: 20px;
            margin-top: 20px;
        }

        h4 {
            font-size: 13pt;
            margin-bottom: 20px;
            margin-top: 20px;
        }

        h5 {
            font-size: 12pt;
            margin-bottom: 20px;
            margin-top: 20px;
        }

        b {
            font-weight: bold;
        }

        p {
            font-size: 12pt;
        }

        li {
            font-size: 12pt;
        }

        pre {
            font-size: 11pt;
            padding: 8px;
            border: solid 1px #e0e0e0;
            border-radius: 4px;
        }

        code {
            color: #e83e8c;
        }

        code.language-input-format {
            color: #222222;
        }

        .testcase_pre {
            font-size: 11pt;
            padding: 8px;
            border: solid 1px #e0e0e0;
            border-radius: 4px;
            overflow: auto;
            max-width: 480;
            max-height: 340;
        }

        .error_pre {
            font-size: 11pt;
            padding: 8px;
            border: solid 1px #f0e0e0;
            border-radius: 4px;
            overflow: auto;
            max-height: 340;
            background-color: #ffeeee;
        }

        .table tbody>tr>td.vert-aligned {
            vertical-align: middle;
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
    <script type="text/javascript"
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.9/MathJax.js?config=TeX-AMS_CHTML">
        </script>
</head>

<body>
    {% for problem in problemset.problems %}
    <div {% if not loop.last %} style="page-break-after: always" {% endif %}>
        {@problem.statement}
    </div>
    {% endfor %}
</body>

</html>
"""

default_template_markdown = """
{% for problem in problemset.problems %}

{@problem.statement}

{% if not loop.last %}
---
{% endif %}

{% endfor %}
"""

default_sample_template_html = """
{% if sample_data.input_text is defined %}
    <h3>{% if sample_data.language == "ja" %}入力例{% elif sample_data.language == "en" %}Sample Input{% endif %} {% if sample_data.do_numbering %}{{ sample_data.i_sample }}{% endif %}</h3>
    <pre>{{ sample_data.input_text }}</pre>
{% endif %}

{% if sample_data.output_text is defined %}
    <h3>{% if sample_data.language == "ja" %}出力例{% elif sample_data.language == "en" %}Sample Output{% endif %} {% if sample_data.do_numbering %}{{ sample_data.i_sample }}{% endif %}</h3>
    <pre>{{ sample_data.output_text }}</pre>
{% endif %}

{% if sample_data.md_text is defined %}
{{ sample_data.md_text }}
{% endif %}

{% if sample_data.explanation_text is defined %}
{{ sample_data.explanation_text }}
{% endif %}
"""

template_pdf_options = {
    "encoding": "UTF-8",
    "page-size": "A4",
    "margin-top": 24,
    "margin-right": 16,
    "margin-bottom": 16,
    "margin-left": 16,
    "javascript-delay": "3000",
    "enable-local-file-access": None,
    "disable-smart-shrinking": None,
    "debug-javascript": None,
}
