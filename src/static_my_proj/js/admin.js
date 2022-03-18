$(document).ready(function() {
	var max = 70;
	var len = $('#id_meta_title').val().length;
	var char = max - len;
	$("#id_meta_title").after("<span id=charNum>" + char);
	$("#id_meta_title").keyup(function () {
		var max = 70;
		var len = $(this).val().length;
		if (len >= max) {
			$('#charNum').text('Over the limit');
		} else {
			var char = max - len;
			$('#charNum').text(' ' + char);
		}
	});

	max = 160;
	len = $('#id_meta_description').val().length;
	char = max - len;

	$("#id_meta_description").after("<span id=descripNum>" + char);
	$("#id_meta_description").keyup(function () {
		var max = 160;
		var len = $(this).val().length;
		if (len >= max) {
			$('#descripNum').text('Over the limit');
		} else {
			var char = max - len;
			$('#descripNum').text(' ' + char);
		}
	});
});