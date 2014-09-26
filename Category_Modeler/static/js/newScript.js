/**
 * @author Prashant Gupta
 */
$(document).ready(function() {

	$('.dropdown-toggle').dropdown();

	$('input[name="testoption"]').click(function() {
		if ($('input[name="testoption"]:checked').attr("id")=="trainingfile") 
			{
				$("#testfile").prop('disabled', false);
				$("#Fold").prop('disabled', true);
				$("#Percentage").prop('disabled', true);
			} 
		else if($('input[name="testoption"]:checked').attr("id")=="CrossValidation") 
			{
				$("#testfile").prop('disabled', true);
				$("#Fold").prop('disabled', false);
				$("#Percentage").prop('disabled', true);
			
			}
		else if	($('input[name="testoption"]:checked').attr("id")=="PercentageSplit") 
			{
				$("#testfile").prop('disabled', true);
				$("#Fold").prop('disabled', true);
				$("#Percentage").prop('disabled', false);
			
			}
			else{
				$("#testfile").prop('disabled', true);
				$("#Fold").prop('disabled', true);
				$("#Percentage").prop('disabled', true);
			}
			;
		
	});


$('#filename').change(function(){
	var file = this.files[0];
	var reader = new FileReader();
    reader.readAsText(file);
     reader.onload = function(event){
      var csv = event.target.result;
      var data = $.csv.toArrays(csv);
     var $container = $('#dataTable');
      $container.handsontable({
    	  data: data
      });
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
    }



	
/*	$.ajax({
		type: "POST",
		url: "http://127.0.0.1:8000/CategoryModeler/preprocess/",
		dataType: "json",
		async: true,
		data: {
			csrfmiddlewaretoken: '{{ csrf_token }}',
			Filename: file
			},
		success: function(response) {
			alert(response);
		//	$('#tablename').text(json.filename);
			
		}
	    
				
	});*/
	
});


	


});
