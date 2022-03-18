$(document).ready(function() {

  var thisForm = $(this)

  $("#send-email").click(function () {
        var subject = $('#subject').val();
        var message = $('#message').text();
        var to_email = $('#to_email').val();
        var from_email = $('#from_email').val();
        var order_id = $('#order_id').val();
        var submitButton = thisForm.find("#send-email")

        submitButton.html("Sending Email <i class='fa fa-spinner fa-spin' style='font-size:20px'></i>")

        $.ajax({
          url: '/email-customer/',
          data: {
            'subject': subject,
            'message': message,
            'to_email': to_email,
            'from_email': from_email,
            'order_id': order_id,
          },
          dataType: 'json',
          success: function (data) {
            last_email_string = data.last_email.replace(/\n/g, "<br />");

            $('#last_email').html(last_email_string)
            submitButton.html("Email Sent <i class='fa fa-check' id='icon-add-to-cart'></i>")
                    setTimeout(
                        function()
                        {
                            // Wait
                            submitButton.attr('class', 'btn btn-outline-success btn-block');
                            submitButton.html("Send Email")
                        }, 700
                    )
          }
        });
  });
});
