import datetime
with open('html_temp/deaths_wa.js', 'r') as read_obj:
    states1_js = ''.join(read_obj.readlines())
with open('html_temp/deaths_wa.div', 'r') as read_obj:
    states1_div = ''.join(read_obj.readlines())

html_raw = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>RT US Deaths</title>

	<script src="https://cdnjs.cloudflare.com/ajax/libs/bokeh/2.0.2/bokeh.min.js">
	</script>

        <!-- COPY/PASTE SCRIPT HERE -->

        {states1_js}

    </head>
    <body>
    <h1>Washington</h1>
    <p><a href = "index.html">home</a></p>
    <p>updated: {date}</p>
        {states1_div}
    </body>
</html>
""".format(
        states1_js = states1_js, 
        states1_div = states1_div,
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

with open('html_temp/wa.html', 'w') as write_obj:
    write_obj.write(html_raw)
