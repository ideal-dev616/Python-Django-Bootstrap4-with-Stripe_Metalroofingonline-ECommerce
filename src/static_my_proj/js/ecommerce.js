$(document).ready(function () {
  // Contact Form Handler
  var contactForm = $(".contact-form");
  var contactFormMethod = contactForm.attr("method");
  var contactFormEndpoint = contactForm.attr("action"); // /abc/

  // Check if device is mobile
  /**
   * jQuery.browser.mobile (http://detectmobilebrowser.com/)
   * jQuery.browser.mobile will be true if the browser is a mobile device
   **/
  (function (a) {
    (jQuery.browser = jQuery.browser || {}).mobile =
      /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(
        a
      ) ||
      /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(
        a.substr(0, 4)
      );
  })(navigator.userAgent || navigator.vendor || window.opera);

  /**
   *
   *           START Cart-Overlay
   *
   **/

  var cartWrapper = $(".cd-cart-container");
  //product id - you don't need a counter in your real project but you can use your real product id
  var productId = 0;

  if (cartWrapper.length > 0) {
    //store jQuery objects
    var cartBody = cartWrapper.find(".cart-overlay-body");
    var cartList = cartBody.find("ul").eq(0);
    var cartTotal = cartWrapper.find(".checkout").find("span");
    var cartTrigger = cartWrapper.children(".cd-cart-trigger");
    var cartCount = cartTrigger.children(".count");
    var addToCartBtn = $(".cd-add-to-cart");
    var undo = cartWrapper.find(".undo");
    var undoTimeoutId;

    //add product to cart
    addToCartBtn.on("click", function (event) {
      event.preventDefault();
      addToCart($(this));
    });

    // open/close cart
    cartTrigger.on("click", function (event) {
      event.preventDefault();
      toggleCart();
    });

    //close cart when clicking on the .cd-cart-container::before (bg layer)
    cartWrapper.on("click", function (event) {
      if ($(event.target).is($(this))) toggleCart();
    });

    //delete an item from the cart
    cartList.on("click", ".delete-item", function (event) {
      event.preventDefault();
      removeProduct($(event.target).parents(".product"));
    });

    //update item quantity
    cartList.on("change", "select", function (event) {
      quickUpdateCart();
    });
  }

  function toggleCart(bool) {
    var cartIsOpen = typeof bool === "undefined" ? cartWrapper.hasClass("cart-open") : bool;

    if (cartIsOpen) {
      cartWrapper.removeClass("cart-open");
      // reset undo
      clearInterval(undoTimeoutId);
      undo.removeClass("visible");
      cartList.find(".deleted").remove();
    } else {
      cartWrapper.addClass("cart-open");
    }
  }

  function addToCart(trigger) {
    var cartIsEmpty = cartWrapper.hasClass("empty");
    //update cart product list
    addProduct();
    //update number of items
    updateCartCount(cartIsEmpty);
    //update total price
    updateCartTotal(trigger.data("price"), true);
    //show cart
    cartWrapper.removeClass("empty");
    // cartWrapper.addClass("cart-open");
  }

  function addProduct(data) {
    //this is just a product placeholder
    //you should insert an item with the selected product info
    //replace productId, productName, price and url with your real product info
    productId = data.pk;

    var productAdded = $(
      '<li class="product" id="' +
        data.pk +
        '">' +
        '<div class="product-image">' +
        '<a href="' +
        $("#product-url").val() +
        '">' +
        '<img src="' +
        $("#product-image").attr("href") +
        '" alt="{{ instance.title }}">' +
        "</a>" +
        "</div>" +
        '<div class="product-details">' +
        "<h3>" +
        '<a href="' +
        $("#product-url").val() +
        '">' +
        $("#title").text() +
        "</a>" +
        "</h3>" +
        '<span class="price text-60-percent">$' +
        data.line_price +
        "</span>" +
        '<div class="actions">' +
        '<a href="#0" class="delete-item text-60-percent">Delete</a>' +
        '<div class="quantity text-60-percent">' +
        '<label for="cd-product-' +
        data.pk +
        '">Qty</label>' +
        data.quantity +
        "</div>" +
        "</div>" +
        "</div>" +
        "</li>"
    );

    cartList.prepend(productAdded);
  }

  function removeProduct(product) {
    clearInterval(undoTimeoutId);
    cartList.find(".deleted").remove();
    var pk = product.attr("id");

    var topPosition = product.offset().top - cartBody.children("ul").offset().top,
      productQuantity = Number(product.find(".quantity").find("select").val()),
      productTotPrice = Number(product.find(".price").text().replace("$", "")) * productQuantity;

    product.css("top", topPosition + "px").addClass("deleted");

    remove_item_url = "/cart-overlay/remove-item";
    $.ajax({
      type: "POST",
      url: remove_item_url,
      headers: { "X-CSRFToken": CSRF_TOKEN },
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        pk: pk,
      },
      success: function (data) {
        if (data.valid == "error") {
          $("#modal-body").text(data.errors);
          $("#myModal").modal("show");
        }
        total = data.total;
        $("#cart-overlay-total").text(total);
        cartCount.find("li").eq(0).text(data.cart_count);
        $("#lblCartCount").text(data.cart_count);
      },
    });
  }

  function quickUpdateCart() {
    var quantity = 0;
    var price = 0;

    cartList.children("li:not(.deleted)").each(function () {
      var singleQuantity = Number($(this).find("select").val());
      quantity = quantity + singleQuantity;
      price = price + singleQuantity * Number($(this).find(".price").text().replace("$", ""));
    });

    cartTotal.text(price.toFixed(2));
    cartCount.find("li").eq(0).text(quantity);
    cartCount
      .find("li")
      .eq(1)
      .text(quantity + 1);
  }

  function updateCartCount(emptyCart, quantity) {
    if (typeof quantity === "undefined") {
      var actual = Number(cartCount.find("li").eq(0).text()) + 1;
      var next = actual + 1;

      if (emptyCart) {
        cartCount.find("li").eq(0).text(actual);
        cartCount.find("li").eq(1).text(next);
      } else {
        cartCount.addClass("update-count");

        setTimeout(function () {
          cartCount.find("li").eq(0).text(actual);
        }, 150);

        setTimeout(function () {
          cartCount.removeClass("update-count");
        }, 200);

        setTimeout(function () {
          cartCount.find("li").eq(1).text(next);
        }, 230);
      }
    } else {
      var actual = Number(cartCount.find("li").eq(0).text()) + quantity;
      var next = actual + 1;

      cartCount.find("li").eq(0).text(actual);
      $("#lblCartCount").text(actual);
      cartCount.find("li").eq(1).text(next);
    }
  }

  function updateCartTotal(price, bool) {
    bool
      ? cartTotal.text((Number(cartTotal.text()) + Number(price)).toFixed(2))
      : cartTotal.text((Number(cartTotal.text()) - Number(price)).toFixed(2));
  }

  /**
   *
   *           END Cart-Overlay
   *
   **/

  contactForm.submit(function (event) {
    event.preventDefault();

    var contactFormSubmitBtn = contactForm.find("[type='submit']");
    var contactFormSubmitBtnTxt = contactFormSubmitBtn.text();

    var contactFormData = contactForm.serialize();
    var thisForm = $(this);
    displaySubmitting(contactFormSubmitBtn, "", true);
    $.ajax({
      method: contactFormMethod,
      url: contactFormEndpoint,
      data: contactFormData,
      success: function (data) {
        contactForm[0].reset();
        $.alert({
          title: "Success!",
          content: data.message,
          theme: "modern",
        });
        setTimeout(function () {
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false);
        }, 500);
      },
      error: function (error) {
        var jsonData = error.responseJSON;
        var msg = "";

        $.each(jsonData, function (key, value) {
          // key, value  array index / object
          msg += key + ": " + value[0].message + "<br/>";
        });

        $.alert({
          title: "Oops!",
          content: msg,
          theme: "modern",
        });

        setTimeout(function () {
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false);
        }, 500);
      },
    });
  });

  var checkoutState = $(".lead").attr("value");

  //------------ START: CARD CAROUSEL SLIDER MAIN PAGE ------------//
  $(".multiple-items").slick({
    dots: true,
    infinite: false,
    speed: 300,
    slidesToShow: 4,
    slidesToScroll: 4,
    arrows: false,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 3,
          infinite: true,
          dots: true,
          arrows: false,
        },
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 2,
          arrows: false,
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
          arrows: false,
        },
      },
      // You can unslick at a given breakpoint now by adding:
      // settings: "unslick"
      // instead of a settings object
    ],
  });

  //------------ START: NAVBAR STATE DROP DOWN ------------//
  // Disable state drop down and change to "LOADING..." While jquery loads
  // Get value of state to change back to once loaded.
  selected_state_val = $("#navbarDropdownState option:selected").val();

  default_check = $("#navbarDropdownState").find(":selected").val();

  // Set default state to VIC
  if (default_check == "SS") {
    $("#navbarDropdownState").val("VIC");
    // Ajax call on state change to clear cart for price difference of state
    changed_state_url = "/cart/state-changed/";
    $.ajax({
      type: "POST",
      url: changed_state_url,
      headers: { "X-CSRFToken": CSRF_TOKEN },
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        id: "VIC",
      },
      success: function (data) {
        selected_state_val = data.state;
        $("#navbarDropdownState option:selected").val(selected_state_val);
        $(".navbar-cart-count").text(0);
      },
    });
  } else {
    $("#selectStateModal").modal("hide");
  }

  // State change API to set request.session.state_selected
  $("#navbarDropdownState").change(function () {
    var selText = $(this).val();
    $("#navbarDropdownState").val(selText);

    // Ajax call on state change to clear cart for price difference of state
    changed_state_url = "/cart/state-changed/";
    $.ajax({
      type: "POST",
      url: changed_state_url,
      headers: { "X-CSRFToken": CSRF_TOKEN },
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        id: selText,
      },
      success: function (data) {
        selected_state_val = data.state;
        $("#navbarDropdownState option:selected").val(selected_state_val);
        $(".navbar-cart-count").text(0);
        location.reload();
      },
    });
  });
  $("#modalDropdownState").change(function () {
    $("#selectStateModal").modal("hide");
    var selText = $(this).val();
    $("#modalDropdownState").val(selText);

    // Ajax call on state change to clear cart for price difference of state
    changed_state_url = "/cart/state-changed/";
    $.ajax({
      type: "POST",
      url: changed_state_url,
      headers: { "X-CSRFToken": CSRF_TOKEN },
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        id: selText,
      },
      success: function (data) {
        selected_state_val = data.state;
        $("#modalDropdownState option:selected").val(selected_state_val);
        $(".navbar-cart-count").text(0);
        location.reload();
      },
    });
  });
  $("#navbarDropdownStateTwo").val(selected_state_val);

  // SECOND NAVBAR STATE DROPDOWN
  //------------ START: NAVBAR TWO STATE DROP DOWN ------------//
  // Disable state drop down and change to "LOADING..." While jquery loads
  // Get value of state to change back to once loaded.
  selected_state_val = $("#navbarDropdownStateTwo option:selected").val();

  default_check = $("#navbarDropdownStateTwo").find(":selected").val();

  // Set default state to VIC
  if (default_check == "SS") {
    $("#navbarDropdownStateTwo").val("VIC");

    // Ajax call on state change to clear cart for price difference of state
    changed_state_url = "/cart/state-changed/";
    $.ajax({
      type: "POST",
      url: changed_state_url,
      data: {
        id: "VIC",
      },
      success: function (data) {
        selected_state_val = data.state;
        $("#navbarDropdownStateTwo option:selected").val(selected_state_val);
        $(".navbar-cart-count").text(0);
      },
    });
  }

  // State change API to set request.session.state_selected
  $("#navbarDropdownStateTwo").change(function () {
    var selText = $(this).val();
    $("#navbarDropdownStateTwo").val(selText);

    // Ajax call on state change to clear cart for price difference of state
    changed_state_url = "/cart/state-changed/";
    $.ajax({
      type: "POST",
      url: changed_state_url,
      data: {
        id: selText,
      },
      success: function (data) {
        selected_state_val = data.state;
        $("#navbarDropdownStateTwo option:selected").val(selected_state_val);
        $(".navbar-cart-count").text(0);
        location.reload();
      },
    });
  });
  $("#navbarDropdownStateTwo").val(selected_state_val);

  // If we're on the product page then load the state into the value of state_selected
  $('[name="state_selected"]').val($("#navbarDropdownState").val());

  // If we are in the cart-home or checkout process then we disable state selecting
  var pathname = window.location.pathname;

  function displaySubmitting(submitBtn, defaultText, doSubmit) {
    if (doSubmit) {
      submitBtn.addClass("disabled");
      submitBtn.html("<i class='fa fa-spin fa-spinner'></i> Sending...");
    } else {
      submitBtn.removeClass("disabled");
      submitBtn.html(defaultText);
    }
  }
  //------------ END: NAVBAR STATE DROP DOWN ------------//

  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////
  //------------              START: CART + ADD PRODUCTS              ------------//
  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////
  var productForm = $(".form-product-ajax");

  $.each(productForm, function (index, object) {
    var $this = $(this);
    var isUser = $this.attr("data-user");
    var submitSpan = $this.find(".submit-span");
    var productInput = $this.find("[name='product_id']");
    var productId = productInput.attr("value");
    var quantityInput = $this.find("[name='quantity']");
    var quantity = quantityInput.attr("value");
  });

  productForm.submit(function (event) {
    event.preventDefault();
    let thisForm = $(this);
    // var actionEndpoint = thisForm.attr("action"); // API Endpoint
    let actionEndpoint = thisForm.attr("data-endpoint");
    let httpMethod = thisForm.attr("method");
    let formData = thisForm.serialize();

    $.ajax({
      url: actionEndpoint,
      method: httpMethod,
      data: formData,
      success: function (data) {
        var submitSpan = thisForm.find(".submit-span");
        var submitButton = thisForm.find("#submit-detail");
        var iconAddToCart = thisForm.find("#submit-detail i");
        var navbarCountValue = $(".navbar-cart-count").text();
        var navbarCart = $("#cartNav");
        var navbarCount = $(".navbar-cart-count");

        if (data.valid == "error") {
          $("#modal-body").text(data.errors);
          $("#myModal").modal("show");
          if (data.errors) {
            $.alert({
              title: "Oops!",
              content: data.errors,
              theme: "modern",
            });
          } else {
            $.alert({
              title: "Oops!",
              content: "An error has occured, please call 1300 886 944 for help",
              theme: "modern",
            });
          }
        } else if (data.added) {
          var product_exist = false;
          // If product already exists increase quantity and line_price
          for (let i = 0; i < data.items.length; i++) {
            product_exist = false;
            $(".product").each(function (index) {
              if ($(this).attr("id") == data.items[i].pk) {
                product_exist = true;
                $(this)
                  .find(".quantity")
                  .text("Qty " + data.items[i].quantity);
                $(this)
                  .find(".price")
                  .text("$" + data.items[i].line_price);
                $(this).insertBefore($(".product").eq(0));
              }
            });

            // New product, add all values to overlay-cart
            if (!product_exist) {
              var html =
                '<li class="product" id="' +
                data.items[i].pk +
                '">' +
                '<div class="product-image">' +
                '<a href="' +
                $("#product-url").val() +
                '">' +
                '<img src="' +
                $("#product-image-url").first().prop("src") +
                '" alt="' +
                $("#title").text() +
                '">' +
                "</a>" +
                "</div>" +
                '<div class="product-details">' +
                "<h3>" +
                '<a href="' +
                $("#product-url").val() +
                '">' +
                $("#title").text() +
                "</a>" +
                "</h3>" +
                '<span class="price text-60-percent">$' +
                data.items[i].line_price +
                "</span>" +
                '<div class="actions">' +
                '<a href="#0" class="delete-item text-60-percent">Delete</a>' +
                '<div class="quantity text-60-percent cart-gap">' +
                '<label for="cd-product-' +
                data.items[i].pk +
                '">Qty</label>' +
                data.items[i].quantity +
                "</div>";

              if (data.items[i].length != null)
                html +=
                  '<div class="length text-60-percent"><label>Length:</label>' + data.items[i].length + "m" + "</div>";
              html += "</div></div></li>";

              var productAdded = $(html);

              cartList.prepend(productAdded);
              cartWrapper.removeClass("empty");
              toggleCart();
            }
          }

          navbarCart.css("color", "orange");
          navbarCount.css("color", "orange");
          submitButton.attr("class", "btn btn-outline-success btn-lg btn-block");
          submitButton.html("Product Added <i class='fa fa-check' id='icon-add-to-cart'></i>");
          setTimeout(function () {
            // Wait
            submitButton.attr("class", "btn background-orange text-white btn-lg btn-block");
            submitButton.html("Add to cart");
          }, 700);
          cartWrapper.addClass("cart-open");
        } else {
          if (data.cartItemCount == 0) {
            navbarCart.css("color", "#9ba8bb");
            navbarCount.css("color", "#9ba8bb");
          }
        }

        // Set cart-count
        $(".count").find("li").eq(0).text(Number(data.cartItemCount));
        $("#lblCartCount").text(data.cartItemCount);

        // Set total to cart total
        $("#cart-overlay-total").text(data.total);

        navbarCount = $(".navbar-cart-count");
        navbarCount.text(data.cartItemCount);
        var currentPath = window.location.href;

        if (currentPath.indexOf("cart") != -1 && data.removed) {
          // Removes an element from the document
          let parentTR = $(thisForm).closest("tr");
          parentTR.remove();
          // Set cart-count
          $(".cart-tax")
            .text("$" + (parseFloat(data.total) / 11).toFixed(2))
            .digits();
          $(".cart-subtotal")
            .text("$" + (parseFloat(data.total) / 1.1).toFixed(2))
            .digits();
          $(".cart-count").text(data.items.length);
          $(".count").find("li").eq(0).text(Number(data.cartItemCount));
          // Set total to cart total
          $(".cart-total").text("$" + data.total);
          $("#cart-overlay-total").text(data.total);
        }
      },
      error: function (errorData) {
        $.alert({
          title: "Oops!",
          content: "An error occurred",
          theme: "modern",
        });
      },
    });
  });

  // During checkout process set state_checkout to whatever state is selected:
  $("#state_checkout").val($("#navbarDropdownState option:selected").val());

  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////
  //------------              END CART + ADD PRODUCTS                 ------------//
  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////

  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////
  //------------ START: PRODUCT DETAIL VIEW (PRICE/LENGTH/COLOUR/ETC)  -----------//
  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////

  // Changed Here by Damian
  $.fn.check_button_state = function () {
    // Make sure all selectable items are selected before we enable button
    let lengthCheck = 5;
    let additionalCheck = 5;
    let colourCheck = 5;
    let custom_length_check = 5;
    let selected_length_data = null;

    if ($("#length").length) {
      lengthCheck = $("#length").children("option").filter(":selected").text();
      if ($("#custom-length").hasClass("active")) {
        var length = $("#length").val() / 1000;
      } else {
        length = $("#length").children("option").filter(":selected").val();
      }
      if (lengthCheck !== "Choose Length") {
        lengthCheck = 1;
        if ($("#quantity").length) {
          selected_length_data = length;
        }
      } else {
        lengthCheck = 0;
      }
    }

    if ($("#additionaldropdown").length) {
      var additional = $("#additionaldropdown").children("option").filter(":selected").text();
      additionalCheck = 0;
      if (additional != "Choose Option") {
        additionalCheck = 1;
      }
    }

    if ($("#colour-select").val() == "Select Colour") {
      colourCheck = 0;
    } else {
      colourCheck = 5;
    }

    // adjust data of custom length form and added it to hidden value #custom_length
    if ($("#custom_length").length) {
      let custom_length_data = adjust_mapping_data("custom_length_div");
      selected_length_data ? selected_length_data : null;
      $("#custom_length").val(selected_length_data);
      custom_length_check = custom_length_data.length;
    }

    if ((lengthCheck != 0 || custom_length_check != 0) && additionalCheck != 0 && colourCheck != 0) {
      $("#submit-detail").prop("disabled", false);
    } else {
      $("#submit-detail").prop("disabled", true);
    }
  };

  // Disable add to cart untill values selected
  $("#submit-detail").check_button_state();

  // Change length to number input field when user selects custom length
  // Clone the original state of length (drop down list) so we can revert to it
  var lengthClone = $("#length-div").clone();
  var lengthCost = 0;
  var colourCost = 0;
  var additionalCost = 0;

  // Current price (based on state)
  var price = $("#display_price").text();
  price = price.substring(1);
  var new_price = price;
  var _quantity = $("#quantity").val();

  // on length - custom field change, update price
  $("#custom-length").click(function () {
    $(".custom").css("display", "none");
    $(".defined").css("display", "none");
    $(this).toggleClass("active");

    if ($(this).hasClass("active")) {
      $(".custom").css("display", "inline");
      $("#length-div").replaceWith(
        '<div class="input-group" id="length-div"><input type="number" class="form-control length border-square-blue text-center no-border-right" name="length" id="length" min="600" max="10000" placeholder="Enter Custom Length" required><div class="input-group-append border-square-blue"><span class="input-group-text">mm</span></div></div>'
      );

      $("#length").bind("keyup mouseup", function () {
        lengthCost = $(this).add_length_price();
        colourCost = $(this).add_colour_price();
        additionalCost = $(this).add_additional_price();
        _quantity = $("#quantity").val() > 0 ? $("#quantity").val() : 1;
        new_price =
          (parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost)) *
          _quantity;

        $("#display_price").text("$" + new_price.toFixed(2));
        $(this).check_button_state();
      });
    } else {
      $("#length-div").replaceWith(lengthClone);

      // On length - drop down change, update price
      $("#length").change(function () {
        lengthCost = $(this).add_length_price();
        colourCost = $(this).add_colour_price();
        additionalCost = $(this).add_additional_price();

        // new_price = parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost);
        _quantity = $("#quantity").val() > 0 ? $("#quantity").val() : 1;
        new_price =
          (parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost)) *
          _quantity;

        $("#display_price").text("$" + new_price.toFixed(2));
        $(this).check_button_state();
      });

      $(".defined").css("display", "inline");
      $(this).check_button_state();
      buildLengthSelect();
    }
  });

  // On length - drop down change, update price
  $("#length").change(function () {
    lengthCost = $(this).add_length_price();
    colourCost = $(this).add_colour_price();
    additionalCost = $(this).add_additional_price();
    // new_price = parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost);
    _quantity = $("#quantity").val() > 0 ? $("#quantity").val() : 1;
    new_price =
      (parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost)) * _quantity;

    $("#display_price").text("$" + new_price.toFixed(2));
    $(this).check_button_state();
  });

  // On colour change, update price, set name after COLOUR SELECTED:
  $("input[name=colourPrice]").click(function () {
    $("label").removeClass("toggled");
    var radio = $(this);
    radio.parent().toggleClass("toggled");

    // Set name of product so user can see colour they've chosen in text form
    $("#colour").val($(this).attr("id"));
    $("#colour-select").val($(this).attr("id"));

    additionalCost = $(this).add_additional_price();
    lengthCost = $(this).add_length_price();
    colourCost = $(this).add_colour_price();

    // new_price = parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost);
    _quantity = $("#quantity").val() > 0 ? $("#quantity").val() : 1;
    new_price =
      (parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost)) * _quantity;

    $("#display_price").text("$" + new_price.toFixed(2));
    $(this).check_button_state();
  });

  $("#colour-select").change(function () {
    id = $("#colour-select").children("option").filter(":selected").text();
    id_string = id.replace("®", "");
    id_string = id_string.replace(/\s+/, "");
    id_string = "input[colour_name=" + id_string + "]";

    if (id != "input[colour_name=SelectColour]") {
      $("label").removeClass("toggled");
      radio = $(id_string);
      radio.prop("checked", true);
      radio.parent().toggleClass("toggled");
    }

    // Highlight selected colour
    $("#colour").val(id);

    additionalCost = $(this).add_additional_price();
    lengthCost = $(this).add_length_price();
    colourCost = $(this).add_colour_price();
    _quantity = $("#quantity").val() > 0 ? $("#quantity").val() : 1;
    new_price =
      (parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost)) * _quantity;
    // new_price = parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost);

    $("#display_price").text("$" + new_price.toFixed(2));
    $(this).check_button_state();
  });

  // On additional drop down change, update price
  $("#additionaldropdown").change(function () {
    additionalCost = $(this).add_additional_price();
    lengthCost = $(this).add_length_price();
    colourCost = $(this).add_colour_price();

    // new_price = parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost);
    quantity = $("#quantity").val() > 0 ? $("#quantity").val() : 1;
    new_price =
      (parseFloat(price) + parseFloat(additionalCost) + parseFloat(lengthCost) + parseFloat(colourCost)) * quantity;

    $("#display_price").text("$" + new_price.toFixed(2));
    $(this).check_button_state();
  });

  // on change of quantity field
  $("#quantity").change(function () {
    var price_per_unit = new_price / _quantity;
    _quantity = $("#quantity").val() > 0 ? $("#quantity").val() : 1;
    new_price = price_per_unit * _quantity;
    $("#display_price").text("$" + new_price.toFixed(2));
    $(this).check_button_state();
  });
  // For products with a length option add the price and unlock add to cart
  $.fn.add_length_price = function () {
    if ($("#custom-length").hasClass("active")) {
      var length = $("#length").val();
    } else {
      length = $("#length").children("option").filter(":selected").text();
      length = length * 1000;
    }

    length = length > 1000 ? length : 1000;

    // Make sure length is selected
    if (length != "Choose Length" && length != "" && length != null) {
      // Add cost of length to price
      price_per_mm = $("#price_per_mm").val();
      additional_cost_length = parseFloat(length) * parseFloat(price_per_mm);

      if (length > 1000) {
        additional_cost_length = parseFloat(additional_cost_length) - parseFloat(price);
      } else {
        additional_cost_length = 0;
      }

      new_price = parseFloat(price) + parseFloat(additional_cost_length);

      return additional_cost_length;
    }
    return 0;
  };

  $.fn.add_colour_price = function () {
    var colourCost = $("input[name=colourPrice]:checked").val();
    var colourName = $("input[name=colourPrice]:checked").attr("id");
    var additional = $("#additionaldropdown").children("option").filter(":selected").text();
    zincalume_discount = $("#zincalume_discount").val();
    var cost = 0;

    if (colourName == "ZINCALUME®") {
      if ($("#custom-length").hasClass("active")) length = $("#length").val() / 1000;
      else length = $("#length").children("option").filter(":selected").text();

      // If the product doesn't have a length
      if (length == null || length == "" || length == " ") {
        // And if the product has no additional option
        if (additional == null || additional == "" || additional == " ") {
          cost = -Math.abs(zincalume_discount);
        }
      } else if (length != "Choose Length") {
        length = length > 1 ? length : 1;
        cost = -Math.abs(zincalume_discount) * (length * 1000);
      } else {
        cost = -Math.abs(zincalume_discount);
      }

      return cost;
    }

    if (colourName != "ChooseColour" && colourName != null && colourName != "") {
      // Add cost of colour to price
      cost = parseFloat(colourCost);

      return cost;
    }

    return cost;
  };

  $.fn.add_additional_price = function () {
    var additional = $("#additionaldropdown").children("option").filter(":selected").text();
    additional = additional.replace(/[^a-z0-9\s]/gi, "").replace(/[_\s]/g, "");
    var additionalCost = $("#additionaldropdown").children("option").filter(":selected").attr("id");
    var additionalDiscount = $("#additionaldropdown").children("option").filter(":selected").attr("data-discount");
    var colourName = $("input[name=colourPrice]:checked").attr("id");

    if (additional != "ChooseOption" && additional != null && additional != "") {
      if (additionalDiscount != null && colourName == "ZINCALUME®") {
        additionalCost = parseFloat(additionalCost) + parseFloat(additionalDiscount);
      }
      return additionalCost;
    }

    return 0;
  };
  //------------ END: PRODUCT DETAIL VIEW (PRICE/LENGTH/COLOUR/ETC)  ------------//

  /////////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////////
  //------------              START: CHECKOUT PROCESS                ------------//
  /////////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////////

  // Disable stripe checkout button when 'checkout' has been clicked
  $("#stripe-checkout-btn").click(function () {
    $(this).prop("hidden", true);
    $("#stripe-checkout-btn-hidden").prop("hidden", false);
  });

  // Set the state to what was selected at type of "checkout" pressed
  if (checkoutState == "shipping") {
    var dropDownState = $("#navbarDropdownState option:selected").val();
    $("#state").val(dropDownState);
  }

  // If the user is in victoria we allow the pickup option to be selected
  if (top.location.pathname === "/cart/checkout/") {
    state = $(navbarDropdownState).find(":selected").val();
    if (state == "VIC") {
      $("#pickupCheck").removeAttr("hidden");
    }

    $("#pickupCheck").click(function () {
      checkbox_val = $("#pickupCheck").val();

      // The value of the actual checkbox itself
      value = $("#id_pickup").is(":checked");
      // Set the address to mornington store and lock the fields
      if (value) {
        $("#address_autocomplete").prop("readonly", true);
        $("#autocomplete-group").attr("hidden", true);
        $("#address_line_1").val("48 Watt Rd");
        $("#address-group").attr("hidden", true);
        $("#city").val("Mornington");
        $("#city-group").attr("hidden", true);
        $("#postal_code").val("3931");
        $("#postal_code-group").attr("hidden", true);
        $("#state").val("VIC");
        $("#state-group").attr("hidden", true);
        $("#country").val("Australia");
        $("#country-group").attr("hidden", true);
        $("#delivery_instructions").prop("readonly", true);
        $("#delivery_instructions").attr("hidden", true);
        $("#same_as_billing").attr("hidden", true);
      }
      // Removes the set address and enables the field
      else {
        $("#address_autocomplete").prop("readonly", false);
        $("#autocomplete-group").attr("hidden", false);
        $("#address_line_1").val("");
        $("#address-group").attr("hidden", false);
        $("#city").val("");
        $("#city-group").attr("hidden", false);
        $("#postal_code").val("");
        $("#postal_code-group").attr("hidden", false);
        $("#state").val("VIC");
        $("#state-group").attr("hidden", false);
        $("#country-group").attr("hidden", false);
        $("#delivery_instructions").prop("readonly", false);
        $("#delivery_instructions-group").attr("hidden", false);
        $("#same_as_billing").attr("hidden", false);
      }
    });
  }

  // QTY Up / Down arrows in cart home
  $("[name='plus-btn']").on("click", function () {
    var button = $(this);

    var id = button
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .find(".values")
      .find(".form-product-ajax")
      .find(".cart-item-product-id")
      .val();
    var colour = button
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .find(".values")
      .find(".form-product-ajax")
      .find(".cart-item-colour")
      .val();
    var length = button
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .find(".values")
      .find(".form-product-ajax")
      .find(".cart-item-length")
      .val();
    var additional = button
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .find(".values")
      .find(".form-product-ajax")
      .find(".cart-item-additionaldropdown")
      .val();

    var quantityURL = "/cart/quantity-changed/";

    $.ajax({
      url: quantityURL,
      data: {
        add: true,
        subtract: false,
        product_id: id,
        colour: colour,
        length: length,
        additional: additional,
      },
      dataType: "json",
      success: function (data) {
        button.parent().parent().find("input").val(data.quantity);
        button
          .parent()
          .parent()
          .parent()
          .parent()
          .parent()
          .parent()
          .find(".values")
          .find(".form-product-ajax")
          .find(".cart-item-quantity")
          .val(data.quantity);
        $(".cart-total")
          .text("$" + parseFloat(data.total).toFixed(2))
          .digits();
        $(".cart-tax")
          .text("$" + parseFloat(data.taxes).toFixed(2))
          .digits();
        $(".cart-subtotal")
          .text("$" + parseFloat(data.subtotal).toFixed(2))
          .digits();
        $("cart-count").text(data.cartitem_set.count);
        $(".count").children("li").first().text(data.total_quantity);
        $("#lblCartCount").text(data.total_quantity);
      },
    });

    // $('#qty_input').val(parseInt($('#qty_input').val()) + 1 );
  });

  $("[name='minus-btn']").on("click", function () {
    var button = $(this);
    var id = button
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .find(".values")
      .find(".form-product-ajax")
      .find(".cart-item-product-id")
      .val();
    var colour = button
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .find(".values")
      .find(".form-product-ajax")
      .find(".cart-item-colour")
      .val();
    var length = button
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .find(".values")
      .find(".form-product-ajax")
      .find(".cart-item-length")
      .val();
    var additional = button
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .parent()
      .find(".values")
      .find(".form-product-ajax")
      .find(".cart-item-additionaldropdown")
      .val();

    var quantityURL = "/cart/quantity-changed/";

    $.ajax({
      url: quantityURL,
      data: {
        add: false,
        subtract: true,
        product_id: id,
        colour: colour,
        length: length,
        additional: additional,
      },
      dataType: "json",
      success: function (data) {
        button.parent().parent().find("input").val(data.quantity);
        button
          .parent()
          .parent()
          .parent()
          .parent()
          .parent()
          .parent()
          .find(".values")
          .find(".form-product-ajax")
          .find(".cart-item-quantity")
          .val(data.quantity);
        $(".cart-total")
          .text("$" + parseFloat(data.total).toFixed(2))
          .digits();
        $(".cart-tax")
          .text("$" + parseFloat(data.taxes).toFixed(2))
          .digits();
        $(".cart-subtotal")
          .text("$" + parseFloat(data.subtotal).toFixed(2))
          .digits();
        $("cart-count").text(data.cartitem_set.count);
        $(".count").children("li").first().text(data.total_quantity);
        $("#lblCartCount").text(data.total_quantity);
      },
    });
  });

  // Check for $17.99 shipping to give option of express
  shipping = $("#shipping").text();
  if (shipping == "$25.99") {
    $("#express").attr("hidden", false);
    $("#express-check").attr("hidden", false);
    $("#express-check").prop("checked", true);
  }
  if (shipping == "$17.99" || shipping == "$25.99") {
    $("#express").attr("hidden", false);
    $("#express-check").attr("hidden", false);
  }

  $("#express-check").change(function () {
    var shipping_url = "/cart/shipping-changed/";
    var express = false;

    if ($("#express-check").prop("checked")) {
      express = true;
    }

    $.ajax({
      url: shipping_url,
      data: {
        express: express,
        order_id: $("#express-check").attr("name"),
      },
      dataType: "json",
      success: function (data) {
        $("#shipping").text("$" + data.shipping_total);
        $("#cart-change-total").text("$" + data.order_total);
        location.reload();
      },
    });
  });

  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////
  //------------                   START: SEARCH BAR                  ------------//
  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////
  $(".search-button").click(function (event) {
    event.preventDefault();

    searchBar = $("#search-bar");

    if (searchBar.attr("hidden")) {
      searchBar.attr("hidden", false);
      $("#search").focus();
    } else {
      searchBar.attr("hidden", true);
    }
  });

  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////
  //------------                   START: POST CODES                  ------------//
  //////////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////////
  var post_code_url = "/get_post_code/";
  if ($("#postage_allowed").length == 0) {
    postage = false;
  } else {
    postage = true;
  }

  $("#post_code_button").click(function (event) {
    $.ajax({
      url: post_code_url,
      method: "POST",
      data: {
        post_code: $("#input_post_code").val(),
        postage: postage,
      },
      dataType: "json",
      success: function (data) {
        $("#post_code_response").html(data.post_code);
        $("#post_code_response").attr("hidden", false);
      },
    });
  });

  // UTILITY FUNCTIONS
  $.fn.digits = function () {
    // Returns a humanized value for integers e.g. "1,200.50"
    return this.each(function () {
      $(this).text(
        $(this)
          .text()
          .replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,")
      );
    });
  };

  if ($("#product_row").children().length == 0) {
    $("#product_row").append(
      "<div class='row'><div class='col text-center mb-5'><h1> We are always working on new delivery areas.</h1></div></div>"
    );
  }

  // SLICK PRODUCT SLIDER
  $(".sc").slick({
    dots: false,
    infinite: false,
    speed: 300,
    slidesToShow: 4,
    slidesToScroll: 4,
    autoplay: true,
    autoplaySpeed: 2000,
    arrows: false,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 3,
          infinite: true,
          dots: true,
        },
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
      // You can unslick at a given breakpoint now by adding:
      // settings: "unslick"
      // instead of a settings object
    ],
  });

  // Slick Testimonial slider
  $(".testimonial-carousel").slick({
    dots: true,
    infinite: true,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 5000,
    arrows: true,
    prevArrow: $(".testimonial-carousel-controls .prev"),
    nextArrow: $(".testimonial-carousel-controls .next"),
  });
});
