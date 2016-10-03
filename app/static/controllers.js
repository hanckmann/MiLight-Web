// On document ready
// A $( document ).ready() block.
$( document ).ready(function() {
  console.log( "ready!" );
  enableValue('');
});


// Change actions when radiobutton is clicked
$('#select-bulb input:radio').click(function() {
  if ($(this).val() === 'RGBW') {
    // console.info('RGBW selected');
    pUrl = '/milight/action_rgbw'
  } else if ($(this).val() === 'WHITE') {
    // console.info('WHITE selected');
    pUrl = '/milight/action_white'
  }
  else {
    $('#bio').text("ERROR: INVALID BULB");
  }

  $.ajax({
    url : pUrl
  }).done(function(message) {
    // console.log(JSON.stringify(message))
    populateSelect('action', JSON.parse(message))
  }).fail(function(message) {
    // console.log(JSON.stringify(message))
    $('#bio').text(JSON.stringify(message));
  });

  document.getElementById('action').disabled = false
});


// Change value input when action is selected
$('#action').change(function() {
  var action = $("#action option:selected").text();
  // console.info('Action selected')
  // console.info(action)

  if (/on|off|white|brightmode|nightmode/.test(action)) {
    // No value to provide
    document.getElementById('sel_value').value = "";
    enableValue('');
  }
  else if (action ==='brightness') {
    // 0 <= value <= 25
    document.getElementById('num_value').value = 13;
    document.getElementById('num_value').min = 0;
    document.getElementById('num_value').max = 25;
    enableValue('num_value');
  }
  else if (/brightness|increase_disco_speed|decrease_disco_speed|increase_brightness|decrease_brightness|increase_warmth|decrease_warmth/.test(action)) {
    // 1 <= value <= 30
    document.getElementById('num_value').value = 15;
    document.getElementById('num_value').min = 1;
    document.getElementById('num_value').max = 30;
    enableValue('num_value');
  }
  else if (/disco|color/.test(action)) {
    pUrl = '/milight/'.concat(action)
    $.ajax({
      url : pUrl
    }).done(function(message) {
      // console.log(JSON.stringify(message))
      populateSelect('sel_value', JSON.parse(message))
    }).fail(function(message) {
      // console.log(JSON.stringify(message))
      $('#bio').text(JSON.stringify(message));
    });
    enableValue('sel_value');
  }
  else {
    $('#bio').text("ERROR: INVALID SEL_VALUE RETURN STUFF");
  }
});

function enableValue(sel) {
  if (sel === 'num_value') {
    document.getElementById('num_value').disabled = false;
    $("#num_value_div").show();
    document.getElementById('sel_value').disabled = true;
    $("#sel_value_div").hide();
  }
  else if (sel === 'sel_value') {
    document.getElementById('num_value').disabled = true;
    $("#num_value_div").hide();
    document.getElementById('sel_value').disabled = false;
    $("#sel_value_div").show();
  }
  else {
    document.getElementById('num_value').disabled = true;
    $("#num_value_div").hide();
    document.getElementById('sel_value').disabled = true;
    $("#sel_value_div").show();
  }
}

function populateSelect(select_id, listObj) {
  var select = document.getElementById(select_id);

  // Remove all options
  $('#'.concat(select_id))
    .find('option')
    .remove()
    .end();

  for(var i = 0; i < listObj.length; i++) {
    // console.info(listObj[i]);
    var opt = document.createElement('option');
    opt.value = listObj[i];
    opt.innerHTML = listObj[i];
    select.appendChild(opt);
  }
}


// Submit the form data
function submitAsJson() {
  var JSONObject = {
    "bridge": document.getElementById("bridge").value,
    "bulb":   document.getElementById("RGBW").checked ? 'RGBW' : 'WHITE',
    "action": document.getElementById("action").value,
    "group":  document.getElementById("group").value,
    "value":  document.getElementById("num_value").value,
  };
  var JSONString = JSON.stringify(JSONObject);
  // console.info(JSONString);

  $.ajax({
    type : "POST",
    url : "/milight/json",
    data: JSONString,
    contentType: 'application/json;charset=UTF-8'
  }).done(function(message) {
    $('#bio').text(JSON.stringify(message));
  }).fail(function(message) {
    $('#bio').text(JSON.stringify(message));
  });
}

// function showValueSlider2(newValue) {
//     document.getElementById("rangeslider2").innerHTML=newValue;
// }
