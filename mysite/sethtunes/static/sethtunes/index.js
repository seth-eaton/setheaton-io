function showDynamicThumbnails() {
    var container = document.getElementById("thumbnails")
    var thumbnails = document.getElementsByClassName("thumbnail")
    
    var cont_width = container.offsetWidth;
    var num_in_row = Math.floor(cont_width / 90);
    var leftover = 400 % num_in_row;
    console.log(leftover);

    for (let i = 0; i < 400; i++) {
        thumbnails[i].style.display = "inline-block";
    }

    var counter = 399;
    for (let i = 0; i < leftover; i++) {
        thumbnails[counter].style.display = "none";
        counter--;
    }
}
