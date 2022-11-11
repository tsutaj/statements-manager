import re
import sys

ENGLISH_UNAVAILABLE = (
    "<!-- begin en only -->\n"
    + '<p style="font-style:italic">English text is not available in this practice contest.</p>\n'
    + "<!-- end en only -->\n"
)


def sub_while_unchange(pattern, repl, str):
    prv_str = ""
    while not prv_str == str:
        prv_str = str
        str = re.sub(pattern, repl, str)
    return str


def postprocess(html_text):
    html_text = re.sub("<blockquote>\n<p>", "<blockquote>", html_text)
    html_text = re.sub("</p>\n</blockquote>", "</blockquote>", html_text)
    html_text = re.sub(r"<pre(.*)><code(.*)>", r"<blockquote>", html_text)
    html_text = re.sub(r"</code></pre>", r"</blockquote>", html_text)
    html_text = re.sub(r"\{,\}", ",", html_text)

    html_text = re.sub(r"\$(.*?)\$", r"<i>\1</i>", html_text)
    html_text = sub_while_unchange(
        r"<i>(.*?)\_\{(.*?)\}(.*?)</i>", r"<i>\1<sub>\2</sub>\3</i>", html_text
    )
    html_text = sub_while_unchange(
        r"<i>(.*?)\_(.)(.*?)\</i>", r"<i>\1<sub>\2</sub>\3</i>", html_text
    )
    html_text = sub_while_unchange(
        r"<i>(.*?)\^\{(.*?)\}(.*?)</i>", r"<i>\1<sup>\2</sup>\3</i>", html_text
    )
    html_text = sub_while_unchange(
        r"<i>(.*?)\^(.)(.*?)\</i>", r"<i>\1<sup>\2</sup>\3</i>", html_text
    )

    html_text = re.sub(r"\\leq", r"&le;", html_text)
    html_text = re.sub(r"\\le", r"&le;", html_text)
    html_text = re.sub(r"\\geq", r"&ge;", html_text)
    html_text = re.sub(r"\\ge", r"&ge;", html_text)
    html_text = re.sub(r"\\neq", r"&ne;", html_text)
    html_text = re.sub(r"\\ne", r"&ne;", html_text)
    html_text = re.sub(r"\\ldots", r"...", html_text)
    html_text = re.sub(r"\\vdots", r"...", html_text)
    html_text = re.sub(r"\\sum", r"&Sigma;", html_text)
    html_text = re.sub(r"\\min", r"min", html_text)
    html_text = re.sub(r"\\max", r"max", html_text)
    html_text = re.sub(r"\\in", r"&isin;", html_text)
    html_text = re.sub(r"\\times", "×", html_text)

    html_text = re.sub("<table>", '<table class="c_table">', html_text)
    html_text = re.sub("<th>", '<th class="c_th">', html_text)
    html_text = re.sub("<td>", '<td class="c_td">', html_text)
    html_text = re.sub("<thead>", '<thead class="c_thead">', html_text)

    # add 'ja only' and 'en only' tag
    # html_text = re.sub(r'<h3>(?![Input|Output|Problem|入力|出力|入出力|Sample])(.*)</h3>', r'<h3>\1</h3>\n<div>\n' +
    #                    ENGLISH_UNAVAILABLE + '<!-- begin ja only -->\n', html_text)
    html_text = re.sub(
        r"<h3>",
        r"</div>\n<h3>",
        html_text,
    )
    html_text = re.sub(
        r"</h3>",
        r"</h3>\n<div>",
        html_text,
    )
    html_text = re.sub(
        r"</div>\n<h3>?",
        r"<h3>",
        html_text,
        1,
    )
    html_text = re.sub(
        r"([\s\S]*)</td>",
        r"\1</div>\n</td>",
        html_text,
        1,
    )
    html_text = re.sub(
        r"([\s\S]*?)<h2>(.*?)</h2>(\s*?)</div>([\s\S]*?)<h3>",
        r"\1</div>\n<h2>\2</h2>\3\4<h3>",
        html_text,
    )
    html_text = re.sub(
        "<h3></h3>",
        "",
        html_text,
    )
    return html_text


def main():
    html_text = sys.stdin.read()
    print(postprocess(html_text))


if __name__ == "__main__":
    main()
