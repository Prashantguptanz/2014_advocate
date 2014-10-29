$(document)
		.ready(
				function() {
					

					function getCookie(name) {
						var cookieValue = null;
						if (document.cookie
								&& document.cookie != '') {
							var cookies = document.cookie
									.split(';');
							for (var i = 0; i < cookies.length; i++) {
								var cookie = jQuery
										.trim(cookies[i]);
								// Does this cookie string
								// begin with the name we
								// want?
								if (cookie.substring(0,
										name.length + 1) == (name + '=')) {
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
						// these HTTP methods do not require
						// CSRF protection
						return (/^(GET|HEAD|OPTIONS|TRACE)$/
								.test(method));
					}

					
					$
							.ajaxSetup({
								beforeSend : function(xhr,
										settings) {
									if (!csrfSafeMethod(settings.type)
											&& !this.crossDomain) {
										xhr
												.setRequestHeader(
														"X-CSRFToken",
														csrftoken);
									}
								}
							});

					$('.dropdown-toggle').dropdown();

					$('input[name="testoption"]')
							.click(
									function() {
										if ($(
												'input[name="testoption"]:checked')
												.attr("id") == "trainingfile") {
											$("#testfile").prop('disabled',
													false);
											$("#Fold").prop('disabled', true);
											$("#Percentage").prop('disabled',
													true);
										} else if ($(
												'input[name="testoption"]:checked')
												.attr("id") == "CrossValidation") {
											$("#testfile").prop('disabled',
													true);
											$("#Fold").prop('disabled', false);
											$("#Percentage").prop('disabled',
													true);

										} else if ($(
												'input[name="testoption"]:checked')
												.attr("id") == "PercentageSplit") {
											$("#testfile").prop('disabled',
													true);
											$("#Fold").prop('disabled', true);
											$("#Percentage").prop('disabled',
													false);

										} else {
											$("#testfile").prop('disabled',
													true);
											$("#Fold").prop('disabled', true);
											$("#Percentage").prop('disabled',
													true);
										}
										;

									});

					//Function to set the height of training data table based on window size
					function setHeight() {
						var headerHeight = $('.container').outerHeight();
						console.log(headerHeight);
						var totalHeight = $(window).height();
						console.log(totalHeight);
						$('#dataTable').css({
							'height' : totalHeight - headerHeight - 10 + 'px'
						});
					}

					//call the setHeight function, everytime window is resized
					$(window).on('resize', function() {
						setHeight();
					});
					//call it for the first time
					setHeight();

					//Script to deal with when the training file is uploaded 
					$('#trainingfile').change(function() {
									var file = this.files[0];
								//	console.log(file);
									var reader = new FileReader(); //FileReader Object reads the content of file as text string into memory
									reader.readAsText(file);
									reader.onload = function(event) {
										var csv = event.target.result;
										var data = $.csv.toArrays(csv);
										//console.log(data);
										var instances = 0
										var attributes = 0
										for ( var head in data[0]) {
											attributes += 1;
										}
										for (var row = 1; row < data.length; row++) {
											instances += 1;
										}
										$('#instances').html(instances);
										$('#Attributes').html(attributes);
	
										var $container = $('#dataTable');
										$container.handsontable({				//HandsonTable library to display interactive data table
											data : data
										});
									};

						

				//Posting file to the server side using formdata						
										var formdata = new FormData();
										formdata.append("trainingfile", file);
										$.ajax({

													type : "POST",
													url : "http://127.0.0.1:8000/CategoryModeler/preprocess/",
													dataType : "json",
													async : true,
													processData : false, // Don't process the files
													contentType : false,
													data : formdata,
													success : function(response) {
														alert(response);

													}
												});

									});

				});
