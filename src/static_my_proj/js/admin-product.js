$(document).ready(function() {

    $("#select_all").click(function() {
        $(".delete").each(function(i) {
            field_name = "#id_colouroption_set-" + i.toString() + "-DELETE";
            length_name = "#id_lengthoption_set-" + i.toString() + "-DELETE";

            if ($(field_name).is(':checked')) {
                $(field_name).show();
                $(field_name).prop('checked', false);
                $(field_name).hide();
            }
            else { 
                $(field_name).show();
                $(field_name).prop('checked', true);
                $(field_name).hide();
            }

            if ($(length_name).is(':checked')) {
                $(length_name).show();
                $(length_name).prop('checked', false);
                $(length_name).hide();
            }
            else { 
                $(length_name).show();
                $(length_name).prop('checked', true);
                $(length_name).hide();
            }
        });
    });
});