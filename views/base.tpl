% setdefault("title", "")

<!doctype html>
<html lang="en" dir="ltr">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>
			% if title:
				{{title}} | twbot
			% else:
				twbot
			% end
		</title>

		<link rel="stylesheet" href="/static/css/style.css">
	</head>

	<body>
		<%
			print("first run is " + str(is_first_run))

			if is_first_run:
				include("first-run.tpl")
			elif is_first_run == False:
		%>
				<nav class="nav">
					<header>twbot</header>

					<a class="{{(title == "Home" and "current-link") or ""}}" href="/">Home</a>
				</nav>

				<section class="content">
					{{!base}}
				</section>
			% else:
				<p>There is a problem with the database, please reset it and any twbot processes and try again.</p>
			% end
	</body>
</html>
