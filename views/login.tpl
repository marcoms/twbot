% rebase("base.tpl", title="Log in")

% if b.request.GET.get("message"):
	<div class="form-warning">
		<strong>{{b.request.GET.get("message")}}</strong>
	</div>
% end

<form id="form-login" action="/login" method="post" autocomplete="off">
	<label for="login-username">Username:</label>
	<input name="username" id="login-username" type="username">
	<label for="login-password">Password:</label>
	<input name="password" id="login-password" type="password">
	<input type="submit">
</form>
