function show_albums() {
    var albums = document.getElementById("albums")
    var eps = document.getElementById("eps")
    var singles = document.getElementById("singles")
    
    if (albums !== null) { albums.style.display = "block"; }
    if (eps !== null) { eps.style.display = "none"; }
    if (singles !== null) { singles.style.display = "none"; }
}

function show_eps() {
    var albums = document.getElementById("albums")
    var eps = document.getElementById("eps")
    var singles = document.getElementById("singles")
        
    if (albums !== null) { albums.style.display = "none"; }
    if (eps !== null) { eps.style.display = "block"; }
    if (singles !== null) { singles.style.display = "none"; }
}

function show_singles() {
    var albums = document.getElementById("albums")
    var eps = document.getElementById("eps")
    var singles = document.getElementById("singles")
        
    if (albums !== null) { albums.style.display = "none"; }
    if (eps !== null) { eps.style.display = "none"; }
    if (singles !== null) { singles.style.display = "block"; }
}
