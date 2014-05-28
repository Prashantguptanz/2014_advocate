/**
 * @author Prashant Gupta
 */
$(document).ready(function() {

	$('.dropdown-toggle').dropdown();

//	$("#trainingfile").click(function() {
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
		
	//	$("#inputtrainingfile").prop('disabled', false);
	});
	
	$('#dataTable').handsontable({
		data: csvfile,
  		minSpareRows: 1,
 		colHeaders: true,
  		contextMenu: true
		
	});
	
	$('#dataTable table').addClass('table');

$('.options input').on('change', function () {
  var method = this.checked ? 'addClass' : 'removeClass';
  $('#dataTable').find('table')[method](this.getAttribute('data-type'));
});

});
