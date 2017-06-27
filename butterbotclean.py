import discord
import asyncio
import operator
from wordcloud import WordCloud

class Butterbot(discord.Client):
    def __init__(self):
        self.player = None
        self.in_channel = None
        self.voice = None
        self.queue = []
        self._is_paused = False
        self._play_msg = None
        self._time_played = 0
        super().__init__()
        self.loop.create_task(self._progress_bar())
    
    def _finished_playing(self):
        self.player = None
        self._time_played = 0
        if self.queue:
            print("Song finished, now playing", self.queue[0])
            ytlink = self.queue.pop(0)
            corout = self._play_song(ytlink, self.in_channel)
            fut = discord.compat.run_coroutine_threadsafe(corout, self.loop)
            try:
                fut.result()
            except:
                print("Something went wrong with running the compat coroutine")
        else:
            self._play_msg = None
        
    @asyncio.coroutine
    def _play_song(self, ytlink, channel, text_channel):
        if channel != self.in_channel:
            if self.player:
                self.player.stop()
            if self.in_channel != None:
                yield from self.voice.disconnect()
            self.voice = yield from self.join_voice_channel(channel)
            self.in_channel = channel
            
        elif self.player:
            self.player.stop()
        self.player = yield from self.voice.create_ytdl_player(ytlink, use_avconv=False, after=self._finished_playing)
        if self._play_msg:
            yield from self.edit_message(self._play_msg, "Now playing: {}\n`".format(self.player.title)+"["+"#"*20+"]`")
        self._play_msg = yield from self.send_message(text_channel, "Now playing: {}\n".format(self.player.title))
        
        self.player.start()
        
   # @asyncio.coroutine
   # def on_message_edit(self, before, after):
   #     yield from self.on_message(after)
    
    @asyncio.coroutine
    def _progress_bar(self):
        yield from self.wait_until_ready()
        while not self.is_closed:
            if self._play_msg:
                played = (int)(20*self._time_played/self.player.duration)
                rest = (int)(20-played)
                yield from self.edit_message(self._play_msg, "Now playing: {}\n`".format(self.player.title)+"["+played*"#"+rest*" "+"]`")
                self._time_played += 3
                
            yield from asyncio.sleep(3)
            
        
    @asyncio.coroutine
    def on_message(self, message):
        if message.content.startswith("!queue"):
            try:
                ytlink = message.content.split()[1]
            except IndexError:
                yield from self.send_message(message.channel, "A youtube link must follow the !play command.")
            if (not self.player or not self.player.is_playing()) and not self.queue and not self._is_paused:
                yield from self._play_song(ytlink, message.author.voice_channel, message.channel)
            else:
                self.queue.append(ytlink)
                
        elif message.content.startswith("!play"):
            try:
                ytlink = message.content.split()[1]
            except IndexError:
                yield from self.send_message(message.channel, "A youtube link must follow the !play command.")
            yield from self._play_song(ytlink, message.author.voice_channel, message.channel)
            
     
        elif message.content.startswith("!stop"):
            if self.player and self.player.is_playing():
                self.player.pause()
                self._is_paused = True
               
        elif message.content.startswith("!start"):
            if self.player and not self.player.is_playing():
                self.player.resume()
                self._is_paused = False
               
        elif message.content.startswith("!gtfo"):
            yield from self.voice.disconnect()
            if self.player:
                self.player.stop()
            self.in_channel = None
            self.voice = None
            self.player = None
            self.queue = []
                                                                                                                        
        elif message.content.startswith("!help"):
            yield from self.send_message(message.channel, "Available commands:\n!play <youtube link>\n!queue <youtube link>\n!stop\n!start\n!gtfo\n!volume [0.0,2.0]\n!favword\n!wisdom\n!wordcloud")
       
        elif message.content.startswith("!favword"):
            tmp = yield from self.send_message(message.channel, 'Calculating...')
            with open("{}.txt".format(message.author), 'r') as f:
                words = f.read().split()
                wordcount = {}
                for word in words:
                    if word in wordcount.keys():
                        wordcount[word] += 1
                    else:
                        wordcount[word] = 1
           
                sorted_words = sorted(wordcount.items(), key=operator.itemgetter(1))
                yield from self.edit_message(tmp, "@{} Your favorite word seems to be \"{}\". Used {} times since I started keeping track.".format(message.author, sorted_words[-1][0],sorted_words[-1][1]))
       
        elif message.content.startswith("!volume"):
            try:
                volume = message.content.split()[1]
            except IndexError:
                yield from self.send_message(message.channel, "The volume command must be followed by a value between 0.0 and 1.0")
            if not self.player:
                yield from self.send_message(message.channel, "Nothing is currently playing.")
                print(self.player)
            else:
                try:
                    self.player.volume = float(volume)
                except:
                    yield from self.send_message(message.channel, "Could not alter volume because of your stupid ass input.")
           
       
        elif message.content.startswith("!whatis bradley"):
            yield from self.send_message(message.channel, "Bradley: a fucking cunt.")
        
        elif message.content.startswith("!wisdom"):
            if "{}".format(message.author) == "Rin#3028":
                yield from self.send_message(message.channel, "You should probably buy PUBG, also I get this arcane tingling from you. This strange sensation of utter cuntery. Are you, perchance, a massive cock?")
            elif "{}".format(message.author) == "Tekoppen#3344" or "{}".format(message.author) == "Youthius#0128":
                yield from self.send_message(message.channel, "Oh, dearest {} I sense you have a friend, seperated from you by a long distance. This friend needs counseling, for he is refusing to make a purchase which will greatly improve his life.".format(str(message.author)[:-5]))
            else:
                print("-{}-".format(message.author))
                yield from self.send_message(message.channel, "I have no wisdom for you at this time, my child.")
                
        elif message.content.startswith("!PerIsAFuckbag"):
            if "{}".format(message.author) == "Rin#3028":
                yield from self.send_message(message.channel, "http://store.steampowered.com/app/578080/PLAYERUNKNOWNS_BATTLEGROUNDS/")
        
        elif message.content.startswith("!wordcloud"):
            author = message.author
            try:
                with open("{}.txt".format(author), 'r') as f:
                    words = f.read()
                    wordcloud = WordCloud(width=1024, height=768).generate(words)
                    image = wordcloud.to_image()
                    image.save('test.jpg')
                    yield from self.send_file(message.channel,fp='test.jpg')
            except:              
                yield from self.send_message(message.channel, "Sorry, couldn't generate the cloud. Probably because I've not got enough words recorded from you.")
        
        else:
            author = message.author
            with open("{}.txt".format(author), 'a') as f:
                for word in message.content.split():
                    try:
                        f.write(word+"\n")
                    except:
                        pass
    @asyncio.coroutine
    def on_ready(self):
        print("Logged in as: ", self.user.name)
        print(self.user.id)
        print("----------")
        
if __name__ == "__main__":
    bot = Butterbot()
    bot.run('MjYxNzYyODgwNzIwODYzMjMy.Cz54hg.x9WpKFMGjHASFrxS3Myh_EDJ9Kc')
