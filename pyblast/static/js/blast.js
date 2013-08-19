$(document).ready(function(){
    var holdingInfoDiv = $('#holding-information');
    var blastResultsDiv = $('#blast-results');

    var checkStatusTimer;

    function checkStatus() {
        console.info('executed');
        $.ajax({
            type: 'GET',
            url: STATUS_ENDPOINT,
            success: function(data) {
                console.log(data);
                if(data.active == false) {
                    window.clearInterval(checkStatusTimer);
                    document.title = "BLAST complete, showing all results";
                    holdingInfoDiv.slideUp();
                    var results = $(data.results_page).hide();
                    blastResultsDiv.append(results);
                    results.slideDown();
                    alignments.create();
                }
            },
            dataType: 'json',
        });
    }

    $.ajax({
        type: 'POST',
        url: RUN_ENDPOINT,
        data: PARAMS,
        success: function(data) {
            document.title = 'BLAST running...';
            checkStatusTimer = window.setInterval(checkStatus, 2000);
            var startedAlert = $('<div class="alert alert-success"><strong>BLAST started:</strong> Results will be returned once the search has completed</div>').hide();
            holdingInfoDiv.append(startedAlert);
            startedAlert.slideDown();
            var spinner = $('<div class="spinner-container"></div>');
            holdingInfoDiv.append(spinner);
            spinner.spin({
                lines: 7,
                radius: 25,
                length: 30,
                color: '#428BCA'
            });
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if(console) {
                console.error(jqXHR, textStatus, errorThrown);
            }
            document.title = 'BLAST search error. Code '+jqXHR.status;

            var message = ''
            if(jqXHR.status == 400) {
                message = '<p>Some of the values entered for your BLAST search where either missing or incorrect.</p><p>Please <a href="#" class="back-link">go back to the options page</a> and check everything is correct</p>'
                var error = $('<div class="alert alert-warning alert-block"><strong>Oops! An error has occured</strong>'+message+'</div><div class="accordion" id="errorMessages"><div class="accordion-group"><div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#errorMessages" href="#errMsg">Error Message</a></div><div id="errMsg" class="collapse accordion-body out"><div class="accordion-inner"><pre>'+jqXHR.responseText+'</pre></div></div></div></div>').hide();
                holdingInfoDiv.append(error);
                error.slideDown();
            } else {
                message = '<p>'+jqXHR.status+': '+jqXHR.statusText+'</p><p>Please <a href="#" class="back-link">go back</a> and retry your request, if the problem persists please contact the administrator.</p>';
                var error = $('<div class="alert alert-warning alert-block"><strong>Oops! An error has occured</strong>'+message+'</div><div class="accordion" id="errorMessages"><div class="accordion-group"><div class="accordion-heading"><a class="accordion-toggle" data-toggle="collapse" data-parent="#errorMessages" href="#errMsg">Error Message</a></div><div id="errMsg" class="collapse accordion-body out"><div class="accordion-inner"><pre>'+jqXHR.responseText+'</pre></div></div></div></div>').hide();
                holdingInfoDiv.append(error);
                error.slideDown();
            }
        },
        dataType: 'html',
    });

    $(document).ajaxStart(function() {
        document.title = 'BLAST started...';
    });

});

