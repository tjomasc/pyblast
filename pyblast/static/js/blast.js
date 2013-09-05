$(document).ready(function(){
    var holdingInfoDiv = $('#holding-information');
    var blastResultsDiv = $('#blast-results');

    var checkStatusTimer;

    function blastError(jqXHR, textStatus, errorThrown) {
        if(console) {
            console.error(jqXHR, textStatus, errorThrown);
        }
        document.title = 'BLAST search error. Code '+jqXHR.status;

        var message = ''
        if(jqXHR.status == 400) {
            message = '<p>Some of the values entered for your BLAST search where either missing or incorrect.</p><p>Please <a href="#" class="back-link">go back to the options page</a> and check everything is correct</p>'
            var error = $('<div class="alert alert-warning alert-block"><strong>Oops! An error has occured</strong>'+message+'</div><div class="accordion" id="errorMessages"><div class="accordion-group"><div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#errorMessages" href="#errMsg">Error Message</a></div><div id="errMsg" class="collapse accordion-body out"><div class="accordion-inner"><pre>'+jqXHR.responseText+'</pre></div></div></div></div>').hide();
            holdingInfoDiv.children('.spinner-container').before(error);
            error.slideDown();
        } else {
            message = '<p>'+jqXHR.status+': '+jqXHR.statusText+'</p><p>Please <a href="#" class="back-link">go back</a> and retry your request, if the problem persists please contact the administrator.</p>';
            var error = $('<div class="alert alert-warning alert-block"><strong>Oops! An error has occured</strong>'+message+'</div><div class="accordion" id="errorMessages"><div class="accordion-group"><div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#errorMessages" href="#errMsg">Error Message</a></div><div id="errMsg" class="collapse accordion-body out"><div class="accordion-inner"><pre>'+jqXHR.responseText+'</pre></div></div></div></div>').hide();
            holdingInfoDiv.children('.spinner-container').before(error);
            error.slideDown();
        }
    }

    function checkStatus() {
        document.title = 'Checking BLAST status...'
        if ($('.checking-alert').length == 0) {
            var checkingAlert = $('<div class="checking-alert alert alert-info"><strong>Checking BLAST status:</strong> Results will be returned once the search has completed</div>').hide();
            holdingInfoDiv.children('.spinner-container').before(checkingAlert);
            checkingAlert.slideDown();
            /*if($('.spinner-container').length == 0) {
                var spinner = $('<div class="spinner-container"></div>');
                holdingInfoDiv.append(spinner);
                spinner.spin({
                    lines: 7,
                    radius: 25,
                    length: 30,
                    color: '#428BCA'
                });
            }
            */
        }
        $.ajax({
            type: 'GET',
            url: STATUS_ENDPOINT,
            success: function(data) {
                if(data.active == false) {
                    window.clearInterval(checkStatusTimer);
                    document.title = "BLAST complete, showing all results";
                    holdingInfoDiv.slideUp();
                    //var results = $('<div></div>');
                    //results.html(data.results_page);
                    //results.innerHTML = data.results_page
                    //results.hide();
                    //blastResultsDiv.append(results);
                    //blastResultsDiv.html(data.results_page);
                    blastResultsDiv[0].innerHTML = data.results_page;
                    //results.slideDown();
                    alignments.create();
                } else {
                    document.title = 'BLAST still running...'
                    checkStatusTimer = window.setInterval(checkStatus, 2000);
                }
            },
            error: blastError,
            dataType: 'json',
        });
    }

    var spinner = $('<div class="spinner-container"></div>');
    holdingInfoDiv.append(spinner);
    spinner.spin({
        lines: 7,
        radius: 25,
        length: 30,
        color: '#428BCA'
    });

    if(EXECUTE) {
        document.title = 'Starting BLAST...'
        $.ajax({
            type: 'POST',
            url: RUN_ENDPOINT,
            data: PARAMS,
            success: function(data) {
                document.title = 'BLAST running...';
                checkStatusTimer = window.setInterval(checkStatus, 2000);
                var startedAlert = $('<div class="alert alert-success"><strong>BLAST started:</strong> Results will be returned once the search has completed</div>').hide();
                holdingInfoDiv.children('.spinner-container').before(startedAlert);
                startedAlert.slideDown();
            },
            error: blastError,
            dataType: 'html',
        });

        $(document).ajaxStart(function() {
            document.title = 'BLAST started...';
        });
    } else {
        checkStatus();
    }

});

