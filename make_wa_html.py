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
        <title>Covid 19 Deaths in Washington State</title>
        <link rel="stylesheet" href="/styles/site.css">

        <script src="https://cdnjs.cloudflare.com/ajax/libs/bokeh/2.0.2/bokeh.min.js"></script>

        <!-- COPY/PASTE SCRIPT HERE -->

        {states1_js}

    </head>
    <body>
        <header>

            <div class="siteName">Covid 19 Data: Cases, Deaths, and Changes by State</div>

            <h1>Covid 19 Deaths in Washington State</h1>

            <p>updated: {date}</p>

            <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="states_cases_rt.html">Infection Rate Growth</a></li>
                    <li><a href="states_deaths.html">Deaths</a></li>
                    <li><a href="states_deaths_rt.html">Death Rate Growth</a></li>
                    <li><a href="wa.html">Deaths In Washington State</a></li>
                </ul>
            </nav>

        </header>

        <main>
            {states1_div}
        </main>

        <footer>
            <address>
                <p>created by <a href="https://github.com/paulhtremblay">Henry Tremblay</a></p>
                <p><a href="https://github.com/paulhtremblay/covid19">contributions welcome</a></p>
            </address>
        </footer>

    </body>
</html>
""".format(
        states1_js = states1_js, 
        states1_div = states1_div
        )

with open('html_temp/wa.html', 'w') as write_obj:
    write_obj.write(html_raw)
