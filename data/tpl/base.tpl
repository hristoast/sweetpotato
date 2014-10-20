<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{{title}} | sweetpotato WebUI</title>
        <link rel='icon' type='img/png' href='/static/gnu-cat.png'>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
        <link rel="stylesheet" href="/static/sweetpotato.min.css">
    </head>
    <body>
        <div id="container">
            <div id="main">
                {{!base}}
            </div>
            <div id="lower_nav">
                % include('lower_nav.tpl')
            </div>
        </div>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
    </body>
</html>
