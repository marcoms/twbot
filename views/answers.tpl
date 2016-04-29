% rebase("base.tpl", title="Answers")

<%
if is_logged_in:
	# all non-multiple choice questions
	answers = c.execute("SELECT * FROM answers;").fetchall()
	unmarked_answers = [answer for answer in answers if answer["score"] is None]
	unmarked_answers = sorted(unmarked_answers, key=lambda answer: answer["id"], reverse=True)

	marked_answers = [answer for answer in answers if answer["score"] is not None]
	marked_answers = sorted(marked_answers, key=lambda answer: answer["id"], reverse=True)
%>
	<h2>Unmarked answers</h2>

	% if unmarked_answers:
		<form action="/mark-answers" method="post">
			<div class="list">
				<%
				for answer in unmarked_answers:
					question = c.execute("SELECT * FROM questions WHERE id = ?;", (answer["question_id"],)).fetchone()
				%>
					<div>
						<p>Question: {{question["question"]}}</p>
						<p>Answer: {{answer["answer"]}}</p>

						<label for="answer-{{answer["id"]}}-score">Score:</label>
						<p class="score-output" data-for="answer-{{answer["id"]}}-score"></p>
						<input class="score-input" id="answer-{{answer["id"]}}-score" name="answer-{{answer["id"]}}" type="range" min="0" max="10">
					</div>
				% end

				<input type="submit" value="Submit all marks">
			</div>
		</form>

		<script>
			var scoreInputs = $$(".score-input");

			for (var i = 0; i < scoreInputs.length; ++i) {
				(function() {
					var scoreInput = scoreInputs[i];
					console.log("score input:", scoreInput);

					var selector = ".score-output[data-for='" + scoreInput.id + "']"
					console.log("selector:", selector);
					var scoreOutput = $(selector);
					console.log("score output:", scoreOutput);

					scoreOutput.textContent = scoreInput.value;

					scoreInput.addEventListener("input", function(evt) {
						var value = scoreInput.value;
						scoreOutput.textContent = value;
					});
				})();
			}
		</script>
	% else:
		<p>There are no unmarked answers</p>
	% end

	<h2>Marked answers</h2>

	% if marked_answers:
		<div class="list">
			<%
			for answer in marked_answers:
				question = c.execute("SELECT * FROM questions WHERE id = ?;", (answer["question_id"],)).fetchone()
			%>
				<div class="answer">
					<p>Question: {{question["question"]}}</p>
					<p>Answer: {{answer["answer"]}}</p>

					<p>Score: {{answer["score"]}}</p>
				</div>
			% end
		</div>
	% else:
		<p>There are no marked answers</p>
	% end
<%
else:
	include("login-warning.tpl")
end
%>
