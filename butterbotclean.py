import os
import discord
import asyncio
import operator
import buttertrivia
from wordcloud import WordCloud

class Butterbot(discord.Client):
    def __init__(self):
        self.commands = {}
        buttertrivia.init_commands()
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
  
    #Call/create logs
    def _get_log_dir(self,author):
        directory = os.path.dirname(__file__)
        directory = os.path.join(directory, 'logs/{}.txt'.format(author))
        return directory

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
    def init_commands(self):
        actions = {
            'queue':self.queue_command,
            'play':self.play_command,
            'hijack':self.hijack_command,
            'overwhelmed':self.overwhelmed_command,
            'stop':self.stop_command,
            'start':self.start_command,
            'gtfo':self.gtfo_command,
            'help':self.help_command,
            'favword':self.favword_command,
            'volume':self.volume_command,
            'whatis':self.whatis_command,
            'wisdom':self.wisdom_command,
            'PerIsAFuckBag':self.PerIsAFuckBag_command,
            'wordcloud':self.wordcloud_command,
            'triviacancermode':self.triviacancermode_command,
            'trivia':self.trivia_command
        }
        return actions

        
    @asyncio.coroutine
    def help_command(self, message):
        commands = """
        Available commands:
        !play <youtube link>
        !queue <youtube link>
        !stop
        !start
        !gtfo
        !volume [0.0,2.0]
        !favword
        !wisdom
        !wordcloud
        !overwhelmed
        !hijack
        !whatis <something>
        !trivia start <trivia>
        !trivia list
        !trivia highscore
        !triviacancermode
        !trivia stop
        !trivia delete <trivia>
        !trivia setquestions <number>
        """
        yield from self.send_message(message.channel, commands)
    
        
    @asyncio.coroutine
    def format_input(self, message):
        #TODO: Kom på nått bättre sätt att initialisera commands...
        if self.commands == {}:
            self.commands = yield from self.init_commands()
        function = message.content.split()[0][1:]
        if function in self.commands:
            function = self.commands[function]
            yield from function(message)
    
    
    @asyncio.coroutine
    def queue_command(self, message):
        try:
            ytlink = message.content.split()[1]
        except IndexError:
            yield from self.send_message(message.channel, "A youtube link must follow the !play command.")
        if (not self.player or not self.player.is_playing()) and not self.queue and not self._is_paused:
            yield from self._play_song(ytlink, message.author.voice_channel, message.channel)
        else:
            self.queue.append((ytlink,message.channel))
    

    @asyncio.coroutine
    def play_command(self, message):
        try:
            ytlink = message.content.split()[1]
        except IndexError:
            yield from self.send_message(message.channel, "A youtube link must follow the !play command.")
        yield from self._play_song(ytlink, message.author.voice_channel, message.channel)
    
    
    @asyncio.coroutine
    def hijack_command(self, message):
        ytlink = message.content.split()[1]
        yield from self._hijack_song(ytlink, message.channel)
    
    
    @asyncio.coroutine
    def overwhelmed_command(self, message):
        yield from self._play_song("https://cdn.discordapp.com/attachments/134346894464778240/329772485660901380/vs_nbarbam2_help.wav", message.author.voice_channel, message.channel)
    
    
    @asyncio.coroutine
    def stop_command(self, message):
        if self.player and self.player.is_playing():
            self.player.pause()
            self._is_paused = True
        return
    
    
    @asyncio.coroutine
    def start_command(self, message):
        if self.player and not self.player.is_playing():
            self.player.resume()
            self._is_paused = False
    
    
    @asyncio.coroutine
    def gtfo_command(self, message):
        yield from self.voice.disconnect()
        if self.player:
            self.player.stop()
        self.in_channel = None
        self.voice = None
        self.player = None
        self.queue = []
    
    
    @asyncio.coroutine
    def favword_command(self, message):
        tmp = yield from self.send_message(message.channel, 'Calculating...')
        with open(self._get_log_dir(message.author), 'r') as f:
            words = f.read().split()
            wordcount = {}
            for word in words:
                if word in wordcount.keys():
                    wordcount[word] += 1
                else:
                    wordcount[word] = 1
       
            sorted_words = sorted(wordcount.items(), key=operator.itemgetter(1))
            yield from self.edit_message(tmp, "@{} Your favorite word seems to be \"{}\". Used {} times since I started keeping track.".format(message.author, sorted_words[-1][0],sorted_words[-1][1]))
        
    
    @asyncio.coroutine
    def volume_command(self, message):
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
           
    
    @asyncio.coroutine
    def whatis_command(self, message):
        arg = message.content.split()[1]
        if arg.lower() == "bradley":
            yield from self.send_message(message.channel, "Bradley: a fucking cunt.")
        elif arg.lower() == "gw2":
            yield from self.send_message(message.channel, "Shitwars shitwo is pretty shit.")
        else:
            yield from self.send_message(message.channel, "I dont know, ask someone else!")
    
    @asyncio.coroutine
    def wisdom_command(self, message):
        if "{}".format(message.author) == "Rin#3028":
            yield from self.send_message(message.channel, "You should probably buy PUBG, also I get this arcane tingling from you. This strange sensation of utter cuntery. Are you, perchance, a massive cock?")
        elif "{}".format(message.author) == "Tekoppen#3344" or "{}".format(message.author) == "Youthius#0128":
            yield from self.send_message(message.channel, "Oh, dearest {} I sense you have a friend, seperated from you by a long distance. This friend needs counseling, for he is refusing to make a purchase which will greatly improve his life.".format(str(message.author)[:-5]))
        else:
            print("-{}-".format(message.author))
            yield from self.send_message(message.channel, "I have no wisdom for you at this time, my child.")
    
    
    @asyncio.coroutine
    def PerIsAFuckBag_command(self, message):
        if "{}".format(message.author) == "Rin#3028":
            yield from self.send_message(message.channel, "http://store.steampowered.com/app/578080/PLAYERUNKNOWNS_BATTLEGROUNDS/")
    
    
    @asyncio.coroutine
    def wordcloud_command(self, message):
        author = message.author
        try:
            with open(self._get_log_dir(author), 'r') as f:
                words = f.read()
                wordcloud = WordCloud(width=1024, height=768).generate(words)
                image = wordcloud.to_image()
                image.save('test.jpg')
                yield from self.send_file(message.channel,fp='test.jpg')
        except:              
            yield from self.send_message(message.channel, "Sorry, couldn't generate the cloud. Probably because I've not got enough words recorded from you.")
    
    
    @asyncio.coroutine
    def triviacancermode_command(self, message):
        if not self.cancermode:
            self.cancermode = True
            yield from self.send_message(message.channel, "Cancer mode activated")
        else:
            self.cancermode = False
            yield from self.send_message(message.channel, "Cancer mode deactivated")
    
    
    @asyncio.coroutine
    def trivia_command(self, message):
        try:
            input_function = message.content.split(" ", 1)[1]
            yield from self.send_message(message.channel, buttertrivia.format_input(input_function))
        except Exception as e:
            print(e)
            yield from self.send_message(message.channel, "Invalid command, use !help to see available commands ")

    
    @asyncio.coroutine
    def trivia_answer(self, message):
        answer = message.content
        if buttertrivia.check_answer(answer):
            buttertrivia.give_score(str(message.author)[:-5])
            
            if self.cancermode:
                yield from self._play_song("https://www.youtube.com/watch?v=twyWHrHWq9E", message.author.voice_channel, message.channel)
            
            yield from self.send_message(message.channel, "Correct!\n\nCurrent standings:\n" + buttertrivia.print_score()) 
            
            if buttertrivia.check_if_more_questions():
                yield from self.send_message(message.channel, " \n" + buttertrivia.get_question())
            else:
                self.running = False
                
                if self.cancermode:
                    yield from self._play_song("https://www.youtube.com/watch?v=UdLagrOvYII", message.author.voice_channel, message.channel)
                
                buttertrivia.update_highscore()
                yield from self.send_message(message.channel, "Trivia is over!\nThe final standings are:\n" + buttertrivia.print_score() + "\nCongratulations to: " + buttertrivia.get_winner())


    @asyncio.coroutine
    def on_message(self, message):

        yield from self.trivia_answer(message)
        if message.content.startswith("!"):
            yield from self.format_input(message) 
        else:	
            author = message.author
            with open(self._get_log_dir(author), 'a') as f:
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
