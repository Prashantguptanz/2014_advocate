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
			'height' : totalHeight - headerHeight - 320 + 'px'
		});
		$('#edittrainingset').css({
			'height' : totalHeight - headerHeight - 256 + 'px'
		});
	};
//
//	function setSignatureFileDetailsHeight() {
//		var headerHeight = $('#top-part').outerHeight();
//		var totalHeight = $(window).height();
//		$('#signaturefiledetails').css({
//			'height' : totalHeight - headerHeight - 180 + 'px'
//		});
//	};
	
	
	// Script for navbar
	var loc = window.location.href;

	$('.nav.navbar-nav > li').each(
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
	
	$('#show_exploration').on('click', function(e) {
		if ($(this).is(':checked')){
			$('#exploration_path_viz').show();
			totalwidth = $(window).width();
			containerwidth = 1170;
			remainingwidth = (totalwidth - containerwidth)/2;
			width_of_exp =(remainingwidth-50) + 'px';
			$('.pop_con').css('width', width_of_exp);
		}
		else{
			$('#exploration_path_viz').hide();
		}
			
	});
	
	if ($('#show_exploration').is(':checked')){
		if (loc.match('http://127.0.0.1:8000/AdvoCate/home/') || loc == "http://127.0.0.1:8000/AdvoCate/") {
			$('#show_exploration').prop("checked", false);
		}
		else{
			if (!$.trim($('#collapse0').html()).length){
				$('#show_exploration').prop("checked", false);
			}
			else{
				$('#exploration_path_viz').show();
				totalwidth = $(window).width();
				containerwidth = 1170;
				remainingwidth = (totalwidth - containerwidth)/2;
				width_of_exp =(remainingwidth-50) + 'px';
				$('.pop_con').css('width', width_of_exp);
			}
		}
	}
	
	$('#exploration_path_viz').on('shown.bs.collapse', function (e){
		if ($('#collapse0').hasClass('in')){
			$('#collapse0').height('600px');
		}
	});

	

	function setWidthOfBody() {
		totalwidth = $(window).width();
		containerwidth = 1170;
		remainingwidth = (totalwidth - containerwidth)/2;
		newwidth = remainingwidth + 'px';
		$('.container').attr('style', 'float:left');
		$('.container').css('margin-left', newwidth);
		
	};
	
	$(window).on('resize',function(){
		setWidthOfBody();
	});
	
	$('[data-toggle="popover"]').popover();
	
	
	var popOverSettings = {
	    placement: 'top',
	    container: '.pop_con',
	    html: true,
	    selector: '[rel="popover"]'
	};
	
	// Script for 'Home' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/home/')) {
		$('[data-toggle="popover"]').popover();

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
	
	$(window).on('resize', function() {
		setTrainingSamplesTableHeight();
	});

	
	// Script for 'Training Samples' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/trainingsample/')) {
		
		$('[data-toggle="popover"]').popover();
		$('.dropdown-toggle').dropdown();
		
		var trainingdatacontainer = document.getElementById('trainingdataTable'), hot;
		hot = new Handsontable(trainingdatacontainer, settings1);
		
		setTrainingSamplesTableHeight();
		// call the setHeight function, every time window is resized
		$(window).on('resize', function() {
			setTrainingSamplesTableHeight();
		});

		$('input[name="choosetrainingfile"]').on('click', function() {
			var $this = $(this);
			$this.next().children().removeAttr('disabled');
			$this.siblings('input').next().children().attr('disabled', 'disabled');
			if ($this.attr('value') == 'option2') {
				$('#newconceptsanddetails').show();
				$('#categoriesandsamples_changeexistingtaxonomy').html("");
				$('#buttonsforcreatingtrainingsample').show();
				$('#trainingsetname1').hide();
				$('#savetrainingset1').hide();
				$('#submittrainingsamples1').hide();
				$('#viewandedittrainingset').hide();
				var no_of_concepts_while_modeling_changes =1;
			} else {
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
		
		
		//Script to deal when a new training set is created for a new taxonomy
		var no_of_concepts =2;
		
		$('#addmorecategories').on('click', function(e) {
			e.preventDefault();
			no_of_concepts +=1;
			a = "<label for=\"concept" + no_of_concepts + "\" style=\"font-weight:normal\">Concept " + no_of_concepts + ":</label>";
			a = a + "<input id=\"concept" + no_of_concepts + "\" style=\"margin-left: 34px\" type=\"text\" placeholder=\"Enter concept name\"  required /><br /><br />";
			$(a).insertBefore('#addmorecategoriesorsubmit');
		
		});
		
		//script to deal when user click submit button after adding all the concept names
		$('#submittrainingsamples').on('click', function(e) {
			e.preventDefault();
			$('#trainingsetanddetails').show();
			$('#savetrainingset').show();
			$('#submittrainingsamples').hide();
			$('#addmorecategories').hide();
			
		});
		
		// Script to deal when user is done uploading the trainingset and details of trainingset collection
		$('#savetrainingset').on('click', function(e) {
			e.preventDefault();
			var $this = $('#categoriesandsamples');
			if ($('#categoriesandsamples input:empty').length == 0){
				console.log($this);
			}
			else{
				console.log("here");
			}
			var formdata = new FormData();
			no_of_concepts = 0;
			concept_list = [];
			while (true){
				if ($($this[0][no_of_concepts]).prop('type')=='text'){
					concept_list.push($this[0][no_of_concepts].value);
					no_of_concepts +=1;
				}
				else{
					break;
				}
				
			}
			console.log(concept_list);
			formdata.append('concept_list', concept_list);
			trainingset = $('#trainingfilefornewtaxonomy')[0].files;
			$.each(trainingset, function(i, file){
				formdata.append('file', file);
			});
			
			formdata.append('trainingsetfilename', $('#trainingsetfilename')[0].value);
			formdata.append('FieldResearcherName', $('#FieldResearcherName')[0].value);
			formdata.append('TrainingTimePeriodStartDate', $('#TrainingTimePeriodStartDate')[0].value);
			formdata.append('TrainingTimePeriodEndDate', $('#TrainingTimePeriodEndDate')[0].value);
			formdata.append('Description', $('#Description')[0].value);
			
			$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/AdvoCate/trainingsample/",
				async : true,
				processData : false,
				contentType : false,
				data : formdata,
				success : function(response) {
					$('#trainingdataTable').show();
					$('#show_exploration').prop("checked", true);
					$('#exploration_path_viz').show();
					totalwidth = $(window).width();
					containerwidth = 1170;
					remainingwidth = (totalwidth - containerwidth)/2;
					width_of_exp =(remainingwidth-50) + 'px';
					$('.pop_con').css('width', width_of_exp);
					$('#newconceptsanddetails').hide();
					$('#viewandedittrainingset').show();
					var trainingdata = response['trainingset'];
					var classes = response['classes'];
					hot.loadData(trainingdata);
					$('#instances').html(trainingdata.length - 1);
					$('#Attributes').html(trainingdata[0].length);

					$('#trainingdataTable').show();
					hot.loadData(trainingdata);
					
					a = "<option>Choose a concept</option>";
					b = "";
					d = "<option>Choose the concept to be split</option>";
					list_of_classes ="";
					for (var i = 0; i < classes.length; i++){
						a = a + "<option>" + classes[i] + "</option>";
						b = b + "<option>" + classes[i] + "</option>";
						d = d + "<option>" + classes[i] + "</option>";
						list_of_classes = list_of_classes + classes[i] + ", ";
					}
					$('#concepttoremove').html(a);
					$('#concepttorename').html(a);
					$('#concepttoedit').html(a);
					$('#conceptstomerge').html(b);
					$('#conceptstogroup').html(b);
					$('#concepttosplit').html(d);
					
					
					
					if (response['new_taxonomy'] == 'True'){
						x = "<div style = \"width:220px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Creating new taxonomy</span></div>";
						for (var i = 0; i < response['current_exploration_chain'].length; i++){
							x = x + "<div style=\"width:1px; height:80px; border: 1px solid rgba(0, 0, 0, 0.5);  margin-right:190px; float:right\"></div>";
							if (response['current_exploration_chain'][i][0]=='Create trainingset'){
								bgcolor = "#fbb4ae";
							}
							else if (response['current_exploration_chain'][i][0]=='Change trainingset'){
								bgcolor = "#b3cde3";
							}
							else if (response['current_exploration_chain'][i][0]=='Training activity'){
								bgcolor = "#ccebc5";
							}
							else if (response['current_exploration_chain'][i][0]=='Classification'){
								bgcolor = "#decbe4";
							}
							else{
								bgcolor = "#fed9a6";
							}
							x = x + "<div style=\"width:135px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background:" +
								bgcolor + "; margin: auto; float:right; margin-right:125px\"><span><a style= \"color: #000\"href=\"javascript://\" rel=\"popover\" title=\"" + response['current_exploration_chain'][i][1] + 
								"\" data-html=\"true\" data-toggle=\"popover\" data-content=\"" + response['current_exploration_chain'][i][2] + "\">" + response['current_exploration_chain'][i][0] + "</a></span></div>";
						}
						$('#collapse0').html(x);
						$('pop_con').popover(popOverSettings);
						$('[data-toggle="popover"]').popover();
					}
					
				}
			});
			
		});

		//Script to deal when a new training set is created to model changes in an existing taxonomy
		var no_of_concepts_while_modeling_changes =1;
		$('#addnewcategory').on('click', function(e) {
			a = "</br><form id=\"concept" + no_of_concepts_while_modeling_changes + "details\"></form>";
			b = $('#newconceptdetails').html();
			
			if (no_of_concepts_while_modeling_changes==1){
				$('#categoriesandsamples_changeexistingtaxonomy').append(a);
				$('#categoriesandsamples_changeexistingtaxonomy form:last').html(b);
				$('#categoriesandsamples_changeexistingtaxonomy form:last').show();
				$('#submittrainingsamples1').show();
				no_of_concepts_while_modeling_changes +=1;
			}
			else{
				$this = $('#categoriesandsamples_changeexistingtaxonomy form:eq(-1)');
				saveTrainingSamples($this, a, b);
			}
		});
		
		$('#addexistingcategory').on('click', function(e) {
			a = "</br><form id=\"concept" + no_of_concepts_while_modeling_changes + "details\"></form>";
			b = $('#existingconceptdetails').html();
			
			if (no_of_concepts_while_modeling_changes==1){
				$('#categoriesandsamples_changeexistingtaxonomy').append(a);
				$('#categoriesandsamples_changeexistingtaxonomy form:last').html(b);
				$('#categoriesandsamples_changeexistingtaxonomy form:last').show();
				$('#submittrainingsamples1').show();
				no_of_concepts_while_modeling_changes +=1;
			}
			else{
				$this = $('#categoriesandsamples_changeexistingtaxonomy form:eq(-1)');
				saveTrainingSamples($this, a, b);
			}
		});
		
		$('#mergecategories').on('click', function(e) {
			a = "</br><form id=\"concept" + no_of_concepts_while_modeling_changes + "details\"></form>";
			b = $('#mergingconceptdetails').html();
						
			if (no_of_concepts_while_modeling_changes==1){
				$('#categoriesandsamples_changeexistingtaxonomy').append(a);
				$('#categoriesandsamples_changeexistingtaxonomy form:last').html(b);
				$('#categoriesandsamples_changeexistingtaxonomy form:last').show();
				$('#submittrainingsamples1').show();
				no_of_concepts_while_modeling_changes +=1;
			}
			else{
				
				$this = $('#categoriesandsamples_changeexistingtaxonomy form:eq(-1)');
				saveTrainingSamples($this, a, b);
			}
		});
		
		$('#splitcategories').on('click', function(e) {
			a = "</br><form id=\"concept" + no_of_concepts_while_modeling_changes + "details\" ></form>";
			b = $('#splittingconceptdetails').html();
						
			if (no_of_concepts_while_modeling_changes==1){
				$('#categoriesandsamples_changeexistingtaxonomy').append(a);
				$('#categoriesandsamples_changeexistingtaxonomy form:last').html(b);
				$('#categoriesandsamples_changeexistingtaxonomy form:last').show();
				$('#submittrainingsamples1').show();
				no_of_concepts_while_modeling_changes +=1;
			}
			else{
				$this = $('#categoriesandsamples_changeexistingtaxonomy form:eq(-1)');
				saveTrainingSamples($this, a, b);
			}
		});
		
		
		
		$('#submittrainingsamples1').on('click', function(e) {
			$this = $('#categoriesandsamples_changeexistingtaxonomy form:eq(-1)');
			saveTrainingSamples($this);
			$('#buttonsforcreatingtrainingsample').hide();
			$('#trainingsetanddetails1').show();
			$('#savetrainingset1').show();
		});
		

		
		// function to save training samples for a new trainingset when modelling changes
		function saveTrainingSamples($this, a1, b1) {
			
			if ($this[0][0].id=='conceptName'){
				if ($this[0][0].value != "" ){
					var formdata = new FormData();
					formdata.append('ConceptName', $this[0][0].value);
					formdata.append('ConceptType', '1');
				}
				else{
					$('#missingfields1').show();
					return true;
				}			
			}
			else if ($this[0][0].id=='existingconceptName'){
				if ( $this[0][0].value != ""){
					var conceptname = $this[0][0].value;
					var formdata = new FormData();
					formdata.append('ConceptName', conceptname);
					formdata.append('ConceptType', '2');
				}
				else{
					$('#missingfields1').show();
					return true;
				}
			}
			else if ($this[0][0].id=='firstconcepttomerge'){
				if ( $this[0][0].value != "" && $this[0][1].value != "" && $this[0][2].value != ""){
					var formdata = new FormData();
					formdata.append('FirstConceptName', $this[0][0].value);
					formdata.append('SecondConceptName', $this[0][1].value);
					formdata.append('MergedConceptName', $this[0][2].value);
					formdata.append('ConceptType', '3');
					
				}
				else{
					$('#missingfields1').show();
					return true;
				}
				
			}
			else{
				if ( $this[0][0].value != "" && $this[0][1].value != "" ){
					var formdata = new FormData();
					formdata.append('ConceptToSplit', $this[0][0].value);
					formdata.append('conceptstosplitinto', $this[0][1].value);
					formdata.append('ConceptType', '4');
				}
				else{
					$('#missingfields1').show();
					return true;
				}
			}
			formdata.append('IsFinalSample', 'False');
			if (no_of_concepts_while_modeling_changes == 2){
				formdata.append('IsFirstSample', 'True');
			}
			
			
		$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/AdvoCate/trainingsample/",
				async : true,
				processData : false,
				contentType : false,
				data : formdata,
				success : function(response) {
					$('#categoriesandsamples_changeexistingtaxonomy').append(a1);
					$('#categoriesandsamples_changeexistingtaxonomy form:last').html(b1);
					$('#categoriesandsamples_changeexistingtaxonomy form:last').show();
					no_of_concepts_while_modeling_changes +=1;
					$('#missingfields1').hide();
					
				}
			}); 

		};
		
		$('#savetrainingset1').on('click', function(e) {
			var formdata = new FormData();
			trainingset = $('#trainingfiletochangeexistingtaxonomy')[0].files;
			$.each(trainingset, function(i, file){
				formdata.append('file', file);
			});
			
			formdata.append('trainingsetfilename', $('#trainingsetfilename1')[0].value);
			formdata.append('FieldResearcherName', $('#FieldResearcherName1')[0].value);
			formdata.append('TrainingTimePeriodStartDate', $('#TrainingTimePeriodStartDate1')[0].value);
			formdata.append('TrainingTimePeriodEndDate', $('#TrainingTimePeriodEndDate1')[0].value);
			formdata.append('Description', $('#Description1')[0].value);
			formdata.append('IsFinalSample', 'True');
			
			$.ajax({
				type : "POST",
				url : "http://127.0.0.1:8000/AdvoCate/trainingsample/",
				async : true,
				processData : false,
				contentType : false,
				data : formdata,
				success : function(response) {
					if (response['trainingset']){
						$('#newconceptsanddetails').hide();
						$('#viewandedittrainingset').show();
						var trainingdata = response['trainingset'];
						var classes = response['classes'];
						$('#instances').html(trainingdata.length - 1);
						$('#Attributes').html(trainingdata[0].length);
						
						$('#show_exploration').prop("checked", true);
						$('#trainingdataTable').show();
						hot.loadData(trainingdata);
						$('#exploration_path_viz').show();
						totalwidth = $(window).width();
						containerwidth = 1170;
						remainingwidth = (totalwidth - containerwidth)/2;
						width_of_exp =(remainingwidth-50) + 'px';
						$('.pop_con').css('width', width_of_exp);
						
						x = "<option>Choose a concept</option>";
						b = "";
						//c = "<option>Choose second concept to merge</option>";
						d = "<option>Choose the concept to be split</option>";
						for (var i = 0; i < classes.length; i++){
							x = x + "<option>" + classes[i] + "</option>";
							b = b + "<option>" + classes[i] + "</option>";
							//c = c + "<option>" + classes[i] + "</option>";
							d = d + "<option>" + classes[i] + "</option>";
						}
						$('#concepttoremove').html(x);
						$('#concepttorename').html(x);
						$('#concepttoedit').html(x);						
						$('#conceptstomerge').html(b);
						$('#conceptstogroup').html(b);
						$('#selectconcepttosplit').html(d);
						
						
						
						if (response['common_categories_message']){
							$('#trainingsetcomparison').show();
							var a = "<label style=\"font-size: 14px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
									"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
							a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common concepts</div>";
							a = a + " <div class=\"panel-body\"> <p><em> Note:" + response['common_categories_message'] + "</em></p></div>";
							a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
						
							for (var i = 0; i < response['common_categories'].length; i++){
								a = a + "<li class=\"list-group-item\">" + response['common_categories'][i] + "</li>";
							}
							a = a + "</ul></div>";
							a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New concepts</div>";
							a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
						
							for (var i = 0; i < response['new_categories'].length; i++){
								a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
							}
							a = a + "</ul></div>";
							
							if (response['deprecated_categories'].length!=0){
								a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Concepts deprecated</div>";
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
							var a = "<label style=\"font-size: 14px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
									"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
							a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common concepts</div>";
							a = a + "<table class=\"table\"><tr><th> Concept</th><th> J-Index (similarity between trainingsamples) </th></tr>";

							for (var i = 0; i < response['common_categories'].length; i++){
								a = a + "<tr><td>" + response['common_categories'][i][0] + "</td><td>" + response['common_categories'][i][1] + "</td></tr>";
							}
							a = a + "</table></div>";
							
							a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New concepts</div>";
							a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
						
							for (var i = 0; i < response['new_categories'].length; i++){
								a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
							}
							a = a + "</ul></div>";
							
							if (response['deprecated_categories'].length!=0){
								a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Concepts deprecated</div>";
								a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
							
								for (var i = 0; i < response['deprecated_categories'].length; i++){
									a = a + "<li class=\"list-group-item\">" + response['deprecated_categories'][i] + "</li>";
								}
								a = a + "</ul></div>";
							}
							$('#trainingsetcomparisondetails').html(a);
							
						}
						if (response['new_taxonomy'] == 'False'){
							x = "<div style = \"width:310px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Exploring changes in existing taxonomy</span></div>";
							for (var i = 0; i < response['current_exploration_chain'].length; i++){
								x = x + "<div style=\"width:1px; height:80px; border: 1px solid rgba(0, 0, 0, 0.5);  margin-right:190px; float:right\"></div>";
								if (response['current_exploration_chain'][i][0]=='Create trainingset'){
									bgcolor = "#fbb4ae";
								}
								else if (response['current_exploration_chain'][i][0]=='Change trainingset'){
									bgcolor = "#b3cde3";
								}
								else if (response['current_exploration_chain'][i][0]=='Training activity'){
									bgcolor = "#ccebc5";
								}
								else if (response['current_exploration_chain'][i][0]=='Classification'){
									bgcolor = "#decbe4";
								}
								else{
									bgcolor = "#fed9a6";
								}
								x = x + "<div style=\"width:135px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background:" +
									bgcolor + "; margin: auto; float:right; margin-right:125px\"><span><a style= \"color: #000\"href=\"javascript://\" rel=\"popover\" title=\"" + response['current_exploration_chain'][i][1] + 
									"\" data-html=\"true\" data-toggle=\"popover\" data-content=\"" + response['current_exploration_chain'][i][2] + "\">" + response['current_exploration_chain'][i][0] + "</a></span></div>";
							}
							$('#collapse0').html(x);
							$('pop_con').popover(popOverSettings);
							$('[data-toggle="popover"]').popover();
						}
						
					}
					
				}
			}); 
			
		});
		
		

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
				b = "";
				//c = "<option>Choose second concept to merge</option>";
				d = "<option>Choose the concept to be split</option>";
				for (var i = 0; i < classes.length; i++){
					a = a + "<option>" + classes[i] + "</option>";
					b = b + "<option>" + classes[i] + "</option>";
					//c = c + "<option>" + classes[i] + "</option>";
					d = d + "<option>" + classes[i] + "</option>";
				}
				$('#concepttoremove').html(a);
				$('#concepttorename').html(a);
				$('#concepttoedit').html(a);
				$('#conceptstomerge').html(b);
				$('#conceptstogroup').html(b);
				$('#selectconcepttosplit').html(d);
				
				if (response['common_categories_message']){
					$('#trainingsetcomparison').show();
					var a = "<label style=\"font-size: 14px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
							"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common concepts</div>";
					a = a + " <div class=\"panel-body\"> <p><em> Note:" + response['common_categories_message'] + "</em></p></div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['common_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['common_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New concepts</div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['new_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					
					if (response['deprecated_categories'].length!=0){
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Concepts deprecated</div>";
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
					var a = "<label style=\"font-size: 14px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
							"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common concepts</div>";
					a = a + "<table class=\"table\"><tr><th> Concept</th><th> J-Index (simialrity between training samples) </th></tr>";

					for (var i = 0; i < response['common_categories'].length; i++){
						a = a + "<tr><td>" + response['common_categories'][i][0] + "</td><td>" + response['common_categories'][i][1] + "</td></tr>";
					}
					a = a + "</table></div>";
					
					if (response['new_categories'].length!=0){
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New concepts</div>";
						a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
					
						for (var i = 0; i < response['new_categories'].length; i++){
							a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
						}
						a = a + "</ul></div>";
					}
					
					
					if (response['deprecated_categories'].length!=0){
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Concepts deprecated</div>";
						a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
					
						for (var i = 0; i < response['deprecated_categories'].length; i++){
							a = a + "<li class=\"list-group-item\">" + response['deprecated_categories'][i] + "</li>";
						}
						a = a + "</ul></div>";
					}
					$('#trainingsetcomparisondetails').html(a);
					
				}
				
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
				conceptname = $('#conceptname').val();
				editoperation = 1;
				var formdata = new FormData();
				var samplesfornewconcept = $('#samplesfornewconcept')[0].files;
				$.each(samplesfornewconcept, function(i, file){
					formdata.append('samplesfornewconcept', file);
				});
				formdata.append('1', '1');
				formdata.append('conceptname', conceptname);
				$.ajax({
					type : "POST",
					url : "http://127.0.0.1:8000/AdvoCate/edittrainingset/",
					async : true,
					processData : false,
					contentType : false,
					data : formdata,
					success : function(response) {
						var a = $('#editop').html();
						a = a + "<li class=\"list-group-item\">" + "Add new concept <em>" + conceptname  + "</em></li>";
						$('#editop').html(a);
						
					}
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
				concepttorename = $('#concepttorename>option:selected').text();
				newname = $('#newname').val();
				editoperation = 3;
				var data = {};
				data[1] = editoperation;
				data[2] = concepttorename;
				data[3] = newname;
				$.post("http://127.0.0.1:8000/AdvoCate/edittrainingset/", data, function(response) {
					var a = $('#editop').html();
					a = a + "<li class=\"list-group-item\">" + "Rename concept <em>" + data[2]  + "</em> to <em>" + data[3] + "</em></li>";
					$('#editop').html(a);
				});
				
			}
			else if ($('input[name=chooseeditoperation]:checked').val() == "option4"){
				concepttoedit = $('#concepttoedit>option:selected').text();
				var formdata = new FormData();
				var samplesforexistingconcept = $('#samplesforexistingconcept')[0].files;
				$.each(samplesforexistingconcept, function(i, file){
					formdata.append('newsamples', file);
				});
				formdata.append('1', '4');
				formdata.append('concepttoedit', concepttoedit);
				$.ajax({
					type : "POST",
					url : "http://127.0.0.1:8000/AdvoCate/edittrainingset/",
					async : true,
					processData : false,
					contentType : false,
					data : formdata,
					success : function(response) {
						var a = $('#editop').html();
						a = a + "<li class=\"list-group-item\">" + "Edit concept <em>" + concepttoedit  + "</em></li>";
						$('#editop').html(a);
						
					}
				});
				
			}
			else if ($('input[name=chooseeditoperation]:checked').val() == "option5"){
				conceptstomerge = $('#conceptstomerge').val();
				mergedconceptname = $('#mergedconceptname').val();
				editoperation = 3;
				var formdata = new FormData();
				formdata.append('1', '5');
				for (var i=0; i<conceptstomerge.length; i++){
					x = "concept" + (i+1) + "tomerge";
					formdata.append(x, conceptstomerge[i]);
				}
				formdata.append('mergedconceptname', mergedconceptname);
				console.log(formdata);
				$.ajax({
					type : "POST",
					url : "http://127.0.0.1:8000/AdvoCate/edittrainingset/",
					async : true,
					processData : false,
					contentType : false,
					data : formdata,
					success : function(response) {
						var a = $('#editop').html();
						a = a + "<li class=\"list-group-item\">" + "Merge concepts (<em>";
						for (var i=0; i< conceptstomerge.length; i++){
							if (i+1 == conceptstomerge.length){
								a = a + conceptstomerge[i] + "</em>)";
							}
							else{
								a = a + conceptstomerge[i] + "</em>, <em>"; 
							}
							
						}
						a = a + " and create <em>" + mergedconceptname + "</em></li>";
						$('#editop').html(a);
						
					}
				});
	
			}
			else if ($('input[name=chooseeditoperation]:checked').val() == "option6"){
				conceptstogroup = $('#conceptstogroup').val();
				groupedconceptname = $('#groupedconceptname').val();
				editoperation = 6;
				var formdata = new FormData();
				formdata.append('1', '6');
				for (var i=0; i<conceptstogroup.length; i++){
					x = "concept" + (i+1) + "togroup";
					formdata.append(x, conceptstogroup[i]);
				}
				formdata.append('groupedconceptname', groupedconceptname);
				console.log(formdata);
				$.ajax({
					type : "POST",
					url : "http://127.0.0.1:8000/AdvoCate/edittrainingset/",
					async : true,
					processData : false,
					contentType : false,
					data : formdata,
					success : function(response) {
						var a = $('#editop').html();
						a = a + "<li class=\"list-group-item\">" + "Group concepts (<em>";
						for (var i=0; i< conceptstogroup.length; i++){
							if (i+1 == conceptstogroup.length){
								a = a + conceptstogroup[i] + "</em>)";
							}
							else{
								a = a + conceptstogroup[i] + "</em>, <em>"; 
							}
							
						}
						a = a + " and create <em>" + groupedconceptname + "</em></li>";
						$('#editop').html(a);
						
					}
				});
	
			}
			else{
				concepttosplit = $('#selectconcepttosplit>option:selected').text();
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
				formdata.append('1', '7');
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
			$('#concepttorename').prop('selectedIndex', 0);
			$('#concepttoedit').prop('selectedIndex', 0);
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
				$('#show_exploration').prop("checked", true);
				$('#exploration_path_viz').show();
				totalwidth = $(window).width();
				containerwidth = 1170;
				remainingwidth = (totalwidth - containerwidth)/2;
				width_of_exp =(remainingwidth-50) + 'px';
				$('.pop_con').css('width', width_of_exp);
				if (response['common_categories_message']){
					$('#trainingsetcomparison').show();
					var a = "<label style=\"font-size: 14px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
							"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common concepts</div>";
					a = a + " <div class=\"panel-body\"> <p><em> Note:" + response['common_categories_message'] + "</em></p></div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['common_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['common_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New concepts</div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['new_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					
					if (response['deprecated_categories'].length!=0){
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Concepts deprecated</div>";
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
					var a = "<label style=\"font-size: 14px; margin-left: 5px; margin-right: 5px; font-weight:normal\"><em>Comparison between new " +
							"training samples and the samples used to create the taxonomy previously:</em></label></br></br>";
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Common concepts</div>";
					a = a + "<table class=\"table\"><tr><th> Concept</th><th> J-Index (similarity between training samples)</th></tr>";

					for (var i = 0; i < response['common_categories'].length; i++){
						a = a + "<tr><td>" + response['common_categories'][i][0] + "</td><td>" + response['common_categories'][i][1] + "</td></tr>";
					}
					a = a + "</table></div>";
					
					a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">New concepts</div>";
					a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
				
					for (var i = 0; i < response['new_categories'].length; i++){
						a = a + "<li class=\"list-group-item\">" + response['new_categories'][i] + "</li>";
					}
					a = a + "</ul></div>";
					
					if (response['deprecated_categories'].length!=0){
						a = a +	"<div class=\"panel panel-default\"><div class=\"panel-heading\" style =\" font-weight:bold\">Concepts deprecated</div>";
						a = a + "<ul class=\" list-group\" style =\" margin-left:7px\">";
					
						for (var i = 0; i < response['deprecated_categories'].length; i++){
							a = a + "<li class=\"list-group-item\">" + response['deprecated_categories'][i] + "</li>";
						}
						a = a + "</ul></div>";
					}
					$('#trainingsetcomparisondetails').html(a);
					
				}
				if (response['new_taxonomy']){
					if (response['new_taxonomy'] == 'True'){
						x = "<div style = \"width:220px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Creating new taxonomy</span></div>";
					}
					else{
						x = "<div style = \"width:310px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Exploring changes in existing taxonomy</span></div>";
					}
					for (var i = 0; i < response['current_exploration_chain'].length; i++){
						x = x + "<div style=\"width:1px; height:80px; border: 1px solid rgba(0, 0, 0, 0.5);  margin-right:190px; float:right\"></div>";
						if (response['current_exploration_chain'][i][0]=='Create trainingset'){
							bgcolor = "#fbb4ae";
						}
						else if (response['current_exploration_chain'][i][0]=='Change trainingset'){
							bgcolor = "#b3cde3";
						}
						else if (response['current_exploration_chain'][i][0]=='Training activity'){
							bgcolor = "#ccebc5";
						}
						else if (response['current_exploration_chain'][i][0]=='Classification'){
							bgcolor = "#decbe4";
						}
						else{
							bgcolor = "#fed9a6";
						}
						x = x + "<div style=\"width:135px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background:" +
							bgcolor + "; margin: auto; float:right; margin-right:125px\"><span><a style= \"color: #000\"href=\"javascript://\" rel=\"popover\" title=\"" + response['current_exploration_chain'][i][1] + 
							"\" data-html=\"true\" data-toggle=\"popover\" data-content=\"" + response['current_exploration_chain'][i][2] + "\">" + response['current_exploration_chain'][i][0] + "</a></span></div>";
					}
					$('#collapse0').html(x);
					$('.pop_con').popover(popOverSettings);
					
				}
			
			});
		});

	}

	// Script for 'Signature file' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/signaturefile/')) {
		$('[data-toggle="popover"]').popover();
		//setSignatureFileDetailsHeight();

		//$(window).on('resize', function() {
		//	setSignatureFileDetailsHeight();
		//});

		$('.dropdown-toggle').dropdown();

		$('input[name="validationoption"]').on('click', function() {
			var $this = $(this);
			$this.next().children().removeAttr('disabled');
			$this.siblings('input').next().children().attr('disabled', 'disabled');

		});
		
		$('#changelimits').on('click', function(e) {
			e.preventDefault();
			$('#jm_limit').removeAttr('disabled');
			$('#acc_limit').removeAttr('disabled');
			$('#submitchangelimits').show();
			$('#changelimits').attr('disabled', 'disabled');
		});
		
		$('#submitchangelimits').on('click', function(e) {
			e.preventDefault();
			$('#jm_limit').attr('disabled', 'disabled');
			$('#acc_limit').attr('disabled', 'disabled');
			$('#submitchangelimits').hide();
			$('#changelimits').removeAttr('disabled');
			var data = {};
			data['1'] = $('#jm_limit').val();
			data['2'] = $('#acc_limit').val();
			console.log(data['1']);
			console.log(data['2']);
			$.post("http://127.0.0.1:8000/AdvoCate/changethresholdlimits/", data, function(response) {
				
			});
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
								$('#signaturefiledetails').show();
								$('#validationscore').html("<b>Validation score:  </b>"+ response['score']);
								$('#kappa').html("<b>Kappa:  </b>"+ response['kappa']);
								if (response['meanvectors']) {
									$('#DecisionTreemodeldetails').hide();
									$('#NaiveBayesmodeldetails').show();
									$('#SVMmodeldetails').hide();
									var a = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Category </th><th> Mean Vector </th><th> Variance </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										a = a + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										var meanvectorarray = response['meanvectors'][i];
										for (var j = 0; j < meanvectorarray.length; j++) {
											a = a + parseFloat(meanvectorarray[j]).toFixed(2) + " |  ";
										}
										a = a + "</td><td>";
										var variancearray = response['variance'][i];
										for (var k = 0; k < variancearray.length; k++) {
											a = a + parseFloat(variancearray[k]).toFixed(2) + " |  ";
										}
										a = a + "</td></tr>";
									}
									a = a + "</table>";
									$('#meanvectorsandvariance').html(a);
	
									var c = "<img style=\"width:50%; height:50%; margin-left:auto; margin-right:auto; display:block\" src=\"/static/images/" + response['cm'] + "\" />";
									$('#confusionmatrix1').html(c);
	
									var d = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Category </th><th> Producer's accuracy </th><th> User's accuracy </th><th> Omission error </th><th> Commission error </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										var producerAccuracy = parseFloat(response['prodacc'][i]);
										var userAccuracy = parseFloat(response['useracc'][i]);
										if (producerAccuracy < response['acc_limit'] && userAccuracy < response['acc_limit'] || (producerAccuracy + userAccuracy)< 2.0* response['acc_limit'] ){
											d = d + "<tr bgcolor=\"#ff7f7f\"><td>" + response['listofclasses'][i] + "</td><td>";
										}
										else {
											d = d + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										}
										
										d = d + producerAccuracy + "</td><td>" + userAccuracy + "</td><td>" + parseFloat(1 - producerAccuracy).toFixed(2)
											+ "</td><td>" + parseFloat(1 - userAccuracy).toFixed(2) + "</td></tr>";
	
									}
									d = d + "</table>";
									$('#ErrorAccuracy').html(d);
									cellwidth = 100/(response['listofclasses'].length+1);
									var e = "<p style=\"font-size: 14px; margin-left: 5px; margin-right: 5px\">Jeffries-Matusita (JM) distance between probability distribution models of various categories:</p><br />";
									e = e + "<table style=\"width:100%\" class=\" table table-bordered\"><tr> <th style=\"width:" +cellwidth+ "\"> </th>";
									
									
									for (var i = 0; i < response['listofclasses'].length; i++) {
										e = e + "<th style=\"width:" + cellwidth +  "%\">" + response['listofclasses'][i] + "</th>";
									}
									e = e + "</tr>";
									
									for (var i = 0; i < response['jmdistances'].length; i++){
										e = e + "<tr><th>" + response['listofclasses'][i] + "</th>";
										for (var j = 0; j < response['jmdistances'][i].length; j++){
											if (response['jmdistances'][i][j] < response['jm_limit'] && response['jmdistances'][i][j] !=0){
												e = e + "<td style=\"width:" + cellwidth +  "%\" bgcolor=\"#ff7f7f\">" + response['jmdistances'][i][j] + "</td>";
											}
											else{
												e = e + "<td style=\"width:" + cellwidth +  "%\">" + response['jmdistances'][i][j] + "</td>";
											}
											
										}
										e = e + "</tr>";
									}
									e = e + "</table>";
									$('#JMDistance').html(e);
									
									if (response['suggestion_list'].length!=0){
										
										var f= "<label style=\"font-size: 15px; margin-left: 15px; margin-bottom:15px\">List of suggestions to increase the accuracy of classification model:</label>";
										f = f + "<label style=\"margin-left:20px; margin-bottom:15px; margin-right: 25px; font-weight: normal\"> <em>Note: To apply one or more suggestions below," 
											+ "click the checkboxes next to them. After you have selected all the suggestions you wish to apply, click on the 'Submit' button.</em>" 
											+ "You may also go back to the 'Training Samples' page and edit the trainingset, if required.</label>";
										f = f +	"<table class=\"table\" style=\" margin: 20px; width:95%\" id=\"suggestion_table\">";
										for (var i = 0; i < response['suggestion_list'].length; i++){											
											f = f + "<tr><td><input type=\"checkbox\" style = \" width:18px; height:18px\" name=\"suggestion\" class=\"suggestion\" value=\"" + response['suggestion_list'][i][0] + "_" + response['suggestion_list'][i][1]
												+ "\" /></td><td> Merge categories - <em>" + response['suggestion_list'][i][0] + "</em> and <em>" + response['suggestion_list'][i][1]
												+ "</em> OR remove category <em>" + response['suggestion_list'][i][0] + "</em></td>"
												+ "<td><div class=\"radiox\" style=\"display:none; margin:0\"> <input type=\"radio\" name=\"mergeorremove" + i + "\" value=\"1\" class=\"mergeorremove\"/>&nbsp;Merge" 
												+ "<input type=\"radio\" name=\"mergeorremove" + i + "\" value=\"2\" class=\"mergeorremove\" style=\"margin-left:20px\"/>&nbsp;Remove</div></td>"
												+ "<td><input  type=\"text\" size=\"25\" placeholder=\"Enter merged category name\" style=\"display:none\" required /></td></tr>";

										}
										f = f + "</table>";
										f = f + "<input type=\"submit\" id=\"submitsuggestions\" value=\"Submit\" class=\"btn btn-default\" style=\"margin:20px; display:none\"/>";
										f = f + "<label id=\"successmessageforappliedsuggestions\" style=\"margin-top: 15px; margin-left:20px; margin-bottom:15px; margin-right: 25px; font-weight: normal; font-size:14px; color:green\"></label>";
										$('#collapse3').html(f);
										$('#suggestions_section').show();
									}
									
								
									
									$('#meanvectorsandvariance').hide();
									$('#confusionmatrix1').show();
									$('#ErrorAccuracy').hide();
									$('#JMDistance').hide();
									$('#collapse1').removeClass("collapse in").addClass("collapse");
								} else if (response['tree']){
									$('#NaiveBayesmodeldetails').hide();
									$('#DecisionTreemodeldetails').show();
									$('#SVMmodeldetails').hide();
									var a = "<img style=\"width:100%; height:100%\" src=\"/static/images/" + response['tree'] + "\" />";
									$('#decisiontree').html(a);
									var b = "<img style=\"width:50%; height:50%; margin-left:auto; margin-right:auto; display:block\" src=\"/static/images/" + response['cm'] + "\" />";
									$('#confusionmatrix2').html(b);
									var d = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Category </th><th> Producer's accuracy </th><th> User's accuracy </th><th> Omission error </th><th> Commission error </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										var producerAccuracy = parseFloat(response['prodacc'][i]);
										var userAccuracy = parseFloat(response['useracc'][i]);
										if (producerAccuracy < response['acc_limit'] && userAccuracy < response['acc_limit'] || (producerAccuracy + userAccuracy)< 2.0* response['acc_limit'] ){
											d = d + "<tr bgcolor=\"#ff7f7f\"><td>" + response['listofclasses'][i] + "</td><td>";
										}
										else {
											d = d + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										}
										d = d + producerAccuracy + "</td><td>" + userAccuracy + "</td><td>" + parseFloat(1 - producerAccuracy).toFixed(2)
											+ "</td><td>" + parseFloat(1 - userAccuracy).toFixed(2)+ "</td></tr>";
	
									}
									d = d + "</table>";
									$('#accuracies').html(d);
									
									if (response['suggestion_list'].length!=0){
										var f= "<label style=\"font-size: 15px; margin-left: 15px; margin-bottom:15px\">List of suggestions to increase the accuracy of classification model:</label>";
										f = f + "<label style=\"margin-left:20px; margin-bottom:15px; margin-right: 25px; font-weight: normal\"> <em>Note: To apply one or more suggestions below," 
											+ "click the checkboxes next to them. After you have selected all the suggestions you wish to apply, click on the 'Submit' button.</em>" 
											+ "You may also go back to the 'Training Samples' page and edit the trainingset, if required.</label>";
										f = f +	"<table class=\"table\" style=\" margin: 20px; width:95%\" id=\"suggestion_table\">";
										for (var i = 0; i < response['suggestion_list'].length; i++){											
											f = f + "<tr><td><input type=\"checkbox\" style = \" width:18px; height:18px\" name=\"suggestion\" class=\"suggestion\" value=\"" + response['suggestion_list'][i][0] + "_" + response['suggestion_list'][i][1]
												+ "\" /></td><td> Merge categories - <em>" + response['suggestion_list'][i][0] + "</em> and <em>" + response['suggestion_list'][i][1]
												+ "</em> OR remove category <em>" + response['suggestion_list'][i][0] + "</em></td>"
												+ "<td><div class=\"radiox\" style=\"display:none; margin:0\"> <input type=\"radio\" name=\"mergeorremove" + i + "\" value=\"1\" class=\"mergeorremove\"/>&nbsp;Merge" 
												+ "<input type=\"radio\" name=\"mergeorremove" + i + "\" value=\"2\" class=\"mergeorremove\" style=\"margin-left:20px\"/>&nbsp;Remove</div></td>"
												+ "<td><input  type=\"text\" size=\"25\" placeholder=\"Enter merged category name\" style=\"display:none\" required /></td></tr>";

										}
										f = f + "</table>";
										f = f + "<input type=\"submit\" id=\"submitsuggestions\" value=\"Submit\" class=\"btn btn-default\" style=\"margin:20px; display:none\"/>";
										f = f + "<label id=\"successmessageforappliedsuggestions\" style=\"margin-top: 15px; margin-left:20px; margin-bottom:15px; margin-right: 25px; font-weight: normal; font-size:14px; color:green\"></label>";
					
										$('#collapse3').html(f);
										$('#suggestions_section').show();
									}
									
									$('#accuracies').hide();
									$('#decisiontree').hide();
									$('#confusionmatrix2').show();
									$('#collapse1').removeClass("collapse in").addClass("collapse");
	
								}
								else{
									$('#NaiveBayesmodeldetails').hide();
									$('#DecisionTreemodeldetails').hide();
									$('#SVMmodeldetails').show();
									
									var b = "<img style=\"width:50%; height:50%; margin-left:auto; margin-right:auto; display:block\" src=\"/static/images/" + response['cm'] + "\" />";
									$('#confusionmatrix3').html(b);
									var d = "<table style=\"width:100%\" class=\" table table-bordered\"><tr><th> Category </th><th> Producer's accuracy </th><th> User's accuracy </th><th> Omission error </th><th> Commission error </th></tr>";
									for (var i = 0; i < response['listofclasses'].length; i++) {
										var producerAccuracy = parseFloat(response['prodacc'][i]);
										var userAccuracy = parseFloat(response['useracc'][i]);
										if (producerAccuracy < response['acc_limit'] && userAccuracy < response['acc_limit'] || (producerAccuracy + userAccuracy)< 2.0* response['acc_limit'] ){
											d = d + "<tr bgcolor=\"#ff7f7f\"><td>" + response['listofclasses'][i] + "</td><td>";
										}
										else {
											d = d + "<tr><td>" + response['listofclasses'][i] + "</td><td>";
										}
										d = d + producerAccuracy + "</td><td>" + userAccuracy + "</td><td>" + parseFloat(1 - producerAccuracy).toFixed(2)
											+ "</td><td>" + parseFloat(1 - userAccuracy).toFixed(2)+ "</td></tr>";
	
									}
									d = d + "</table>";
									$('#accuracies2').html(d);
									
									if (response['suggestion_list'].length!=0){
										var f= "<label style=\"font-size: 15px; margin-left: 15px; margin-bottom:15px\">List of suggestions to increase the accuracy of classification model:</label>";
										f = f + "<label style=\"margin-left:20px; margin-bottom:15px; margin-right: 25px; font-weight: normal\"> <em>Note: To apply one or more suggestions below," 
											+ "click the checkboxes next to them. After you have selected all the suggestions you wish to apply, click on the 'Submit' button.</em>" 
											+ "You may also go back to the 'Training Samples' page and edit the trainingset, if required.</label>";
										f = f +	"<table class=\"table\" style=\" margin: 20px; width:95%\" id=\"suggestion_table\">";
										for (var i = 0; i < response['suggestion_list'].length; i++){											
											f = f + "<tr><td><input type=\"checkbox\" style = \" width:18px; height:18px\" name=\"suggestion\" class=\"suggestion\" value=\"" + response['suggestion_list'][i][0] + "_" + response['suggestion_list'][i][1]
												+ "\" /></td><td> Merge categories - <em>" + response['suggestion_list'][i][0] + "</em> and <em>" + response['suggestion_list'][i][1]
												+ "</em> OR remove category <em>" + response['suggestion_list'][i][0] + "</em></td>"
												+ "<td><div class=\"radiox\" style=\"display:none; margin:0\"> <input type=\"radio\" name=\"mergeorremove" + i + "\" value=\"1\" class=\"mergeorremove\"/>&nbsp;Merge" 
												+ "<input type=\"radio\" name=\"mergeorremove" + i + "\" value=\"2\" class=\"mergeorremove\" style=\"margin-left:20px\"/>&nbsp;Remove</div></td>"
												+ "<td><input  type=\"text\" size=\"25\" placeholder=\"Enter merged category name\" style=\"display:none\" required /></td></tr>";

										}
										f = f + "</table>";
										f = f + "<input type=\"submit\" id=\"submitsuggestions\" value=\"Submit\" class=\"btn btn-default\" style=\"margin:20px; display:none\"/>";
										f = f + "<label id=\"successmessageforappliedsuggestions\" style=\"margin-top: 15px; margin-left:20px; margin-bottom:15px; margin-right: 25px; font-weight: normal; font-size:14px; color:green\"></label>";
					
										$('#collapse3').html(f);
										$('#suggestions_section').show();
									}
									
									$('#accuracies2').hide();
									$('#confusionmatrix3').show();
									$('#collapse1').removeClass("collapse in").addClass("collapse");
									
								}
								
								if (response['common_categories_comparison'] || response['split_categories_comparison'] || response['merged_categories_comparison']) {
									a= "";
									if (response['common_categories_comparison'] && response['common_categories_comparison'][0].length==9){
										a = a + "<table style=\"width:95%\" align=\"center\"class=\" table table-bordered\"><tr><th>Category</th><th>Model type</th><th>Validation</th>" +
												"<th>Prod accuracy</th><th>User accuracy</th><th>Model type (new)</th><th>Validation (new)</th><th>Prod accuracy (new)</th><th>User accuracy (new)</th></tr>";
										for (var i=0; i< response['common_categories_comparison'].length; i++){
											a = a + "<tr><td>" + response['common_categories_comparison'][i][0] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][5] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][6] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][7] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][8] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][1] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][2] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][3] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][4] + "</td></tr>";
										}
										if (response['common_categories_with_different_names_comparison'] && response['common_categories_with_different_names_comparison'].length>0){
											for (var j=0; j< response['common_categories_with_different_names_comparison'].length; j++){
												a = a + "<tr><td>" + response['common_categories_with_different_names_comparison'][j][0] + "/" + response['common_categories_with_different_names_comparison'][j][5] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][6] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][7] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][8] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][9] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][1] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][2] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][3] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][4] + "</td></tr>";
											}
										}
										a = a + "</table>";
										
									}
									if (response['common_categories_comparison'] && response['common_categories_comparison'][0].length==10){
										a = a + "<table style=\"width:95%\" align=\"center\"class=\" table table-bordered\"><tr><th>Category</th><th>Model type</th><th>Validation</th>" +
												"<th>Prod accuracy</th><th>User accuracy</th><th>Model type (new)</th><th>Validation (new)</th><th>Prod accuracy (new)</th><th>User accuracy (new)</th><th>JM distance</th></tr>";
										for (var i=0; i< response['common_categories_comparison'].length; i++){
											a = a + "<tr><td>" + response['common_categories_comparison'][i][0] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][5] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][6] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][7] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][8] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][1] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][2] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][3] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][4] + "</td>";
											a = a + "<td>" + response['common_categories_comparison'][i][9] + "</td></tr>";
										}
										if (response['common_categories_with_different_names_comparison'] && response['common_categories_with_different_names_comparison'].length>0){
											for (var j=0; j< response['common_categories_with_different_names_comparison'].length; j++){
												a = a + "<tr><td>" + response['common_categories_with_different_names_comparison'][j][0] + "/" + response['common_categories_with_different_names_comparison'][j][5] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][6] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][7] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][8] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][9] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][1] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][2] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][3] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][4] + "</td>";
												a = a + "<td>" + response['common_categories_with_different_names_comparison'][j][10] + "</td></tr>";
											}
										}
										a = a + "</table>";
										
										
									}
									if (response['split_categories_comparison'] && response['split_categories_comparison'].length>0){
										a = a + "<br /><br /><table style=\"width:95%\" align=\"center\"class=\" table table-bordered\"><tr><th>New category modelled</th><th>Existing category (that is split)</th>" +
										"<th>JM distance</th></tr>";
										for (var i=0; i< response['split_categories_comparison'].length; i++){
											a = a + "<tr><td>" + response['split_categories_comparison'][i][0] + "</td>";
											a = a + "<td>" + response['split_categories_comparison'][i][1] + "</td>";
											a = a + "<td>" + response['split_categories_comparison'][i][2] + "</td></tr>";
										}
										a = a + "</table>";
									}
									if (response['merged_categories_comparison'] && response['merged_categories_comparison'].length>0){
										a = a + "<br /><br /><table style=\"width:95%\" align=\"center\"class=\" table table-bordered\"><tr><th>Merged category (new)</th><th>Existing category (that is merged)</th>" +
										"<th>JM distance</th></tr>";
										for (var i=0; i< response['merged_categories_comparison'].length; i++){
											a = a + "<tr><td>" + response['merged_categories_comparison'][i][0] + "</td>";
											a = a + "<td>" + response['merged_categories_comparison'][i][1] + "</td>";
											a = a + "<td>" + response['merged_categories_comparison'][i][2] + "</td></tr>";
										}
										a = a + "</table>";
									}
									if (response['categories_merged_from_new_and_existing_comparison'] && response['categories_merged_from_new_and_existing_comparison'].length>0){
										a = a + "<br /><br /><table style=\"width:95%\" align=\"center\"class=\" table table-bordered\"><tr><th>Generalized category (new)</th><th>Existing category</th>" +
										"<th>JM distance</th></tr>";
										for (var i=0; i< response['categories_merged_from_new_and_existing_comparison'].length; i++){
											a = a + "<tr><td>" + response['categories_merged_from_new_and_existing_comparison'][i][0] + "</td>";
											a = a + "<td>" + response['categories_merged_from_new_and_existing_comparison'][i][1] + "</td>";
											a = a + "<td>" + response['categories_merged_from_new_and_existing_comparison'][i][2] + "</td></tr>";
										}
										a = a + "</table>";
									}

									$('#collapse4').html(a);
									$('#signaturefilecomparison').show();
									
								}
								if (response['new_taxonomy']){
									if (response['new_taxonomy'] == 'True'){
										x = "<div style = \"width:220px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Creating new taxonomy</span></div>";
									}
									else{
										x = "<div style = \"width:310px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Exploring changes in existing taxonomy</span></div>";
									}
									for (var i = 0; i < response['current_exploration_chain'].length; i++){
										x = x + "<div style=\"width:1px; height:80px; border: 1px solid rgba(0, 0, 0, 0.5);  margin-right:190px; float:right\"></div>";
										if (response['current_exploration_chain'][i][0]=='Create trainingset'){
											bgcolor = "#fbb4ae";
										}
										else if (response['current_exploration_chain'][i][0]=='Change trainingset'){
											bgcolor = "#b3cde3";
										}
										else if (response['current_exploration_chain'][i][0]=='Training activity'){
											bgcolor = "#ccebc5";
										}
										else if (response['current_exploration_chain'][i][0]=='Classification'){
											bgcolor = "#decbe4";
										}
										else{
											bgcolor = "#fed9a6";
										}
										x = x + "<div style=\"width:135px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background:" +
											bgcolor + "; margin: auto; float:right; margin-right:125px\"><span><a style= \"color: #000\"href=\"javascript://\" rel=\"popover\" title=\"" + response['current_exploration_chain'][i][1] + 
											"\" data-html=\"true\" data-toggle=\"popover\" data-content=\"" + response['current_exploration_chain'][i][2] + "\">" + response['current_exploration_chain'][i][0] + "</a></span></div>";
									}
									$('#collapse0').html(x);
									$('.pop_con').popover(popOverSettings);
									
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
						$('#meanvectorsandvariance').show();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').hide();
						$('#JMDistance').hide();
					} else if (detailsoption == '2') {
						$('#meanvectorsandvariance').hide();
						$('#confusionmatrix1').show();
						$('#ErrorAccuracy').hide();
						$('#JMDistance').hide();
					} else if (detailsoption == '3') {
						$('#meanvectorsandvariance').hide();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').show();
						$('#JMDistance').hide();
					} else {
						$('#meanvectorsandvariance').hide();
						$('#confusionmatrix1').hide();
						$('#ErrorAccuracy').hide();
						$('#JMDistance').show();

					}
				});

		$('input[name="DecisionTreemodeldetails"]').on('click',function(e) {
			var detailsoption = $('input[name="DecisionTreemodeldetails"]:checked').val();
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
		
		$('input[name="SVMmodeldetails"]').on('click',function(e) {
			var detailsoption = $('input[name="SVMmodeldetails"]:checked').val();
			if (detailsoption == '1') {
				$('#confusionmatrix3').show();
				$('#accuracies2').hide();
			} else if (detailsoption == '2') {
				$('#confusionmatrix3').hide();
				$('#accuracies2').show();
			} 
		});
		
		$('#collapse3').on('click','.suggestion', function(e) {
			$this = $(this);
			$this.closest('td').next().next().find('.radiox').toggle();
			$this.closest('td').next().next().find('.mergeorremove').prop('checked', false);
			$this.closest('td').next().next().next().find('input').hide();
			
			if ($('#collapse3 input:checkbox:checked').length > 0){
				$('#submitsuggestions').show();
			}
			else{
				$('#submitsuggestions').hide();
			}
			
		});
		
		$('#collapse3').on('click','.mergeorremove', function(e) {
			if ($(this).val() =='1'){
				$(this).closest('td').next().find('input').show();
			}
			else{
				$(this).closest('td').next().find('input').hide();
			}
			
		});
		
		$('#collapse3').on('click', '#submitsuggestions', function(e){
			e.preventDefault();
			var hasCallbackCompleted = [ true ];
			$('#collapse3 input:checkbox:checked').each(function(index){
				var f = arguments.callee;
                var args = arguments;
                var t = this;
                
                if( !hasCallbackCompleted[ index ] ){
                  window.setTimeout( function(){ f.apply(t, args); }, 5 );
                  return true; 
                }
                
                hasCallbackCompleted[ index + 1 ] = false;
				
				data = {};
				categories = $(this).val();
				categories_arr = categories.split('_');
				x = $(this).closest('td').next().next().find('.mergeorremove:checked').val();
				console.log(x);
				if (x=='1'){
					y = $(this).closest('td').next().next().next().find('input').val();
					console.log(y);
					data['1'] = '5';
					data['concept1tomerge'] = categories_arr[0];
					data['concept2tomerge'] = categories_arr[1];
					data['mergedconceptname'] = y;
					console.log(data);
					$.post("http://127.0.0.1:8000/AdvoCate/edittrainingset/", data, function(response) {
						console.log(response);
						hasCallbackCompleted[ index + 1 ] = true;
						if ($('#collapse3 input:checkbox:checked').length == index+1){
							$.get("http://127.0.0.1:8000/AdvoCate/applyeditoperations/", function(response){
								$('#submitsuggestions').hide();
								$('#successmessageforappliedsuggestions').html("The training file is updated with the suggestions submitted. Try and recreate the classification model to check the difference.");
								
								if (response['new_taxonomy']){
									if (response['new_taxonomy'] == 'True'){
										x = "<div style = \"width:220px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Creating new taxonomy</span></div>";
									}
									else{
										x = "<div style = \"width:310px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Exploring changes in existing taxonomy</span></div>";
									}
									for (var i = 0; i < response['current_exploration_chain'].length; i++){
										x = x + "<div style=\"width:1px; height:80px; border: 1px solid rgba(0, 0, 0, 0.5);  margin-right:190px; float:right\"></div>";
										if (response['current_exploration_chain'][i][0]=='Create trainingset'){
											bgcolor = "#fbb4ae";
										}
										else if (response['current_exploration_chain'][i][0]=='Change trainingset'){
											bgcolor = "#b3cde3";
										}
										else if (response['current_exploration_chain'][i][0]=='Training activity'){
											bgcolor = "#ccebc5";
										}
										else if (response['current_exploration_chain'][i][0]=='Classification'){
											bgcolor = "#decbe4";
										}
										else{
											bgcolor = "#fed9a6";
										}
										x = x + "<div style=\"width:135px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background:" +
											bgcolor + "; margin: auto; float:right; margin-right:125px\"><span><a style= \"color: #000\"href=\"javascript://\" rel=\"popover\" title=\"" + response['current_exploration_chain'][i][1] + 
											"\" data-html=\"true\" data-toggle=\"popover\" data-content=\"" + response['current_exploration_chain'][i][2] + "\">" + response['current_exploration_chain'][i][0] + "</a></span></div>";
									}
									$('#collapse0').html(x);
									$('.pop_con').popover(popOverSettings);
								}
							});
							
						}
					});
				}
				
				else{
					data['1'] = '2';
					data['2'] = categories_arr[0];
					$.post("http://127.0.0.1:8000/AdvoCate/edittrainingset/", data, function(response) {
						console.log(response);
						hasCallbackCompleted[ index + 1 ] = true;
						if ($('#collapse3 input:checkbox:checked').length == index+1){
							$.get("http://127.0.0.1:8000/AdvoCate/applyeditoperations/", function(response){
								$('#submitsuggestions').hide();
								$('#successmessageforappliedsuggestions').html("The training file is updated with the suggestions submitted. Try and recreate the classification model to check the difference.");
								if (response['new_taxonomy']){
									if (response['new_taxonomy'] == 'True'){
										x = "<div style = \"width:220px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Creating new taxonomy</span></div>";
									}
									else{
										x = "<div style = \"width:310px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Exploring changes in existing taxonomy</span></div>";
									}
									for (var i = 0; i < response['current_exploration_chain'].length; i++){
										x = x + "<div style=\"width:1px; height:80px; border: 1px solid rgba(0, 0, 0, 0.5);  margin-right:190px; float:right\"></div>";
										if (response['current_exploration_chain'][i][0]=='Create trainingset'){
											bgcolor = "#fbb4ae";
										}
										else if (response['current_exploration_chain'][i][0]=='Change trainingset'){
											bgcolor = "#b3cde3";
										}
										else if (response['current_exploration_chain'][i][0]=='Training activity'){
											bgcolor = "#ccebc5";
										}
										else if (response['current_exploration_chain'][i][0]=='Classification'){
											bgcolor = "#decbe4";
										}
										else{
											bgcolor = "#fed9a6";
										}
										x = x + "<div style=\"width:135px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background:" +
											bgcolor + "; margin: auto; float:right; margin-right:125px\"><span><a style= \"color: #000\"href=\"javascript://\" rel=\"popover\" title=\"" + response['current_exploration_chain'][i][1] + 
											"\" data-html=\"true\" data-toggle=\"popover\" data-content=\"" + response['current_exploration_chain'][i][2] + "\">" + response['current_exploration_chain'][i][0] + "</a></span></div>";
									}
									$('#collapse0').html(x);
									$('.pop_con').popover(popOverSettings);
									
								}
							});
							
						}
					});
				}
				
			});
			

			
		});
		
	}
	
	//Script for 'unsupervised classification' page
	
	if (loc.match('http://127.0.0.1:8000/AdvoCate/unsupervised/')) {
		
		$('#doclustering').on('click', function(e) {
			$this = $('#clusteringdetails');
			if ($this[0][0].files.length != 0 && $this[0][1].value != ""){
				e.preventDefault();				
				clusteringfiles = $this[0][0].files;								
				var formdata = new FormData();
				$.each(clusteringfiles, function(i, file){
					formdata.append('file', file);
				});
				
				formdata.append('numberofclusters', $this[0][1].value);
				$.ajax({
					type : "POST",
					url : "http://127.0.0.1:8000/AdvoCate/unsupervised/",
					async : true,
					processData : false,
					contentType : false,
					data : formdata,
					success : function(response) {
						$('#scatterplot_display').show();
						var a = "<img style=\"width:80%; align:center\" src=\"/static/images/" + response['scatterplot'] + "\" />";
						$('#collapse32').html(a);
						$('#collapse32').show();
						$('#collapse31').removeClass("collapse in").addClass("collapse");
						
						if (response['new_taxonomy']){
							if (response['new_taxonomy'] == 'True'){
								x = "<div style = \"width:220px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Creating new taxonomy</span></div>";
							}
							else{
								x = "<div style = \"width:310px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Exploring changes in existing taxonomy</span></div>";
							}
							for (var i = 0; i < response['current_exploration_chain'].length; i++){
								x = x + "<div style=\"width:1px; height:80px; border: 1px solid rgba(0, 0, 0, 0.5);  margin-right:190px; float:right\"></div>";
								if (response['current_exploration_chain'][i][0]=='Create trainingset'){
									bgcolor = "#fbb4ae";
								}
								else if (response['current_exploration_chain'][i][0]=='Change trainingset'){
									bgcolor = "#b3cde3";
								}
								else if (response['current_exploration_chain'][i][0]=='Training activity'){
									bgcolor = "#ccebc5";
								}
								else if (response['current_exploration_chain'][i][0]=='Classification'){
									bgcolor = "#decbe4";
								}
								else{
									bgcolor = "#fed9a6";
								}
								x = x + "<div style=\"width:135px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background:" +
									bgcolor + "; margin: auto; float:right; margin-right:125px\"><span><a style= \"color: #000\"href=\"javascript://\" rel=\"popover\" title=\"" + response['current_exploration_chain'][i][1] + 
									"\" data-html=\"true\" data-toggle=\"popover\" data-content=\"" + response['current_exploration_chain'][i][2] + "\">" + response['current_exploration_chain'][i][0] + "</a></span></div>";
							}
							$('#collapse0').html(x);
							$('.pop_con').popover(popOverSettings);
							
						}
					}
				});
				
			}
		});
		
		
	}
	

	// Script for 'Supervised Classification' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/supervised/')) {
		// Script to deal with when the test file is uploaded
		$('#doclassification').on('click', function(e) {
			if (($('#testfile'))[0].files.length > 0){
				e.preventDefault();
				var newtestfile = ($('#testfile'))[0].files[0];
				var formdata = new FormData();
				$('#categoriesandcolors input').each(function(index){
					category = $(this).attr('id');
					color = $(this).css('background-color');
					formdata.append(index, color);
				});
				// Posting file to the server side using formdata
				
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
						$('#categoriesandcolors input').each(function(index){
							d = d + "<tr><td>" + "<div style=\"width:20px; height:20px; border: 1px solid rgba(0, 0, 0, .2); background:" + $(this).css('background-color') + "\"></div></td><td>" 
								+ $(this).attr('id') + "</td></tr>";
						});				
						d = d + "</table>";
							
						$('#categorycolors').html(d);
						if (response['old_categories']){
							a = "<table style=\"width:95%\" align=\"center\" class=\" table table-bordered\"><tr><th>#</th>";
							for (var i=0; i< response['categories'].length; i++){
								a = a + "<th>" + response['categories'][i] + "</th>";
							}
							a = a + "<th>Total</th></tr>";
							
							for (var j=0; j < response['old_categories'].length; j++){
								a = a + "<tr><th>" + response['old_categories'][j] + "</th>";
								for (var k=0; k < response['change_matrix'][j].length; k++){
									a = a + "<td>" + response['change_matrix'][j][k] + "</td>";
								}
								a = a + "</tr>";
							}
							a = a + "<tr><th>Total</th>";
							for (var l = 0; l< response['change_matrix'][response['old_categories'].length].length; l++){
								a = a + "<td>" + response['change_matrix'][response['old_categories'].length][l] + "</td>";
							}
							a = a + "</tr>";
							
							$('#changematrix_display').show();
							$('#collapse10').html(a);
							
						}
						
						$('#collapse8').removeClass("collapse in").addClass("collapse");
						$('#collapse10').removeClass("collapse in").addClass("collapse");
						if (response['new_taxonomy']){
							if (response['new_taxonomy'] == 'True'){
								x = "<div style = \"width:220px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Creating new taxonomy</span></div>";
							}
							else{
								x = "<div style = \"width:310px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background: gainsboro; color:#000; margin: auto\"><span>Start: Exploring changes in existing taxonomy</span></div>";
							}
							for (var i = 0; i < response['current_exploration_chain'].length; i++){
								x = x + "<div style=\"width:1px; height:80px; border: 1px solid rgba(0, 0, 0, 0.5);  margin-right:190px; float:right\"></div>";
								if (response['current_exploration_chain'][i][0]=='Create trainingset'){
									bgcolor = "#fbb4ae";
								}
								else if (response['current_exploration_chain'][i][0]=='Change trainingset'){
									bgcolor = "#b3cde3";
								}
								else if (response['current_exploration_chain'][i][0]=='Training activity'){
									bgcolor = "#ccebc5";
								}
								else if (response['current_exploration_chain'][i][0]=='Classification'){
									bgcolor = "#decbe4";
								}
								else{
									bgcolor = "#fed9a6";
								}
								x = x + "<div style=\"width:135px; height:35px; line-height:35px; text-align: center; border: 1px solid rgba(0, 0, 0, .2); border-radius:5px; background:" +
									bgcolor + "; margin: auto; float:right; margin-right:125px\"><span><a style= \"color: #000\"href=\"javascript://\" rel=\"popover\" title=\"" + response['current_exploration_chain'][i][1] + 
									"\" data-html=\"true\" data-toggle=\"popover\" data-content=\"" + response['current_exploration_chain'][i][2] + "\">" + response['current_exploration_chain'][i][0] + "</a></span></div>";
							}
							$('#collapse0').html(x);
							$('.pop_con').popover(popOverSettings);
							
						}
						
					}
				});
			}
		});

	}

	// Script for 'Change recognition' page

	if (loc.match('http://127.0.0.1:8000/AdvoCate/changerecognition/')) {
		
		$('[data-toggle="popover"]').popover();
		
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
				$('#collapse11').removeClass("collapse in").addClass("collapse");
			});
		});
		
		$('#yesforchangeinexisting').on('click', function(e) {
			$('#yesforchangeinexisting').attr('disabled', 'disabled');
			$('#noforchangeinexisting').attr('disabled', 'disabled');
			$('#newtaxonomyversionorchangeexisting').show();
			
		});
		
		$('#newtaxonomyversion').on('click', function(e) {
			e.preventDefault();
			$.get("http://127.0.0.1:8000/AdvoCate/createChangeEventForNewTaxonomyVersion/", function(data){
				$('#listofchangeoperations').show();
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
				$('#changeevent').show();
				$('#compositechangeoperations').html(x);
				$('#commit').show();
				$('#newtaxonomyversion').attr('disabled', 'disabled');
				$('#changeexistingtaxonomy').attr('disabled', 'disabled');
				$('#collapse13').removeClass("collapse in").addClass("collapse");
				
			});
			
		});
		
		$('#changeexistingtaxonomy').on('click', function(e) {
			e.preventDefault();
			$('#newtaxonomyversion').attr('disabled', 'disabled');
			$('#changeexistingtaxonomy').attr('disabled', 'disabled');
			$('#thresholdlimitforchange').show();
		});
		
		$('#yesforthresholdlimit').on('click', function(e) {
			e.preventDefault();
			$('#yesforthresholdlimit').attr('disabled', 'disabled');
			$('#noforthresholdlimit').attr('disabled', 'disabled');
			$('#userinputforchangeevent').show();
			$('#thresholdlimitforchangedetails').show();
		});
		
		$('#changethresholdvalues').on('click', function(e) {
			e.preventDefault();
			$('#changethresholdvalues').attr('disabled', 'disabled');
			$('#submitthresholdvalues').show();
			$('#int_change_limit_min').removeAttr('disabled');
			$('#int_change_limit_max').removeAttr('disabled');
			$('#ext_change_limit_min').removeAttr('disabled');
			$('#ext_change_limit_max').removeAttr('disabled');
		});
		
		$('#submitthresholdvalues').on('click', function(e) {
			e.preventDefault();
			data = {};
			data['1'] = $('#int_change_limit_min').val();
			data['2'] = $('#int_change_limit_max').val();
			data['3'] = $('#ext_change_limit_min').val();
			data['4'] = $('#ext_change_limit_max').val();
			
			$.post("http://127.0.0.1:8000/AdvoCate/changeintandextThresholdLimits/", data, function(data) {
				$('#int_change_limit_min').attr('disabled', 'disabled');
				$('#int_change_limit_max').attr('disabled', 'disabled');
				$('#ext_change_limit_min').attr('disabled', 'disabled');
				$('#ext_change_limit_max').attr('disabled', 'disabled');
				$('#submitthresholdvalues').hide();
				$('#changethresholdvalues').removeAttr('disabled');
			});
		});
		
		$('#displaychangesuggestions').on('click', function(e) {
			e.preventDefault();
			$.get("http://127.0.0.1:8000/AdvoCate/getChangeSuggestionsBasedOnThresholdLimits/", function(response){
				var a = "<br /> <br />";
				if (response['evolutionary_versions'].length ==0 & response['competing_versions'].length ==0){
					a = a + "<p> None of the categories for the existing concepts cross the threshold limits of computational intension or extension. So, the categories corresponding to the common" +
						"concepts remain same.</p>";
				}
				else{
					if (response['evolutionary_versions'].length >0){
						a  = a + "<p> For the following concepts, evolutionary versions of their corresponding categories will be created:</p>";
						for (var i = 0; i < response['evolutionary_versions'].length; i++){
							a = a + "<label style =\" font-weight: normal\">" + (i+1) + ": " + response['evolutionary_versions'][i] + "</label><br />";
						}
						a = a + "<br />";
					}
					
					if (response['competing_versions'].length >0){
						a  = a + "<p> For the following concepts, competing versions of their corresponding categories will be created:</p>";
						for (var i = 0; i < response['competing_versions'].length; i++){
							a = a + "<label style =\" font-weight: normal\">" + (i+1) + ": " + response['competing_versions'][i] + "</label><br />";
						}
						a = a + "<br />";
					}
					
				}
				
				$('#suggestionbasedonthresholdlimit').html(a);
				$('#createchangeevent').show();
			});
			
		});
		
		$('#createchangeevent').on('click', function(e) {
			e.preventDefault();
			$.get("http://127.0.0.1:8000/AdvoCate/createChangeEventForExistingTaxonomy/", function(response) {
				$('#listofchangeoperations').show();
				x = "";
				for (var i = 0; i < response['listOfOperations'].length; i++) {
					a = i + 1;
					id = "operation_" + i;
					x = x + "<dt style=\"cursor:pointer; font-weight:normal; line-height: 2.5em; background:#e4e4e4; border-bottom: 1px solid #c4c4c4; border-top: 1px solid white\"> &nbsp;&nbsp;" + a + ". &nbsp;&nbsp;&nbsp;" + response['listOfOperations'][i][0] + "</dt>";
					for (var j = 0; j < response['listOfOperations'][i][1].length; j++){
						b = j+1;
						x = x + "<dd style=\" margin-left:10px; padding: 0.5em 0; border-bottom: 1px solid #c4c4c4; display: none\"> &nbsp;&nbsp;" + b + ". &nbsp; &nbsp; &nbsp;" + response['listOfOperations'][i][1][j] + "</dd>";
					}
					
				}
				x = x + "</dl>";
				$('#changeevent').show();
				$('#compositechangeoperations').html(x);
				$('#commit').show();
				$('#collapse15').removeClass("collapse in").addClass("collapse");
				
			});
		});
		
		$('#noforthresholdlimit').on('click', function(e) {
			e.preventDefault();
			$('#yesforthresholdlimit').attr('disabled', 'disabled');
			$('#noforthresholdlimit').attr('disabled', 'disabled');
			$.get("http://127.0.0.1:8000/AdvoCate/getUserInputToCreateChangeEvent/", function(response){
				var a = "<br /><br /><form class=\"form-group\" id=\"userinputdetails\">";
				if (response['existing_categories'].length >0){
					a = a + "<label style=\"font-size: 15px\"> User input for changes in existing catgeories:</label>";
					
					a = a +	"<table class=\"table\" style=\" margin: 20px; width: 70%\" id=\"common_categories_change_table\">";
					for (var i = 0; i < response['existing_categories'].length; i++){											
						a = a + "<tr><td>" + response['existing_categories'][i] + "</td><td>Create a new version? &nbsp;&nbsp;&nbsp;&nbsp;" +
							"<div class=\"radiox\" style=\"margin:0; display:inline\">" + "<input type=\"radio\" name=\"" + response['existing_categories'][i] + "\" value=\"1\" class=\"yesornofornewversion\"/>&nbsp;Yes" +
							"<input type=\"radio\" name=\"" + response['existing_categories'][i] + "\" value=\"2\" class=\"yesornofornewversion\" style=\"margin-left:20px\"/>&nbsp;No</div></td><td>" + 
							
							"<div class=\"radiox\" style=\"display:none; margin:0\">" + "<input type=\"radio\" name=\"EvolOrComp" + i + "\" value=\"1\" class=\"EvolOrComp\"/>&nbsp;Evolutionary" +
							"<input type=\"radio\" name=\"EvolOrComp" + i + "\" value=\"2\" class=\"EvolOrComp\" style=\"margin-left:20px\"/>&nbsp;Competing</div></td></tr>";
							
					}
					a = a + "</table><br /><br />";
										
				}
				
				a = a + "<input type=\"submit\" id=\"submituserinput\" value=\"Submit\" class=\"btn btn-default\" style=\"margin:20px\"/></form>";
				
				$('#userinput').html(a);
				$('[data-toggle="popover"]').popover();
			});
			$('#userinputforchangeevent').show();
			$('#collapse13').removeClass("collapse in").addClass("collapse");
			
		});
		
		$('#userinput').on('click', '.yesornofornewversion', function(e){
			$this = $(this);
			if ($this.val() =='1'){
				$this.closest('td').next().find('div').show();
			}
			else{
				$this.closest('td').next().find('.EvolOrComp').prop('checked', false);
				$this.closest('td').next().find('div').hide();
			}
		});
		
		$('#userinput').on('click', '#submituserinput', function(e){
			e.preventDefault();
			$this = $('#userinput form');
			var a = 1;
			data = {};
			for (var i=0; i< ($this[0].length)-1; i++){
				if (($this[0][i]).className == 'yesornofornewversion'){
					if ($($this[0][i]).is(':checked')){
						x = $($this[0][i]).attr('name');
						if ($($this[0][i+2]).is(':checked')){
							data[a] = x + " evol";
						}
						else{
							data[a] = x + " comp";
						}
						a = a + 1;
						i = i + 3;
					}
					else{
						i = i + 3;
					}
				}
				
			}
			console.log(data);
			$.post("http://127.0.0.1:8000/AdvoCate/createChangeEventForExistingTaxonomy/", data, function(data) {
				$('#listofchangeoperations').show();
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
				$('#changeevent').show();
				$('#compositechangeoperations').html(x);
				$('#commit').show();
				$('#collapse15').removeClass("collapse in").addClass("collapse");
				$('#userinput #submituserinput').attr('disabled', 'disabled');
			});
			
		});
		
		
		
		
		$('#compositechangeoperations').on('click', 'dt', function(e) {
			e.preventDefault();
			$(this).nextUntil('dt').toggle();
			$(this).siblings('dt').nextUntil('dt').hide();
			
			
		});
		
		$('#explorationchain').on('click', 'dt', function(e) {
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
				$('#collapse11').removeClass("collapse").addClass("collapse in");
			});
		});
		
		$('#yesforcommitfornewtaxonomyversion').on('click', function(e) {
			e.preventDefault();
			$('#yesforcommitfornewtaxonomyversion').attr('disabled', 'disabled');
			$('#noforcommitfornewtaxonomyversion').attr('disabled', 'disabled');
			$.get("http://127.0.0.1:8000/AdvoCate/applyChangeOperations/", function(data){
				$('#changeevent').hide();
				$('#userinputforchangeevent').hide();
				$('#implement').hide();
				$('#commitsuccessmessage').show();
				$('#successmessage').html(data);
				$('#collapse11').removeClass("collapse").addClass("collapse in");
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