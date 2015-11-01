<div class="first-run">
	<h1>Welcome to twbot</h1>
	% if first_run_step == 0:
		<h2>Set up your account</h2>

		<form id="form-register" action="/register" method="post" autocomplete="off">
			<label for="reg-username">Username:</label>
			<input type="username" name="username" id="reg-username">
			<label for="reg-password">Password:</label>
			<input type="password" name="password" id="reg-password">
			<input type="submit" value="Register">
		</form>
	% elif first_run_step == 1:
		<h2>Connect to Twitter</h2>

		<h3>Add your phone number</h3>
		<h4>Go to <a target="twbot-twitter" title="Add phone number" href="https://twitter.com/settings/add_phone">twitter.com/settings/add_phone</a></h4>
		<ul>
			<li>You must add your phone number to your Twitter account before you can register an app</li>
			<li>Use your real number, as Twitter will send you a confirmation text to verify the number</li>
		</ul>

		<h3>Create the Twitter app</h3>
		<h4>Go to <a target="twbot-twitter" title="Create Twitter app" href="https://apps.twitter.com">apps.twitter.com</a></h4>
		<ul>
			<li>By creating a Twitter application, twbot will be able to access a Twitter account and run properly</li>
			<li>When entering the application name, enter &lsquo;twbot&rsquo; prefixed by the current Twitter account so as to prevent name clashes with other twbot users (e.g. &lsquo;@Linus__Torvalds twbot&rsquo; for user @Linus__Torvalds)</li>
			<li>You must fill the description and website fields to proceed, however twbot ignores these fields</li>
		</ul>

		<h3>Enter your app details</h3>
		<h4>Go to <a target="twbot-twitter" title="Retrieve your app details" href="https://apps.twitter.com">apps.twitter.com</a></h4>
		<ol>
			<li>Select your newly created app</li>
			<li>Open the &lsquo;Keys and Access Tokens&rsquo; tab</li>
			<li>Enter your consumer key and secret below</li>
		</ol>

		% if b.request.GET.get("message"):
			<div class="form-warning">
				<strong>{{b.request.GET.get("message")}}</strong>
			</div>
		% end

		<form id="form-register-tokens" action="/register-tokens" method="post" autocomplete="off">
			<label for="reg-tokens-key">Consumer Key:</label>
			<input name="api-key" id="reg-tokens-key" type="text">
			<label for="reg-tokens-secret">Consumer Secret:</label>
			<input name="api-secret" id="reg-tokens-secret" type="password">
			<input type="submit">
		</form>
	% elif first_run_step == 2:
		<h3>Go to <a target="twbot-twitter" title="Authorization URL" href="{{auth_url}}">{{auth_url}}</a></h3>

		<p>Enter the PIN you are given below</p>

		<form id="form-register-pin" action="/register-pin" method="post" autocomplete="off">
			<label for="reg-pin">PIN:</label>
			<input name="pin" type="password" inputmode="numeric" maxlength="7" required>
			<input type="submit">
		</form>
	% end
</div>
