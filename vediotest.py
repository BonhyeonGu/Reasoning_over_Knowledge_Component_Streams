from pytube import YouTube

url = 'https://www.youtube.com/watch?v=C_Fc1x_aeFQ'
yt = YouTube(url)
st = yt.streams.filter(only_audio = True).first()
st.download()
caption = yt.captions.get_by_language_code('en')
caption.download(yt.title)