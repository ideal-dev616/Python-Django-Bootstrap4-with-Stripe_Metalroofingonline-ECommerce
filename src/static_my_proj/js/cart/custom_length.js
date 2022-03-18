// Created By Damian

// Add new row with data or blank values
function add_row(div_id, quantity = "", length = "") {
  var html = '<div class="row"><div class="col-sm-4"><div class="form-group">';
  html += '<input type="number" class="form-control border-square-blue text-center quantity" value="' + quantity + '">';
  html += '</div></div><div class="col-sm-8"><div class="row"><div class="col-sm-10"><div class="input-group mb-3">';
  html +=
    '<input type="number" class="form-control border-square-blue text-center no-border-right length" value="' +
    length +
    '">';
  html += '<div class="input-group-append border-square-blue"><span class="input-group-text">mm</span></div>';
  html += '</div></div><div class="col-sm-2 text-center sym-div" onclick="remove_row(this)"><div class="form-group">';
  html += '<i class="fa fa-minus-circle"></i></div></div></div></div></div>';

  $("#" + div_id).append(html);
  $("#" + div_id + " input").change(function (eve) {
    $(this).check_button_state();
  });
}

// remove a row when remove button is clicked.
function remove_row(e) {
  console.log(e.parentNode.parentNode.parentNode);
  let parent = e.parentNode.parentNode.parentNode;
  parent.parentNode.removeChild(parent);
}

// Get JSON data from quantity and length fields
function adjust_mapping_data(div_id) {
  // get dict array by using quantity_field and length_field
  let quantity_fields = $("#" + div_id + " .quantity");
  let length_fields = $("#" + div_id + " .length");

  let arr = [];

  for (let i = 0; i < quantity_fields.length; i++) {
    let quantity = quantity_fields[i].value;
    let length = length_fields[i].value / 1000;
    if (quantity && length) arr.push({ quantity: quantity, length: length });
  }
  return arr;
}

function init_mapping(div_id, ele_name) {
  let json_data = $('input[name="' + ele_name + '"]').val();
  if (json_data) {
    let data = JSON.parse(json_data);
    if (data.length > 0) {
      for (let i = 1; i < data.length; i++) {
        add_row(div_id, data[i]["quantity"], data[i]["length"]);
      }
    }
  }
}

$(document).ready(function () {
  $("#custom_length_div input").change(function (eve) {
    $(this).check_button_state();
  });
});
