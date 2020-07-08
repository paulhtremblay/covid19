from bokeh.io import show
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot


def square_graph():
    output_file("lines.html")
    p=figure(title="Squares", x_axis_label='x', y_axis_label='Square of x')
    p.line(x=(x for x in range(0,10)), y = (x**2 for x in range(0,10)),linwidth=2)
    show(p)