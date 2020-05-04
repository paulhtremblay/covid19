from bokeh.io import show

from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.embed import components
from bokeh.layouts import gridplot

p1 = figure()
p1.line([1,2, 3, 4], [1, 2, 3,4])
p2 = figure()
p2.line([1,2, 3, 4], [1, 2, 3,4])
p3 = figure()
p3.line(x = [1, 2], y = [1, 2])
grid = gridplot([p1, p2], ncols = 4)


script, div = components(grid)
script2, div2 = components(p3)

html_raw = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Bokeh Scatter Plots</title>

	<script src="https://cdnjs.cloudflare.com/ajax/libs/bokeh/2.0.2/bokeh.min.js">
	</script>

        <!-- COPY/PASTE SCRIPT HERE -->

        {states1_js}

    </head>
    <body>
    <p>is not working</p>
        {states_div}
    </body>
</html>
""".format(
        script = script, 
        div = div,
        script2 = script2, 
        div2 = div2
        )

with open('html_dir/states.html', 'w') as write_obj:
    write_obj.write(html_raw)
