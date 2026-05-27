from app.src.utils.YM import client
from yandex_music import Artist as artist, Track as track, Album as album
from app.src.utils.YM.album import Album
from app.src.utils.YM.playlist import Playlist
from app.src.utils.YM.track import Track


async def search(prompt):
    mediaItem = await client.search(prompt)

    best = getattr(mediaItem, 'best', None)
    if best and getattr(best, 'result', None) is not None:
        best_result = best.result

        if isinstance(best_result, track):
            return await Track(track_object=best_result).fetch_track()

        if isinstance(best_result, album):
            return await Album(best_result.id).fetch_album()

        if isinstance(best_result, artist):
            playlists_obj = getattr(mediaItem, 'playlists', None)
            if playlists_obj and getattr(playlists_obj, 'results', None):
                first_playlist = playlists_obj.results[0]
                if first_playlist and hasattr(first_playlist, 'uid') and hasattr(first_playlist, 'kind'):
                    return await Playlist(first_playlist.uid, first_playlist.kind).fetch_playlist()

    # fallback: first track from search results
    tracks_obj = getattr(mediaItem, 'tracks', None)
    if tracks_obj and getattr(tracks_obj, 'results', None):
        first_track = tracks_obj.results[0]
        if first_track and hasattr(first_track, 'result') and first_track.result:
            return await Track(track_object=first_track.result).fetch_track()

    return None
        