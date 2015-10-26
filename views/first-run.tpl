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
		<h4>Go to <a href="https://twitter.com/settings/add_phone">twitter.com/settings/add_phone</a></h4>
		<ul>
			<li>You must add your phone number to your Twitter account before you can register an app</li>
			<li>Use your real number, as Twitter will send you a confirmation text to verify the number</li>
		</ul>

		<h3>Create the Twitter app</h3>
		<h4>Go to <a href="https://apps.twitter.com/">apps.twitter.com</a></h4>
		<ul>
			<li>By creating a Twitter application, twbot will be able to access a Twitter account and run properly</li>
			<li>When entering the application name, enter &lsquo;twbot&rsquo; prefixed by the current Twitter account so as to prevent name clashes with other twbot users (e.g. &lsquo;Linus__Torvalds-twbot&rsquo; for user @Linus__Torvalds)</li>
			<li>You must fill the Description and Website fields to proceed, however their contents are not important for twbot applications</li>
		</ul>
	% end
</div>
