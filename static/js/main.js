function $(selector) {
	return document.querySelector(selector);
}

function $$(selector) {
	return document.querySelectorAll(selector);
}

function log(text) {
	console.log(Date.now() + " " + text);
}