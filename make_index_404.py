import datetime
import os

from jinja2 import Environment, select_autoescape, FileSystemLoader


ENV = Environment(
    loader=FileSystemLoader([
          os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
          os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes'),
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

def make_index():
    t = ENV.get_template('index.j2')
    html = t.render(date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            page_class_attr = ["home"],
            )
    with open(os.path.join('html_temp', 'index.html'), 'w') as write_obj:
        write_obj.write(html)

def make_404():
    t = ENV.get_template('404.j2')
    html = t.render(page_title = 'Error',
            page_class_attr = ["error"],
            )
    with open(os.path.join('html_temp', '404.html'), 'w') as write_obj:
        write_obj.write(html)


if __name__ == '__main__':
    make_index()
    make_404()
