import discord
import math
import json
import os
os.chdir("..")

bot = discord.Client()

SERVER_ID = 842865613918699590
TRACK_CHANNEL_ID = 871100630251499530

@bot.event
async def on_ready():
    guild: discord.Guild = bot.get_guild(id=SERVER_ID)
    track_channel: discord.TextChannel = guild.get_channel(channel_id=TRACK_CHANNEL_ID)

    with open("./ct_config.json", "r", encoding="utf8") as f:
        ct_config = json.load(f)

    async for message in track_channel.history(limit=5000):
        if message.author.id == bot.user.id:
            raw_score = message.embeds[0].fields[0].value
            sha1 = message.embeds[0].fields[5].value
            score = float(raw_score.split(" ")[0])
            if score % 1 >= 0.5: score = math.ceil(score)
            else: score = math.floor(score)

            for track in ct_config["tracks_list"]:
                if track["sha1"] == sha1:
                    if track["score"] != score:
                        print(f"updated score of {track['name']} from {track['score']} to {score}")
                    track["score"] = score
                    break
            else:
                for cup in ct_config["cup"].values():
                    for track in cup["tracks"].values():
                        if "sha1" in track:
                            if track["sha1"] == sha1:
                                if track["name"] != "_":
                                    if track["score"] != score:
                                        print(f"updated score of {track['name']} from {track['score']} to {score}")
                                    track["score"] = score
                                    break

    with open("./ct_config.json", "w", encoding="utf8") as f:
        json.dump(ct_config, f, ensure_ascii=False)
    print("end !")


bot.run(os.environ['DISCORD_GR_TOKEN'])