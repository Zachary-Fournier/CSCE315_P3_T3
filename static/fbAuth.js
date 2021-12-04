window.fbAsyncInit = function() {
    FB.init({
      appId      : '628039024905744',
      cookie     : true,                     // Enable cookies to allow the server to access the session.
      xfbml      : true,                     // Parse social plugins on this webpage.
      version    : 'v12.0'           // Use this Graph API version for this call.
    });

    let fbBtn = document.querySelector(".fb-login-button")

    fbBtn.addEventListener("click", () => {
        FB.login(function(response) {
            console.log("Shouldn't be here.");
        }, {scope: 'public_profile,email,pages_manage_posts'});
    });
}