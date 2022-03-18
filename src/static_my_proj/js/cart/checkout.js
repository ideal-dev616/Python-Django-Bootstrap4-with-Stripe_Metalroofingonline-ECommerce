$(document).ready(function() {
  // Check whether a paypal button has been rendered yet
  var paypal_rendered = false;
  // State set to whatever is selected in header
  var state_selected = $("#navbarDropdownState option:selected").val();
  $("#state").val(state_selected);

  // Get delivery options
  $("#postal_code").change(function() {
    if ($("#standard").is(":checked") || $("#express").is(":checked")) {
      // DO NOTHING WHEN POSTAGE CHECKED
    } else {
      $("#delivery-option").html(
        '<i class="fas fa-spinner fa-spin"></i><br>Finding your delivery options!'
      );
      var postal_code = $("#postal_code").val();
      var cart_total = $("#cart_total").val();
      var collect_link = $("#collect-link");

      delivery_options_url = "/cart/delivery-options/";
      $.ajax({
        url: delivery_options_url,
        type: "post",
        data: {
          postal_code: postal_code,
          csrfmiddlewaretoken: CSRF_TOKEN
        },
        dataType: "json",
        success: function(data) {
          console.log("ajax success");
          if (data.post_code == "0") {
            $("#delivery-option").html(data.message);
            $("#date_hidden_input").attr("required", false);
            $("#submit_btn").attr("disabled", true);
          } else {
            if (data.message) {
              $("#delivery-option").html(
                "$" +
                  data.price +
                  " Delivery to post code: " +
                  data.post_code +
                  '<i class="fas fa-check ml-2"></i><br/>' +
                  data.message
              );
            } else {
              $("#delivery-option").html(
                "$" +
                  data.price +
                  " Delivery to post code: " +
                  data.post_code +
                  '<i class="fas fa-check ml-2"></i>'
              );
            }
            $("#postage").val(data.price);
            $("#delivery-amount").text(data.price);
            $("#total").text(
              (parseFloat(data.price) + parseFloat(cart_total)).toFixed(2)
            );
            $("#delivery-date-selector").attr("hidden", false);
            $("#date_hidden_input").attr("required", true);
            $("#submit_btn").attr("disabled", false);
          }
        }
      });
    }
  });

  // When customer selects delivery
  $("#deliver-link").click(function(event) {
    event.preventDefault();
    //$("#postage").val("");
    $('#autocomplete').val("");
    $("#deliver-link").addClass("themed-grid-col-selected");
    $("#collect-link").removeClass("themed-grid-col-selected");
    $("#delivery-option").html(
      "Please enter your address to see delivery options"
    );

    $("#address_line_1").val("");
    $("#city").val("");
    $("#postal_code").val("");

    if ($("#autocomplete-group").is(":hidden")) {
      $("#autocomplete-group").attr("hidden", false);
      $("#delivery-autocomplete-label").attr("hidden", false);
    }
    if ($("#postage-option").is(":hidden")) {
      $("#postage-option").attr("hidden", false);
      $("#pickup-option").attr("hidden", true);
      $("#delivery-amount").text("17.99");
      var total = $("#cart_total").val();
      $("#total").text((parseFloat(total) + parseFloat(17.99)).toFixed(2));
    }
  });

  // When customer selects "collect"
  $("#collect-link").click(function(event) {
    event.preventDefault();

    var total = $("#cart_total").val();
    var shipping = $("#delivery-amount").val();

    $("#standard").attr("required", false);
    $("#postage").val("pickup");
    $("#deliver-link").removeClass("themed-grid-col-selected");
    $("#collect-link").addClass("themed-grid-col-selected");
    $("#delivery-date-selector").attr("hidden", true);
    $("#date_hidden_input").attr("required", false);

    $("#address_line_1").val("48 Watt Rd");
    $("#city").val("Mornington");
    $("#postal_code").val("3931");
    $("#state").val("VIC");
    $("#delivery-amount").text("0");
    $("#delivery-option").html(
      "Free pickup has been selected.<br/>Please collect from 48 Watt Road, Mornington.<br />Collection must be in an appropriate vehicle.<br/>Photo of your vehicle will be requested.<br />"
    );
    $("#total").text(total);

    if ($("#autocomplete-group").is(":visible")) {
      $("#autocomplete-group").attr("hidden", true);
      $("#delivery-autocomplete-label").attr("hidden", true);
    }
    if ($("#address-group").is(":visible")) {
      $("#address-group").attr("hidden", true);
      $("#city-group").attr("hidden", true);
      $("#postal-group").attr("hidden", true);
      $("#state-group").attr("hidden", true);
    }
    if ($("#postage-option").is(":visible")) {
      $("#postage-option").attr("hidden", true);
      $("#pickup-option").attr("hidden", false);
    }
  });

  // When customer needs to manually enter their address
  $("#full-form-link").click(function(event) {
    event.preventDefault();
    if ($("#address-group").is(":visible")) {
      $("#address-group").attr("hidden", true);
      $("#city-group").attr("hidden", true);
      $("#postal-group").attr("hidden", true);
      $("#state-group").attr("hidden", true);
    } else {
      $("#address-group").attr("hidden", false);
      $("#city-group").attr("hidden", false);
      $("#postal-group").attr("hidden", false);
      $("#state-group").attr("hidden", false);
    }
  });

  // Selecting "Choose a date"
  $("#choose_btn").click(function(event) {
    $("#asap_btn").removeClass("delivery-type-btn");
    $("#asap_btn").addClass("delivery-type-unselected");
    $("#choose_btn").removeClass("delivery-type-unselected");
    $("#choose_btn").addClass("delivery-type-btn");

    $("#asap_check").attr("hidden", true);
    $("#choose_check").attr("hidden", false);

    $("#calendar").attr("hidden", false);
  });

  // Selecting "Deliver as soon as possible"
  $("#asap_btn").click(function(event) {
    $("#postage").val("pickup");
    $("#date_hidden_input").val("ASAP");
    $("#choose_btn").removeClass("delivery-type-btn");
    $("#choose_btn").addClass("delivery-type-unselected");
    $("#asap_btn").removeClass("delivery-type-unselected");
    $("#asap_btn").addClass("delivery-type-btn");

    $("#choose_check").attr("hidden", true);
    $("#asap_check").attr("hidden", false);

    $("#calendar").attr("hidden", true);
  });

  // Customer selecting stripe
  $("#stripe-payment").click(function(event) {
    event.preventDefault();
    $("#paypal-payment").removeClass("themed-grid-col-selected");
    $("#stripe-payment").addClass("themed-grid-col-selected");
    $("#stripe-form").attr("hidden", false);
    $("#place_order_btn").attr("hidden", false);
    $("#place_order_btn_paypal").attr("hidden", true);
    $("#paypal-button-container").attr("hidden", true);
  });

  // Customer selecting paypal
  $("#paypal-payment").click(function(event) {
    event.preventDefault();
    $("#stripe-payment").removeClass("themed-grid-col-selected");
    $("#paypal-payment").addClass("themed-grid-col-selected");
    $("#stripe-form").attr("hidden", true);
    $("#place_order_btn").attr("hidden", true);
    $("#place_order_btn_paypal").attr("hidden", false);
  });

  // When customer selects "set a different billing address"
  $("#billing_btn").click(function(event) {
    event.preventDefault();
    if ($("#billing_group").is(":visible")) {
      $("#billing_group").attr("hidden", true);

      // Set form to required
      $("#billing_first_name").attr("required", false);
      $("#billing_last_name").attr("required", false);
      $("#billing_phone_number").attr("required", false);
      $("#billing_address_line_1").attr("required", false);
      $("#billing_city").attr("required", false);
      $("#billing_state").attr("required", false);
      $("#billing_postal_code").attr("required", false);
      $("#billing_country").attr("required", false);
    } else {
      $("#billing_group").attr("hidden", false);

      // Remove required
      $("#billing_first_name").attr("required", true);
      $("#billing_last_name").attr("required", true);
      $("#billing_phone_number").attr("required", true);
      $("#billing_address_line_1").attr("required", true);
      $("#billing_city").attr("required", true);
      $("#billing_state").attr("required", true);
      $("#billing_postal_code").attr("required", true);
      $("#billing_country").attr("required", true);
    }
  });

  // Place your order with STRIPE
  $("#place_order_btn").click(function(event) {
    event.preventDefault();

    console.log("checkValidity = ", $("#main_form")[0].checkValidity());

    if (!$("#main_form")[0].checkValidity()) {
      no_postage();
      $("#full-form-link").click();
      $("#submit_btn").click();
    } else {
      $("#postage-error").attr("hidden", true);
      $("#place_order_btn").attr("disabled", true);
      $("#place_order_btn").html(
        '<i class="fa fa-spinner fa-spin" aria-hidden="true"></i> PROCESSING'
      );
      stripeSubmit();
    }
  });

  function no_postage() {
    if ($("#postage").val() != "pickup") {
      if (!$("#standard").is(":checked") && !$("#express").is(":checked")) {
        $("#postage-error").attr("hidden", false);
      }
      $("#full-form-link").click();
      $("#submit_btn").click();
    }
    return;
  }

  // Place your order with PAYPAL
  $("#place_order_btn_paypal").click(function(event) {
    event.preventDefault();

    if (!$("#main_form")[0].checkValidity()) {
      no_postage();
    } else {
      $("#postage-error").attr("hidden", true);
      $("#place_order_btn_paypal").attr("disabled", true);
      $("#place_order_btn_paypal").html(
        '<i class="fa fa-spinner fa-spin" aria-hidden="true"></i> PROCESSING'
      );

      var formData = $("#main_form").serialize();
      // api request to validate form
      validate_form_url = "/cart/validate-form-paypal/";
      $.ajax({
        url: validate_form_url,
        type: "post",
        data: formData,
        dataType: "json",
        success: function(data) {
          if (data.valid == "stripe_error") {
            console.log("stripe_error");
            $("#modal-body").text(data.errors);
            $("#myModal").modal("show");
            $("#place_order_btn_paypal").attr("disabled", false);
            $("#place_order_btn_paypal").html(
              '<i class="mr-2 far fa-credit-card"></i>PLACE YOUR ORDER'
            );
          } else if (data.valid == "form_error") {
            console.log("form_error");
            $("#modal-body").html(data.errors);
            $("#myModal").modal("show");
            $("#place_order_btn_paypal").attr("disabled", false);
            $("#place_order_btn_paypal").html(
              '<i class="mr-2 far fa-credit-card"></i>PLACE YOUR ORDER'
            );
          } else if (data.valid == "true") {
            console.log("TRUE");
            window.location.replace("/cart/checkout/paypal/");
          }
        },
        error: function(error) {
          // error here
          $("#place_order_btn_paypal").attr("disabled", false);
          $("#place_order_btn_paypal").html(
            '<i class="mr-2 far fa-credit-card"></i>CONTINUE TO CHECKOUT'
          );
        }
      });
    }
  });

  // Place your order with PAYPAL
  $("#save_your_cart").click(function(event) {
    event.preventDefault();
    console.log("click");

    if (!$("#main_form")[0].checkValidity()) {
      console.log("if");
      no_postage();
    } else {
      console.log("else");
      $("#postage-error").attr("hidden", true);
      $("#save_your_cart").attr("disabled", true);
      $("#save_your_cart").html(
        '<i class="fa fa-spinner fa-spin" aria-hidden="true"></i> PROCESSING'
      );
      console.log("before serial");

      var formData = $("#main_form").serialize();
      console.log("after serial: ", formData);
      // api request to validate form
      validate_form_url = "/cart/validate-form-cart/";
      $.ajax({
        url: validate_form_url,
        type: "post",
        data: formData,
        dataType: "json",
        success: function(data) {
          if (data.valid == "true") {
            console.log("TRUE");
            // window.location.replace("/");
            // $('.toast').toast('show');

            $.toastDefaults.position = 'top-right';
            $.toastDefaults.dismissible = true;
            $.toastDefaults.stackable = true;
            $.toastDefaults.pauseDelayOnHover = true;
            
            $.toast({
              title:'Success!',
              // subtitle:'',
              content:'Your cart is saved successfully.',
              type:'info',
              delay: 3000,
              dismissible:true,
              // img: {
              //   src:'image.png',
              //   class:'rounded',
              //   title:'<a href="https://www.jqueryscript.net/tags.php?/Thumbnail/">Thumbnail</a> Title',
              //   alt:'Alternative'
              // }
            });

            $("#save_your_cart").attr("disabled", false);
            $("#save_your_cart").html(
              '<i class="mr-2 far fa-credit-card"></i>SAVE YOUR CART FOR LATER'
            );

          } else {
            console.log("false");
            $("#save_your_cart").attr("disabled", false);
            $("#save_your_cart").html(
              '<i class="mr-2 far fa-credit-card"></i>SAVE YOUR CART FOR LATER'
            );
          }
        },
        error: function(error) {
          // error here
          $("#save_your_cart").attr("disabled", false);
          $("#save_your_cart").html(
            '<i class="mr-2 far fa-credit-card"></i>SAVE YOUR CART FOR LATER'
          );
        }
      });
    }
  });

  // Change postage option
  $("input:radio").change(function() {
    var total = $("#cart_total").val();

    $("#postage-error").attr("hidden", true);

    if ($(this).val() == "standard") {
      $("#postage").val("standard");

      if ($("#navbarDropdownState").val() == "WA") {
        $("#delivery-amount").text("20.99");
        $("#total").text((parseFloat(total) + parseFloat(20.99)).toFixed(2));
      } else {
        $("#delivery-amount").text("17.99");
        $("#total").text((parseFloat(total) + parseFloat(17.99)).toFixed(2));
      }
    } else {
      $("#postage").val("express");

      if ($("#navbarDropdownState").val() == "WA") {
        $("#delivery-amount").text("28.99");
        $("#total").text((parseFloat(total) + parseFloat(28.99)).toFixed(2));
      } else {
        $("#delivery-amount").text("25.99");
        $("#total").text((parseFloat(total) + parseFloat(25.99)).toFixed(2));
      }
    }
  });

  // Datepicker
  // Disable Sat/Sun
  daysOfWeekDisabled = [0, 6];
  // Instantiate inline date picker
  $(function() {
    $("#datepicker").datepicker({
      inline: true,
      locale: "en-AU",
      startDate: startDate,
      format: "dd/mm/yyyy",
      datesDisabled: datesDisabled,
      daysOfWeekDisabled: daysOfWeekDisabled,
      templates: {
        leftArrow: '<i class="fas fa-chevron-left"></i>',
        rightArrow: '<i class="fas fa-chevron-right"></i>'
      },
      todayHighlight: true,
      weekStart: 1
    });
  });

  $("#datepicker").on("changeDate", function() {
    $("#date_hidden_input").val($("#datepicker").datepicker("getDate"));
  });

  // STRIPE START
  // Create a Stripe client.
  var stripe = Stripe(pub_key);

  // Create an instance of Elements.
  var elements = stripe.elements();

  // Custom styling can be passed to options when creating an Element.
  // (Note that this demo uses a wider set of styles than the guide below.)
  var style = {
    base: {
      color: "#32325d",
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: "antialiased",
      fontSize: "16px",
      "::placeholder": {
        color: "#aab7c4"
      }
    },
    invalid: {
      color: "#fa755a",
      iconColor: "#fa755a"
    }
  };

  // Create an instance of the card Element.
  var card = elements.create("card", { style: style });

  // Add an instance of the card Element into the `card-element` <div>.
  card.mount("#card-element");

  // Handle real-time validation errors from the card Element.
  card.addEventListener("change", function(event) {
    var displayError = document.getElementById("card-errors");
    if (event.error) {
      displayError.textContent = event.error.message;
    } else {
      displayError.textContent = "";
    }
  });

  // Handle form submission.
  function stripeSubmit(event) {
    if ($("#main_form")[0].checkValidity()) {
      stripe.createToken(card).then(function(result) {
        if (result.error) {
          // Inform the user if there was an error.
          var errorElement = document.getElementById("card-errors");
          errorElement.textContent = result.error.message;
          $("#place_order_btn").attr("disabled", false);
          $("#place_order_btn").html(
            '<i class="mr-2 far fa-credit-card"></i>PLACE YOUR ORDER'
          );
        } else {
          // Send the token to your server.
          $("#stripe_token").val(result.token.id);
          stripeTokenHandler(result.token);
        }
      });
    }
  }

  // Submit the form with the token ID
  function stripeTokenHandler(token) {
    var formData = $("#main_form").serialize();

    // api request to validate form
    validate_form_url = "/cart/validate-form-stripe/";
    $.ajax({
      url: validate_form_url,
      type: "post",
      data: formData,
      dataType: "json",
      success: function(data) {
        if (data.valid == "stripe_error") {
          $("#modal-body").text(data.errors);
          $("#myModal").modal("show");
          $("#place_order_btn").attr("disabled", false);
          $("#place_order_btn").html(
            '<i class="mr-2 far fa-credit-card"></i>PLACE YOUR ORDER'
          );
        } else if (data.valid == "form_error") {
          $("#modal-body").html(data.errors);
          $("#myModal").modal("show");
          $("#place_order_btn").attr("disabled", false);
          $("#place_order_btn").html(
            '<i class="mr-2 far fa-credit-card"></i>PLACE YOUR ORDER'
          );
        } else if (data.valid == "true") {
          console.log("TRUE");
          window.location.replace("/cart/checkout/success/");
        }
      },
      error: function(error) {
        // error here
        $("#place_order_btn").attr("disabled", false);
        $("#place_order_btn").html(
          '<i class="mr-2 far fa-credit-card"></i>PLACE YOUR ORDER'
        );
      }
    });
  }
});
