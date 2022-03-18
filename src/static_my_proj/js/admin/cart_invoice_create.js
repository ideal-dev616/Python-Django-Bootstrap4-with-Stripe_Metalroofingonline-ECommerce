$(document).ready(function() {
    var pickup = false;
    var billing_same = false;
    var postage_standard = false;
    var postage_express = false;



    $('#pickup').change(function() {
        if ($('#pickup').is(":checked")){
            pickup = true;
            $('#address').val("48 Watt Rd");
            $('#suburb').val("Mornington");
            $('#post-code').val("3931");
            $('#state').val("VIC");

            if ($('#postage-express').is(":checked")){
                $("#postage-express").prop( "checked", false );
            }
            if (postage_express == true) {
                postage_express = false;
            }

            if ($('#postage-standard').is(":checked")){
                $("#postage-standard").prop( "checked", false );
            }
            if ( postage_standard == true) {
                postage_standard = false;
            }

        } else {
            pickup = false;
        }
    });

    $('#postage-standard').change(function() {
        if ($('#postage-standard').is(":checked")){
            postage_standard = true;

            if ($('#postage-express').is(":checked")){
                $("#postage-express").prop( "checked", false );
            }
            if (postage_express == true) {
                postage_express = false;
            }

            if ($('#pickup').is(":checked")){
                $("#pickup").prop( "checked", false );
            }
            if (pickup == true) {
                pickup = false;
            }
        } else {
            postage_standard = false;
        }
    });

    $('#postage-express').change(function() {
        if ($('#postage-express').is(":checked")){
            postage_express = true;
            if ($('#postage-standard').is(":checked")){
                $("#postage-standard").prop( "checked", false );
            }
            if ( postage_standard == true) {
                postage_standard = false;
            }

            if ($('#pickup').is(":checked")){
                $("#pickup").prop( "checked", false );
            }
            if (pickup == true) {
                pickup = false;
            }
        } else {
            postage_express = false;
        }
    });

    $('#billing-same').change(function() {
        if ($('#billing-same').is(":checked")) {
            billing_same = true;
            $('#billing-address').val($('#address').val());
            $('#billing-suburb').val($('#suburb').val());
            $('#billing-post-code').val($('#post-code').val());
            $('#billing-state').val($('#state').val());
        } else {
            billing_same = false;
        }
    });

    $('#create-button').click(function(event) {
        event.preventDefault();

        $('#create-button').text("Sending...");

        var name = $('#name').val();
        var phone_number = $('#phone-number').val();
        var email = $('#email').val();
        var address = $('#address').val();
        var suburb = $('#suburb').val();
        var postcode = $('#post-code').val();
        var state = $('#state').val();
        var billing_address = $('#billing-address').val();
        var billing_suburb = $('#billing-suburb').val();
        var billing_postcode = $('#billing-post-code').val();
        var billing_state = $('#billing-state').val();
        var pk = $('#cart-pk').val();

        var sendData = {
            'name': name,
            'phone_number': phone_number,
            'email': email,
            'pickup': pickup,
            'postage_standard': postage_standard,
            'postage_express': postage_express,
            'address': address,
            'suburb': suburb,
            'postcode': postcode,
            'state': state,
            'billing_address': billing_address,
            'billing_suburb': billing_suburb,
            'billing_postcode': billing_postcode,
            'billing_state': billing_state,
            'billing_same': billing_same,
            'pk': pk,
        };

        $.ajax({
            url: '/xero/create-invoice',
            dataType: 'json',
            type: 'post',
            data: sendData,

            success: function (data) {
                $('#create-button').text("Sent!!!");
                console.log("data = ", data);
                if (data.success == "success") {
                    location.href = data.authorization_url;
                }
            },
            error: function(data) {
                alert('Error');
            },
        });
    });
});
