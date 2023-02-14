function show(view) {
    if (view === "songs") { show_song_content(); }
    else if (view === "pitchfork") { show_pf_content(); }
    else if (view === "seth") { show_seth_content(); }
}

function show_song_content() {
    var songs = document.getElementById("songContent");
    var pf = document.getElementById("pitchforkContent");
    var seth = document.getElementById("sethContent");

    if (songs !== null) { songs.style.display = "block"; }
    if (pf !== null) { pf.style.display = "none"; }
    if (seth !== null) { seth.style.display = "none"; }
}

function show_pf_content() {
    var songs = document.getElementById("songContent");
    var pf = document.getElementById("pitchforkContent");
    var seth = document.getElementById("sethContent");
        
    if (songs !== null) { songs.style.display = "none"; }
    if (pf !== null) { pf.style.display = "block"; }
    if (seth !== null) { seth.style.display = "none"; }
}

function show_seth_content() {
    var songs = document.getElementById("songContent");
    var pf = document.getElementById("pitchforkContent");
    var seth = document.getElementById("sethContent");
        
    if (songs !== null) { songs.style.display = "none"; }
    if (pf !== null) { pf.style.display = "none"; }
    if (seth !== null) { seth.style.display = "block"; }
}
