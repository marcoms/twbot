% rebase("base.tpl", title="Settings")

% if is_logged_in:
	<p>You will be required to log in once again after updating these settings</p>

	% if req.GET.get("message"):
		<div class="warning">
			<strong>{{req.GET["message"]}}</strong>
		</div>
	% end

	<form id="form-config" action="/update-meta" method="post">
		<label for="config-username">Username:</label>
		<input id="config-username" name="username" type="text" value="{{username}}">

		<label for="config-password">Password:</label>
		<input id="config-password" name="password" type="text">

		<label for="config-api-key">API key:</label>
		<input id="config-api-key" name="api-key" type="text" value="{{api_key}}">

		<label for="config-api-secret">API secret:</label>
		<input id="config-api-secret" name="api-secret" type="password">

		<label for="config-access-key">Access key:</label>
		<input id="config-access-key" name="access-key" type="text" value="{{access_key}}">

		<label for="config-access-secret">Access secret:</label>
		<input id="config-access-secret" name="access-secret" type="password">

		<input type="submit" value="Update">
	</form>

	<p>The following actions cannot be undone!</p>

	<form action="/rm-tweets-dms" method="post">
		<input type="submit" value="Remove all tweets and direct messages">
	</form>

	<form action="/reset" mothod="post">
		<input type="submit" value="Reset all data">
	</form>
<%
else:
	include("login-warning.tpl")
end
%>