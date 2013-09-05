$(document).ready(function(){

    // Check the form before it is sent.
    $('.blast-form').submit(function() {
        var valid = true;
        $('.submit-error').remove();
        if($('textarea[name="sequence"]').attr('value') == '') {
            valid = false;
            $('textarea[name="sequence"]').after('<p class="submit-error alert alert-danger">Please enter a FASTA sequence to BLAST</p>');
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
        var existing = programs.find('option[selected="selected"]');
        if($(this).data('type') === 'prot') {
            programs.find('option[selected="selected"]').removeAttr('selected');
            if(existing.length > 0 && popt.find('option[value="'+existing.attr('value')+'"]').length > 0) {
                existing.attr('selected', 'selected');
            } else {
                popt.children(':first').attr('selected', 'selected');
            }
            popt.show();
            nopt.hide();
        } else {
            programs.find('option[selected="selected"]').removeAttr('selected');
            if(existing.length > 0 && nopt.find('option[value="'+existing.attr('value')+'"]').length > 0) {
                existing.attr('selected', 'selected');
            } else {
                nopt.children(':first').attr('selected', 'selected');
            }
            nopt.show();
            popt.hide();
        }
    });
    $('.databases input[checked="checked"]').change();
});
