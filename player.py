from colorist import Color
from time import sleep
import discord
import yt_dlp
import os



class Song:

  def __init__(self, ytUrl):
    self.ytUrl = ytUrl
    self.title = ""
    self.songUrl = ""

  def __str__(self):
    return f"{Color.BLUE}{self.title}{Color.OFF}"
  
  def update(self, title,songUrl):
    self.title = title
    self.songUrl = songUrl

class Playlist(Song):

  songList = []
  index = 1

  def __init__(self, ytUrl):
    super().__init__(ytUrl)

  def update(self, song):
    self.songList.append(song)
    self.index += 1

class Player:
  yt_opts = {
    "verbose": True,
    "format": "bestaudio",
    "lazy-playlist": True,
    "break-match-filters": True,
    "download-archive": "archive.txt",
    "paths": {"home":"/yt_archive/home","temp":"/yt_archive/temp"},
    "no-continue": True,
    "flat-playlist": True,
    "quiet": True,
    "noprogress": True,
    "yes-playlist": True,
    "playlist_items": "1",
    'cookiefile': 'cookies.txt'
  }
  ffmpegOptions = "-vn"
  beforeOptions = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
  songQueue = []
  songsPlayed = []
  playlist = []
  currentlyPlaying = {}

  def __init__(self,client):
    """takes in the discord client as a variable"""
    self.songQueue = []
    self.client = client

  def PlayNext(self,channelID,isPlaylist=None):
    if(self.currentlyPlaying == None and len(self.songQueue) > 0):
      if(isPlaylist == True):
        playlist = self.currentlyPlaying
      else:
        playlist = self.songQueue.pop()
        self.currentlyPlaying = playlist
      self.Play(playlist,channelID, isPlaylist)
  
  def Play(self, playlist,channelID,isPlaylist=None):
    vc = self.client.voice_clients[0]
    self.yt_opts.update({"playlist_items": f"{playlist.index}"})
    song = Song(playlist.ytUrl)
    with yt_dlp.YoutubeDL(self.yt_opts) as ydl:
        info = ydl.extract_info(playlist.ytUrl, download=False)
        #playlist
        if('entries' in info):
            isPlaylist = True
            if(len(info['entries']) != 0):
                print(f"{Color.YELLOW}playlist info {Color.OFF} {info['entries'][0]['url']}")
                #update song details
                song.update(info['entries'][0]['title'],info['entries'][0]['url'])
            #end of playlist
            if(song.songUrl == None):
                print(f"{Color.MAGENTA}end of playlist, skipping... {Color.OFF}")
                self.PlayNext(channelID, isPlaylist)

        #single song
        if('url' in info):
            print(f"{Color.YELLOW}song info {Color.OFF} {info['url']}")
            #update song details
            song.update(info['title'],info['url'])
            #invalid song
            if(song.songUrl == None):
                print(f"{Color.MAGENTA}invalid song, skipping... {Color.OFF}")
                self.PlayNext(channelID, isPlaylist)
        #update song to playlist
        playlist.update(song)
        # record down song url
        self.songsPlayed.append(song)
        self.client.loop.create_task(self.client.get_channel(channelID).send(f"Now playing: {song.title}"))
        #play the song and call for next song after
        vc.play(source=discord.FFmpegPCMAudio(source=song.songUrl, before_options=self.beforeOptions,options=self.ffmpegOptions),after=lambda e : self.PlayNext(channelID, isPlaylist))


  def Queue(self, ytUrl):
    """Queue the youtube URL"""
    self.playlist = Playlist(ytUrl)
    self.songQueue.append(self.playlist)
  
  def Stop(self):
    """Stops the player"""
    self.songQueue.clear()
    self.currentlyPlaying = {}