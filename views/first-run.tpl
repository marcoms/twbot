<div class="first-run">
	% if first_run_step == 0:
		<h1>Welcome to twbot</h1>
		<h2>Set up your account</h2>

		<form action="/register" method="post">
			<label class="reg-label" for="reg-username">Username:</label>
			<input type="username" name="username" id="reg-username">
			<label class="reg-label" for="reg-password">Password:</label>
			<input type="password" name="password" id="reg-password">
			<br>
			<input class="reg-submit" type="submit" value="Register">
		</form>
	% elif first_run_step == 1:
		<h1>Connect to Twitter</h1>
	% end
</div>
