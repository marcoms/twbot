<div class="first-run">
	<img title="twbot" src="/static/img/twbot.svg" width="128" height="128">
	<h1>Welcome to twbot</h1>
	% if first_run_step == 0:
		<h2>Set up your account</h2>

		% if req.GET.get("message"):
			<div class="warning">
				<strong>{{req.GET["message"]}}</strong>
			</div>
		% end

		<form action="/register" method="post" autocomplete="off">
			<label for="reg-username">Username:</label>
			<input type="username" name="username" id="reg-username" required>
			<label for="reg-password">Password:</label>
			<input type="password" name="password" id="reg-password" required>
			<input type="submit" value="Next">
		</form>
	% elif first_run_step == 1:
		<h2>Connect to Twitter</h2>

		<h3><a target="twbot-twitter" title="Add phone number" href="https://twitter.com/settings/add_phone">Add phone number</a></h3>
		<ul>
			<li>You must add your phone number to your Twitter account before you can register an app</li>
			<li>Use your real number, as Twitter will send you a confirmation text to verify the number</li>
		</ul>

		<h3><a target="twbot-twitter" title="Create Twitter app" href="https://apps.twitter.com">Create Twitter app</a></h3>
		<ul>
			<li>By creating a Twitter application, twbot will be able to access a Twitter account and run properly</li>
			<li>When entering the application name, enter &lsquo;twbot&rsquo; prefixed by the current Twitter account so as to prevent name clashes with other twbot users (e.g. &lsquo;@peter_banterson twbot&rsquo; for user @peter_banterson)</li>
			<li>You must fill the description and website fields to proceed, however twbot ignores these fields</li>
		</ul>

		<h3><a target="twbot-twitter" title="Set app permissions" href="https://apps.twitter.com">Set app permissions</a></h3>
		<p>In order for twbot to function properly, you will need to set the app permissions.</p>
		<ol>
			<li>Select your app</li>
			<li>Open the &lsquo;Permissions&rsquo; tab</li>
			<li>Set the permissions to &lsquo;Read, Write and Access direct messages&rsquo;</li>
			<li>Go to the &lsquo;Keys and Access Tokens&rsquo; tab</li>
			<li>Click &lsquo;Regenerate My Access Token and Token Secret&rsquo;</li>
		</ol>

		<h3><a target="twbot-twitter" title="Retrieve app details" href="https://apps.twitter.com">Retrieve app details</a></h3>
		<ol>
			<li>Select your app</li>
			<li>Open the &lsquo;Keys and Access Tokens&rsquo; tab</li>
			<li>Enter your consumer key, consumer secret, access key, and access secret below</li>
		</ol>

		% if req.GET.get("message"):
			<div class="warning">
				<strong>{{req.GET["message"]}}</strong>
			</div>
		% end

		<form action="/register-tokens" method="post" autocomplete="off">
			<label for="reg-api-key">Consumer key:</label>
			<input name="api-key" id="reg-api-key" type="text" required>

			<label for="reg-api-secret">Consumer secret:</label>
			<input name="api-secret" id="reg-api-secret" type="password" required>

			<label for="reg-access-key">Access key:</label>
			<input name="access-key" id="reg-access-key" type="text" required>

			<label for="reg-access-secret">Access secret:</label>
			<input name="access-secret" id="reg-access-secret" type="password" required>

			<input type="submit" value="Next">
		</form>
	% elif first_run_step == 2:
		<h3>Congratulations, you have set up twbot! You may now log in.</h3>

		<form action="/finish-setup" method="post">
			<input type="submit" value="Okay">
		</form>
</div>
