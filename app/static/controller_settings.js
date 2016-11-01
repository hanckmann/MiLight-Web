// On document ready
// A $( document ).ready() block.
$( document ).ready(function() {
  $('#div-error').hide();
  $('#div-message').hide();
});


// Submit the form data
// http://stackoverflow.com/questions/1184624/convert-form-data-to-javascript-object-with-jquery

function submitSettings() {
  var JSONString = JSON.stringify($('form').serializeObject());
  console.info(JSONString);

  $.ajax({
    type : "POST",
    url : "/milight/settings",
    data: JSONString,
    contentType: 'application/json;charset=UTF-8'
  }).done(function(message) {
    showMessage(message);
  }).fail(function(message) {
    showError(message);
  });
}

$.fn.serializeObject = function() {
  var o = {};
  var a = this.serializeArray();
  $.each(a, function() {
    if (o[this.name] !== undefined) {
      if (!o[this.name].push) {
        o[this.name] = [o[this.name]];
      }
      o[this.name].push(this.value || '');
    } else {
      o[this.name] = this.value || '';
    }
  });
  return o;
};


// General functions

function showMessage(message) {
  console.log(message)
  $('#result-oke').text(message);
  hideCountdown('#div-message', 1000);
}

function showError(message) {
  console.error(message)
  err = "ERROR: ";
  $('#result-error').text(err.concat(message));
  hideCountdown('#div-error', 5000);
}

function hideCountdown(div_name, milliseconds) {
  $(div_name).show();
  setTimeout(function() {
    $(div_name).fadeOut(1500);
  }, milliseconds, div_name);
}