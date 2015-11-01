% setdefault("title", "")

<!doctype html>
<html lang="en" dir="ltr">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>
			% if title:
				{{title}} · twbot
			% else:
				twbot
			% end
		</title>

		<link rel="stylesheet" href="/static/css/style.css">
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
						<a class="{{(title == "Administrate" and "current-link" or "")}}" href="/admin">{{admin_username}}</a>
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
