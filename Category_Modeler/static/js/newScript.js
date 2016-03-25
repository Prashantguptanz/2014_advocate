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
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});

	// Function to set the height of training data table based on window size
	function setTrainingSamplesTableHeight() {
		var headerHeight = $('#top-part').outerHeight();
		var totalHeight = $(window).height();
		$('#trainingdataTable').css({
			'height' : totalHeight - headerHeight - 140 + 'px'
		});
	}
	;

	function setSignatureFileDetailsHeight() {
		var headerHeight = $('#top-part').outerHeight();
		var totalHeight = $(window).height();
		$('#signaturefiledetails').css({
			'height' : totalHeight - headerHeight - 140 + 'px'
		});
	}
	;
	// Script for navbar

	var loc = window.location.href;

	$('.nav.nav-pills.nav-justified > li').each(
			function() {
				var $this = $(this);
				if (loc.match('http://127.0.0.1:8000'
						+ $this.children().attr('href'))) {
					$this.addClass("active");
					$this.siblings().removeClass("active");
				}
			});

	// Script for sign in and register tab
	$('#session').click(function() {
		// Conditional states allow the dropdown box appear and disappear
		if ($('#signin-dropdown').is(":visible")) {
			$('#signin-dropdown').hide();
			$('#session').removeClass('active'); // When the dropdown is not
			$('#register-dropdown').hide(); // visible removes the class
			// "active"
		} else {
			$('#signin-dropdown').show();
			$('#session').addClass('active'); // When the dropdown is visible
			// add class "active"
		}
		return false;
	});

	$('#register-link').on('click', function(e) {
		$('#register-dropdown').show();
		$('#signin-dropdown').hide();
	});

	$('#signin-link-bak').on('click', function(e) {
		$('#register-dropdown').hide();
		$('#signin-dropdown').show();
	});

	// Allow to hide the dropdown box if you click anywhere on the document.
	$('#signin-dropdown').click(function(e) {
		e.stopPropagation();
	});
	$('#register-dropdown').click(function(e) {
		e.stopPropagation();
	});
	$(document).click(function() {
		$('#signin-dropdown').hide();
		$('#session').removeClass('active');
		$('#register-dropdown').hide();
	});

	$('#Signin')
			.on(
					'click',
					function(e) {
						if ($('#username').val() != ""
								&& $('#password').val() != "") {
							e.preventDefault();
							var $this = $('#signindetails');
							$
									.post(
											"http://127.0.0.1:8000/AdvoCate/accounts/auth/",
											$this.serialize(),
											function(response) {
												if ('error' in response) {
													$('p#signinerror').html(
															response['error']);
												} else {
													$('div#topnav')
															.html(
																	"<div id=\"logoutsession\"><strong>Welcome "
																			+ response['user_name']
																			+ " &nbsp; &nbsp;</strong><a id=\"logout-link\" href=\"/AdvoCate/accounts/logout/\"> Sign out </a></div>");
												}

											});
						}

					});

	// Script for 'Home' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/home/')) {

		$('input[name="chooseactivity"]').on('click', function() {
			var $this = $(this);

			if ($this.attr('value') == 'option2') {
				$('#existingtaxonomydetails').show();
				$('#newtaxonomydetails').hide();
				$('#activitythree').hide();
			} else if ($this.attr('value') == 'option1') {
				$('#existingtaxonomydetails').hide();
				$('#activitythree').hide();
				$('#newtaxonomydetails').show();
			} else if ($this.attr('value') == 'option3') {
				$('#newtaxonomydetails').hide();
				$('#existingtaxonomydetails').hide();
				$('#activitythree').show();
			} else {
				$('#newtaxonomydetails').hide();
				$('#existingtaxonomydetails').hide();
				$('#activitythree').hide();
			}
		});

		$('#savetaxonomynameandexternaltrigger').on('click', function(e) {
			e.preventDefault();
			var $this = $('#existingtaxonomydetails');
			$.post("http://127.0.0.1:8000/AdvoCate/saveexistingtaxonomydetails/", $this.serialize(), function(response) {
				$('#savetaxonomynameandexternaltrigger').attr('disabled','disabled');
				$('#messageforexploringchanges').html(response);
				$('#chooseanactivitymessage').hide();
			});

		});

		$('#savenewtaxonomydetails').on('click',function(e) {
			e.preventDefault();
			var $this = $('#newtaxonomydetails');
			$.post("http://127.0.0.1:8000/AdvoCate/savenewtaxonomydetails/", $this.serialize(), function(response) {
				$('#savenewtaxonomydetails').attr('disabled','disabled');
				$('#messagefornewtaxonomymodelling').html(response);
				$('#chooseanactivitymessage').hide();
			});

		});
		
		$('#chooseactivitythree').on('click',function(e) {
			e.preventDefault();
			$.post("http://127.0.0.1:8000/AdvoCate/compareexistingtaxonomies/", "activity3", function(response) {
				$('#chooseactivitythree').attr('disabled','disabled');
				$('#messageforviewingexistingtaxonomies').html(response);
				$('#chooseanactivitymessage').hide();
			});

		});

	}

	// Script for 'Training Samples' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/trainingsample/')) {

		$('input[name="choosetrainingfile"]').on(
				'click',
				function() {
					var $this = $(this);
					$this.next().children().removeAttr('disabled');
					$this.siblings('input').next().children().attr('disabled',
							'disabled');

					if ($this.attr('value') == 'option2') {
						$('#newtrainingdatasetdetails').show();
					} else {
						$('#newtrainingdatasetdetails').hide();
					}

				});

		function firstRowRenderer(instance, td, row, col, prop, value,
				cellProperties) {
			Handsontable.renderers.TextRenderer.apply(this, arguments);
			td.style.fontWeight = 'bold';
			td.style.background = 'gainsboro';
		}

		var settings1 = {
			contextMenu : true,
			afterChange : function(change, source) {
				if (source === 'loadData') {
					return;
				}

				$('#saveChanges').show();
				$('#changedtrainingdata').show();
			},
			cells : function(row, col, prop) {
				var cellProperties = {};
				if (row == 0) {
					cellProperties.readOnly = true;
					cellProperties.renderer = firstRowRenderer;
				}
				return cellProperties;
			}

		};

		var trainingdatacontainer = document
				.getElementById('trainingdataTable'), hot;
		hot = new Handsontable(trainingdatacontainer, settings1);

		// Script to deal with when the existing training file is selected
		$('#existingtrainingfiles').on(
				'change',
				function() {
					$('#instanceslabel').show();
					$('#attributeslabel').show();

					var filepkey = this.value;
					var filename = $('#existingtrainingfiles>option:selected')
							.text();
					var data = {};
					data[1] = filepkey;
					data[2] = filename;
					$.post("http://127.0.0.1:8000/AdvoCate/trainingsample/",
							data, function(response) {
								var trainingdata = $.csv.toArrays(response);
								$('#instances').html(trainingdata.length - 1);
								$('#Attributes').html(trainingdata[0].length);

								$('#trainingdataTable').show();
								hot.loadData(trainingdata);
							});

				});

		// Script to deal with when the training file is uploaded
		$('#trainingfile').on('change', function() {
			$('#instanceslabel').show();
			$('#attributeslabel').show();
			$('#trainingfileformatError').html("");
			//var ext = this.value.match(/\.(.+)$/)[1];
			
		//	var newtrainingdataset = this.files[0];
			var newtrainingdatasets = this.files;
			
			// If only one file is uploaded
			if (newtrainingdatasets.length ==1){
				var ext = this.value.match(/\.(.+)$/)[1];
			
				if (ext == 'csv') {
					// FileReader Object reads the content
					// of file as text string into memory
					var reader = new FileReader();
	
					reader.onload = function(event) {
						var csv = reader.result; // I can also write
													// event.target.result
						var trainingdata = $.csv.toArrays(csv);
	
						$('#instances').html(trainingdata.length - 1);
						$('#Attributes').html(trainingdata[0].length);
	
						$('#trainingdataTable').show();
						hot.loadData(trainingdata);
	
					};
					reader.readAsText(newtrainingdatasets[0]);
	
				}
			}
			
			// Posting file to the server side using formdata
			var formdata = new FormData();
			$.each(newtrainingdatasets, function(i, file){
				formdata.append('file', file);
			});
			$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/AdvoCate/trainingsample/",
				async : true,
				processData : false,
				contentType : false,
				data : formdata,
				success : function(response) {
					if (response['error']){
						console.log(response['error']);
						$('#trainingfileformatError').html(response['error']);
					}
					else if (response['Content-Disposition'] !== -1) {
						var trainingdata = $.csv.toArrays(response);
						$('#instances').html(trainingdata.length - 1);
						$('#Attributes').html(trainingdata[0].length);

						$('#trainingdataTable').show();
						hot.loadData(trainingdata);
					}
				}
			});

		});

		setTrainingSamplesTableHeight();
		// call the setHeight function, every time window is resized
		$(window).on('resize', function() {
			setTrainingSamplesTableHeight();
		});

		$('#savetrainingdatadetails').on('click', function(e) {
			e.preventDefault();
			var $this = $('#newtrainingdatasetdetails');
			$.post("http://127.0.0.1:8000/AdvoCate/savetrainingdatadetails/", $this.serialize(), function(response) {
			});
		});

		$('#saveChanges').on('click', function() {
			// So after the execution it doesn't refresh back
			change_message = JSON.stringify($.trim($('#reasonforchange').val()));
			table_data = hot.getData();
			table_data.unshift(change_message);
			data = JSON.stringify(table_data);
			event.preventDefault();
			$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/AdvoCate/saveNewTrainingVersion/",
				async : true,
				processData : false,
				contentType : false,
				data : data,
				success : function(response) {
					$('#saveChanges').hide();
					$('#changedtrainingdata').hide();
					$('#newversionstoredsuccessfully').show();
					$('#successmessage').html(response);
				}

			});
		});

	}

	// Script for 'Signature file' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/signaturefile/')) {

		setSignatureFileDetailsHeight();

		$(window).on('resize', function() {
			setSignatureFileDetailsHeight();
		});

		$('.dropdown-toggle').dropdown();

		$('input[name="validationoption"]').on(
				'click',
				function() {
					var $this = $(this);
					$this.next().children().removeAttr('disabled');
					$this.siblings('input').next().children().attr('disabled',
							'disabled');

				});

		$('#createsignaturefile').on('click', function(e) {
				if ($('#classifiertype').val() != "" && $('input[name=validationoption]:checked').val() != null) {
					e.preventDefault();
					var $this = $('#trainingoptions');
					var formData = new FormData($this[0]);
					$.ajax({
							type : "POST",
							url : "http://127.0.0.1:8000/AdvoCate/signaturefile/",
							async : true,
							processData : false,
							contentType : false,
							data : formData,
							success : function(response) {
								$('#validationscore').html("<b>Validation score:  </b>"+ response['score']);
								$('#kappa').html("<b>Kappa:  </b>"+ response['kappa']);
								if (response['meanvectors']) {
									$('#DecisionTreemodeldetails').hide();
									$('#NaiveBayesmodeldetails').show();
									var a = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Class </th><th> Mean Vector </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										a = a + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										var meanvectorarray = response['meanvectors'][i];
										for (var j = 0; j < meanvectorarray.length; j++) {
											a = a + parseFloat(meanvectorarray[j]).toFixed(2) + " |  ";
										}
										a = a + "</td></tr>";
									}
									a = a + "</table>";
									$('#meanvectors').html(a);
	
									var b = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Class </th><th> Variance </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										b = b + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										var variancearray = response['variance'][i];
										for (var k = 0; k < variancearray.length; k++) {
											b = b + parseFloat(variancearray[k]).toFixed(2) + " |  ";
										}
	
										b = b + "</td></tr>";
									}
									b = b + "</table>";
									$('#variance').html(b);
	
									var c = "<img style=\"width:100%; height:100%\" src=\"/static/images/" + response['cm'] + "\" />";
									$('#confusionmatrix1').html(c);
	
									var d = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Class </th><th> Producer's accuracy </th><th> User's accuracy </th><th> Omission error </th><th> Commission error </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										d = d + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										var producerAccuracy = parseFloat(response['prodacc'][i]);
										var userAccuracy = parseFloat(response['useracc'][i]);
										d = d + producerAccuracy + "</td><td>" + userAccuracy + "</td><td>" + parseFloat(1 - producerAccuracy).toFixed(2)
											+ "</td><td>" + parseFloat(1 - userAccuracy).toFixed(2) + "</td></tr>";
	
									}
									d = d + "</table>";
									$('#ErrorAccuracy').html(d);
									$('#meanvectors').hide();
									$('#variance').hide();
									$('#confusionmatrix1').hide();
									$('#ErrorAccuracy').hide();
								} else {
									$('#NaiveBayesmodeldetails').hide();
									$('#DecisionTreemodeldetails').show();
									var a = "<img style=\"width:100%; height:100%\" src=\"/static/images/" + response['tree'] + "\" />";
									$('#decisiontree').html(a);
									var b = "<img style=\"width:100%; height:100%\" src=\"/static/images/" + response['cm'] + "\" />";
									$('#confusionmatrix2').html(b);
									var d = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Class </th><th> Producer's accuracy </th><th> User's accuracy </th><th> Omission error </th><th> Commission error </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										d = d + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										var producerAccuracy = parseFloat(response['prodacc'][i]);
										var userAccuracy = parseFloat(response['useracc'][i]);
										d = d + producerAccuracy + "</td><td>" + userAccuracy + "</td><td>" + parseFloat(1 - producerAccuracy).toFixed(2)
											+ "</td><td>" + parseFloat(1 - userAccuracy).toFixed(2)+ "</td></tr>";
	
									}
									d = d + "</table>";
									$('#accuracies').html(d);
									$('#accuracies').hide();
									$('#decisiontree').hide();
									$('#confusionmatrix2')
											.hide();
	
								}
	
							}
	
					});
				 
				 }

			});

		$('input[name="NaiveBayesmodeldetails"]').on(
				'click',
				function(e) {

					var detailsoption = $(
							'input[name="NaiveBayesmodeldetails"]:checked')
							.val();
					if (detailsoption == '1') {
						$('#meanvectors').show();
						$('#variance').hide();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').hide();
					} else if (detailsoption == '2') {
						console.log(detailsoption);
						$('#meanvectors').hide();
						$('#variance').show();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').hide();
					} else if (detailsoption == '3') {
						$('#meanvectors').hide();
						$('#variance').hide();
						$('#confusionmatrix1').show();
						$('#ErrorAccuracy').hide();
					} else {
						$('#meanvectors').hide();
						$('#variance').hide();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').show();

					}
				});

		$('input[name="DecisionTreemodeldetails"]').on(
				'click',
				function(e) {
					var detailsoption = $(
							'input[name="DecisionTreemodeldetails"]:checked')
							.val();
					if (detailsoption == '1') {
						$('#decisiontree').show();
						$('#confusionmatrix2').hide();
						$('#accuracies').hide();
					} else if (detailsoption == '2') {
						$('#decisiontree').hide();
						$('#confusionmatrix2').show();
						$('#accuracies').hide();
					} else {
						$('#decisiontree').hide();
						$('#confusionmatrix2').hide();
						$('#accuracies').show();
					}
				});

	}

	// Script for 'Classification' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/supervised/')) {
		// Script to deal with when the test file is uploaded
		$('#doclassification').on('click', function(e) {
			e.preventDefault();
			console.log("I am here");
			var newtestfile = ($('#testfile'))[0].files[0];
			// Posting file to the server side using formdata
			var formdata = new FormData();
			formdata.append("testfile", newtestfile);
			$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/AdvoCate/supervised/",
				async : true,
				processData : false,
				contentType : false,
				data : formdata,
				success : function(response) {
					var c = "<img style=\"width:95%; height:95%\" src=\"/static/maps/" + response['map'] + "\" />";
					$('#classifiedmap').html(c);
					var d = "<label>Legend</label>"
									+ "<table style=\"width:100%\" class=\" table table-bordered\">"
									+ "<tr><td>"
									+ "<img src=\"/static/images/artificial_surface.png\" />"
									+ "</td><td>" + "Artificial surface"
									+ "</td></tr>"
									+ "<tr><td>"
									+ "<img src=\"/static/images/forest.png\" />"
									+ "</td><td>" + "Forest"
									+ "</td></tr>"
									+ "<tr><td>"
									+ "<img src=\"/static/images/grassland.png\" />"
									+ "</td><td>" + "Grassland"
									+ "</td></tr>"
									+ "<tr><td>"
									+ "<img src=\"/static/images/water.png\" />"
									+ "</td><td>" + "Water"
									+ "</td></tr>"
									+ "<tr><td>"
									+ "<img src=\"/static/images/shadow.png\" />"
									+ "</td><td>" + "Shadow"
									+ "</td></tr>"
									+ "<tr><td>"
									+ "<img src=\"/static/images/inland_water.png\" />"
									+ "</td><td>" + "Inland Water"
									+ "</td></tr>"
									+ "<tr><td>"
									+ "<img src=\"/static/images/cloud.png\" />"
									+ "</td><td>" + "Cloud"
									+ "</td></tr>"
							
									+ "</table>";
						
					$('#categorycolors').html(d);
					
				}
			});
		});

	}

	// Script for 'Classification' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/changerecognition/')) {
		
		$('#yesforchange').on('click', function(e) {
			e.preventDefault();
			$.get("http://127.0.0.1:8000/AdvoCate/createChangeEventForNewTaxonomy/", function(data){
				$('#listofchangeoperations').show();
				var d = "<table style=\"width:50%\" class=\" table table-bordered\">";
				d = d + "<tr><th>No.</th><th>Change operation</th>" ;
				for (var k = 1; k < data['listOfOperations'].length+1; k++) {
					d = d + "<tr><td>" + k + "</td>" + "<td>" + data['listOfOperations'][k-1] + "</td></tr>";
				}				
				d = d + "</table>";
				
		
				$('#listofchangeoperations').html(d);
				$('#commit').show();
				
				$('#yesforchange').attr('disabled', 'disabled');
				$('#noforchange').attr('disabled', 'disabled');
			});
		});
		
		$('#yesforcommit').on('click', function(e) {
			e.preventDefault();
			$.get("http://127.0.0.1:8000/AdvoCate/applyChangeOperations/", function(data){
				$('#listofchangeoperations').hide();
				$('#commit').hide();
				$('#implement').hide();
				$('#commitsuccessmessage').show();
				$('#successmessage').html(data);
			});
		});
		
		
		
		
	}

	// Script for visualization

	/*
	 * $('#creategraph').on('click', function(){ var G = jsnx.Graph();
	 * G.add_nodes_from([ ['Built Space', {color: 'red'}, {count: 18}], [2,
	 * {color: 'blue'}],
	 * 
	 * ]); G.add_edges_from([['Built Space',2]]);
	 * 
	 * console.log(G.nodes(true));
	 * 
	 * 
	 * 
	 * jsnx.draw(G, { element: '#networkGraph', with_labels: true, node_style: {
	 * fill: function(d) { return d.data.color; } } });
	 * 
	 * });
	 */

});