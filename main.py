""" 
Anti-Raid Tool made with Python. 

Features:
Moderation commands = Ban/Kick/Mute
Guild Backup/Revert = Channels, Categories, Roles, Permissions
Joining tests like who bot was added by, age of account
Logging features
Stop any nuke attempts by banning anyone who starts to delete too much

"""

import asyncio
import aiofiles
from datetime import datetime
from time import time, ctime
import discord
from discord.ext import commands, tasks

#asyncDB
import aiofiles # to open the files asyncly
import os

# Custom Exceptions
class DatabaseError(Exception): pass
class AlreadyCreated(Exception): pass
class AlreadyRegistered(Exception): pass
class MemberNotFound(Exception): pass

# functions
async def create_db(filename):
    try:
        try:
            async with aiofiles.open(filename, mode="r") as file:
                return False

        except FileNotFoundError:
            async with aiofiles.open(filename, mode="w") as file:
                return True

    except Exception as error:
        raise DatabaseError(f"Failed to create a new database because of error: {error}")

async def remove_db(filename):
    try:
        os.remove(filename)

    except Exception as error:
        raise DatabaseError(f"Failed to remove database because of error: {error}")

async def find_values(db, target_id): # get the data from a specific value
    try:
        async with aiofiles.open(db, mode="r") as file:
            for line in await file.readlines():
                user_id = line.strip("\n").split(" ")[0]
                if int(user_id) == target_id:
                    return line.strip("\n").split(" ")[1:] # return data like dict, eg: give key = get value

            raise MemberNotFound("Could not find member by given id.") # if the id wasn't found, raise exception

    except Exception as error:
        raise DatabaseError(f"Failed accessing values because of error: {error}")
        
async def register(db, target_id, predata=""): # register a new value
    try:
        try: 
            await find_values(db, target_id) # try use my find_value function and check if the id isn't already registered
            return False
            #raise AlreadyRegistered("Member has already been registered.") # if the account was already registered, raise an error.

        except:
            async with aiofiles.open(db, mode="r") as file:
                file_lines = await file.readlines()

            async with aiofiles.open(db, mode="a") as file:
                line = f"{target_id}"
                for part in predata:
                    line += f" {part}" 

                if len(file_lines) != 0:
                    await file.write(f"\n{line}") # write a new line
                else:
                    await file.write(line) # just write the data on the first line instead of writing a new line as well

            return True

    except Exception as error:
        raise DatabaseError(f"Failed to register new value into database because of error: {error}")
        
async def remove_id(db, target_id): # remove a user from the file
    try:
        async with aiofiles.open(db, mode="r") as file: 
            file_lines = await file.readlines()
            found = False
            for line in file_lines:
                user_id = line.strip("\n").split(" ")[0]
                if int(user_id) == target_id: 
                    file_lines.remove(line) # remove the line from the list
                    found = True
    
        if found:
            async with aiofiles.open(db, mode="w") as file: 
                for line in file_lines:
                    if file_lines[-1] != line: # if it isn't the last line in the file
                        await file.write(line) # write the line as it has a \n on the end
                    else:
                        await file.write(line.strip("\n")) # write the line without a new line
                    
                return True

        else:
            raise MemberNotFound("Member id was not found.")

    except Exception as error:
        raise DatabaseError(f"Failed to remove values from database because of error: {error}")

async def add_part(db, target_id, new_data): # for adding to the target values
    try:
        async with aiofiles.open(db, mode="r") as file:
            file_lines = await file.readlines() 

            for i in range(len(file_lines)):
                line_parts = file_lines[i].split(" ")
                user_id = line_parts[0]

                if target_id == int(user_id):
                    if file_lines[-1] != file_lines[i]: 
                        file_lines[i] = f"{target_id} {new_data}\n" # then rewrite the line with the new data
                    else:
                        file_lines[i] = f"{target_id} {new_data}"

        async with aiofiles.open(db, mode="w") as file: # write the data back
            for line in file_lines:
                await file.write(line)
        
        return True

    except Exception as error:
        raise DatabaseError(f"Failed to update values because of error: {error}")

# create prefixes file
with open("prefixes.txt", "a") as file:
    pass

# load prefixes from stored prefixes
custom_prefixes = {}
with open("prefixes.txt", "r") as file:
    for line in file.readlines():
        parts = line.strip("\n").split(" ")
        custom_prefixes[int(parts[0])] = parts[1]

def get_prefix(bot, message):
    if message.guild:
        return custom_prefixes[message.guild.id]

    else:
        return "-"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, help_command=None, intents=intents)

# functions
async def log(guild_id, action):
    current_time = ctime()
    async with aiofiles.open(f"{guild_id}_logs.txt", mode="a") as db:
        await db.write(f"{current_time} : {action}\n")

async def show_help(ctx):
    help_embed = discord.Embed(title=f"How to protect your server using me!", url="https://www.youtube.com/alphascript", colour=discord.Color.gold())
    help_embed.description = "> **Background Protection**\n"
    help_embed.description += "*I constantly check for any suspicious activity or signs of a raid or nuking attempt. For example, deleting too many channels in a short amount of time will get you banned, this doesn't matter if you're whitelisted. As well as this, accounts less than a week old will be stopped from joining. Only whitelisted members can invite bots, otherwise the bot will be instantly kicked. This is the best way for everyone.*\n**Please make sure to give this bot the highest role possible for maximum security.**\n\n"
    help_embed.description += "> **Owner Only Commands** :pencil:\n"
    help_embed.description += f"__Setup:__ \n**{custom_prefixes[ctx.guild.id]}set_prefix <prefix>** : Changes the prefix for the given prefix.\n"
    help_embed.description += f"**{custom_prefixes[ctx.guild.id]}whitelisted** : Displays a list of the whitelisted administrators.\n" 
    help_embed.description += f"**{custom_prefixes[ctx.guild.id]}whitelist <administrator>** : Whitelists the given administrator allowing them to use whitelisted commands.\n"
    help_embed.description += f"**{custom_prefixes[ctx.guild.id]}unwhitelist <administrator>** : Unwhitelists the given whitelisted administrator stopping them from using whitelisted commands.\n"
    help_embed.description += f"**{custom_prefixes[ctx.guild.id]}backup** : Overwrites the current server backup (requires more confirmation).\n"
    help_embed.description += f"**{custom_prefixes[ctx.guild.id]}revert** : Reverts the server to the current backup (requires more confirmation).\n\n"

    help_embed.description += "> **Whitelisted Administrator Commands** :lock:\n"
    help_embed.description += f"__Moderation:__ :\n**{custom_prefixes[ctx.guild.id]}kick <member> <reason>** : Kicks the given member for the given reason.\n"
    help_embed.description += f"**{custom_prefixes[ctx.guild.id]}ban <member> <reason>** : Bans the given member for the given reason.\n"
    help_embed.description += f"**{custom_prefixes[ctx.guild.id]}mute <member> <hours> <reason>** : Mutes the given member for the given hours for the given reason.\n"
    help_embed.description += f"**{custom_prefixes[ctx.guild.id]}unmute <member> <hours> <reason>** : Unmutes the given member for the given reason.\n\n"

    help_embed.set_footer(text="Thanks for using me! Coded by youtube.com/alphascript", icon_url=bot.user.avatar_url)
    help_embed.set_thumbnail(url=bot.user.avatar_url)

    await ctx.channel.send(embed=help_embed)

async def check_perms(ctx): # check if someone has admin and is whitelisted
    try:
        await find_values(f"{ctx.guild.id}_whitelist.txt", ctx.author.id)
        check = True 

    except:
        check = False

    if ctx.author.permissions_in(ctx.message.channel).administrator and check:
        return True

    else:
        await ctx.send(f"{ctx.author.mention} you must have administrator permissions and be whitelisted to do this!")
        return False

async def get_perms(guild, obj):
    role_perms = ""
    for role in guild.roles:
        if not all(value == None for key, value in obj.overwrites_for(role)):
            role_perms += role.name.replace(" ", "\\") + "\\\\"
            role_perms += ",".join([str(value).lower() for name, value in obj.overwrites_for(role)])
            if role != guild.roles[-1]:
                role_perms += "\\\\\\"

    member_perms = ""
    for member in guild.members:
        if not all(value == None for key, value in obj.overwrites_for(member)):
            member_perms += str(member.id) + "\\\\"
            member_perms += ",".join([str(value).lower() for key, value in obj.overwrites_for(member)])

            if member != guild.members[-1]:
                member_perms += "\\\\\\"

    return role_perms, member_perms

async def create_backup(guild):
    file = f"{guild.id}_backup.txt"
    async with aiofiles.open(file, mode="w") as backup:
        date = datetime.today().strftime("%Y-%m-%d")
        await backup.write(date)

        for role in guild.roles[1:]: # store roles
            permissions = ",".join([name for name, value in role.permissions if value])
            members = ",".join([str(member.id) for member in role.members])

            name = role.name.replace(" ", "\\")
            await backup.write(f"\nr {name} {role.colour.value} {role.mentionable} {role.hoist} {permissions} {members}")
        
        for category in guild.categories: # store categories
            name = category.name.replace(" ", "\\")
            role_perms, member_perms = await get_perms(guild, category)

            await backup.write(f"\nc {name} {role_perms} {member_perms}")
        
        for channel in guild.text_channels: #store text channels
            category = None if channel.category is None else channel.category.name.replace(" ", "\\")
            b = "true" if channel.permissions_synced else "false"
            
            name = channel.name.replace(" ", "\\")

            role_perms, member_perms = await get_perms(guild, channel)
            await backup.write(f"\nt {name} {category}\\\\{b} {role_perms} {member_perms}")

        for channel in guild.voice_channels: # store voice channels
            category = None if channel.category is None else channel.category.name.replace(" ", "\\")
            b = "true" if channel.permissions_synced else "false"
            name = channel.name.replace(" ", "\\")
            
            role_perms, member_perms = await get_perms(guild, channel)
            await backup.write(f"\nv {name} {category}\\\\{b} {role_perms} {member_perms}")

async def revert_server(ctx):
    file = f"{ctx.guild.id}_backup.txt"

    await ctx.send("Storing current data.")
    old_ids = {"channels" : [], "roles" : []}
    
    for channel in ctx.guild.channels:
        old_ids["channels"].append(channel.id)

    for role in ctx.guild.roles:
        old_ids["roles"].append(role.id)

    async with aiofiles.open(file, mode="r") as backup: # dont make duplicates of role names
        lines = await backup.readlines()
        backup_time = lines[0].strip("\n")
        await ctx.send(f"Reverting to last backup from : {backup_time}")

        for line in lines[1:]:
            line = line.strip("\n").split(" ")
            name = line[1].replace("\\", " ")

            if line[0] == "r": # revert roles and give them back to members
                try: # if there are permissions, update them
                    perms = line[5].split(",")
                    permissions = discord.Permissions()
                    permissions.update(**dict.fromkeys(perms, True))

                except IndexError: # ignore no permissions
                    pass

                if line[2].strip(" ") != "":
                    mentionable = True if line[3].strip(" ") == "True" else False
                    hoist = True if line[4].strip(" ") == "True" else False
                    
                    role = await ctx.guild.create_role(name=name, permissions=permissions, hoist=hoist, mentionable=mentionable, colour=discord.Color(value=int(line[2])))

                if line[6].strip(" ") != "":
                    members = line[6].split(",")
                    for member_id in members:
                        try:
                            member = await ctx.guild.fetch_member(int(member_id))
                            await member.add_roles(role)

                        except Exception as error:
                            await log(ctx.guild.id, f"Failed reverting role to member because of {error}.")

            
            elif line[0] == "c": # categories
                name = line[1].replace("\\", " ")
                overwrites = {}

                if line[2].strip(" ") != "":
                    for part in line[2].split("\\\\\\"):
                        if part.strip(" ") != "":
                            
                            parts = part.split("\\\\")
                            role_name = parts[0].replace("\\", " ")
                            perms = parts[1].split(",")

                            permissions = discord.PermissionOverwrite()
                            i = 0
                            for perm, val in permissions:
                                if perms[i] == "true": b = True
                                elif perms[i] == "false": b = False
                                else: b = None
                                permissions.update(**{perm : b})

                                i += 1

                            for role in ctx.guild.roles:
                                if role.name == role_name:
                                    overwrites[role] = permissions
                
                if line[3].strip(" ") != "":
                    for part in line[3].split("\\\\\\"):
                        if part.strip(" ") != "":
                            parts = part.split("\\\\")
                            member_id = int(parts[0])
                            perms = parts[1].split(",")
                            permissions = discord.PermissionOverwrite()

                            i = 0
                            for perm, val in permissions:
                                if perms[i] == "true": b = True
                                elif perms[i] == "false": b = False
                                else: b = None
                                permissions.update(**{perm : b})
                            
                                i += 1
                                

                            for member in ctx.guild.members:
                                if member.id == member_id:
                                    overwrites[member] = permissions

                await ctx.guild.create_category(name=name, overwrites=overwrites) 

            # perms synced always returns false, doesn't work
            elif line[0] == "t": # revert text_channels
                overwrites = {}

                if line[3].strip(" ") != "":
                    for part in line[3].split("\\\\\\"):
                        if part.strip(" ") != "":
                            
                            parts = part.split("\\\\")
                            role_name = parts[0].replace("\\", " ")
                            perms = parts[1].split(",")

                            permissions = discord.PermissionOverwrite()
                            i = 0
                            for perm, val in permissions:
                                if perms[i] == "true": b = True
                                elif perms[i] == "false": b = False
                                else: b = None
                                permissions.update(**{perm : b})

                                i += 1

                            for role in ctx.guild.roles:
                                if role.name == role_name:
                                    overwrites[role] = permissions
                
                if line[4].strip(" ") != "":
                    for part in line[4].split("\\\\\\"):
                        if part.strip(" ") != "":
                            parts = part.split("\\\\")
                            member_id = int(parts[0])
                            perms = parts[1].split(",")
                            permissions = discord.PermissionOverwrite()

                            i = 0
                            for perm, val in permissions:
                                if perms[i] == "true": b = True
                                elif perms[i] == "false": b = False
                                else: b = None
                                permissions.update(**{perm : b})
                            
                                i += 1
                                
                            for member in ctx.guild.members:
                                if member.id == member_id:
                                    overwrites[member] = permissions

                category_parts = line[2].split("\\\\")
                if category_parts[0] == "None":
                    await ctx.guild.create_text_channel(name=name, overwrites=overwrites)

                else:
                    for category in ctx.guild.categories:
                        if category.name == category_parts[0].replace("\\", " "):
                            if category_parts[1] == "true":
                                await category.create_text_channel(name=name) 

                            else:
                                await category.create_text_channel(name=name, overwrites=overwrites)

            elif line[0] == "v": # revert voice_channels
                overwrites = {}

                if line[3].strip(" ") != "":
                    for part in line[3].split("\\\\\\"):
                        if part.strip(" ") != "":
                            
                            parts = part.split("\\\\")
                            role_name = parts[0].replace("\\", " ")
                            perms = parts[1].split(",")

                            permissions = discord.PermissionOverwrite()
                            i = 0
                            for perm, val in permissions:
                                if perms[i] == "true": b = True
                                elif perms[i] == "false": b = False
                                else: b = None
                                permissions.update(**{perm : b})

                                i += 1

                            for role in ctx.guild.roles:
                                if role.name == role_name:
                                    overwrites[role] = permissions
                
                if line[4].strip(" ") != "":
                    for part in line[4].split("\\\\\\"):
                        if part.strip(" ") != "":
                            parts = part.split("\\\\")
                            member_id = int(parts[0])
                            perms = parts[1].split(",")
                            permissions = discord.PermissionOverwrite()

                            i = 0
                            for perm, val in permissions:
                                if perms[i] == "true": b = True
                                elif perms[i] == "false": b = False
                                else: b = None
                                permissions.update(**{perm : b})
                            
                                i += 1
                                
                            for member in ctx.guild.members:
                                if member.id == member_id:
                                    overwrites[member] = permissions

                category_parts = line[2].split("\\\\")
                if category_parts[0] == "None":
                    await ctx.guild.create_voice_channel(name=name, overwrites=overwrites)

                else:
                    for category in ctx.guild.categories:
                        if category.name == category_parts[0].replace("\\", " "):
                            if category_parts[1] == "true":
                                await category.create_voice_channel(name=name) 

                            else:
                                await category.create_voice_channel(name=name, overwrites=overwrites)

    await ctx.send("Removing old data.")
    for channel_id in old_ids["channels"]:
        try:
            channel = ctx.guild.get_channel(channel_id)
            await channel.delete()

        except Exception as error:
            await log(ctx.guild.id, f"failed to remove channel when restoring: {error}")

    for role_id in old_ids["roles"]:
        try:
            role = ctx.guild.get_role(role_id)
            await role.delete()

        except Exception as error:
            await log(ctx.guild.id, f"failed to remove role when restoring: {error}")
 
# events
@bot.event
async def on_ready():
    for guild in bot.guilds: # register all guilds if not already registered
        if await register("prefixes.txt", guild.id, "-"):
            custom_prefixes[guild.id] = "-"

        if await create_db(f"{guild.id}_whitelist.txt"):
            await register(f"{guild.id}_whitelist.txt", guild.owner.id)

        if await create_db(f"{guild.id}_backup.txt"):
            await create_backup(guild)

        await create_db(f"{guild.id}_logs.txt")

    await bot.change_presence(activity=discord.Activity(name="mention me for help!", type=discord.ActivityType.watching))
    
    # stores of events
    bot.bans = {} # {id : (amount, time)}
    bot.kicks = {}
    bot.creating_channels = {}
    bot.removing_channels = {}
    bot.creating_roles = {}
    bot.removing_roles = {}
    
    print(f"{bot.user.name} is ready for use!")
    
@bot.event
async def on_message(message): # show help on mention
    if bot.user.mentioned_in(message):
        try:
            await find_values(f"{message.guild.id}_whitelist.txt", message.author.id)
            check = True 

        except:
            check = False
        
        if message.author.permissions_in(message.channel).administrator and check:
            await show_help(message)

        else:
            await message.channel.send(f"{message.author.mention} you must have administrator permissions and be whitelisted to do this!")
            return False

    else:
        await bot.process_commands(message)
    
@bot.event
async def on_command_error(ctx, error): # handle command errors
    if isinstance(error, commands.CommandNotFound):
        return
    
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"One or more of the arguments given was invalid. Please use **'{custom_prefixes[ctx.guild.id]}help'** for the syntax of this command.")

    elif isinstance(error, DatabaseError):
        await ctx.send(f"Updating the database failed, please contact an admin urgently.")
        await log(ctx.guild.id, f"Database update failed because of error : {error}")

    elif isinstance(error, MemberNotFound):
        await ctx.send(f"Member couldn't be found in the database.")

    else: 
        await log(ctx.guild.id, f"Random error : {error}")

@bot.event
async def on_member_join(member):
    if member.bot:
        async for event in member.guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1): # just get 1 as bot add is less common
            try:
                await find_values(f"{member.guild.id}_whitelist.txt", event.user.id)
                await log(member.guild.id, f"Allowed {member.name} to join because it was added by {event.user}.")

            except DatabaseError:
                await member.kick(reason="Bot added by non-whitelisted member.")
                await log(member.guild.id, f"Kicked bot {member.name} when added by {event.user} because they aren't whitelisted.")

            except Exception as error:
                await log(member.guild.id, f"Failed when testing bot added by {event.user} because of error {error}.")
                
    else:
        c = datetime.today().strftime("%Y-%m-%d").split("-")
        c_y = int(c[0])
        c_m = int(c[1])
        c_d = int(c[2])

        if c_y == member.created_at.year and c_m == member.created_at.month and c_d - member.created_at.day < 7: # year can only be less or equal, month can only be less or equal, then check days
            await member.kick(reason="Sorry, your account is less than 7 days old! Please join back when your account is older.")
            await log(member.guild.id, f"Kicked {member.name} for having an account less than a week old.")

@bot.event
async def on_guild_join(guild):
    await register("prefixes.txt", guild.id, "-")
    custom_prefixes[guild.id] = "-"
    await create_db(f"{guild.id}_whitelist.txt")
    await register(f"{guild.id}_whitelist.txt", guild.owner.id)
    await create_db(f"{guild.id}_backup.txt")
    await create_backup(guild)
    await create_db(f"{guild.id}_logs.txt")

@bot.event
async def on_guild_remove(guild):
    await remove_id("prefixes.txt", guild.id)
    custom_prefixes.pop(guild.id)
    await remove_db(f"{guild.id}_whitelist.txt")
    await remove_db(f"{guild.id}_backup.txt")
    await remove_db(f"{guild.id}_logs.txt")

@bot.event # if someone gives a dangerous role without being whitelisted
async def on_member_update(before, after):
    new_roles = [role for role in after.roles if role not in before.roles and role.permissions.administrator]
    if len(new_roles) > 0:
        async for event in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=3): # get last 3 incase someone gives role at exact time?
            if event.target.id == after.id and event.user.id != bot.user.id: # check if correct member
                try:
                    await find_values(f"{after.guild.id}_whitelist.txt", event.user.id)
                    await log(after.guild.id, f"Allowed {after.name} to have administrator because it was given by {event.user}.")

                except DatabaseError:
                    for role in new_roles:
                        await after.remove_roles(role)

                    await log(after.guild.id, f"Removed admin from {after.name} when added by {event.user} because they aren't whitelisted.")
                    return

                except Exception as error:
                    await log(after.guild.id, f"Failed when testing role given to {after.name} by {event.user} because of error {error}.")

@bot.event
async def on_member_ban(guild, banned):
    async for event in guild.audit_logs(action=discord.AuditLogAction.ban, limit=3): # get last 3 incase someone bans at exact time?
        if event.user is not bot.user:
            if event.target.id == banned.id:
                try:
                    amount, last = bot.bans[event.user.id]
                    if time() - last < 8: # 8 seconds between each ban will be flagged
                        amount += 1
                        last = time()

                        if amount >= 3:
                            await event.user.ban(reason="For banning 3 or more members at once.")
                            await log(guild.id, f"successfully banned {event.user.name} for banning more than 3 members at once.")
                            return

                    else: # otherwise reset the time
                        amount = 1
                        last = 0
                        
                    bot.bans[event.user.id] = (amount, last)

                except KeyError:
                    bot.bans[event.user.id] = (1, time())

                except Exception as error:
                    await log(guild.id, f"failed at {error} whilst calculating ban amounts.")

                finally:
                    break
    
    """
    for key in bot.bans: # check each time to remove people, saves space?
        if event.target.id != key:
            amount, last = bot.bans[key]
            if time() - last > 5: # if they haven't banned someone in 5 seconds, remove them
                bot.bans.pop(key)
    """

@bot.event
async def on_member_remove(member):
    guild = member.guild
    async for event in guild.audit_logs(action=discord.AuditLogAction.kick, limit=3): # get last 3 incase someone kick at exact time?
        if event.user is not bot.user:
            if event.target.id == member.id:
                try:
                    amount, last = bot.kicks[event.user.id]
                    if time() - last < 8: # 8 seconds between each kick will be flagged
                        amount += 1
                        last = time()
                        
                        if amount >= 3:
                            await event.user.ban(reason="For kicking 3 or more members at once.")
                            await log(guild.id, f"successfully banned {event.user.name} for kicking more than 3 members at once.")
                            return

                    else: # otherwise reset the time
                        amount = 1
                        last = 0
                        
                    bot.kicks[event.user.id] = (amount, last)

                except KeyError:
                    bot.kicks[event.user.id] = (1, time())

                except Exception as error:
                    await log(guild.id, f"failed at {error} whilst calculating kick amounts.")
                    
                finally:
                    break

    """       
    for key in bot.kicks: # check each time to remove people, saves space?
        if event.target.id != key:
            amount, last = bot.kicks[key]
            if time() - last > 5: # if they haven't kicked someone in 5 seconds, remove them
                bot.kicks.pop(key)
    """

@bot.event
async def on_guild_channel_create(channel): # shorter time due to faster creation? more typical creation?
    guild = channel.guild
    async for event in guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=3): # get last 3 incase someone create at exact time?
        if event.user is not bot.user:
            if event.target.id == channel.id:
                try:
                    amount, last = bot.creating_channels[event.user.id]
                    if time() - last < 5: # 5 seconds between each creation will be flagged
                        amount += 1
                        last = time()

                        if amount >= 3:
                            await event.user.ban(reason="For creating 3 or more channels at once.")
                            await log(guild.id, f"successfully banned {event.user.name} for creating more than 3 channels at once.")
                            return

                    else: # otherwise reset the time
                        amount = 1
                        last = 0
                        
                    bot.creating_channels[event.user.id] = (amount, last)

                except KeyError:
                    bot.creating_channels[event.user.id] = (1, time())

                except Exception as error:
                    await log(guild.id, f"failed at {error} whilst calculating channel creation amounts.")
                    
                finally:
                    break
    
@bot.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    async for event in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=3): # get last 3 incase someone delete at exact time?
        if event.user is not bot.user:
            if event.target.id == channel.id:
                try:
                    amount, last = bot.removing_channels[event.user.id]
                    if time() - last < 5: # 5 seconds between each creation will be flagged
                        amount += 1
                        last = time()

                        if amount >= 3:
                            await event.user.ban(reason="For deleting 3 or more channels at once.")
                            await log(guild.id, f"successfully banned {event.user.name} for deleting more than 3 channels at once.")
                            return

                    else: # otherwise reset the time
                        amount = 1
                        last = 0
                        
                    bot.removing_channels[event.user.id] = (amount, last)

                except KeyError:
                    bot.removing_channels[event.user.id] = (1, time())

                except Exception as error:
                    await log(guild.id, f"failed at {error} whilst calculating channel deletion amounts.")
                    
                finally:
                    break


    """ 
    NOT USED
    for key in bot.removing_channels: # check each time to remove people, saves space?
        if event.target.id != key:
            amount, last = bot.removing_channels[key]
            if time() - last > 3: # if they haven't deleted a channel in 3 seconds, remove them
                bot.removing_channels.pop(key)
    """

@bot.event
async def on_guild_role_create(role):
    guild = role.guild
    async for event in guild.audit_logs(action=discord.AuditLogAction.role_create, limit=3): # get last 3 incase someone create at exact time?
        if event.user is not bot.user:
            if event.target.id == role.id:
                try:
                    amount, last = bot.creating_roles[event.user.id]
                    if time() - last < 5: # 5 seconds between each creation will be flagged
                        amount += 1
                        last = time()

                        if amount >= 3:
                            await event.user.ban(reason="For creating 3 or more roles at once.")
                            await log(guild.id, f"successfully banned {event.user.name} for creating more than 3 roles at once.")
                            return

                    else: # otherwise reset the time
                        amount = 1
                        last = 0
                        
                    bot.creating_roles[event.user.id] = (amount, last)

                except KeyError:
                    bot.creating_roles[event.user.id] = (1, time())

                except Exception as error:
                    await log(guild.id, f"failed at {error} whilst calculating role creation amounts.")
                    
                finally:
                    break

@bot.event
async def on_guild_role_delete(role):
    guild = role.guild
    async for event in guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=3): # get last 3 incase someone create at exact time?
        if event.user is not bot.user:
            if event.target.id == role.id:
                try:
                    amount, last = bot.removing_roles[event.user.id]
                    if time() - last < 5: # 5 seconds between each deletion will be flagged
                        amount += 1
                        last = time()

                        if amount >= 3:
                            await event.user.ban(reason="For creating 3 or more roles at once.")
                            await log(guild.id, f"successfully banned {event.user.name} for deleting more than 3 roles at once.")
                            return

                    else: # otherwise reset the time
                        amount = 1
                        last = 0
                        
                    bot.removing_roles[event.user.id] = (amount, last)

                except KeyError:
                    bot.removing_roles[event.user.id] = (1, time())

                except Exception as error:
                    await log(guild.id, f"failed at {error} whilst calculating role deletion amounts.")
                    
                finally:
                    break

# commands
# setup
@bot.command()
@commands.guild_only()
async def help(ctx):
    if not await check_perms(ctx):
        return

    await show_help(ctx)
        
@bot.command()
@commands.guild_only()
async def set_prefix(ctx, new_prefix=None):
    if not await check_perms(ctx):
        return

    elif new_prefix is None:
        await ctx.send(f"{ctx.author.mention} you forgot to include a new prefix. Please use the command like this: **'{custom_prefixes[ctx.guild.id]}set_prefix <prefix>'**.")

    # write prefix
    elif await add_part("prefixes.txt", ctx.guild.id, new_prefix):
        custom_prefixes[ctx.guild.id] = new_prefix

        await ctx.send(f"Successfully updated guild prefix to: **'{new_prefix}'**.")
        await log(ctx.guild.id, f"Prefix updated to: '{new_prefix}'.")

@bot.command()
@commands.guild_only()
async def whitelisted(ctx):
    if not await check_perms(ctx):
        return 
    
    whitelist_embed = discord.Embed(title="Whitelisted Administrators", description="__Here are the admins able to use me:__\n\n", colour=discord.Color.light_grey())
    whitelist_embed.set_footer(text="Protecting your server!", icon_url=bot.user.avatar_url)

    async with aiofiles.open(f"{ctx.guild.id}_whitelist.txt", mode="r") as db:
        lines = await db.readlines()

    for i in range(len(lines)):
        admin = await ctx.guild.fetch_member(int(lines[i].strip("\n")))
        whitelist_embed.description += f"{i+1}) {admin.mention}\n"

    await ctx.send(embed=whitelist_embed)
    

@bot.command()
@commands.guild_only()
async def whitelist(ctx, member: discord.Member=None):
    if ctx.guild.owner != ctx.author:
        await ctx.send("Only the owner can perform this command.")
        return

    if member is None:
        await ctx.send(f"{ctx.author.mention} you forgot to include a member to whitelist. Please use the command like this: **'{custom_prefixes[ctx.guild.id]}whitelist <member>'**.")
        return

    if await register(f"{ctx.guild.id}_whitelist.txt", member.id):
        await ctx.send("Member has been successfully whitelisted.")
        await log(ctx.guild.id, f"Successfully whitelisted {member.name}.")

    else:
        await ctx.send("Member has already been whitelisted.")

@bot.command()
@commands.guild_only()
async def unwhitelist(ctx, member: discord.Member=None):
    if ctx.guild.owner != ctx.author:
        await ctx.send("Only the owner can perform this command.")
        return

    if member is None:
        await ctx.send(f"{ctx.author.mention} you forgot to include a member to unwhitelist. Please use the command like this: **'{custom_prefixes[ctx.guild.id]}unwhitelist <member>'**.")
        return

    elif member == ctx.guild.owner:
        await ctx.send(f"{ctx.author.mention} you cannot unwhitelist yourself!")
        return

    await remove_id(f"{ctx.guild.id}_whitelist.txt", member.id)
    await ctx.send("Member has been successfully unwhitelisted.")
    await log(ctx.guild.id, f"Successfully unwhitelisted {member.name}.")

@bot.command()
@commands.guild_only()
async def backup(ctx):
    if ctx.guild.owner != ctx.author:
        await ctx.send("Only the owner can perform this command.")
        return

    backup_embed = discord.Embed(title="Backup Server", description="*Are you sure you want to backup?*\n\n", color=discord.Color.teal())
    backup_embed.description += "> **What this backup does:**\n"
    backup_embed.description += "1) Saves your channels, roles...\n"
    backup_embed.description += "2) Saves your members roles.\n"
    backup_embed.description += "3) Allows you to completely reset your server to the most recent backup.\n\n"
    backup_embed.description += "> **What this backup doesn't do:**\n"
    backup_embed.description += "1) Save your members or bots.\n\n"
    backup_embed.description += "**This will overwrite your previous backup, are you sure you want to do this?**\n\n"
    backup_embed.description += "React with :white_check_mark: to confirm.\nReact with :no_entry_sign: to cancel."

    backup_embed.set_footer(text="Thank you for using me to protect your server!", icon_url=bot.user.avatar_url)
    confirmation = await ctx.send(embed=backup_embed)

    await confirmation.add_reaction(u"\u2705")
    await confirmation.add_reaction(u"\U0001F6AB")

    def check_reaction(reaction, user):
        return user == ctx.author and reaction.emoji in [u"\u2705", u"\U0001F6AB"]

    try:
        reaction, user = await bot.wait_for("reaction_add", check=check_reaction, timeout=60)
            
    except asyncio.TimeoutError:
        backup_embed.title = "Backup Server - TIMED OUT"
        backup_embed.color = discord.Color.red()
        await confirmation.edit(embed=backup_embed)

        await confirmation.clear_reactions()
        return

    else:
        if reaction.emoji == u"\U0001F6AB":
            backup_embed.title = "Backup Server - CANCELLED"
            backup_embed.color = discord.Color.red()
            await confirmation.edit(embed=backup_embed)

            await confirmation.clear_reactions()
            return

    try:
        await create_backup(ctx.guild)

        backup_embed.title = "Backup Server - SUCCESSFUL"
        backup_embed.color = discord.Color.green()
        await confirmation.edit(embed=backup_embed)
        await ctx.send(f"{ctx.author.mention} *backup successful,* to revert to this backup, use the command: **'{custom_prefixes[ctx.guild.id]}revert'**.")
        await log(ctx.guild.id, "Server was successfully backed up.")

    except Exception as error:
        backup_embed.title = "Backup Server - FAILED"
        backup_embed.color = discord.Color.red()
        await confirmation.edit(embed=backup_embed)
        await ctx.send(f"{ctx.author.mention} *backup failure.*")
        await log(ctx.guild.id, "Server failed to be backed up.")

    finally:
        await confirmation.clear_reactions()

@bot.command()
@commands.guild_only()
async def revert(ctx):
    if ctx.guild.owner != ctx.author:
        await ctx.send("Only the owner can perform this command.")
        return

    try:
        async with aiofiles.open(f"{ctx.guild.id}_backup.txt", mode="r") as backup:
            date = await backup.readline()
            date = date.strip("\n")

    except FileNotFoundError:
        await ctx.send("Could not find a backup to revert to.")
        return

    revert_embed = discord.Embed(title="Revert Server", description="*Are you sure you want to revert?*\n\n", color=discord.Color.teal())
    revert_embed.description += "> **What this revert does:**\n"
    revert_embed.description += "1) Reverts your channels and roles.\n"
    revert_embed.description += "2) Reverts your member's roles.\n"
    revert_embed.description += "3) Removes all previous channels and roles.\n\n"
    revert_embed.description += "> **What this revert doesn't do:**\n"
    revert_embed.description += "1) Revert your members or bots.\n"
    revert_embed.description += "2) ?\n\n"
    revert_embed.description += f"**This will use your most recent backup from '{date}', are you sure you want to do this?**\n\n"
    revert_embed.description += "React with :white_check_mark: to confirm.\nReact with :no_entry_sign: to cancel."

    revert_embed.set_footer(text="Thank you for using me to protect your server!", icon_url=bot.user.avatar_url)
    confirmation = await ctx.send(embed=revert_embed)

    await confirmation.add_reaction(u"\u2705")
    await confirmation.add_reaction(u"\U0001F6AB")

    def check_reaction(reaction, user):
        return user == ctx.author and reaction.emoji in [u"\u2705", u"\U0001F6AB"]

    try:
        reaction, user = await bot.wait_for("reaction_add", check=check_reaction, timeout=60)
            
    except asyncio.TimeoutError:
        revert_embed.title = "Revert Server - TIMED OUT"
        revert_embed.color = discord.Color.red()
        await confirmation.edit(embed=revert_embed)

        await confirmation.clear_reactions()
        return

    else:
        if reaction.emoji == u"\U0001F6AB":
            revert_embed.title = "Revert Server - CANCELLED"
            revert_embed.color = discord.Color.red()
            await confirmation.edit(embed=revert_embed)

            await confirmation.clear_reactions()
            return

    try:
        await revert_server(ctx)

        revert_embed.title = "Revert Server - SUCCESSFUL"
        revert_embed.color = discord.Color.green()
        await confirmation.edit(embed=revert_embed)
        await ctx.send(f"{ctx.author.mention} *revert successful*, thank you for using me.")
        await log(ctx.guild.id, "Server was successfully reverted.")
                
    except Exception as error:
        revert_embed.title = "Revert Server - FAILED"
        revert_embed.color = discord.Color.red()
        await confirmation.edit(embed=revert_embed)
        await ctx.send(f"{ctx.author.mention} *revert failure.* because of error: **{error}**")
        await log(ctx.guild.id, f"Server failed to revert because of {error}.")

    finally:
        await confirmation.clear_reactions()

# moderation
@bot.command()
@commands.guild_only()
async def kick(ctx, member: discord.Member=None, *, reason=None):
    if not await check_perms(ctx): # if they don't have permissions
        return
    
    if member is None:
        await ctx.send(f"{ctx.author.mention} you forgot to include a member. Please use the command like this: **'{custom_prefixes[ctx.guild.id]}kick <member> <reason>'**.")

    elif ctx.author != ctx.guild.owner or find_values(f"{ctx.guild.id}_whitelist.txt", member.id):
        await ctx.send(f"{ctx.author.mention} you cannot kick another whitelisted admin sorry!.")

    else:
        try:
            await member.kick(reason=reason)
            await ctx.send("Successfully kicked the given member.")
            await log(ctx.guild.id, f"Successfully kicked {member.name} for {reason}.")

        except:
            await ctx.send("Couldn't kick the given member.")
            await log(ctx.guild.id, f"Failed to kick {member.name} for {reason}.")

@bot.command() # clone of kick, except bans
@commands.guild_only()
async def ban(ctx, member: discord.Member=None, *, reason=None):
    if not await check_perms(ctx): # if they don't have permissions
        return
    
    if member is None:
        await ctx.send(f"{ctx.author.mention} you forgot to include a member. Please use the command like this: **'{custom_prefixes[ctx.guild.id]}ban <member> <reason>'**.")

    elif ctx.author != ctx.guild.owner or find_values(f"{ctx.guild.id}_whitelist.txt", member.id):
        await ctx.send(f"{ctx.author.mention} you cannot ban another whitelisted admin sorry!.")

    else:
        try:
            await member.ban(reason=reason)
            await ctx.send("Successfully banned the given member.")
            await log(ctx.guild.id, f"Successfully banned {member.name} for {reason}.")

        except:
            await ctx.send("Couldn't ban the given member.")
            await log(ctx.guild.id, f"Failed to ban {member.name} for {reason}.")
    
@bot.command()
@commands.guild_only()
async def mute(ctx, member: discord.Member=None, hours: int=0, *, reason=None): # reason for logging
    if not await check_perms(ctx):
        return 

    if member is None:
        await ctx.send(f"{ctx.author.mention} you forgot to include a member. Please use the command like this: **'{custom_prefixes[ctx.guild.id]}mute <member> <hours> <reason>'**.")
        return

    if hours < 1: # 0 or negative
        await ctx.send(f"{ctx.author.mention} you forgot to include an amount of hours to be muted for or set and invalid amount. Please use the command like this: **'{custom_prefixes[ctx.guild.id]}mute <member> <hours> <reason>'**.")
        return

    muted_role = None
    for role in ctx.guild.roles:
        if role.name == "Muted":
            muted_role = role

    if muted_role is None:
        muted_role = await ctx.guild.create_role(name="Muted", reason="Created a 'Muted' role to mute members.")
        
        permissions = discord.PermissionOverwrite(send_messages=False, send_tts_messages=False, connect=False)
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, overwrite=permissions)     

        await ctx.send("Created a 'Muted' role to mute members and edited all channel permissions for role.")
        await log(ctx.guild.id, "Created muted role and updated server permissions accordingly.")

    await member.add_roles(muted_role)
    await ctx.send(f"Successfully muted {member.mention} for {hours} hours.")
    await log(ctx.guild.id, f"Successfully muted {member.name} for {hours} hours for {reason}.")

    await asyncio.sleep(hours*3600)
    await member.remove_roles(muted_role)
    await ctx.send(f"{member.mention} has been unmuted.")
    await log(ctx.guild.id, f"Successfully unmuted {member.name} after {hours}.")

@bot.command()
@commands.guild_only()
async def unmute(ctx, member: discord.Member=None, *, reason=None):
    if not await check_perms(ctx):
        return 

    elif member is None:
        await ctx.send(f"You forgot to include a member to unmute. Please use the command like this: **'{custom_prefixes[ctx.guild.id]}unmute <member> <reason>'**.")

    else:
        for role in member.roles:
            if role.name == "Muted":
                await member.remove_roles(role, reason=reason)
                await ctx.send(f"Successfully unmuted {member.mention}.")
                await log(ctx.guild.id, f"Successfully unmuted {member.name}.")
                return

        await ctx.send("The given member was not muted in the first place.")

try:
    with open("bot_token.txt", "r") as file:
        token = file.read().strip("\n")
    bot.run(token)

except Exception as error:
    with open("bot_token.txt", "a") as file:
        print(f"Error when reading token : {error}")

hold = input("Press enter to close the program.")
