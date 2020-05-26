import datetime
import os
import ssl
import urllib.request
import json

from jinja2 import Environment, select_autoescape, FileSystemLoader

with urllib.request.urlopen("https://api.github.com/repos/paulhtremblay/covid19/contributors") as url:
    contributors = json.loads(url.read().decode())

ENV = Environment(
    loader=FileSystemLoader(os.path.join(
        os.path.split(os.path.abspath(__file__))[0], 
        'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

def make_about():
    t = ENV.get_template('about.j2')
    html = t.render(title = 'about', 
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            page_title = 'About this site',
            contributors = contributors
            )
    with open(os.path.join('html_temp', 'about.html'), 'w') as write_obj:
        write_obj.write(html)

if __name__ == '__main__':
    make_about()
