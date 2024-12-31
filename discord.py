import disnake
from disnake.ext import commands
import asyncio
from datetime import datetime

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

whitelist = [1295101713195208764, 1301961038270304256, 987628397364666438, 1164187712702652426, 605638562343288843, 1268958767391707313, 1290669323832131607,1295101713195208764,1320868322769637406]
log_channel_id = 1314992124424491108

active_changes = {}

@bot.slash_command(description="Изменить ник участника несколько раз")
async def fucktracker(inter: disnake.ApplicationCommandInteraction, user_id: str, text: str, count: int):
    if inter.author.id not in whitelist:
        await inter.response.send_message("У вас нет прав использовать эту команду.", ephemeral=True)
        return

    guild = inter.guild
    if not guild:
        await inter.response.send_message("Команду можно использовать только на сервере.", ephemeral=True)
        return

    try:
        user = guild.get_member(int(user_id))
        if not user:
            await inter.response.send_message("Участник не найден.", ephemeral=True)
            return

        if not guild.me.guild_permissions.manage_nicknames:
            await inter.response.send_message("У меня нет прав менять ники на этом сервере.", ephemeral=True)
            return

        if count < 1 or count > 100:
            await inter.response.send_message("Количество повторений должно быть от 1 до 100.", ephemeral=True)
            return

        log_channel = guild.get_channel(log_channel_id)
        if not log_channel:
            await inter.response.send_message("Лог-канал не найден.", ephemeral=True)
            return

        original_nick = user.nick or user.name
        active_changes[user.id] = True

        await log_channel.send(f"Начинаю изменение ника {user.mention} {count} раз.")
        await inter.response.send_message(f"Изменение ника {user.display_name} начато.", ephemeral=True)

        for i in range(1, count + 1):
            if not active_changes.get(user.id):
                await log_channel.send(f"Изменение ника {user.mention} остановлено.")
                return

            new_nick = f"{text} {i}"
            if user.nick != new_nick:
                try:
                    await user.edit(nick=new_nick)
                except disnake.Forbidden:
                    await log_channel.send(f"Не удалось изменить ник {user.mention}. Нет прав.")
                    break
                except Exception as e:
                    await log_channel.send(f"Ошибка при изменении ника {user.mention}: {e}")
                    break
            await asyncio.sleep(0.5)

        await user.edit(nick=original_nick)
        await log_channel.send(f"Ник {user.mention} возвращён к оригиналу: {original_nick}.")
        del active_changes[user.id]

    except ValueError:
        await inter.response.send_message("ID пользователя должен быть числом.", ephemeral=True)
    except Exception as e:
        await inter.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)

@bot.event
async def on_member_remove(member: disnake.Member):
    if member.id in active_changes:
        del active_changes[member.id]
        log_channel = member.guild.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(f"Процесс изменения ника для {member.mention} остановлен: участник покинул сервер.")

bot.run("MTMyMDQ1MDgzMzc4MzA2NjYyNA.G3nXa2.fgzPd4-UZ6Lh6QfX0Kr2QqJR6aPMIIQjINg1tg")