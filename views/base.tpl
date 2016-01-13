% setdefault("title", "")

<!doctype html>
<html lang="en" dir="ltr">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>
			% if title:
				{{title}} &#183; twbot
			% else:
				twbot
			% end
		</title>

		<link rel="stylesheet" href="/static/css/style.css">

		<link rel="icon" sizes="16x16" href="/static/img/twbot-icon-16.png" type="image/png">
		<link rel="icon" sizes="32x32" href="/static/img/twbot-icon-32.png" type="image/png">
		<link rel="icon" sizes="48x48" href="/static/img/twbot-icon-48.png" type="image/png">
		<link rel="icon" sizes="64x64" href="/static/img/twbot-icon-64.png" type="image/png">
	</head>

	<body>
		<%
			if is_first_run:
				include("first-run.tpl")
			elif is_first_run == False:
		%>
				<nav class="nav">
					<header>twbot</header>

					<a class="{{(title == "Home" and "current-link") or ""}}" href="/">Home</a>
					<a class="{{(title == "About" and "current-link") or ""}}" href="/about">About</a>
					<div class="flex-spacer"></div>
					% if is_logged_in:
						<a class="{{(title == "Administration" and "current-link" or "")}}" href="/admin">{{admin_username}}</a>
					% else:
						<a class="{{(title == "Log in" and "current-link") or ""}}" href="/login">Log in</a>
					% end
				</nav>

				<section class="content">
					{{!base}}
				</section>
			% else:
				<p>There is a problem with the database, please reset it and any twbot processes and try again.</p>
			% end
	</body>
</html>
