import discord
import subprocess
import shutil
import os
import io

from source.CT_Config import CT_Config
from source.Track import Track
from source.wszst import szs
from scripts.minimap import obj_to_png

bot = discord.Client()
SERVER_ID = 842865613918699590
TRACK_CHANNEL_ID = 871100630251499530
OLD_TRACK_CHANNEL_ID = 842867283428507699  # previous channel used by the program to get score
DATA_CHANNEL_ID = 871469647617216652

warning_level_message = [
    "No special glitch",
    "minor glitch",
    "major glitch"
]

EMOTE_1STAR = 843109869107413012
EMOTE_2STAR = 843109881385058325
EMOTE_3STAR = 843109892330881107

placeholder_image_url = "https://media.discordapp.net/attachments/871469647617216652/871487829023289404/Placeholder.png"


def get_track_minimap(track: Track):
    if os.path.exists("./scripts/tmp/"): shutil.rmtree("./scripts/tmp/")
    if not os.path.exists("./scripts/tmp/"): os.makedirs("./scripts/tmp/")

    szs.extract(track.file_szs, "./scripts/tmp/track.szs")
    subprocess.run(["abmatt", "convert", "./scripts/tmp/track.szs.d/map_model.brres",
                    "to", "./scripts/tmp/map_model.obj"])
    image = obj_to_png.render_top_view(obj_file="./scripts/tmp/map_model.obj")

    return image


@bot.event
async def on_ready():
    guild: discord.Guild = bot.get_guild(id=SERVER_ID)
    track_channel: discord.TextChannel = guild.get_channel(channel_id=TRACK_CHANNEL_ID)
    old_track_channel: discord.TextChannel = guild.get_channel(channel_id=OLD_TRACK_CHANNEL_ID)
    data_channel: discord.TextChannel = guild.get_channel(channel_id=DATA_CHANNEL_ID)

    message_from_sha1 = {}
    old_message_from_sha1 = {}

    message: discord.Message
    async for message in track_channel.history(limit=5000):
        if message.author.id == bot.user.id:
            for field in message.embeds[0].fields:
                if "sha1" in field.name:
                    message_from_sha1[field.value] = message

    async for message in old_track_channel.history(limit=5000):
        if message.author.id == bot.user.id:
            sha1 = message.content.split("ct.wiimm.de/i/")[-1].replace("|", "").strip()
            old_message_from_sha1[sha1] = message

    ct_config = CT_Config()
    ct_config.load_ctconfig_file("./ct_config.json")

    for track in ct_config.all_tracks:
        try:
            if track.name == "_": continue

            if track.sha1 in message_from_sha1:
                embed = message_from_sha1[track.sha1].embeds[0]
            else:
                embed = discord.Embed(title=f"**{track.get_track_name()}**",
                                      description="", url=f"https://ct.wiimm.de/i/{track.sha1}")
                for _ in range(6): embed.add_field(name="empty", value="empty")

            author_link = ""
            if "," not in track.author: author_link = "http://wiki.tockdom.com/wiki/" + track.author
            embed.set_author(name=track.author, url=author_link)

            track_technical_data = szs.analyze(track.file_szs)

            if hasattr(track, "score"):
                scores = [track.score]
                if track.sha1 in old_message_from_sha1:
                    for reaction in old_message_from_sha1[track.sha1].reactions:
                        if str(EMOTE_1STAR) in str(reaction.emoji): scores.extend([1] * (reaction.count - 1))
                        elif str(EMOTE_2STAR) in str(reaction.emoji): scores.extend([2] * (reaction.count - 1))
                        elif str(EMOTE_3STAR) in str(reaction.emoji): scores.extend([3] * (reaction.count - 1))

                if track.sha1 in message_from_sha1:
                    for reaction in message_from_sha1[track.sha1].reactions:
                        if str(EMOTE_1STAR) in str(reaction.emoji): scores.extend([1] * (reaction.count - 1))
                        elif str(EMOTE_2STAR) in str(reaction.emoji): scores.extend([2] * (reaction.count - 1))
                        elif str(EMOTE_3STAR) in str(reaction.emoji): scores.extend([3] * (reaction.count - 1))

                moy_score = round(sum(scores) / len(scores), 2)

                embed.set_field_at(index=0, name="Track Score", value=f"{moy_score} (vote : {len(scores)})")
            if hasattr(track, "warning"):
                embed.set_field_at(index=1, name="Warning level", value=warning_level_message[track.warning])
            if hasattr(track, "since_version"):
                embed.set_field_at(index=2, name="Here since version", value=track.since_version)

            embed.set_field_at(index=3, name="Lap count", value=track_technical_data["lap_count"])
            embed.set_field_at(index=4, name="Speed multiplier", value=track_technical_data["speed_factor"])

            embed.set_image(url=placeholder_image_url)  # TODO

            embed.set_field_at(index=5, name="sha1", value=track.sha1)

            if track.sha1 not in message_from_sha1:

                with io.BytesIO() as image_binary:
                    image = get_track_minimap(track)
                    image.save(image_binary, "PNG")
                    image_binary.seek(0)
                    message_minimap = await data_channel.send(
                        file=discord.File(fp=image_binary, filename=f"minimap {track.sha1}.png"))
                embed.set_thumbnail(url=message_minimap.attachments[0].url)

                message = await track_channel.send(embed=embed)
                await message.add_reaction(bot.get_emoji(EMOTE_1STAR))
                await message.add_reaction(bot.get_emoji(EMOTE_2STAR))
                await message.add_reaction(bot.get_emoji(EMOTE_3STAR))
                await message.add_reaction("❌")

            else:
                message = message_from_sha1[track.sha1]
                await message.edit(embed=embed)

        except Exception as e:
            print(f"error for track {track.name} : {str(e)}")

bot.run(os.environ['DISCORD_GR_TOKEN'])
