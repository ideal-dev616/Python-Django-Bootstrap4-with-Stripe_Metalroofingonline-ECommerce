function buildLengthSelect() {
  try {
    var lengthSelectField = document.getElementById("length");
    var maxLength = parseFloat(document.getElementById("max_length").value);
    var minLength = parseFloat(document.getElementById("min_length").value);
    var lengthSteps = parseFloat(document.getElementById("length_steps").value);

    console.log(lengthSteps);
    console.log(maxLength);
    console.log(maxLength);

    for (let i = minLength; i <= maxLength; i += lengthSteps) {
      if (i > 0) {
        let option = document.createElement("option");
        option.text = parseFloat(i).toFixed(3);
        option.value = parseFloat(i).toFixed(3);
        lengthSelectField.add(option);
      }
    }
  } catch (err) {
    console.log("No Lengths to be built");
  }
}

$(document).ready(function () {
  buildLengthSelect();
});
