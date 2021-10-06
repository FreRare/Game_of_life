import statistics
import functools
import time


def rs(function):
    @functools.wraps(function)
    def wrapper_runtime_stopper(*args, **kwargs):
        start_time = time.perf_counter()
        ret_value = function(*args, **kwargs)
        stop_time = time.perf_counter()
        elapsed_time = stop_time - start_time
        print(f"The {function} function's runtime was: {elapsed_time:0.4f} seconds.")
        return ret_value
    return wrapper_runtime_stopper


class Playlist(object):
    def __init__(self, length: int = 0, musics: list = None):
        if isinstance(length, int):
            self.length = length
        if isinstance(musics, list) and isinstance(musics[0], dict):
            self.musics = musics
        else:
            self.musics = None

    @rs
    def read_in_musics(self, filename: str):
        if not isinstance(filename, str):
            print("Invalid filename!")
            return
        if self.musics is None:
            self.musics = []
        with open(filename, "r") as f:
            row = f.readline()
            while row:
                track = row.split(";")
                music = dict()
                music["artist"] = str(track[0])
                music["title"] = str(track[1])
                music["style"] = str(track[2])
                music["length"] = int(track[3])
                self.musics.append(music)
                row = f.readline()

    def total_length(self):
        for track in self.musics:
            self.length += track.get("length")
        minute = self.length // 60
        second = self.length % 60
        with open("total_length.txt", "w") as h:
            h.write(f"The total length of the playlist is: {minute} minute(s), {second} second(s)\n")

    @rs
    def longest_rock(self):

        longest = next((track for track in self.musics if track["length"] == max((map(lambda track: track["length"] if track["style"] == "rock" else 0, self.musics))) and track["style"] == "rock"), None)
        if longest is None:
            raise ValueError()
        with open("longest_rock.txt", "w") as lr:
            lr.write(longest["title"] + "\n")

    @rs
    def favourite_style(self):
        style = statistics.mode(map(lambda track: track["style"], self.musics))
        with open("fav.txt", "w") as fav:
            fav.write(style + "\n")

    @rs
    def list_by_artist(self, artist: str):
        if not isinstance(artist, str):
            print(f"Error! Invalid artist name: {artist}")
            return
        if next((track for track in self.musics if track["artist"].lower() == artist.lower()), None) is None:
            print(f"Artist not found! ({artist})")
            return
        with open(artist.lower().replace(" ", "_") + "_songs.txt", "w") as lbs:
            for track in self.musics:
                if track["artist"].lower() == artist.lower():
                    lbs.write(";".join(str(t) for t in track.values()) + "\n")


def main():
    playlist1 = Playlist()
    playlist1.read_in_musics("playlist.csv")
    playlist1.total_length()
    playlist1.longest_rock()
    playlist1.favourite_style()
    playlist1.list_by_artist("powerwolf")


if __name__ == "__main__":
    main()
