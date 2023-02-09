function showDynamicPicks() {
    var container = document.getElementById("thumbnails");
    var thumbnails = document.getElementsByClassName("thumbnail");
    var pickcount = thumbnails.length;

    var cont_width = container.offsetWidth;
    var num_in_row = Math.floor(cont_width / 90);
    var leftover = pickcount % num_in_row;
    console.log(leftover);

    for (let i = 0; i < pickcount; i++) {
        thumbnails[i].style.display = "inline-block";
    }

    var counter = pickcount - 1;
    for (let i = 0; i < leftover; i++) {
        thumbnails[counter].style.display = "none";
        counter--;
    }
}
