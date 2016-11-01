// On document ready
// A $( document ).ready() block.
$( document ).ready(function() {
  bridge = document.getElementById("bridge").value;
  bulb = 'RGBW';
  if (document.getElementById("WHITE").checked) {
    bulb = 'WHITE';
  }
  updateGroupNames(bridge, bulb);
  updateActions(bulb);
  enableValue('');
  $('#div-error').hide();
  $('#div-message').hide();
});


// Change group-names and actions when radiobutton is clicked
$('#select-bulb input:radio').click(function() {
  bridge = document.getElementById("bridge").value;
  bulb = $(this).val();
  updateGroupNames(bridge, bulb);
  updateActions(bulb);
});

function updateGroupNames(bridge, bulb) {
  pUrl = '/milight/settings/' + bridge;
  if (bulb !== 'RGBW' && bulb !== 'WHITE') {
    showError("Invalid bulb");
    return;
  }

  $.ajax({
    url : pUrl
  }).done(function(message) {
    // console.log(JSON.stringify(message))
    var setting = JSON.parse(message);
    var setting_bulb = setting[bulb.toLowerCase()];
    selectValue = ['ALL', '1', '2', '3', '4'];
    selectInnerHTML = [setting_bulb['group'], setting_bulb['group-1'], setting_bulb['group-2'], setting_bulb['group-3'], setting_bulb['group-4'] ];
    populateSelect('group', selectValue, selectInnerHTML)
    showMessage(message);
  }).fail(function(message) {
    // console.log(JSON.stringify(message))
    showError(message);
  });

  document.getElementById('action').disabled = false
}

function updateActions(bulb) {
  if (bulb === 'RGBW') {
    // console.info('RGBW selected');
    pUrl = '/milight/action_rgbw'
  }
  else if (bulb === 'WHITE') {
    // console.info('WHITE selected');
    pUrl = '/milight/action_white'
  }
  else {
    showError("Invalid bulb");
  }

  $.ajax({
    url : pUrl
  }).done(function(message) {
    // console.log(JSON.stringify(message))
    populateSelect('action', JSON.parse(message), JSON.parse(message))
    showMessage(message);
  }).fail(function(message) {
    // console.log(JSON.stringify(message))
    showError(message);
  });

  document.getElementById('action').disabled = false
}


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
  else if (action ==='disco') {
    pUrl = '/milight/'.concat(action)
    $.ajax({
      url : pUrl
    }).done(function(message) {
      // console.log(JSON.stringify(message))
      populateSelect('sel_value', JSON.parse(message), JSON.parse(message))
    }).fail(function(message) {
      // console.log(JSON.stringify(message))
      showError(message);
    });
    enableValue('sel_value');
  }
  else if (action ==='color') {
    pUrl = '/milight/'.concat(action)
    $.ajax({
      url : pUrl
    }).done(function(message) {
      // console.log(JSON.stringify(message))
      populateSelect('sel_value', JSON.parse(message), JSON.parse(message), is_color=true)
    }).fail(function(message) {
      // console.log(JSON.stringify(message))
      showError(JSON.stringify(message));
    });
    enableValue('sel_value');
  }
  else {
    showError("Invalid sel_value return stuff");
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

function populateSelect(select_id, selectValue, selectInnerHTML, is_color=false) {
  var select = document.getElementById(select_id);

  // Remove all options
  $('#'.concat(select_id))
    .find('option')
    .remove()
    .end();

  for(var i = 0; i < selectValue.length; i++) {
    // console.info(selectValue[i]);
    var opt = document.createElement('option');
    if (is_color === true) {
        attributedata = 'background: ';
        opt.setAttribute('style', attributedata.concat(selectValue[i]));
    }
    opt.value = selectValue[i];
    opt.innerHTML = selectInnerHTML[i];
    select.appendChild(opt);
  }
}

function outputUpdate(vol) {
  document.querySelector('#set_value').value = vol;
}


// Submit the form data
function submitForm() {
  bridge = document.getElementById("bridge").value;
  bulb = document.getElementById("RGBW").checked ? 'RGBW' : 'WHITE';
  action = document.getElementById("action").value;
  group = document.getElementById("group").value;
  value = getCurrentValue();
  submitAsJson(bridge, bulb, action, group, value);
}


// Quick-Action functions

function everythingOn() {
  for (var i = 0; i < document.getElementById("bridge").length; ++i) {
    bridge = document.getElementById("bridge")[i].value
    submitAsJson(bridge, 'WHITE', 'ON', 'ALL', null)
    submitAsJson(bridge, 'RGBW', 'ON', 'ALL', null)
  }
}

function everythingOff() {
  for (var i = 0; i < document.getElementById("bridge").length; ++i) {
    bridge = document.getElementById("bridge")[i].value
    submitAsJson(bridge, 'WHITE', 'OFF', 'ALL', null)
    submitAsJson(bridge, 'RGBW', 'OFF', 'ALL', null)
  }
}


// MiLight interaction (JSON based)

function submitAsJson(bridge, bulb, action, group, value) {
  var JSONObject = {
    "bridge": bridge,
    "bulb":   bulb,
    "action": action,
    "group":  group,
    "value":  value,
  };
  var JSONString = JSON.stringify(JSONObject);
  // console.info(JSONString);

  $.ajax({
    type : "POST",
    url : "/milight/json",
    data: JSONString,
    contentType: 'application/json;charset=UTF-8'
  }).done(function(message) {
    showMessage(message);
  }).fail(function(message) {
    showError(message);
  });
}

function getCurrentValue() {
  if (!document.getElementById('num_value').disabled) {
    // Return num_value
    return document.getElementById("num_value").value
  }
  if (!document.getElementById('sel_value').disabled) {
    // Return sel_value
    return $("#sel_value option:selected").text()
  }
  // In all other cases return an empty string
  return ""
}


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

function getCurrentValue() {
  if (!document.getElementById('num_value').disabled) {
    // Return num_value
    return document.getElementById("num_value").value
  }
  if (!document.getElementById('sel_value').disabled) {
    // Return sel_value
    return $("#sel_value option:selected").text()
  }
  // In all other cases return an empty string
  return ""
}

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