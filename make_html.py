with open('html_dir/states1.js', 'r') as read_obj:
    states1_js = ''.join(read_obj.readlines())
with open('html_dir/states1.div', 'r') as read_obj:
    states1_div = ''.join(read_obj.readlines())

html_raw = """
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
    <h1>States</h1>
        {states1_div}
    </body>
</html>
""".format(
        states1_js = states1_js, 
        states1_div = states1_div,
        )

with open('html_dir/states.html', 'w') as write_obj:
    write_obj.write(html_raw)
