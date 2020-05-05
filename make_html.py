with open('html_temp/states1.js', 'r') as read_obj:
    states1_js = ''.join(read_obj.readlines())
with open('html_temp/states1.div', 'r') as read_obj:
    states1_div = ''.join(read_obj.readlines())

html_raw = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Covid 19 Deaths</title>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/bokeh/2.0.2/bokeh.min.js"></script>

        <!-- COPY/PASTE SCRIPT HERE -->

        {states1_js}

    </head>

    <body>

        <h1>Covid 19 Deaths</h1>

        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="states_cases_rt.html">Infection Rate Growth</a></li>
                <li><a href="states_deaths.html">Deaths</a></li>
                <li><a href="states_deaths_rt.html">Death Rate Growth</a></li>
                <li><a href="wa.html">Deaths In Washington State</a></li>
            </ul>
        </nav>

        {states1_div}

    </body>
</html>
""".format(
        states1_js = states1_js, 
        states1_div = states1_div,
        )

with open('html_temp/states_deaths.html', 'w') as write_obj:
    write_obj.write(html_raw)
