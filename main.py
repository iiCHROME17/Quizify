
from spotipy.oauth2 import SpotifyOAuth
from fuzzywuzzy import fuzz
import requests
import re
import random
import spotipy



class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_url, scope="user-top-read"):
        # Initialize OAuth for Spotify
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_url,
            scope=scope
        ))

    def get_top_tracks(self, range, term):
        # Get the user's top tracks
        results = self.sp.current_user_top_tracks(time_range=range, limit=term)
        return results

    def get_random_song(self):
        # Get a random song from the user's top tracks
        results = self.get_top_tracks('long_term', 50)
        random_song = random.choice(results['items'])
        song = [random_song['name'], random_song['artists'][0]['name']]
        return song


class LyricsClient:
    def __init__(self):
        self.base_url = "https://api.lyrics.ovh/v1/"

    def strip_all_empty_lines(self, data):
        # Get a song and remove all lines with no text
        lines = data.splitlines()

        # Filter out [] Lines and empty ones
        stripped = [
            line for line in lines
            if line.strip() and not re.match(r'^\[.*?\]$', line.strip())
        ]
        # Join the remaining lines back into a single string with line breaks
        result = "\n".join(stripped)
        return result

    def get_lyrics(self, artist, song):
        # Get the lyrics of a song
        url = f"{self.base_url}{artist}/{song}"
        response = requests.get(url)
        data = response.json()

        if 'lyrics' in data:
            #strip the data of the line with the song title (includes "Paroles de la chanson")
            lines = data['lyrics'].split("\n")
            cleaned_lyrics = [line for line in lines if not line.startswith("Paroles de la chanson")]
            cleaned_lyrics = "\n".join(cleaned_lyrics)
            return cleaned_lyrics
        else:
            return "Lyrics missing"

    def get_random_line(self, lyrics):
        # Get a random line from the lyrics
        lines = lyrics.split("\n")
        random_line = random.choice(lines)
        return random_line

    def match_lyrics(self, lyrics, guess):
        # Match the lyrics with the guess
        bool = False
        ratio = fuzz.ratio(lyrics.lower(), guess.lower())
        if ratio > 65:
            bool = True
        return bool


class GameClient:
    def __init__(self, score, player_name, mode):
        self.score = score
        self.player_name = player_name
        self.mode = mode

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score





    def init_game(self):
        # Initialize the game
        self.score = 0
        self.mode = ''
        self.player_name = input("Enter your name: ")
        self.begin_play()

    def begin_play(self):
        # Welcome message to the game
        print(f"Welcome {self.player_name}! Let's play the game!")
        print("In this game, you'll need to guess the songs of the top tracks from your friend's Spotify.")

        while self.mode not in ['1', '2', '3']:
            print("Which mode would you like to play?\n1. Lyric Guesser\n2. Mix and Match\n3. Quit")
            self.mode = input("Enter the number of the mode you'd like to play: ")

        if self.mode == '1':
            self.play_mode_1()
        elif self.mode == '2':
            self.play_mode_2()
        elif self.mode == '3':
            exit()

    def play_mode_1(self):
        # Play the game in mode 1
        count = 0
        max_songs = 10
        used_songs = []  # List to store songs that have been used

        #User will be given a song's lyrics and they'll need to guess the song
        #User will have 3 hints, but each hint will reduce the score

        # Define scores based on the number of hints used
        hint_scores = [30, 20, 10, 5]

        print("Mode 1: Lyric Guesser")
        print("You will be given a song's lyrics and you'll need to guess the song.")
        print("You will have 3 chances to guess the song.")
        print("Let's start the game!\n")

        while count < max_songs:
            # Get a random unused song
            while True:
                currentquizsong = spotify_client.get_random_song()
                song_key = f"{currentquizsong[0]} - {currentquizsong[1]}"
                if song_key not in used_songs:
                    used_songs.append(song_key)  # Mark this song as used
                    break

            currentquizlyrics = lyrics_client.get_lyrics(currentquizsong[1], currentquizsong[0])
            currentquizlyrics = lyrics_client.strip_all_empty_lines(currentquizlyrics)

            if currentquizlyrics == "Lyrics missing":
                continue

            #print(currentquizlyrics)

            hints_used = 0
            current_lyric_line = ""
            while current_lyric_line == "":
                current_lyric_line = lyrics_client.get_random_line(currentquizlyrics)
            print(f"Lyrics: {current_lyric_line}")

            # Allow the user to ask for another line of lyrics
            while hints_used < 3:
                hint_prompt = input("Do you want another line? (Y/N): ").upper()
                if hint_prompt == 'Y':
                    print(f"Lyrics: {lyrics_client.get_random_line(currentquizlyrics)}")
                    hints_used += 1
                else:
                    break

            guess = input("Enter the name of the song: ")
            attempt = lyrics_client.match_lyrics(currentquizsong[0], guess)

            if attempt:

                print("Correct!")
                print(f"+ {hint_scores[hints_used]}")
                # Use the number of hints used to get the score
                if hints_used < len(hint_scores):
                    self.score += hint_scores[hints_used]
                else:
                    self.score += hint_scores[-1]  # In case hints_used is more than 3
            else:
                print("Incorrect!")
                print(f"Correct answer was: {currentquizsong[0]} - {currentquizsong[1]}")

            count += 1

        print(f"Good Game, {self.player_name}! Your score is {self.score}/{max_songs * 30}.")
        print("Thank you for playing!")

        exit_input = ''
        while exit_input not in ['X', 'P']:
            print("Exit or Play again?")
            exit_input = input("Enter 'X' to exit or 'P' to open menu: ").upper()
            if exit_input == 'X':
                return
            elif exit_input == 'P':
                self.init_game()  # Restart the game

    def play_mode_2(self):
        # Play the game in mode 2

        max_songs = 10
        used_songs = []  # List to store songs that have been used
        used_artists = set()  # Set to store artists that have been used

        print("Mode 2: Mix and Match")
        print("You will be given a list of songs and artists, you'll need to match the song with the artist.")
        print("Let's start the game!\n")

        song_list = []
        artist_list = []

        while len(song_list) < max_songs:
            currentquizsong = spotify_client.get_random_song()
            song_key = f"{currentquizsong[0]} - {currentquizsong[1]}"
            artist = currentquizsong[1]

            # Ensure the artist has not already been used
            if song_key not in used_songs and artist not in used_artists:
                used_songs.append(song_key)
                used_artists.add(artist)  # Add the artist to the used list
                song_list.append(currentquizsong[0])
                artist_list.append(artist)

        shuffled_artist_list = random.sample(artist_list, len(artist_list))


        print("\nArtists:")
        for idx, artist in enumerate(shuffled_artist_list):
            print(f"{chr(65 + idx)}. {artist}")

        correct_matches = 0

        for idx, song in enumerate(song_list):
            artist_input = input(f"Enter the letter of the artist for song '{song}': ").upper()
            correct_artist_index = shuffled_artist_list.index(artist_list[idx])
            correct_letter = chr(65 + correct_artist_index)

            if artist_input == correct_letter:
                print("Correct!")
                correct_matches += 1
                self.score += 30
            else:
                print(f"Incorrect! The correct artist was {artist_list[idx]} ({correct_letter})")

        print(f"\nGood Game, {self.player_name}! Your score is {self.score}/{max_songs * 30}.")
        print("Thank you for playing!")

        exit_input = ''
        while exit_input not in ['X', 'P']:
            print("Exit or Play again?")
            exit_input = input("Enter 'X' to exit or 'P' to open menu: ").upper()
            if exit_input == 'X':
                return
            elif exit_input == 'P':
                self.init_game()


# Main
if __name__ == "__main__":
    file =open("cred.csv")
    #create credentials array, use each line as a credential
    credentials = file.readlines()

    for i in range(len(credentials)):
        credentials[i] = credentials[i].strip()

    # Spotify API credentials use csv file
    SPOTIPY_CLIENT_ID =  credentials[0]
    SPOTIPY_CLIENT_SECRET = credentials[1]
    SPOTIPY_CLIENT_REDIR = credentials[2]

    # Class instances
    spotify_client = SpotifyClient(client_id=SPOTIPY_CLIENT_ID,
                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                   redirect_url=SPOTIPY_CLIENT_REDIR)

    lyrics_client = LyricsClient()

    game_client = GameClient(0, "", "")
    game_client.init_game()
