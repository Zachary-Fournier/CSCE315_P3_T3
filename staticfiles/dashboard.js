function changeToUser() {
    // document.getElementById("5").textContent = "@THEIRTWITTERHANDLE";
    // document.getElementById("6").textContent = "@THEIRINSTAGRAMHANDLE";
    // document.getElementById("7").textContent = "@THEIRFACEBOOKHANDLE";

    // document.getElementById("10").textContent = "FACEBOOK POSTS NUMBER";
    // document.getElementById("12").textContent = "INSTAGRAM POSTS NUMBER";
    // document.getElementById("14").textContent = "TWITTER POSTS NUMBER";

}

window.onload = changeToUser;

function switchTheme() {
    var bg = document.body;
    bg.classList.toggle("dark-mode");

    var el = document.getElementById("50");
    var style = window.getComputedStyle(el, null).getPropertyValue('background-color');
    if (style == "rgb(255, 255, 255)") {
        for (let i = 50; i < 57; i++) {
            var el = document.getElementById(i.toString());
            var style = window.getComputedStyle(el, null).getPropertyValue('background-color');
            el.style.backgroundColor = "#323335";
        }
        var el = document.getElementById("postText");
        var style = window.getComputedStyle(el, null).getPropertyValue('background-color');
        el.style.color = "white";
        el.style.backgroundColor = "#323335";

        var el = document.getElementById("themesettingcolor");
        var style = window.getComputedStyle(el, null).getPropertyValue('color');
        el.style.color = "white";

        var el = document.getElementById("fontsettingcolor");
        var style = window.getComputedStyle(el, null).getPropertyValue('color');
        el.style.color = "white";

        return;
    } 


    for (let i = 50; i < 57; i++) {
        var el = document.getElementById(i.toString());
        var style = window.getComputedStyle(el, null).getPropertyValue('background-color');
        el.style.backgroundColor = "white";
    }
    var el = document.getElementById("postText");
    var style = window.getComputedStyle(el, null).getPropertyValue('background-color');
    el.style.backgroundColor = "white";
    el.style.color = "black";

    var el = document.getElementById("themesettingcolor");
    var style = window.getComputedStyle(el, null).getPropertyValue('color');
    el.style.color = "black";

    var el = document.getElementById("fontsettingcolor");
    var style = window.getComputedStyle(el, null).getPropertyValue('color');
    el.style.color = "black";
}

function post() {
    var words = document.getElementById("postText").value;

    const file = document.querySelector('input[type=file]').files[0];
    const reader = new FileReader();
    reader.addEventListener("load", function () {
        console.log(reader.result);
        document.getElementById('imagePreview').src = reader.result;
    }, false);

    if (file) {
        reader.readAsDataURL(file);
    }

    var el = document.getElementById("loader");
    var style = window.getComputedStyle(el, null).getPropertyValue('border');
    el.style.border = "0px solid #f3f3f3";
    var style = window.getComputedStyle(el, null).getPropertyValue('border-top');
    el.style.borderTop = "0px solid #3498db"

    alert("Your post(s) have been made!");
    if (document.getElementById('fbToggle')) {

    }
    if (document.getElementById('twitterToggle')) {
        
    }
    if (document.getElementById('instagramToggle')) {
        
    }
}

function changeLoader() {
    var el = document.getElementById("loader");
    var style = window.getComputedStyle(el, null).getPropertyValue('border');
    el.style.border = "16px solid #f3f3f3";

    var style = window.getComputedStyle(el, null).getPropertyValue('border-top');
    el.style.borderTop = "16px solid #3498db"
}

function loadFile(file) {
    var input = file.target;
    var reader = new FileReader();

    reader.onload = function() {
        var dataURL = reader.result;
        var outputElement = document.getElementById('imagePreview');
        output.src = dataURL;
    }
    reader.readAsDataURL(input.files[0]);
};

function changeFontSize() {
    var el = document.getElementById("1");
    var style = window.getComputedStyle(el, null).getPropertyValue('font-size');
    if (parseFloat(style) == 24) {
        for (let i = 1; i < 20; i++) {
            var el = document.getElementById(i.toString());
            var style = window.getComputedStyle(el, null).getPropertyValue('font-size');
            var fontSize = parseFloat(style);
            el.style.fontSize = (fontSize + 10) + 'px';
        }
    }

    for (let i = 1; i < 20; i++) {
        var el = document.getElementById(i.toString());
        var style = window.getComputedStyle(el, null).getPropertyValue('font-size');
        var fontSize = parseFloat(style);
        el.style.fontSize = (fontSize - 10) + 'px';
    }
}

function resetImage() {
    document.getElementById('uploadButton').value = null;
    document.getElementById('imagePreview').src = "";
}