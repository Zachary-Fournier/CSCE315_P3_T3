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

    let fbBtn = document.querySelector(".fb-login-button")
    fbBtn.onlogin = () => {checkLoginState();}
    
    fbBtn.addEventListener("click", () => {
        FB.login(function(response) {
            console.log(response);
            if (response.status == 'connected') {   // Logged into your webpage and Facebook.
                var redirectURL = "https://baszl.herokuapp.com/fbtoken/";
                redirectURL += response.authResponse.accessToken;

                // Get the page access token
                FB.api(
                    "/" + response.authResponse.userID + "/accounts",
                    {
                        "access_token": response.authResponse.accessToken
                    },
                    function (response) {
                        console.log(response);
                        if (response && !response.error) {
                            // Get page id
                            pgToken = response.data.access_token
                            pgID = response.data.id;
                            console.log(pgToken);
                            console.log(pgID);
                            FB.api(
                                "/" + pgID + "/feed",
                                "POST",
                                {
                                    "message": "What's goin on 'ere?!?!",
                                    "access_token": "page-access-token"
                                },
                                function (response) {
                                    if (response && !response.error) {
                                        console.log(response);
                                        console.log(response.id);
                                    }
                                }
                            );
                            }
                    }
                );

                // Get name and send
                /*FB.api('/me', function(response) {
                    redirectURL += "&" + response.name;
                    window.location.replace(redirectURL);
                });*/
            } else {
                console.log("Not logged in.");
            }
        }, {scope: 'public_profile, pages_manage_posts, pages_read_engagement, pages_manage_metadata, pages_show_list'});
    });
}