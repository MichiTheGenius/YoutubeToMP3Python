import pytube
import os
from pytube import Playlist

# ansi color codes to print out colored text in the terminal
black = "\u001b[30m"
red = "\u001b[31m"
green = "\u001b[32m"
yellow = "\u001b[33m"
blue = "\u001b[34m"
magenta = "\u001b[35m"
cyan = "\u001b[36m"
white = "\u001b[37m"
reset = "\u001b[0m"


def get_playlist_urls(url):
    # make an array with all video urls in the playlist with the help of pytube
    playlist = Playlist(url)

    video_urls = playlist.video_urls

    return video_urls


def reset_color():
    print(reset)


def print_blue_text(text):
    print(f'{blue}{text}', end="")
    reset_color()


def print_red_text(text):
    print(f'{red}{text}', end="")
    reset_color()


def filter_out_correct_video(video):
    # get correct video format -> this took a lot of trying around to fine tune
    return video.streams.filter(audio_codec="mp4a.40.2", mime_type="audio/mp4").first()


def get_mp4_file(path, correct_video):
    # replace the single and double quotes with nothing from the song name as it causes errors
    default_filename = correct_video.default_filename.replace(
        "'", "").replace('"', '')
    # if the path from the user doesn't have a "/" at the end we need to add it
    if not path.endswith("/"):
        return f"{path}/{default_filename}"
    else:
        return f"{path}{default_filename}"


def make_mp3_file(path, correct_video, channel_name):
    # replace the single and double quotes with nothing from the song name as it causes errors
    default_filename = correct_video.default_filename.replace(
        ".mp4", ".mp3").replace("'", "").replace('"', '')
    channel_name = channel_name.replace("'", "").replace('"', '')
    # if the path from the user doesn't have a "/" at the end we need to add it
    if not path.endswith("/"):
        return f"{path}/{channel_name} - {default_filename}"
    else:
        return f"{path}{channel_name} - {default_filename}"


def get_path_from_file():
    # open the path file and assign a path variable the content of that file
    path = ""
    with open("path.txt", "r") as path_file:
        path = path_file.read()
    return path


def path_file_exists():
    return os.path.isfile("path.txt")


def write_path_to_file(path):
    with open("path.txt", "w") as path_file:
        path_file.write(path)


def change_path():
    new_path = ""
    if path_file_exists():
        current_path = get_path_from_file()
        new_path = input(
            f"Enter a new download path (The current one is {current_path}): ")
    else:
        new_path = input(
            f"Enter a new download path: ")

    # if the inputted path is empty we don't write it ti the file
    if new_path != "":
        write_path_to_file(new_path)


def list_path():
    if path_file_exists():
        current_path = get_path_from_file()
        print(f"The current path is {current_path}")
    else:
        print("You don't have a path file yet! Create one by entering c in the url field.")


def main():
    while True:
        playlist_url_input = input(
            "Enter playlist url(or q to quit, c to change the path, l to list the path): ")
        if playlist_url_input.lower() == 'q':
            quit()
        elif playlist_url_input.lower() == 'c':
            change_path()
            continue  # jump to start of while loop -> ask the user again what he wants to do
        elif playlist_url_input.lower() == 'l':
            list_path()
            continue
        else:
            break

    playlist_urls = get_playlist_urls(playlist_url_input)

    amount_of_videos = len(playlist_urls)
    print(f"You have {amount_of_videos} videos in your playlist")
    # first video should be 1 in youtube -> first element in array is 0 -> -1 solves the problem
    start_index = int(
        input("Enter the start index(The first video is always 1): ")) - 1

    # youtubes last video is e.g. 10 -> loop ends at 9 -> array ends at 9 -> perfect
    end_index = int(
        input(f"Enter the end index(the maximum is {amount_of_videos}): "))

    for i in range(start_index, end_index):
        # make a video out of the current url in the loop that pytube can use
        pytube_video = pytube.YouTube(playlist_urls[i])
        channel_url = pytube_video.channel_url
        channel_name = pytube.Channel(channel_url).channel_name

        # get the current download path from the text file
        download_path = get_path_from_file()
        print_blue_text(f"video is downloading to {download_path}!")

        # get the audio file out of all the options
        correct_video = filter_out_correct_video(pytube_video)

        # download that file
        correct_video.download(download_path)
        print_blue_text("finished downloading!")

        print_blue_text("converting to mp3!")

        # input filename for ffmpeg
        mp4_file = get_mp4_file(download_path, correct_video)
        # output mp3 file (replace the default .mp4 in the filename with .mp3)
        mp3_output = make_mp3_file(download_path, correct_video, channel_name)

        # command to convert mp4 to mp3 with ffmpeg. -i for input, -f for filetype, -ab for bitrate, -vn for no video
        convert_command = f"ffmpeg -i '{mp4_file}' -f mp3 -ab 192000 -vn '{mp3_output}'"

        # execute the convert command
        os.system(convert_command)

        # delete the remaining mp4 file we don't need anymore
        os.remove(mp4_file)

        print_blue_text("finished converting!")
    print_red_text(
        f"Finished downloading all of your videos! Find your tunes in the folder {download_path}!")


if __name__ == "__main__":
    main()
