<div class="first-run">
	<h1>Welcome to twbot</h1>
	% if first_run_step == 0:
		<h2>Set up your account</h2>

		% if req.GET.get("message"):
			<div class="form-warning">
				<strong>{{req.GET["message"]}}</strong>
			</div>
		% end

		<form id="form-register" action="/register" method="post" autocomplete="off">
			<label for="reg-username">Username:</label>
			<input type="username" name="username" id="reg-username" required>
			<label for="reg-password">Password:</label>
			<input type="password" name="password" id="reg-password" required>
			<input type="submit" value="Next">
		</form>
	% elif first_run_step == 1:
		<h2>Connect to Twitter</h2>

		<h3><a target="twbot-twitter" title="Add phone number" href="https://twitter.com/settings/add_phone">Add your phone number</a></h3>
		<ul>
			<li>You must add your phone number to your Twitter account before you can register an app</li>
			<li>Use your real number, as Twitter will send you a confirmation text to verify the number</li>
		</ul>

		<h3><a target="twbot-twitter" title="Create Twitter app" href="https://apps.twitter.com">Create the Twitter app</a></h3>
		<ul>
			<li>By creating a Twitter application, twbot will be able to access a Twitter account and run properly</li>
			<li>When entering the application name, enter &lsquo;twbot&rsquo; prefixed by the current Twitter account so as to prevent name clashes with other twbot users (e.g. &lsquo;@peter_banterson twbot&rsquo; for user @peter_banterson)</li>
			<li>You must fill the description and website fields to proceed, however twbot ignores these fields</li>
		</ul>

		<h3><a target="twbot-twitter" title="Retrieve your app details" href="https://apps.twitter.com">Retrieve your app details</a></h3>
		<ol>
			<li>Select your newly created app</li>
			<li>Open the &lsquo;Keys and Access Tokens&rsquo; tab</li>
			<li>Enter your consumer key and secret below</li>
		</ol>

		% if req.GET.get("message"):
			<div class="form-warning">
				<strong>{{req.GET["message"]}}</strong>
			</div>
		% end

		<form id="form-register-tokens" action="/register-tokens" method="post" autocomplete="off">
			<label for="reg-tokens-key">Consumer Key:</label>
			<input name="api-key" id="reg-tokens-key" type="text" required>
			<label for="reg-tokens-secret">Consumer Secret:</label>
			<input name="api-secret" id="reg-tokens-secret" type="password" required>
			<input type="submit" value="Next">
		</form>
	% elif first_run_step == 2:
		<h3><a target="twbot-twitter" title="Authorization URL" href="{{auth_url}}">Authorise twbot</a></h3>

		<p>Finally, please enter the PIN you are given</p>

		<form id="form-register-pin" action="/register-pin" method="post" autocomplete="off">
			<label for="reg-pin">PIN:</label>
			<input name="pin" type="password" inputmode="numeric" maxlength="7" required>
			<input type="submit" value="Next">
		</form>
	% elif first_run_step == 3:
		<h3>Congratulations, you have set up twbot! You may now log in.</h3>

		<form action="/finish-setup" method="post">
			<input type="submit" value="Okay">
		</form>
</div>
