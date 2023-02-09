from .models import Album

def sort_albums(raw_albums):
    albums = []
    eps = []
    singles = []

    for album in list(raw_albums):
        if 'single' in album.album_name.lower():
            singles.append(album)
        elif 'remix' in album.album_name.lower() or 'EP' in album.album_name:
            eps.append(album)
        else:
            albums.append(album)

    sorted_albums = {}
    if len(singles) > 0:
        sorted_albums.update({'singles':singles})
    else:
        sorted_albums.update({'singles':None})
    if len(eps) > 0:
        sorted_albums.update({'eps':eps})
    else:
        sorted_albums.update({'eps':None})
    if len(albums) > 0:
        sorted_albums.update({'albums':albums})
    else:
        sorted_albums.update({'albums':None})
    return sorted_albums
