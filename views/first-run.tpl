<div class="first-run">
	<h1>Welcome to twbot</h1>
	% if first_run_step == 0:
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
		<h2>Connect to Twitter</h2>


		<h3>Add your phone number</h3>
		<video class="first-run-video" controls loop>
			<source type="video/webm" src="/static/video/adding-phone-number.webm">
			<source type="video/ogg" src="/static/video/adding-phone-number.ogg">
			<source type="video/mp4" src="/static/video/adding-phone-number.mp4">
		</video>

		<h3>Create the Twitter app</h3>
		<video class="first-run-video" controls loop>
			<source type="video/webm" src="/static/video/creating-twitter-app.webm">
			<source type="video/ogg" src="/static/video/creating-twitter-app.ogg">
			<source type="video/mp4" src="/static/video/creating-twitter-app.mp4">
		</video>
	% end
</div>
