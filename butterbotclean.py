import discord
import asyncio
import operator
import buttertrivia
from wordcloud import WordCloud

class Butterbot(discord.Client):
    def __init__(self):
        self.cancermode = False
        self.running = False
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
        corout = self.edit_message(self._play_msg, "Now playing: {}\n`".format(self.player.title)+"["+20*"#"+"]`")
        fut = discord.compat.run_coroutine_threadsafe(corout, self.loop)
        try:
            fut.result()
        except:
            print("Something went wrong with running the compat coroutine")
            
        self.player = None
        self._time_played = 0
        self._play_msg = None

        if self.queue:
            ytlink, channel = self.queue.pop(0)
            corout = self._play_song(ytlink, self.in_channel, channel)
            fut = discord.compat.run_coroutine_threadsafe(corout, self.loop)
            try:
                fut.result()
            except:
                print("Something went wrong with running the compat coroutine")
        
    @asyncio.coroutine
    def _play_song(self, ytlink, channel, text_channel):
        self._time_played = 0
        self._play_msg = None
        
        if channel != self.in_channel:
            if self.player:
                self.player.stop()
            if self.in_channel != None:
                yield from self.voice.disconnect()
            self.voice = yield from self.join_voice_channel(channel)
            self.in_channel = channel
        elif self.player:
            self.player.stop()
        self.player = yield from self.voice.create_ytdl_player(ytlink, use_avconv=False, after=self._finished_playing, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 3") 
        self._play_msg = yield from self.send_message(text_channel, "Now playing: {}\n".format(self.player.title))
            
        self.player.start()

    #Precious precious hijack command, dont remove!! //BatRiderTheGreat
    @asyncio.coroutine
    def _hijack_song(self, ytlink, text_channel):
        self.player = yield from self.voice.create_ytdl_player(ytlink, use_avconv=False, after=self._finished_playing, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 3")
        self._play_msg = yield from self.send_message(text_channel, "Now playing: {}\n".format(self.player.title))
        self.player.start()
    

   # @asyncio.coroutine
   # def on_message_edit(self, before, after):
   #     yield from self.on_message(after)
    

    @asyncio.coroutine
    def _progress_bar(self):
        yield from self.wait_until_ready()
        while not self.is_closed:
            if self._play_msg and self.player:
                try:
                    played = (int)(20*self._time_played/self.player.duration)
                    rest = (int)(20-played)
                    self._time_played += 3
                    if self._time_played > self.player.duration:
                        played = 20
                        rest = 0
                    yield from self.edit_message(self._play_msg, "Now playing: {}\n`".format(self.player.title)+"["+played*"#"+rest*" "+"]`")
                except:
                    pass
            yield from asyncio.sleep(3)
    

    @asyncio.coroutine
    def on_message(self, message):
        if(self.running):
            answer = message.content
            if(buttertrivia.check_answer(answer)):
                buttertrivia.give_score(str(message.author)[:-5])
                if(self.cancermode):
                    yield from self._play_song("https://www.youtube.com/watch?v=twyWHrHWq9E", message.author.voice_channel, message.channel)
                yield from self.send_message(message.channel, "Correct!\n\nCurrent standings:\n" + buttertrivia.print_score()) 
                if(buttertrivia.check_if_more_questions()):
                    yield from self.send_message(message.channel, " \n" + buttertrivia.get_question())
                else:
                    self.running = False
                    if(self.cancermode):
                        yield from self._play_song("https://www.youtube.com/watch?v=UdLagrOvYII", message.author.voice_channel, message.channel)
                    buttertrivia.update_highscore()
                    yield from self.send_message(message.channel, "Trivia is over!\nThe final standings are:\n" + buttertrivia.print_score() + "\nCongratulations to: " + buttertrivia.get_winner())

        if message.content.startswith("!queue"):
            try:
                ytlink = message.content.split()[1]
            except IndexError:
                yield from self.send_message(message.channel, "A youtube link must follow the !play command.")
            if (not self.player or not self.player.is_playing()) and not self.queue and not self._is_paused:
                yield from self._play_song(ytlink, message.author.voice_channel, message.channel)
            else:
                self.queue.append((ytlink,message.channel))
                
        elif message.content.startswith("!play"):
            try:
                ytlink = message.content.split()[1]
            except IndexError:
                yield from self.send_message(message.channel, "A youtube link must follow the !play command.")
            yield from self._play_song(ytlink, message.author.voice_channel, message.channel)
        elif message.content.startswith("!hijack"):
            ytlink = message.content.split()[1]
            yield from self._hijack_song(ytlink, message.channel)
        elif message.content.startswith("!overwhelmed"):
            yield from self._play_song("https://cdn.discordapp.com/attachments/134346894464778240/329772485660901380/vs_nbarbam2_help.wav", message.author.voice_channel, message.channel)

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
            yield from self.send_message(message.channel, "Available commands:\n!play <youtube link>\n!queue <youtube link>\n!stop\n!start\n!gtfo\n!volume [0.0,2.0]\n!favword\n!wisdom\n!wordcloud\n!trivia <trivia>\n!trivialist\n!triviahighscore\n!triviaadd <trivia> <question> <answer1> <answer2> ...\n!triviacancermode\n!triviastop\n!triviaquestions <trivia>\n!triviaremovequestion <trivia> <index>\n!triviadelete <trivia>")
       
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
        
        #Wow, someone speaks truth here!! //BatRiderTheGreat
        elif message.content.startswith("!whatis gw2"):
            yield from self.send_message(message.channel, "Shitwars shitwo is pretty shit.")
        
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

        elif message.content.startswith("!trivialist"):
            yield from self.send_message(message.channel, buttertrivia.get_trivias())
        elif message.content.startswith("!triviastop"):
            buttertrivia.update_highscore()
            yield from self.send_message(message.channel, "Trivia stopped!\nCurrent standings:\n" + buttertrivia.print_score() + "\nThe winner is: " + buttertrivia.get_winner())
            self.running = buttertrivia.exit_trivia()
        
        elif message.content.startswith("!triviacancermode"):
            if not self.cancermode:
                self.cancermode = True
                yield from self.send_message(message.channel, "Cancer mode activated!")
            else:
                self.cancermode = False
                yield from self.send_message(message.channel, "Cancer mode deactivated!")
        elif message.content.startswith("!triviahighscore"):
            yield from self.send_message(message.channel, buttertrivia.get_highscore())
        elif message.content.startswith("!triviaquestions"):
            try:
                trivia = message.content.split()[1]
                yield from self.send_message(message.channel, buttertrivia.list_questions(trivia))
            except IndexError:
                yield from self.send_message(message.channel, "Invalid input. Use !triviaquestions <trivia>")
        elif message.content.startswith("!triviaremove"):
            try:
                trivia = message.content.split()[1]
                question_nr = message.content.split()[2]
                buttertrivia.remove_question(trivia, question_nr)
                yield from self.send_message(message.channel, "Successfully removed question " + str(question_nr) + " from " + trivia.capitalize())
            except IndexError:
                yield from self.send_message(message.channel, "Invalid inpud. Use !triviaremove <trivia> <index>")
        elif message.content.startswith("!triviaadd"):
            try:
                trivia = message.content.split()[1]
                question = message.content.split()[2]
                answers = message.content.split(" ",3)[3:]
                buttertrivia.add_question(trivia, question, answers)
                yield from self.send_message(message.channel, "Successfully added question to trivia " + trivia.lower())
            except IndexError:
                yield from self.send_message(message.channel, "Invalid input. Use !triviaadd <trivia> <question> <answer> or !triviaadd <trivia> <question> <answer1> <answer2> ...")
        elif message.content.startswith("!triviadelete"):
            try:
                trivia = message.content.split()[1]
                if buttertrivia.remove_trivia(trivia):
                    yield from self.send_message(message.channel, "Successfully removed trivia " + trivia.capitalize())
                else:
                    yield from self.send_message(message.channel, "There is no trivia with the name " + trivia.capitalize())
            except IndexError:
                yield from self.send_message(message.channel, "Invalid input. Use !triviadelete <trivia>")
        elif message.content.startswith("!trivia"):
            try:
                trivia = message.content.split()[1]
                if not self.running:
                    self.running = buttertrivia.search_trivias(trivia)
                    if(self.running):
                        buttertrivia.set_trivia(trivia)
                        yield from self.send_message(message.channel, "Successfully initialized trivia " + trivia.capitalize() + "!\n" + buttertrivia.get_question())
                    else:
                        yield from self.send_message(message.channel, "There is no trivia with name: " + trivia)
                elif self.running:
                    yield from self.send_message(message.channel, "Theres already a trivia running!")
            except IndexError:
                yield from self.send_message(message.channel, "To start a trivia type on the format '!trivia name'")
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
    bot.run('MzQ5NTEyOTc5MDIyMzQ4Mjkx.DH2nZg.s_4FdamAf96BljdzT3Bb7m2fgCw')
