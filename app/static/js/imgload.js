document.getElementById("file").onchange = function () {
    var reader = new FileReader();

    reader.onload = function (e) {
        document.getElementById("img").src = e.target.result;
    };

    reader.readAsDataURL(this.files[0]);
};