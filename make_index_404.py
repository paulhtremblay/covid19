import os
import textile

from jinja2 import Environment, select_autoescape, FileSystemLoader

from slugify import slugify

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

ENV.filters['slugify'] = slugify

def make_index():
    if not os.path.isfile(os.path.join('home_page', 'script')):
        script = ''
        div = ''
        text_commentary = ''
    else:
        with open('home_page/script', 'r') as read_obj:
            script = ''.join(read_obj.readlines())
        with open('home_page/div', 'r') as read_obj:
            div = ''.join(read_obj.readlines())
        with open('home_page/text.txt', 'r') as read_obj:
            text_commentary = ''.join(read_obj.readlines())
            text_commentary = textile.textile(text_commentary )
    t = ENV.get_template('index.j2')
    html = t.render(
            page_class_attr = ["home"],
            script = script,
            div = div,
            text_commentary = text_commentary
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
