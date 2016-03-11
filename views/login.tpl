% rebase("base.tpl", title="Log in")

% if req.GET.get("message"):
	<div class="form-warning">
		<strong>{{req.GET["message"]}}</strong>
	</div>
% end

<form id="form-login" action="/login" method="post" autocomplete="off">
	<label for="login-username">Username:</label>
	<input name="username" id="login-username" type="username" required>
	<label for="login-password">Password:</label>
	<input name="password" id="login-password" type="password" required>
	<input type="submit">
</form>
