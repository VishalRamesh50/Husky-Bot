from discord.ext import commands
import youtube_dl


class Voice:
    def __init__(self, client):
        self.client = client
        self.players = {}  # dictionary of players across all servers
        self.queues = {}  # queue of music

    @commands.command(name="join", pass_context=True)  # joins voice channel
    async def join(self, ctx):
        channel = ctx.message.author.voice.voice_channel
        if channel is None:  # if user is not already in voice channel
            await self.client.say('You must be in a voice channel first!')
        await self.client.join_voice_channel(channel)
        await self.client.say("Joined the voice channel.")

    @commands.command(pass_context=True)  # leave voice channel
    async def leave(self, ctx):
        for x in self.client.voice_clients:
            if(x.server == ctx.message.server):
                await self.client.say('Left the voice channel.')
                return await x.disconnect()
        await self.client.say("I am not connected to any voice channel on this server!")

    @commands.command(pass_context=True)  # plays music
    async def play(self, ctx, url):
        server = ctx.message.server
        voice_client = self.client.voice_client_in(server)
        player = await voice_client.create_ytdl_player(url, ytdl_options={'default_search': 'auto'}, after=lambda: self.check_queue(server.id))
        self.players[server.id] = player
        player.start()

    @commands.command(pass_context=True)  # pauses music
    async def pause(self, ctx):
        id = ctx.message.server.id
        self.players[id].pause()

    @commands.command(pass_context=True)  # resumes music
    async def resume(self, ctx):
        id = ctx.message.server.id
        self.players[id].resume()

    @commands.command(pass_context=True)  # skips music
    async def skip(self, ctx):
        id = ctx.message.server.id
        self.players[id].stop()

    def check_queue(self, id):
        if self.queues[id] != []:
            player = self.queues[id].pop(0)  # access next player
            self.players[id] = player
            player.start()

    @commands.command(pass_context=True)  # adds music to queue
    async def queue(self, ctx, url):
        server = ctx.message.server
        voice_client = self.client.voice_client_in(server)
        player = await voice_client.create_ytdl_player(url, ytdl_options={'default_search': 'auto'}, after=lambda: self.check_queue(server.id))

        if server.id in self.queues:
            self.queues[server.id].append(player)
        else:
            self.queues[server.id] = [player]
        await self.client.say('Music added to queue.')


def setup(client):
    client.add_cog(Voice(client))
