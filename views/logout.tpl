% rebase("base.tpl", title="Log out")

% if is_logged_in:
    <p>You are logged in as the administrator ({{username}}).</p>

    <form id="form-logout" action="/logout" method="post">
    	<input type="submit" value="Log Out">
    </form>
<%
else:
    include("login-warning.tpl")
end
%>