$(function() {
	
		function getCookie(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie != '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie
								.substring(name.length + 1));
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
				if (!csrfSafeMethod(settings.type)
						&& !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
				}
			}
		});


// Script for 'Preprocess Data' page		
		
		$('input[name="choosetrainingfile"]').on('click', function(){
			var $this = $(this);
			$this.next().children().removeAttr('disabled');
			$this.siblings('input').next().children().attr('disabled', 'disabled');
			
			if ($this.attr('value')=='option2'){
				$('#newtrainingdatasetdetails').show();
			}
			else{
				$('#newtrainingdatasetdetails').hide();
			}
			
		});
		
		


		
		
		// Script to deal with when the training file is uploaded
		$('#trainingfile').on('change', function() { 
			$('#instanceslabel').show();
			$('#attributeslabel').show();
			var newtrainingdataset = this.files[0];
		
			// FileReader Object reads the content
			// of file as text string into memory
			var reader = new FileReader();
			
			reader.onload = function(event) {
				var csv = reader.result;  // I can also write event.target.result
				var trainingdata = $.csv.toArrays(csv);
			
				$('#instances').html(trainingdata.length-1);
				$('#Attributes').html(trainingdata[0].length);

				var $container = $('#trainingdataTable');
				// HandsonTable library to display interactive data table
				$container.handsontable({
					data : trainingdata,

				});
			};
			
			reader.readAsText(newtrainingdataset);

			// Posting file to the server side using formdata
			var formdata = new FormData();
			formdata.append("trainingfile", newtrainingdataset);
			$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/CategoryModeler/preprocess/",
				dataType : "json",
				async : true,
				processData : false, 
				contentType : false,
				data : formdata,
				success : function(response) {

				}
			});

			var $container = $('#trainingdataTable');
			$container.handsontable({
				afterChange : function(change,
						source) {
					if (source === 'loadData') {
						return;
					} else {
						$('#saveChanges').show();
					}

				}

			});

		});
		
		// Function to set the height of training data table based on window size
		(function setHeight() {
			var headerHeight = $('.container').outerHeight();
			var totalHeight = $(window).height();
			$('#trainingdataTable').css({'height' : totalHeight - headerHeight + 'px'});
		})();

		// call the setHeight function, every time window is resized
		$(window).on('resize', function() {
			setHeight();
		});
		
		$('#savetrainingdatadetails').on('click', function(e){
			e.preventDefault();
			var $this = $('#newtrainingdatasetdetails');
			$.post("http://127.0.0.1:8000/CategoryModeler/savetrainingdatadetails/", $this.serialize(), function(response){
				alert(response);
			});
			
		});

		$('#saveChanges').on('click', function() { 
			//So after the execution it doesn't refresh back
			event.preventDefault();
			var handsontable = $('#dataTable').data('handsontable');
					$.ajax({
						type : "POST",
						url : "http://127.0.0.1:8000/CategoryModeler/preprocess/",
						dataType : "json",
						async : true,
						processData : false,
						contentType : false,
						data : JSON.stringify(handsontable.getData()),
						success : function(response) {

						}

					});
		});
		
		
// Script for Category Modeling page		

		$('.dropdown-toggle').dropdown();
		
		$('input[name="testoption"]').on('click',function() {
			var $this = $(this);
			$this.next().children().removeAttr('disabled');
			$this.siblings('input').next().children().attr('disabled', 'disabled');
			
		});

	});
