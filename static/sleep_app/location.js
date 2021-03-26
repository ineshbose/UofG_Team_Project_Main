// from https://developers.google.com/web/fundamentals/native-hardware/user-location/
window.onload = function() {

  function sendForm(form){
  httpRequest = new XMLHttpRequest();
    httpRequest.open('POST', "");

//  taken from https://docs.djangoproject.com/en/3.1/ref/csrf/
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

//  is this the best way to do this? Partly based on https://docs.djangoproject.com/en/3.0/ref/csrf/
    if (!this.crossDomain){
        httpRequest.setRequestHeader("X-CSRFToken", csrftoken, 'Content-Type', 'application/x-www-form-urlencoded');
    }

    httpRequest.send(form)
  }


  var geoSuccess = function(position) {
    alert(gettext("Your GPS location has been recorded. Please enter your location into the search bar as well."));
    var startPos;
    startPos = position;

    var form = new FormData();
    form.append('lat',encodeURIComponent(startPos.coords.latitude))
    form.append('long', encodeURIComponent(startPos.coords.longitude))

    sendForm(form);
  };


  var geoError = function(){
    //making the data have the same structure regardless of error status makes handling it in the view easier
    var form = new FormData();
    form.append('lat',encodeURIComponent("no-permission"));
    form.append('long', encodeURIComponent("no-permission"));
    sendForm(form);
  }


  navigator.geolocation.getCurrentPosition(geoSuccess, geoError);
};

