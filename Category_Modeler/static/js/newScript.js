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
			'height' : totalHeight - headerHeight - 240 + 'px'
		});
		$('#edittrainingset').css({
			'height' : totalHeight - headerHeight - 176 + 'px'
		});
	}
	;

	function setSignatureFileDetailsHeight() {
		var headerHeight = $('#top-part').outerHeight();
		var totalHeight = $(window).height();
		$('#signaturefiledetails').css({
			'height' : totalHeight - headerHeight - 180 + 'px'
		});
	};
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

	$('#Signin').on('click', function(e) {
		if ($('#username').val() != "" && $('#password').val() != "") {
			e.preventDefault();
			var $this = $('#signindetails');
			$.post("http://127.0.0.1:8000/AdvoCate/accounts/auth/", $this.serialize(), function(response) {
				if ('error' in response) {
					$('p#signinerror').html(response['error']);
				} 
				else {
					$('div#topnav').html("<div id=\"logoutsession\"><strong>Welcome " + response['user_name']
										+ " &nbsp; &nbsp;</strong><a id=\"logout-link\" href=\"/AdvoCate/accounts/logout/\">"
										+ "Sign out </a></div>");
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
			var legendpkey = $('#existingtaxonomies').val();
			console.log(legendpkey);
			var legendname = $('#existingtaxonomies>option:selected').text();
			console.log(legendname);
			var Etrigger = $('#externaltriggers>option:selected').text();
			var data = {};
			data[1] = legendpkey;
			data[2] = legendname;
			data[3] = Etrigger;
			$.post("http://127.0.0.1:8000/AdvoCate/saveexistingtaxonomydetails/", data, function(response) {
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

		$('input[name="choosetrainingfile"]').on('click', function() {
			var $this = $(this);
			$this.next().children().removeAttr('disabled');
			$this.siblings('input').next().children().attr('disabled', 'disabled');
			if ($this.attr('value') == 'option2') {
				$('#newconceptsanddetails').show();
			} else {
				$('#newtrainingdatasetdetails').hide();
				$('#newconceptsanddetails').hide();
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
		
		
		//Script to deal when a new training set is created
		var no_of_concepts =1;
		
		$('#addmorecategories').on('click', function(e) {
			e.preventDefault();
			
			var $this = $('#categoriesandsamples form:last');
			newtrainingdatasets = $this[0][1].files;
			
			var formdata = new FormData();
			
			$.each(newtrainingdatasets, function(i, file){
				formdata.append('file', file);
			});
			
			formdata.append('conceptName', $this[0][0].value);
			formdata.append('FieldResearcherName', $this[0][2].value);
			formdata.append('TrainingLocation', $this[0][3].value);
			formdata.append('TrainingTimePeriodStartDate', $this[0][4].value);
			formdata.append('TrainingTimePeriodEndDate', $this[0][5].value);
			formdata.append('OtherDetails', $this[0][6].value);
			formdata.append('IsFinalSample', 'False');
			$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/AdvoCate/trainingsample/",
				async : true,
				processData : false,
				contentType : false,
				data : formdata,
				success : function(response) {
					
				}
			});
			
			
			
			no_of_concepts +=1;
			console.log($('#categoriesandsamples form:last'));
			a = "</br><form id=\"concept" + no_of_concepts + "details\" enctype=\"multipart/form-data\" action=\"#\"></form>";
			$('#categoriesandsamples').append(a);
			b = $('#concept1details').html();
			$('#categoriesandsamples form:last').html(b);
			
		});
		
		$('#submittrainingsamples').on('click', function(e) {
			e.preventDefault();
			$('#trainingsetname').show();
			$('#savetrainingset').show();
			$('#submittrainingsamples').attr('disabled','disabled');
			$('#addmorecategories').attr('disabled','disabled');
			
			
			
		});
		
		$('#savetrainingset').on('click', function(e) {
			e.preventDefault();
			var $this = $('#categoriesandsamples form:last');
			newtrainingdatasets = $this[0][1].files;
			console.log($('#trainingsetfilename'));
			console.log($('#trainingsetfilename').val());
			var formdata = new FormData();
			
			$.each(newtrainingdatasets, function(i, file){
				formdata.append('file', file);
			});
			
			formdata.append('conceptName', $this[0][0].value);
			formdata.append('FieldResearcherName', $this[0][2].value);
			formdata.append('TrainingLocation', $this[0][3].value);
			formdata.append('TrainingTimePeriodStartDate', $this[0][4].value);
			formdata.append('TrainingTimePeriodEndDate', $this[0][5].value);
			formdata.append('OtherDetails', $this[0][6].value);
			formdata.append('IsFinalSample', 'True');
			formdata.append('TrainingsetName', $('#trainingsetfilename').val());
			$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/AdvoCate/trainingsample/",
				async : true,
				processData : false,
				contentType : false,
				data : formdata,
				success : function(response) {
					$('#newconceptsanddetails').hide();
					$('#viewandedittrainingset').show();
					var trainingdata = response['trainingset'];
					var classes = response['classes'];
					$('#instances').html(trainingdata.length - 1);
					$('#Attributes').html(trainingdata[0].length);

					$('#trainingdataTable').show();
					hot.loadData(trainingdata);
					
					a = "<option>Choose a concept</option>";
					b = "<option>Choose first concept to merge</option>";
					c = "<option>Choose second concept to merge</option>";
					d = "<option>Choose the concept to be split</option>";
					for (var i = 0; i < classes.length; i++){
						a = a + "<option>" + classes[i] + "</option>";
						b = b + "<option>" + classes[i] + "</option>";
						c = c + "<option>" + classes[i] + "</option>";
						d = d + "<option>" + classes[i] + "</option>";
					}
					$('#concepttoremove').html(a);
					$('#firstconcepttomerge').html(b);
					$('#secondconcepttomerge').html(c);
					$('#concepttosplit').html(d);
					
					
				}
			});
			
		});
		


		var trainingdatacontainer = document.getElementById('trainingdataTable'), hot;
		hot = new Handsontable(trainingdatacontainer, settings1);
		
		// Script to deal with when the existing training file is selected
		$('#existingtrainingfiles').on('change', function() {
			$('#viewandedittrainingset').show();
			$('#instanceslabel').show();
			$('#attributeslabel').show();

			var filepkey = this.value;
			var filename = $('#existingtrainingfiles>option:selected').text();
			var data = {};
			data[1] = filepkey;
			data[2] = filename;
			$.post("http://127.0.0.1:8000/AdvoCate/trainingsample/", data, function(response) {
			//	var trainingdata = $.csv.toArrays(response);
			//	console.log(trainingdata);
				var trainingdata = response['trainingset'];
				var classes = response['classes'];
				$('#instances').html(trainingdata.length - 1);
				$('#Attributes').html(trainingdata[0].length);
				$('#trainingdataTable').show();
				hot.loadData(trainingdata);
				
				a = "<option>Choose a concept</option>";
				b = "<option>Choose first concept to merge</option>";
				c = "<option>Choose second concept to merge</option>";
				d = "<option>Choose the concept to be split</option>";
				for (var i = 0; i < classes.length; i++){
					a = a + "<option>" + classes[i] + "</option>";
					b = b + "<option>" + classes[i] + "</option>";
					c = c + "<option>" + classes[i] + "</option>";
					d = d + "<option>" + classes[i] + "</option>";
				}
				$('#concepttoremove').html(a);
				$('#firstconcepttomerge').html(b);
				$('#secondconcepttomerge').html(c);
				$('#concepttosplit').html(d);
				
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
				if (response['common_categories_message']){
					$('#newtrainingdatasetdetails').hide();
					$('#trainingsetcomparison').show();
					var a = "<label style=\"font-size: 16px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
							"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common Categories</div>";
					a = a + " <div class=\"panel-body\"> <p><em> Note:" + response['common_categories_message'] + "</em></p></div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['common_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['common_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New Categories</div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['new_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					
					if (response['deprecated_categories'].length!=0){
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Categories deprecated</div>";
						a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
					
						for (var i = 0; i < response['deprecated_categories'].length; i++){
							a = a + "<li class=\"list-group-item\">" + response['deprecated_categories'][i] + "</li>";
						}
						a = a + "</ul></div>";
					}
					$('#trainingsetcomparisondetails').html(a);
					
				}
				else if (response['common_categories']){
					$('#newtrainingdatasetdetails').hide();
					$('#trainingsetcomparison').show();
					var a = "<label style=\"font-size: 16px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
							"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common Categories</div>";
					a = a + "<table class=\"table\"><tr><th> Category</th><th> J-Index </th></tr>";

					for (var i = 0; i < response['common_categories'].length; i++){
						a = a + "<tr><td>" + response['common_categories'][i][0] + "</td><td>" + response['common_categories'][i][1] + "</td></tr>";
					}
					a = a + "</table></div>";
					
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New Categories</div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['new_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					
					if (response['deprecated_categories'].length!=0){
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Categories deprecated</div>";
						a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
					
						for (var i = 0; i < response['deprecated_categories'].length; i++){
							a = a + "<li class=\"list-group-item\">" + response['deprecated_categories'][i] + "</li>";
						}
						a = a + "</ul></div>";
					}
					$('#trainingsetcomparisondetails').html(a);
					
				}
				else{
					$('#newtrainingdatasetdetails').hide();
				}
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
					if (response['common_categories_message']){
						$('#trainingsetcomparison').show();
						var a = "<label style=\"font-size: 16px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
								"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common Categories</div>";
						a = a + " <div class=\"panel-body\"> <p><em> Note:" + response['common_categories_message'] + "</em></p></div>";
						a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
					
						for (var i = 0; i < response['common_categories'].length; i++){
							a = a + "<li class=\"list-group-item\">" + response['common_categories'][i] + "</li>";
						}
						a = a + "</ul></div>";
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New Categories</div>";
						a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
					
						for (var i = 0; i < response['new_categories'].length; i++){
							a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
						}
						a = a + "</ul></div>";
						
						if (response['deprecated_categories'].length!=0){
							a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Categories deprecated</div>";
							a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
						
							for (var i = 0; i < response['deprecated_categories'].length; i++){
								a = a + "<li class=\"list-group-item\">" + response['deprecated_categories'][i] + "</li>";
							}
							a = a + "</ul></div>";
						}
						$('#trainingsetcomparisondetails').html(a);
						
					}
				else if (response['common_categories']){
					$('#trainingsetcomparison').show();
					var a = "<label style=\"font-size: 16px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
							"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common Categories</div>";
					a = a + "<table class=\"table\"><tr><th> Category</th><th> J-Index </th></tr>";

					for (var i = 0; i < response['common_categories'].length; i++){
						a = a + "<tr><td>" + response['common_categories'][i][0] + "</td><td>" + response['common_categories'][i][1] + "</td></tr>";
					}
					a = a + "</table></div>";
					
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New Categories</div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['new_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					
					if (response['deprecated_categories'].length!=0){
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Categories deprecated</div>";
						a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
					
						for (var i = 0; i < response['deprecated_categories'].length; i++){
							a = a + "<li class=\"list-group-item\">" + response['deprecated_categories'][i] + "</li>";
						}
						a = a + "</ul></div>";
					}
					$('#trainingsetcomparisondetails').html(a);
					
					}
				}

			});
		});
		
		$('input[name="chooseeditoperation"]').on('click', function() {
			var $this = $(this);
			$this.next().show();
			$this.next().children().show();
			$this.siblings('input').next().hide();
			$this.siblings('input').children().hide();
			$('#addtoeditoperationslist').show();
			$('#listofeditingoperations').show();
			
		});
		
		$('#addtoeditoperationslist').on('click', function(e) {
			e.preventDefault();
			if ($('input[name=chooseeditoperation]:checked').val() == "option1"){
				nodatavalue = $('#nodatavalue').val();
				editoperation = 1;
				var data = {};
				data[1] = editoperation;
				data[2] = nodatavalue;
				$.post("http://127.0.0.1:8000/AdvoCate/edittrainingset/", data, function(response) {
					var a = $('#editop').html();
					a = a + "<li class=\"list-group-item\">" + "Remove <em>No data</em> values" + "</li>";
					$('#editop').html(a);
					
				});
				
			}
			else if ($('input[name=chooseeditoperation]:checked').val() == "option2"){
				concepttoremove = $('#concepttoremove>option:selected').text();
				console.log(concepttoremove);
				editoperation = 2;
				var data = {};
				data[1] = editoperation;
				data[2] = concepttoremove;
				$.post("http://127.0.0.1:8000/AdvoCate/edittrainingset/", data, function(response) {
					var a = $('#editop').html();
					a = a + "<li class=\"list-group-item\">" + "Remove concept <em>" + data[2]  + "</em></li>";
					$('#editop').html(a);
				});
				
			}
			else if ($('input[name=chooseeditoperation]:checked').val() == "option3"){
				firstconcepttomerge = $('#firstconcepttomerge>option:selected').text();
				secondconcepttomerge = $('#secondconcepttomerge>option:selected').text();
				mergedconceptname = $('#mergedconceptname').val();
				editoperation = 3;
				var data = {};
				data[1] = editoperation;
				data[2] = firstconcepttomerge;
				data[3] = secondconcepttomerge;
				data[4] = mergedconceptname;
				$.post("http://127.0.0.1:8000/AdvoCate/edittrainingset/", data, function(response) {
					var a = $('#editop').html();
					a = a + "<li class=\"list-group-item\">" + "Merge concepts <em>" + firstconcepttomerge  + "</em> and <em>" + secondconcepttomerge + "</em> and create <em>" + mergedconceptname + "</em></li>";
					$('#editop').html(a);
					
				});
				
			}
			else{
				concepttosplit = $('#concepttosplit>option:selected').text();
				concept1 = $('#firstsplitconcept').val();
				concept2 = $('#secondsplitconcept').val();
				
				var samplesforconcept1 = $('#samplesforfirstsplitconcept')[0].files;
				console.log($('#samplesforfirstsplitconcept'));
				console.log(samplesforconcept1);
				var samplesforconcept2 = $('#samplesforsecondsplitconcept')[0].files;
				
				var formdata = new FormData();				
				
				$.each(samplesforconcept1, function(i, file){
					formdata.append('filesforconcept1', file);
				});
				
				$.each(samplesforconcept2, function(i, file){
					formdata.append('filesforconcept2', file);
				});
				formdata.append('1', '4');
				formdata.append('concepttosplit', concepttosplit);
				formdata.append('concept1', concept1);
				formdata.append('concept2', concept2);
				
				$.ajax({
					type : "POST",
					url : "http://127.0.0.1:8000/AdvoCate/edittrainingset/",
					async : true,
					processData : false,
					contentType : false,
					data : formdata,
					success : function(response) {
						var a = $('#editop').html();
						a = a + "<li class=\"list-group-item\">" + "Split concept <em>" + concepttosplit  + "</em> into <em>" + concept1 + "</em> and <em>" + concept2 + "</em></li>";
						$('#editop').html(a);
						
					}
				});
				
			}
			var $this = $('input[name="chooseeditoperation"]');
			$this.next().children().val('');
			$this.next().children().next().children().val('');
			$('#concepttoremove').prop('selectedIndex', 0);
			$('#firstconcepttomerge').prop('selectedIndex', 0);
			$('#secondconcepttomerge').prop('selectedIndex', 0);
			$('#concepttosplit').prop('selectedIndex', 0);
			$('#applyeditoperations').show();
		});
		
		$('#applyeditoperations').on('click', function(e) {
			e.preventDefault();
			$.get("http://127.0.0.1:8000/AdvoCate/applyeditoperations/", function(response){
				var trainingdata = response['trainingset'];
				$('#updatedtrainingsetmessage').html("Trainingset updated!");
				$('#instances').html(trainingdata.length - 1);
				$('#Attributes').html(trainingdata[0].length);
				hot.loadData(trainingdata);
				$('#applyeditoperations').attr('disabled', 'disabled');
			
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

		$('input[name="validationoption"]').on('click', function() {
			var $this = $(this);
			$this.next().children().removeAttr('disabled');
			$this.siblings('input').next().children().attr('disabled', 'disabled');

		});

		$('#createsignaturefile').on('click', function(e) {
				if ($('#classifiertype').val() != "" && $('input[name=validationoption]:checked').val() != null) {
					e.preventDefault();
					$('#suggestions_section').hide();
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
									var a = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Category </th><th> Mean Vector </th></tr>";
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
	
									var b = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Category </th><th> Variance </th></tr>";
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
	
									var d = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Category </th><th> Producer's accuracy </th><th> User's accuracy </th><th> Omission error </th><th> Commission error </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										d = d + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										var producerAccuracy = parseFloat(response['prodacc'][i]);
										var userAccuracy = parseFloat(response['useracc'][i]);
										d = d + producerAccuracy + "</td><td>" + userAccuracy + "</td><td>" + parseFloat(1 - producerAccuracy).toFixed(2)
											+ "</td><td>" + parseFloat(1 - userAccuracy).toFixed(2) + "</td></tr>";
	
									}
									d = d + "</table>";
									$('#ErrorAccuracy').html(d);
									
									var e = "<p style=\"font-size: 14px; margin-left: 5px; margin-right: 5px\">Jeffries-Matusita (JM) distance between probability distribution models of various categories:</p><br />";
									e = e + "<table style=\"width:100%\" class=\" table table-bordered\"><tr> <th> </th>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										e = e + "<th>" + response['listofclasses'][i] + "</th>";
									}
									e = e + "</tr>";
									for (var i = 0; i < response['jmdistances'].length; i++){
										e = e + "<tr><th>" + response['listofclasses'][i] + "</th>";
										for (var j = 0; j < response['jmdistances'][i].length; j++){
											e = e + "<td>" + response['jmdistances'][i][j] + "</td>";
										}
										e = e + "</tr>";
									}
									e = e + "</table>";
									$('#JMDistance').html(e);
									
									if (response['suggestion_list'].length!=0){
										
										var f = "<legend style=\"font-size: 18px; background-color: gainsboro\" align=\"center\">Suggestions</legend>";
										f= f + "<label style=\"font-size: 15px; margin-left: 5px; margin-right: 5px\">List of suggestions to increase the accuracy of classification model:</label>" + 
											"<ul class=\" list-group\" style=\" margin-left: 5px; margin-right: 5px; margin-bottom: 5px\">";
										for (var i = 0; i < response['suggestion_list'].length; i++){
											f = f + "<li class=\"list-group-item\"> Merge categories - <em>" + response['suggestion_list'][i][0] + "</em> and <em>" + response['suggestion_list'][i][1] +
												"</em> </br> OR remove category <em>" + response['suggestion_list'][i][0] + "</em></li>";
										}
										f = f + "</ul>";
										$('#suggestions_section').html(f);
										$('#suggestions_section').show();
									}
									
									
									
									$('#meanvectors').hide();
									$('#variance').hide();
									$('#confusionmatrix1').hide();
									$('#ErrorAccuracy').hide();
									$('#JMDistance').hide();
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
									$('#confusionmatrix2').hide();
	
								}
								if (response['common_categories_comparison']) {
									if (response['common_categories_comparison'][0].length==9){
										var a = "<legend style=\"font-size: 18px; background-color: gainsboro\" align=\"center\">Comparison between existing categories and the new modelled categories</legend>";
										a =	a + "<table style=\"width:95%\" align=\"center\"class=\" table table-bordered\"><tr><th>Category</th><th>Model type</th><th>Validation</th>" +
												"<th>Prod accuracy</th><th>User accuracy</th><th>Model type (new)</th><th>Validation (new)</th><th>Prod accuracy (new)</th><th>User accuracy (new)</th></tr>";
										for (var i=0; i< response['common_categories_comparison'].length; i++){
											a = a + "<tr><td>" + response['common_categories_comparison'][i][0] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][6] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][5] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][7] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][8] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][1] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][2] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][3] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][4] + "</td></tr>";
										}
										a = a + "</table>";
										
										$('#signaturefilecomparison').html(a);
										$('#signaturefilecomparison').show();
									}
									else{
										var a = "<legend style=\"font-size: 18px; background-color: gainsboro\" align=\"center\">Comparison between existing categories and the new modelled categories</legend>";
										a =	a + "<table style=\"width:95%\" align=\"center\"class=\" table table-bordered\"><tr><th>Category</th><th>Validation</th>" +
												"<th>Prod accuracy</th><th>User accuracy</th><th>Validation (new)</th><th>Prod accuracy (new)</th><th>User accuracy (new)</th><th>JM distance</th></tr>";
										for (var i=0; i< response['common_categories_comparison'].length; i++){
											a = a + "<tr><td>" + response['common_categories_comparison'][i][0] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][6] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][5] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][7] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][8] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][1] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][2] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][3] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][4] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][9] + "</td></tr>";
										}
										a = a + "</table>";
										
										$('#signaturefilecomparison').html(a);
										$('#signaturefilecomparison').show();
										
									}
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
						$('#JMDistance').hide();
					} else if (detailsoption == '2') {
						console.log(detailsoption);
						$('#meanvectors').hide();
						$('#variance').show();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').hide();
						$('#JMDistance').hide();
					} else if (detailsoption == '3') {
						$('#meanvectors').hide();
						$('#variance').hide();
						$('#confusionmatrix1').show();
						$('#ErrorAccuracy').hide();
						$('#JMDistance').hide();
					} else if (detailsoption == '4') {
						$('#meanvectors').hide();
						$('#variance').hide();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').show();
						$('#JMDistance').hide();
					} else {
						$('#meanvectors').hide();
						$('#variance').hide();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').hide();
						$('#JMDistance').show();

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
					$('#classificationresult').show();
					var c = "<img style=\"width:95%; height:95%\" src=\"/static/maps/" + response['map'] + "\" />";
					$('#classifiedmap').html(c);
					var d = "<label>Legend</label>"
							+ "<table style=\"width:100%\" class=\" table table-bordered\">";
					for (var i = 0; i < response['categories'].length; i++) {
						d = d + "<tr><td>" + "<img src=\"/static/images/" + response['categories'][i] + ".png\" />" +
							"</td><td>" + response['categories'][i] + "</td></tr>";
					}							
					d = d + "</table>";
						
					$('#categorycolors').html(d);
					
				}
			});
		});

	}

	// Script for 'Change recognition' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/changerecognition/')) {
		
		$('#yesforchange').on('click', function(e) {
			e.preventDefault();
			$.get("http://127.0.0.1:8000/AdvoCate/createChangeEventForNewTaxonomy/", function(data){
				$('#listofchangeoperations').show();
				//x = "<dl id = \"compositechangeoperations\"style=\" margin:auto; width: 550px\">";
				x = "";
				for (var i = 0; i < data['listOfOperations'].length; i++) {
					a = i + 1;
					id = "operation_" + i;
					x = x + "<dt style=\"cursor:pointer; font-weight:normal; line-height: 2.5em; background:#e4e4e4; border-bottom: 1px solid #c4c4c4; border-top: 1px solid white\"> &nbsp;&nbsp;" + a + ". &nbsp;&nbsp;&nbsp;" + data['listOfOperations'][i][0] + "</dt>";
					for (var j = 0; j < data['listOfOperations'][i][1].length; j++){
						b = j+1;
						x = x + "<dd style=\" margin-left:10px; padding: 0.5em 0; border-bottom: 1px solid #c4c4c4; display: none\"> &nbsp;&nbsp;" + b + ". &nbsp; &nbsp; &nbsp;" + data['listOfOperations'][i][1][j] + "</dd>";
					}
					
				}
				x = x + "</dl>";
			//	var d = "<table style=\"width:50%; margin: 0 auto\" class=\" table table-bordered\">";
			//	d = d + "<tr><th>#</th><th>Change operation</th>" ;
			//	for (var k = 1; k < data['listOfOperations'].length+1; k++) {
			//		d = d + "<tr><td>" + k + "</td>" + "<td>" + data['listOfOperations'][k-1] + "</td></tr>";
			//	}				
			//	d = d + "</table>";
				
				$('#changeevent').show();
				$('#compositechangeoperations').html(x);
				$('#commit').show();
				
				$('#yesforchange').attr('disabled', 'disabled');
				$('#noforchange').attr('disabled', 'disabled');
			});
		});
		
		$('#compositechangeoperations').on('click', 'dt', function(e) {
			e.preventDefault();
			$(this).nextUntil('dt').toggle();
			$(this).siblings('dt').nextUntil('dt').hide();
			
			
		});
		
	

		
		$('#yesforcommit').on('click', function(e) {
			e.preventDefault();
			$('#yesforcommit').attr('disabled', 'disabled');
			$('#noforcommit').attr('disabled', 'disabled');
			$.get("http://127.0.0.1:8000/AdvoCate/applyChangeOperations/", function(data){
				$('#changeevent').hide();
				$('#implement').hide();
				$('#commitsuccessmessage').show();
				$('#successmessage').html(data);
			});
		});
		
		
		
		
	}

// Script for visualization page
	if (loc.match('http://127.0.0.1:8000/AdvoCate/visualizer/')) {
		
		$('input[name="choosetaxonomyorconcepttovisualize"]').on('click', function() {
			var $this = $(this);
			if ($this.attr('value') == 'option2') {
				$('#chooseoptionsfortaxonomy').hide();
			} else {
				$('#chooseoptionsfortaxonomy').show();
			}

		});
		
		
		
		$('#ChooseLegend').on('change', function(e) {
			e.preventDefault();
			$('#Chooseconcept').attr('disabled','disabled');
			var legendpkey = this.value;
			var legendname = $('#ChooseLegend>option:selected').text();
			var data = {};
			data[1] = legendpkey;
			data[2] = legendname;
			$.post("http://127.0.0.1:8000/AdvoCate/visualizer/", data, function(response) {
				$('#taxonomy_details').show();
				var a = "<img style=\"width:70%; height:70%\" src=\"/static/taxonomyimage/" + response['image_name'] + "\" />";				
				$('#taxonomy_viz').html(a);
				var b = "<p><b>" + "Note: </b>" + response['message'] + "</p>";
				$('#model_details').html(b);
				$('#Chooseconcept').removeAttr('disabled');
				
				var b = "<option value=\"\"> Concepts in the taxonomy</option>";
				for (var i=0; i<response['concept_list'].length; i++){
					b = b + "<option id=\"concept" + i + "\" value=\"" + response['concept_list'][i][0] + "\">" + response['concept_list'][i][1] + "</option>";
				}
				$('#Chooseconcept').html(b);
				
			});
		});
		
		$('#Chooseconcept').on('change', function(e) {
			e.preventDefault();
			var conceptid = this.value;
			var conceptname = $('#Chooseconcept>option:selected').text();
			var data = {};
			data[1] = conceptid;
			data[2] = conceptname;
			$.post("http://127.0.0.1:8000/AdvoCate/getconceptdetails/", data, function(response) {
				
				
			});
		});
		
		
	}	
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