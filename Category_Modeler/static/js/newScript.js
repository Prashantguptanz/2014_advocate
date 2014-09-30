/**
 * @author Prashant Gupta
 */
$(document).ready(function() {

	$('.dropdown-toggle').dropdown();

	$('input[name="testoption"]').click(function() {
		if ($('input[name="testoption"]:checked').attr("id") == "trainingfile") {
			$("#testfile").prop('disabled', false);
			$("#Fold").prop('disabled', true);
			$("#Percentage").prop('disabled', true);
		} else if ($('input[name="testoption"]:checked').attr("id") == "CrossValidation") {
			$("#testfile").prop('disabled', true);
			$("#Fold").prop('disabled', false);
			$("#Percentage").prop('disabled', true);

		} else if ($('input[name="testoption"]:checked').attr("id") == "PercentageSplit") {
			$("#testfile").prop('disabled', true);
			$("#Fold").prop('disabled', true);
			$("#Percentage").prop('disabled', false);

		} else {
			$("#testfile").prop('disabled', true);
			$("#Fold").prop('disabled', true);
			$("#Percentage").prop('disabled', true);
		}
		;

	});

	$('#filename').change(function() {
		var file = this.files[0];
		var reader = new FileReader();
		reader.readAsText(file);
		reader.onload = function(event) {
			var csv = event.target.result;
			var data = $.csv.toArrays(csv);
			var $container = $('#dataTable');
			$container.handsontable({
				data : data
			});
		};
		
		/*         var html = '';
		 var instances = 0
		 var attributes = 0
		 html +='<tr>\r\n';
		 for (var head in data[0]){
		 html += '<th>' + data[0][head] + '</th>\r\n';
		 attributes +=1;
		 }
		 html += '</tr>\r\n';

		 for(var row =1; row < data.length; row++ ) {
		 html += '<tr>\r\n';
		 instances +=1;
		 for(var item in data[row]) {
		 html += '<td>' + data[row][item] + '</td>\r\n';
		 }
		 html += '</tr>\r\n';
		 }
		 $('#contents').html(html);
		 $('#instances').html( instances);
		 $('#Attributes').html( attributes);*/
		
		var data = new FormData(file);

		function getCookie(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie != '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
						break;
					}
				}
			}
			return cookieValue;
		}

		var csrftoken = getCookie('csrftoken');

		function csrfSafeMethod(method) {
			// these HTTP methods do not require CSRF protection
			return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
		}


		$.ajaxSetup({
			beforeSend : function(xhr, settings) {
				if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
				}
			}
		});

		$.ajax({

			type : "POST",
			url : "http://127.0.0.1:8000/CategoryModeler/preprocess/",
			dataType : "json",
			async : true,
			processData : false, // Don't process the files
			contentType : false,
			data : {
				csrfmiddlewaretoken : '{{ csrf_token }}',
				somedata : data
			},
			success : function(response) {
				alert(response);

			}
		});

	});

});

