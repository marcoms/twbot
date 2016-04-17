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
		<script src="/static/js/main.js"></script>

		<link rel="icon" sizes="16x16" href="/static/img/twbot-icon-16.png" type="image/png">
		<link rel="icon" sizes="32x32" href="/static/img/twbot-icon-32.png" type="image/png">
		<link rel="icon" sizes="48x48" href="/static/img/twbot-icon-48.png" type="image/png">
		<link rel="icon" sizes="64x64" href="/static/img/twbot-icon-64.png" type="image/png">
	</head>

	<body>
		<%
		if first_run_step > -1:
			include("first-run.tpl")
		elif first_run_step == -1:
		%>
			<nav class="nav">
				<div class="nav-contents">
					<header>twbot</header>

					<a class="{{(title == "Leaderboard" and "current-link") or ""}}" href="/">Leaderboard</a>
					<a class="{{(title == "Players" and "current-link") or ""}}" href="/players">Players</a>
					<div class="spacer"></div>
					% if is_logged_in:
						<a class="{{(title == "Questions" and "current-link" or "")}}" href="/questions">Questions</a>
						<a class="{{(title == "Answers" and "current-link" or "")}}" href="/answers">Answers</a>
						<a class="{{(title == "Settings" and "current-link" or "")}}" href="/settings">Settings</a>
						<a class="{{(title == "Log out" and "current-link" or "")}}" href="/logout">Log out</a>
					% else:
						<a class="{{(title == "Log in" and "current-link") or ""}}" href="/login">Log in</a>
					% end
				</div>
			</nav>

			<section class="content">
				{{!base}}
			</section>
		% end
	</body>
</html>
