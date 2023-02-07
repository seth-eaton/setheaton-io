function showDynamicThumbnails() {
    var container = document.getElementById("thumbnails")
    var thumbnails = document.getElementsByClassName("thumbnail")
    cont_width = container.offsetWidth;
    num_in_row = Math.floor(cont_width / 90);
    leftover = 400 % num_in_row;
    console.log(leftover);

    for (let i = 350; i < 400; i++) {
        thumbnails[i].style.display = "inline-block";
    }

    counter = 399;
    for (let i = 0; i < leftover; i++) {
        thumbnails[counter].style.display = "none";
        counter--;
    }
}
