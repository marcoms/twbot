% rebase("base.tpl", title="Players")

% if handle:
	<a href="/players" title="Players">&lt; All players</a>
	<%
	try:
		twitter_user = api.get_user(screen_name=handle)
	except:
		twitter_user = None
	end

	if twitter_user:
		player_id = twitter_user.id
		players = c.execute("SELECT * FROM players WHERE id = ?;", (player_id,)).fetchall()
		player = players[0] if players else None
	else:
		player = None
	end

	if player:
		answers = c.execute("SELECT * FROM answers WHERE player_id = ?;", (player["id"],)).fetchall()
		points = get_points(player_id)
%>
		<h2>@{{handle}}</h2>
		<p>Points: {{points}}</p>
		<a target="twbot-twitter" href="https://twitter.com/{{handle}}" title="Twitter profile">Twitter profile</a>
	% else:
		<div class="warning">
			<strong>No such player @{{handle}}</strong>
		</div>
	<% end
else:
	%>
	<div class="list-mini">
	<%
	players = c.execute("SELECT * FROM players;").fetchall()
	players = [dict(player) for player in players]
	for player in players:
		twitter_user = api.get_user(user_id=player["id"])
		player["handle"] = twitter_user.screen_name

	players = sorted(players, key=lambda player: player["handle"])

	for player in players:
	%>
		<div>
			<a href="/players/{{player["handle"]}}">@{{player["handle"]}}</a>
		</div>
	% end
	</div>
% end