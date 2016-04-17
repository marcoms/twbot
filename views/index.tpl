% rebase("base.tpl", title="Leaderboard")

<%
players = c.execute("SELECT * FROM players;").fetchall()

if players:
%>
	<div class="list-mini">
		<%
		# only display a maximum of 10 players
		players = players[:10]

		ranked_players = []

		for player in players:
			twitter_user = api.get_user(user_id=player["id"])
			handle = twitter_user.screen_name
			points = get_points(player["id"])

			ranked_players.append({"handle": handle, "points": points})
		end

		ranked_players = sorted(ranked_players, key=lambda ranked_player: ranked_player["points"])
		for rank, ranked_player in enumerate(ranked_players):
			rank += 1

			handle = ranked_player["handle"]
			points = ranked_player["points"]
		%>
			<div>
				<div>#{{rank}}: <a href="/players/{{handle}}">@{{handle}}</a></div>
				<div class="spacer"></div>
				<div>{{points}} points</div>
			</div>
		% end
	</div>
% else:
	<p>No players</p>
% end