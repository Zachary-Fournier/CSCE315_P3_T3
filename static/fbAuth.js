const loginCallback = function() {
    FB.login(function(response) {
        if (response.status == 'connected') {   // Logged into your webpage and Facebook.
            var redirectURL = "https://baszl.herokuapp.com/fbandigaccess?";
            var userAccessToken = response.authResponse.accessToken;
            redirectURL += "user_access_token=" + userAccessToken;

            // Get the page access token
            FB.api(
                "/" + response.authResponse.userID + "/accounts",
                {
                    "access_token": userAccessToken
                },
                function (response) {
                    if (response && !response.error) {
                        // Get page id
                        redirectURL += "&page_access_token=" + response.data[0].access_token;
                        redirectURL += "&page_id=" + response.data[0].id;

                        // Get ig
                        FB.api('/' + response.data[0].id,
                        { 
                            "fields": "instagram_business_account",
                            "access_token": userAccessToken
                        }, 
                        function(response) {
                            redirectURL += "&instagram_id=" + response.instagram_business_account.id

                            FB.api(
                                "/" + response.instagram_business_account.id,
                                { "fields": "username"},
                                function (response) {
                                  if (response && !response.error) {
                                    console.log(response);
                                  }
                                }
                            );
                            /*
                            FB.api('/' + response.instagram_business_account.id,
                            {
                                "fields": "username",
                                "access_token": userAccessToken
                            }, 
                            function(response) {console.log(response);});
                            */

                            // Get name and send
                            /*
                            FB.api('/me', function(response) {
                                redirectURL += "&name=" + response.name;
                                window.location.replace(redirectURL);
                            });
                            */
                        });
                    }
                }
            );
        } else {
            console.log("Not logged in.");
        }
    }, {scope: 'public_profile, pages_manage_posts, pages_read_engagement, pages_manage_metadata, pages_show_list, instagram_basic, instagram_content_publish'});
}

window.fbAsyncInit = function() {
    FB.init({
      appId      : '628039024905744',
      cookie     : true,                     // Enable cookies to allow the server to access the session.
      xfbml      : true,                     // Parse social plugins on this webpage.
      version    : 'v12.0'           // Use this Graph API version for this call.
    });

    let fbBtn = document.querySelector(".fb-login-button")
    fbBtn.addEventListener("click", loginCallback);

    let igBtn = document.querySelector(".instagramButton")
    igBtn.addEventListener("click", loginCallback);
}