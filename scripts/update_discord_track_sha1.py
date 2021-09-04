import discord, os

bot = discord.Client()
replace_list = {
    "old_sha1": "new_sha1"
}

SERVER_ID = 842865613918699590
TRACK_CHANNEL_ID = 871100630251499530

@bot.event
async def on_ready():
    server = bot.get_guild(SERVER_ID)
    channel = server.get_channel(TRACK_CHANNEL_ID)
    async for message in channel.history(limit=5000):
        if message.author == bot.user:
            embed = message.embeds[0]
            org_sha1 = embed.fields[5].value
            if org_sha1 in replace_list:
                embed.set_field_at(5, name="sha1", value=replace_list[org_sha1])
                await message.edit(embed=embed)
                print(f"edited {org_sha1} to {replace_list[org_sha1]}")
    print("finished !")

bot.run(os.environ['DISCORD_GR_TOKEN'])
