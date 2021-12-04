// Called with the results from FB.getLoginStatus().
function statusChangeCallback(response) {
    if (response.status === 'connected') {   // Logged into your webpage and Facebook.
      token = window.localStorage.getItem('fblst_628039024905744');
      if (token) {
          console.log('token found');
          let redirectURL = "https://baszl.herokuapp.com/fbtoken/" + token;
          window.location.replace(redirectURL);
      } else {
          console.log('token not found');
      }  
    } else {                                 // Not logged into your webpage or we are unable to tell.
      console.log("Not logged in.");
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

    FB.getLoginStatus(function(response) {   // Called after the JS SDK has been initialized.
      statusChangeCallback(response);        // Returns the login status.
    });

    document.querySelector(".fb-login-button").addEventListener("click", () => {
        FB.login(function(response) {
            statusChangeCallback(response);
        }, {scope: 'public_profile,email,pages_manage_posts'});
    });
}