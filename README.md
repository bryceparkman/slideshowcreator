# Slideshow Creator
  This program attempts to create a slideshow of a given audio file (.mp3) and its transcript, in which the images are displayed in time with the words being said. Works best with audio without much background audio or music, but music videos can be created in this fashion with some success. The images displayed are taken from Google Images. There is no guarantee these pictures are liscense free, so please make sure of that if you are utilizing this for anything other than personal use.
  
## The Requirements
  Because of all the moving parts, this program requires quite a few libraries and software.
  
  Python libraries:
  * [Lyrics Genius](https://github.com/johnwmillr/LyricsGenius)
  * [pygame](https://www.pygame.org/news)
  * [requests](https://pypi.org/project/requests/)
  * [google_images_download](https://github.com/hardikvasa/google-images-download)
  * [textblob](https://pypi.org/project/textblob/)
  
  Misc:
  * [gentle](using docker installation for Windows)](https://github.com/lowerquality/gentle)
  * [Genius API](https://genius.com/developers) (You must create an API and get a Genius client access token if using that feature)
  
## Usage
  Once everything is installed it's time to create the slideshow! Create a folder in the same directory as the script, named whatever you want. Inside the folder, include your mp3 file named ("audio.mp3"). If you are using audio that doesn't have lyrics on genius.com, also include a transcript of the audio called "transcript.txt". Also make sure your docker teminal displays "listening on port 8765" before running the script. If you already have the transcript, just run `create.py [folder_name]`, otherwise if you want to gather the lyrics from genius add the `-s` tag before the folder name. Then, you simply have to wait while your audio is analyzed and the program downloads the images, and then a video will be played for you via a pygame window. If you want to run the same video again, just rerun the program and it will recognize that all the work has already been done and instantly play.
