$(document).ready(function() {

    $('.field-store').each(function() {
        if ($(this).html() == '✓') {
            $(this).css({'text-align': 'center', 'background': '#ffffba'});
        }
        else if ($(this).html() == 'Ordered' || $(this).html() == 'Created') {
            $(this).css({'text-align': 'center', 'background': '#ffb3ba'});
            $(this).text(" ")
        }
        else if ($(this).html() == '?') {
            $(this).css({'text-align': 'center', 'background': '#ffb3ba'});
        }
    });

    $('.field-site').each(function() {
        if ($(this).html() == '✓') {
            $(this).css({'text-align': 'center', 'background': '#ffffba'});
        }
        else if ($(this).html() == 'Ordered' || $(this).html() == 'Created') {
            $(this).css({'text-align': 'center', 'background': '#baffc9'});
            $(this).text(" ")
        }
        else if ($(this).html() == '?') {
            $(this).css({'text-align': 'center', 'background': '#baffc9'});
        }
    });

    $('.field-flash').each(function() {
        if ($(this).html() == '✓') {
            $(this).css({'text-align': 'center', 'background': '#ffffba'});
        }
        else if ($(this).html() == 'Ordered' || $(this).html() == 'Created') {
            $(this).css({'text-align': 'center', 'background': '#ffdfba'});
            $(this).text(" ")
        }
        else if ($(this).html() == '?') {
            $(this).css({'text-align': 'center', 'background': '#ffdfba'});
        }
    });

    $('.field-pack').each(function() {
        if ($(this).html() == '✓') {
            $(this).css({'text-align': 'center', 'background': '#ffffba'});

        }
        else if ($(this).html() == 'Ordered' || $(this).html() == 'Created') {
            $(this).css({'text-align': 'center', 'background': '#bae1ff'});
            $(this).text(" ")
        }
        else if ($(this).html() == '?') {
            $(this).css({'text-align': 'center', 'background': '#bae1ff'});
        }
    });

    // Reduce size of supplier eta in the order splash screen
    $('.field-supplier_eta').each(function(i) {
        field_name = '#id_form-' + i.toString() + '-supplier_eta';
        $(field_name).css('width', '8em');
    });

    // Reduce size of customer eta in the order splash screen
    $('.field-customer_eta').each(function(i) {
        field_name = '#id_form-' + i.toString() + '-customer_eta';
        $(field_name).css('width', '8em');
    });

    // Change Payment Accepted to green
    $('.field-status').each(function(i) {
        field_name = '#select2-id_form-' + i.toString() + '-status-container';
        console.log(field_name);
        if ($(field_name).text() == 'Payment Accepted') {
            $(field_name).css('background', '#b4ecb4');
        }
        else if ($(field_name).text() == 'In Progress') {
            $(field_name).css('background', '#ffc04d');
        }
        else if ($(field_name).text() == 'Reviewing Order'){
            $(field_name).css('background', '#FEC8D8');
        }
        else if ($(field_name).text() == 'Completed') {
            $(field_name).css('background', '#fdfd96');
        }
    });

    // Add dollar sign before totals
    $('.field-total').each(function() {
        value = "None";
        if ($(this).text().trim() != 'Total:') {
            value = '$' + $(this).text().toString();
        }
        if (value != "None") {
            $(this).text(value);
        }
    });

    // Select all for completed
    $("#select_all").click(function() {
        $(".field-completed").each(function(i) {
            field_name = "#id_orderitem_set-" + i.toString() + "-completed";
            console.log(field_name);
            if ($(field_name).is(':checked')) {
                $(field_name).show();
                $(field_name).prop('checked', false);
                $(field_name).hide();
            } else {
                $(field_name).show();
                $(field_name).prop('checked', true);
                $(field_name).hide();
            }
        });
    });

    $('#id_delivery_instructions').attr('placeholder', 'e.g. leave at the door');
    $('#id_order_instructions').attr('placeholder', 'Is there anything we need to know about your order?');
});