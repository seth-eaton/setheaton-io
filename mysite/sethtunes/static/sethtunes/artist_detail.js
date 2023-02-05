function show_albums() {
    var albums = document.getElementById("albums")
    var eps = document.getElementById("eps")
    var singles = document.getElementById("singles")
        
    albums.style.display = "block";
    eps.style.display = "none";
    singles.style.display = "none";
}

function show_eps() {
    var albums = document.getElementById("albums")
    var eps = document.getElementById("eps")
    var singles = document.getElementById("singles")
        
    albums.style.display = "none";
    eps.style.display = "block";
    singles.style.display = "none";
}

function show_singles() {
    var albums = document.getElementById("albums")
    var eps = document.getElementById("eps")
    var singles = document.getElementById("singles")
        
    albums.style.display = "none";
    eps.style.display = "none";
    singles.style.display = "block";
}
