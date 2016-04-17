% rebase("base.tpl", title="Questions")

% if is_logged_in:
	% if req.GET.get("message"):
		<div class="warning">
			<strong>{{req.GET["message"]}}</strong>
		</div>
	% end

	<details>
		<summary>Create question</summary>

		<div class="area">
			<form action="/create-question" method="post">
				<label for="question-question">Question*:</label>
				<textarea id="question-question" required name="question" rows="4" cols="80" maxlength="140"></textarea>
				<p>Question marks are not inserted or removed automatically. Add them at your discrescion</p>

				<input type="checkbox" class="question-is-multiple-choice" id="question-is-multiple-choice" name="is-multiple-choice">
				<label class="label-inline" for="question-is-multiple-choice">Multiple choice</label>

				<div class="multiple-choice-answers">
					<div>
						<h4>Possible answers</h4>

						<label for="multiple-choice-answer-a">A*:</label>
						<input maxlength="140" type="text" data-multiple-choice-required name="answer-a" id="multiple-choice-answer-a">

						<label for="multiple-choice-answer-b">B*:</label>
						<input maxlength="140" type="text" data-multiple-choice-required name="answer-b" id="multiple-choice-answer-b">

						<label for="multiple-choice-answer-c">C:</label>
						<input maxlength="140" type="text" name="answer-c" id="multiple-choice-answer-c">

						<label for="multiple-choice-answer-d">D:</label>
						<input maxlength="140" type="text" name="answer-d" id="multiple-choice-answer-d">
					</div>

					<div>
						<h4>Correct answer*:</h4>
						<input type="radio" data-multiple-choice-required id="answer-correct-a" name="correct-answer" value="a">
						<label class="label-inline" for="answer-correct-a">A</label>

						<br>

						<input type="radio" id="answer-correct-b" name="correct-answer" value="b">
						<label class="label-inline" for="answer-correct-b">B</label>

						<br>

						<input type="radio" id="answer-correct-c" name="correct-answer" value="c">
						<label class="label-inline" for="answer-correct-c">C</label>

						<br>

						<input type="radio" id="answer-correct-d" name="correct-answer" value="d">
						<label class="label-inline" for="answer-correct-d">D</label>
					</div>
				</div>

				<label class="label-inline" for="question-ask-time">Time to tweet:</label>
				<input name="ask-time" id="question-ask-time" type="datetime-local">

				<script>
					var time = new Date();
					var tzOffsetMins = time.getTimezoneOffset();

					time.setTime(time.getTime() - (tzOffsetMins * 60 * 1000));

					var isoTime = time.toISOString();
					isoTime = isoTime.substring(0, isoTime.indexOf(".") - 3);

					var askTimeInput = $("#question-ask-time");
					askTimeInput.value = isoTime;
				</script>

				<input type="submit" value="Create">
			</form>
		</div>
	</details>

	<h2>Questions</h2>

	<%
	questions = c.execute("SELECT * FROM questions;").fetchall()
	questions = sorted(questions, key=lambda question: question["id"], reverse=True)

	if questions:
	%>
		<div class="list">

		% for question in questions:
			<div>
				<h3>{{question["question"]}}</h3>

				% if question["possible_answer_id"]:
					<h4>Possible answers:</h4>
					<ul>
						<%
						# multiple choice

						possible_answers = c.execute("SELECT * FROM possible_answers WHERE question_id = ?", (question["id"],)).fetchall()

						for possible_answer in possible_answers:
							if possible_answer["id"] == question["possible_answer_id"]:
								correct_answer = possible_answer
							end
						%>
							<li>{{possible_answer["letter"].upper()}}: {{possible_answer["answer"]}}</li>
						% end
					</ul>

					<p>Correct answer: {{correct_answer["letter"].upper()}}</p>
				% end

				<p>
					<%
					ask_time = question["ask_time"]
					ask_time = dmc.epoch(ask_time)

					if question["is_asked"]:
					%>
						Asked on {{ask_time.format_datetime()}} ({{ask_time.humanize()}})
					% else:
						To be asked on {{ask_time.format_datetime()}} ({{ask_time.humanize()}})
					% end
				</p>

				<form action="/delete-question/{{question["id"]}}" method="post">
					<input type="submit" value="Delete">
				</form>
			</div>
		% end

		</div>
	% else:
		<p>There are no questions. You may create one using the form above.</p>
	% end

	<script>
		// this code dynamically sets the "required" attribute on certain inputs
		// when multiple choice is enabled

		var multipleChoiceRequired = $$("[data-multiple-choice-required]");
		var multipleChoiceInputs = $$(".multiple-choice-answers input");
		var multipleChoiceToggle = $("#question-is-multiple-choice");

		function processInputs() {
			var checked = multipleChoiceToggle.checked;
			for (var i = 0; i < multipleChoiceRequired.length; ++i) {
				multipleChoiceRequired[i].required = checked;
			}

			for (var i = 0; i < multipleChoiceInputs.length; ++i) {
				multipleChoiceInputs[i].disabled = !checked;
			}
		}

		processInputs();
		multipleChoiceToggle.addEventListener("change", processInputs);
	</script>
<%
else:
	include("login-warning.tpl")
end
%>