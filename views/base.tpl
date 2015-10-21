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
		<nav class="nav">
			<header class="nav__header">twbot</header>

			<a class="nav__link {{(title == "Home" and "nav__link--current") or ""}}" href="/">Home</a>
		</nav>

		<section class="content">
			{{!base}}
		</section>
	</body>
</html>
