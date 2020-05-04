import datetime
with open('html_temp/states_deaths_rt.js', 'r') as read_obj:
    states1_js = ''.join(read_obj.readlines())
with open('html_temp/states_deaths_rt.div', 'r') as read_obj:
    states1_div = ''.join(read_obj.readlines())
with open('html_temp/states_cases_rt.js', 'r') as read_obj:
    states2_js = ''.join(read_obj.readlines())
with open('html_temp/states_cases_rt.div', 'r') as read_obj:
    states2_div = ''.join(read_obj.readlines())

html_raw = """
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
    <h1>States Rate of Growth Deaths</h1>
    <p>updated: {date}</p>
    <p><a href = "index.html">home</a></p>
    <p><a href = "states_cases_rt.html">cases</a></p>
        {states1_div}
    </body>
</html>
""".format(
        states1_js = states1_js, 
        states1_div = states1_div,
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

html_raw2 = """
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>RT Cases US</title>

	<script src="https://cdnjs.cloudflare.com/ajax/libs/bokeh/2.0.2/bokeh.min.js">
	</script>

        <!-- COPY/PASTE SCRIPT HERE -->

        {states2_js}

    </head>
    <body>
    <h1>States Rate of Growth Cases</h1>
    <p>updated: {date}</p>
    <p><a href = "index.html">home</a></p>
    <p><a href = "states_deaths_rt.html">deaths</a></p>
        {states2_div}
    </body>
</html>
""".format(
        states2_js = states2_js, 
        states2_div = states2_div,
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )


with open('html_temp/states_deaths_rt.html', 'w') as write_obj:
    write_obj.write(html_raw)
with open('html_temp/states_cases_rt.html', 'w') as write_obj:
    write_obj.write(html_raw2)
