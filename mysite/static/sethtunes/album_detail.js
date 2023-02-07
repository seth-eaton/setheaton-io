function show_song_content() {
    var songs = document.getElementById("songContent");
    var pf = document.getElementById("pitchforkContent");
        
    songs.style.display = "block";
    pf.style.display = "none";
}

function show_pf_content() {
    var songs = document.getElementById("songContent");
    var pf = document.getElementById("pitchforkContent");
        
    songs.style.display = "none";
    pf.style.display = "block";
}
