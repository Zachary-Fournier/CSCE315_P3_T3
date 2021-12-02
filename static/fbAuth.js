// Testing Graph API after login.  See statusChangeCallback() for when this call is made.
function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
      console.log('Successful login for: ' + response.name);
      document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
    });
}

// Called with the results from FB.getLoginStatus().
function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);                   // The current login status of the person.
    if (response.status === 'connected') {   // Logged into your webpage and Facebook.
      testAPI();
      token = window.localStorage.getItem('fblst_628039024905744');
      if (token) {
          console.log('token found');
          let redirectURL = "https://baszl.herokuapp.com/fbtoken/" + token;
          window.location.replace(redirectURL);
      } else {
          console.log('token not found');
      }  
    } else {                                 // Not logged into your webpage or we are unable to tell.
      console.log("Login failed");
    }
}

// Called when a person is finished with the Login Button.
function checkLoginState() {
    FB.getLoginStatus(function(response) {   // See the onlogin handler
      statusChangeCallback(response);
    });
}


window.fbAsyncInit = function() {
    FB.init({
      appId      : '628039024905744',
      cookie     : true,                     // Enable cookies to allow the server to access the session.
      xfbml      : true,                     // Parse social plugins on this webpage.
      version    : 'v12.0'           // Use this Graph API version for this call.
    });
}