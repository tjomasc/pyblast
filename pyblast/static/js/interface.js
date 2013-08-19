$(document).ready(function(){

    $('select[name="program"]').on('change', function() {
        var selected = $(this).attr('value');
        $.ajax({
            type: 'GET',
            url: OPTION_ENDPOINT,
            data: {program: selected},
            success: function(data) {
                $('#blastoptions').html(data);
            },
            error: function() { //jqXHR, textStatus, errorThrown) {
                //console.error(jqXHR, textStatus, errorThrown);
                $('#blastoptions').html('Advanced options are currently unavailable');
            },
            dataType: 'html'
        });
    }).change();

    // Check the form before it is sent.
    $('.blast-form').submit(function() {
        var valid = true;
        $('.submit-error').remove();
        if($('textarea[name="sequence"]').attr('value') == '') {
            valid = false;
            $('textarea[name="sequence"]').after('<p class="submit-error alert alert-error">Please enter a FASTA sequence to BLAST</p>');
        }
        if(valid) {
            return true;
        }
        return false;
    });

    // Change available programs based on whatever database is selected
    $('.databases input').change(function() {
        var programs = $('select[name="program"]');
        var nopt = programs.children('optgroup[label="Nucleotide"]');
        var popt = programs.children('optgroup[label="Protein"]');
        if($(this).data('type') === 'prot') {
            programs.children('input[selected="selected"]').removeAttr('selected');
            popt.children(':first').attr('selected', 'selected');
            popt.show();
            nopt.hide();
        } else {
            programs.children('input[selected="selected"]').removeAttr('selected');
            nopt.children(':first').attr('selected', 'selected');
            nopt.show();
            popt.hide();
        }
    });
    $('.databases input[checked="checked"]').change();
});
