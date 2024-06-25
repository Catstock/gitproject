from html.parser import HTMLParser
from html import unescape
# 使用 color_name_to_rgb 来将颜色名称转换为 RGB 元组
def color_name_to_rgb(color_name):
    from matplotlib import colors
    return tuple(map(lambda x: int(x * 255), colors.to_rgba(color_name)[:3]))
class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.bold = False
        self.color = None

    def handle_starttag(self, tag, attrs):
        if tag == 'b':
            self.bold = True
        if tag == 'font':
            for attr, value in attrs:
                if attr == 'color':
                    try:
                        self.color = tuple(map(int, value.split(',')))
                    except ValueError:
                        self.color = color_name_to_rgb(unescape(value))

    def handle_endtag(self, tag):
        if tag == 'b':
            self.bold = False
        if tag == 'font':
            self.color = None

    def handle_data(self, data):
        self.result.append((data, self.bold, self.color))