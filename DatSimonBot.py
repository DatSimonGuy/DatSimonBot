from telebot.async_telebot import AsyncTeleBot as atelebot
from dotenv import load_dotenv
import os
from utils import greetings
from utils.help import GetHelp
from utils.fileHandler import SaveData, ReadData
import utils.types as types
import asyncio
from telebot.types import ReactionTypeEmoji
from utils.converter import ToPollParams
import math
from utils.types import Group
from utils.games import ContextoGame
import re
import shutil

load_dotenv()

if not os.path.isdir("data"):
    os.mkdir("data")

if not os.path.isdir("data/groups"):
    os.mkdir("data/groups")

admins = os.environ.get("ADMINS").split(",")
token = os.environ.get("BOT_TOKEN")

bot = atelebot(token, parse_mode=None)

def GetLinkedGroup(chat_id):
    links = ReadData("links", 0) or {}
    try:
        return links[chat_id]
    except:
        return chat_id

def GetChatGroup(message) -> Group:
    group_id = GetLinkedGroup(message.chat.id)
    group = ReadData(f"{group_id}/group_info", 1)
    
    if not isinstance(group, Group):
        group = Group("", id=group_id)
    
    return group

@bot.message_handler(commands=['start'])
async def Greeting(message):
    greeting = greetings.RandomGreeting()
    
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if GetChatGroup(message) is None:
            new_group = types.Group(name=message.chat.title, id=message.chat.id)
            new_group.saveSelf()
        elif GetChatGroup(message).name != message.chat.title:
            GetChatGroup(message).name = message.chat.title
            GetChatGroup(message).saveSelf()
    
    await bot.send_message(message.chat.id, greeting)

@bot.message_handler(content_types=['new_chat_members'])
async def JoinGroup(message):
    if bot.username in message.new_chat_members:
        if message.chat.type == "group" or message.chat.type == "supergroup":
            if GetChatGroup(message) is None:
                new_group = types.Group(name=message.chat.title, id=message.chat.id)
                new_group.saveSelf()
            elif GetChatGroup(message).name != message.chat.title:
                GetChatGroup(message).name = message.chat.title
                GetChatGroup(message).saveSelf()

@bot.message_handler(commands=['help'])
async def Help(message):
    reply = GetHelp()

    if len(reply):
        await bot.reply_to(message, reply)

current_games = {}

@bot.message_handler(commands=['new_contexto'])
async def Contexto(message):
    group = GetChatGroup(message)
    
    current_games[group.id] = ContextoGame.initGame()

    await bot.reply_to(message, "Contexto game started")

@bot.message_handler(commands=['c'])
async def Guess(message):
    group = GetChatGroup(message)

    try:
        word = message.text.replace("/c ", "")

        try:
            score = current_games[group.id].getScore(word)
        except KeyError:
                await bot.send_message(message.chat.id, "No game currently")
                return
        except Exception as e:
            if str(e) == "Unfunny":
                await bot.send_message(message.chat.id, f"@{message.from_user.username} Unfunny")
                return
            if str(e) == "WON":
                await bot.send_message(message.chat.id, f"@{message.from_user.username} You won it was {word}")
                del current_games[group.id]
                return
            else:
                print(f"Exception occured during contexto game: {e}")
                return

        await bot.delete_message(message.chat.id, message.id)
        await bot.send_message(message.chat.id, f"{word}: {score}")

        for message_id in current_games[group.id].last_messages:
            try:
                await bot.delete_message(message.chat.id, message_id)
            except:
                pass

        sent_message = await bot.send_message(message.chat.id, str(current_games[group.id]))
        current_games[group.id].last_messages.append(sent_message.id)
    except KeyError:
        await bot.reply_to(message, "No game currently started")

@bot.message_handler(commands=['hint'])
async def GetContextoHint(message):
    group = GetChatGroup(message)

    try:
        hint = current_games[group.id].getHint()
    except KeyError:
        await bot.reply_to(message, "No game currently started")
        return
    except Exception as e:
        if str(e) == "CANT":
            await bot.reply_to(message, "Can't get hint")
            return
        else:
            print(f"Exception occured during contexto game: {e}")
            return

    await bot.delete_message(message.chat.id, message.id)
    await bot.send_message(message.chat.id, f"The hint is: {hint}")

@bot.message_handler(commands=['show'])
async def Show(message):
    group = GetChatGroup(message)

    params = message.text.split()

    content, arrows = group.show(params)
    
    await bot.send_message(message.chat.id, content, reply_markup=arrows)

@bot.message_handler(commands=['add'])
async def Add(message):
    group = GetChatGroup(message)

    params = message.text.split()

    reply = group.add(params, message)
    group.saveSelf()

    if isinstance(reply, tuple):
        if reply[1] is None:
            await bot.send_message(message.chat.id, reply[0])
            return
        await bot.send_message(message.chat.id, reply[0], reply_markup=reply[1])
        return
    
    if reply is None:
        await bot.reply_to(message, "Wrong input, please try again")
        return
    
    if reply != "Done":
        await bot.reply_to(message, reply)
    else:
        await bot.set_message_reaction(message.chat.id, message.id, [ReactionTypeEmoji("👍")])

@bot.message_handler(commands=['remove'])
async def Remove(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    reply = group.remove(params, message)
    
    if isinstance(reply, tuple):
        await bot.send_message(message.chat.id, reply[0], reply_markup=reply[1])
        return
    
    if reply != "Done":
        await bot.reply_to(message, reply)
    else:
        await bot.set_message_reaction(message.chat.id, message.id, [ReactionTypeEmoji("👍")])
        group.saveSelf()

@bot.message_handler(commands=['edit'])
async def Edit(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    reply, keyboard = group.edit(params)
    
    await bot.reply_to(message, reply, reply_markup=keyboard)

@bot.message_handler(commands=['link'])
async def Link(message):
    group = GetChatGroup(message)
    if message.chat.type != "group" and message.chat.type != "supergroup":
        params = message.text.split()

        if len(params) == 1:
            await bot.reply_to(message, "Please provide the group id")
            return

        group.link(params[1])

        await bot.reply_to(message, "Group linked")
    else:
        await bot.reply_to(message, f"Sent this to me in private chat:\n`/link {group.id}`", parse_mode="MarkdownV2")

@bot.message_handler(commands=['plan'])
async def Plan(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    reply, buttons = group.show(["/show", "plan"] + params[1:])
    
    await bot.send_message(message.chat.id, reply, reply_markup=buttons)

@bot.message_handler(commands=['status'])
async def Status(message):
    group = GetChatGroup(message)
    
    reply = group.status()
    
    if reply is None:
        await bot.reply_to(message, "No status")
    else:
        await bot.reply_to(message, reply)

@bot.message_handler(commands=['kys'])
async def TurnOff(message):
    if str(message.from_user.username) in admins:
        await bot.send_message(message.chat.id, "Shutting down")
        exit()

@bot.message_handler(commands=['export_data'])
async def Export(message):
    if str(message.from_user.username) in admins:
        shutil.copyfile(".env", "data/.env")
        data = shutil.make_archive("temp/data_export", "zip", "data")
        with open(data, "rb") as data:
            await bot.send_document(message.chat.id, data)
        os.unlink("data/.env")
        os.unlink("temp/data_export.zip")

@bot.message_handler(commands=['import_data'])
async def Import(message):
    if not os.path.isdir("temp"):
        os.mkdir("temp")
    if str(message.from_user.username) in admins:
        if message.reply_to_message is not None:
            if message.reply_to_message.document is not None:
                file_id = message.reply_to_message.document.file_id
                file = await bot.get_file(file_id)
                file_path = file.file_path
                with open("temp/data_import.zip", "wb") as data:
                    data.write(await bot.download_file(file_path))
                if os.path.isdir("data"):
                    shutil.rmtree("data")
                shutil.unpack_archive("temp/data_import.zip", "data")
                shutil.move("data/.env", ".env")
                await bot.reply_to(message, "Data imported")
                os.unlink("temp/data_import.zip")
            else:
                await bot.reply_to(message, "Please reply to a document")
        else:
            await bot.reply_to(message, "Please reply to a document")

@bot.message_handler(commands=['add_lesson'])
async def AddLesson(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    reply, keyboard = group.addLesson(["/add", "lesson"] + params[1:])
    
    await bot.reply_to(message, reply, reply_markup=keyboard)

@bot.message_handler(commands=['remove_lesson'])
async def RemoveLesson(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    reply, keyboard = group.removeLesson(["/remove", "lesson"] + params[1:])
    
    await bot.reply_to(message, reply, reply_markup=keyboard)

@bot.message_handler(commands=['gurasay'])
async def GuraSay(message):
    text = " ".join(word for word in message.text.split()[1:])
    if len(text) == 0:
        await bot.reply_to(message, "Please provide text")
    if len(text) > 10:
        await bot.reply_to(message, "Max 10 characters")
        return
    else:
        alphabet = ReadData("sticker_alphabet")
        for letter in str(text).upper():
            if letter == " ":
                continue
            else:
                await bot.send_sticker(message.chat.id, alphabet[letter])

@bot.message_handler(commands=['append_role'])
async def AppendRole(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    reply, keyboard = group.appendRole(params[1])
    
    if keyboard is None:
        await bot.reply_to(message, reply)
        return
    
    await bot.reply_to(message, reply, reply_markup=keyboard)

@bot.message_handler(commands=['remove_role'])
async def RemoveRole(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    reply, keyboard = group.removeRole(params[1])
    
    if keyboard is None:
        await bot.reply_to(message, reply)
        return
    
    await bot.reply_to(message, reply, reply_markup=keyboard)

@bot.message_handler(commands=['ping'])
async def PingRole(message):
    group = GetChatGroup(message)
    if "/ping" in message.text:
        roles = [message.text.split()[1]]
    else:
        roles = re.findall(r"@.*", message.text)
    for person in group.people.values():
        for role in roles:
            if hasattr(person, "roles"):
                if role.replace("@", "") in person.roles:
                    await bot.send_message(message.chat.id, f"@{person.nick}")
            else:
                person.roles = []

@bot.message_handler(commands=['everyone'])
async def PingEveryone(message):
    group = GetChatGroup(message)
    
    people = group.people
    
    if len(people) == 0:
        await bot.reply_to(message, "Only added people are pinged add using /add them or /add me")
        return
    
    reply = "\n".join([f"@{person.nick}" for person in people.values()])
    
    await bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=['add_gif'])
async def AddGif(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    try:
        if message.reply_to_message is not None:
            group.gifs[params[1]] = message.reply_to_message.animation.file_id
            group.saveSelf()
            await bot.reply_to(message, "Gif added")
    except IndexError:
        await bot.reply_to(message, "Please name the gif")

@bot.message_handler(commands=['show_gifs'])
async def ShowGifs(message):
    group = GetChatGroup(message)

    gifs = group.show(["/show", "gifs"])[0]

    await bot.send_message(message.chat.id, gifs)

@bot.message_handler(commands=['remove_gif'])
async def RemoveGif(message):
    group = GetChatGroup(message)

    params = message.text.split()

    if message.reply_to_message is not None:
        try:
            gif_name = params[1]
            group.gifs.remove(gif_name)
            group.saveSelf()
            await bot.reply_to(message, "Gif removed")
        except IndexError:
            await bot.reply_to(message, "Please name the gif")

@bot.message_handler(commands=['send_gif'])
async def SendGif(message):
    group = GetChatGroup(message)

    params = message.text.split()

    try:
        gif_name = params[1]
        gif = group.gifs[gif_name]
        await bot.send_animation(message.chat.id, gif)
    except IndexError:
        await bot.reply_to(message, "Please name the gif")
    except KeyError:
        await bot.reply_to(message, "Gif not found")

@bot.message_handler(commands=['add_sticker'])
async def AddSticker(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    try:
        if message.reply_to_message is not None:
            group.stickers[params[1]] = message.reply_to_message.sticker.file_id
            group.saveSelf()
            await bot.reply_to(message, "Sticker added")
    except IndexError:
        await bot.reply_to(message, "Please name the sticker")

@bot.message_handler(commands=['show_stickers'])
async def ShowStickers(message):
    group = GetChatGroup(message)

    stickers = group.show(["/show", "stickers"])[0]

    await bot.send_message(message.chat.id, stickers)

@bot.message_handler(commands=['remove_sticker'])
async def RemoveSticker(message):
    group = GetChatGroup(message)

    params = message.text.split()

    if message.reply_to_message is not None:
        try:
            sticker_name = params[1]
            group.stickers.remove(sticker_name)
            group.saveSelf()
            await bot.reply_to(message, "Sticker removed")
        except IndexError:
            await bot.reply_to(message, "Please name the sticker")

@bot.message_handler(commands=['send_sticker'])
async def SendSticker(message):
    group = GetChatGroup(message)

    params = message.text.split()

    try:
        sticker_name = params[1]
        sticker = group.stickers[sticker_name]
        await bot.send_sticker(message.chat.id, sticker)
    except IndexError:
        await bot.reply_to(message, "Please name the sticker")
    except KeyError:
        await bot.reply_to(message, "Sticker not found")

@bot.message_handler(commands=['poll'])
async def CreatePoll(message):
    params = message.text.split()
    try:
        poll_parameters, quiz, multichoice, correct, anonymous = ToPollParams(params[1:])
    except IndexError:
        await bot.reply_to(message, "Please provide question and answers")
        return

    poll_parameters[0] = poll_parameters[0]

    await bot.delete_message(message.chat.id, message.id)
    await bot.send_poll(message.chat.id, poll_parameters[0], poll_parameters[1:], correct_option_id=correct if quiz else None, is_anonymous=anonymous, type="quiz" if quiz else "regular", allows_multiple_answers=multichoice)

@bot.message_handler(commands=['join'])
async def Joingroup(message):
    group = GetChatGroup(message)

    params = message.text.split()
    
    if len(params) == 1:
        await bot.reply_to(message, "Please provide the group name")
        return
    
    if len(params) == 4:
        reply, keyboard = group.join(params[1], message.from_user, params[2], params[3])
    else:
        reply, keyboard = group.join(params[1], message.from_user)
        if keyboard is None:
            await bot.reply_to(message, reply)
            return
    
    group.saveSelf()
    
    await bot.reply_to(message, reply, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda x: "-" in x.data or "+" in x.data)
async def TurnPage(x):
    group = GetChatGroup(x.message)
    
    params = ["/show", "activities"]
    
    page_before = int(x.data[1:])
    page = (int(x.data[1:]) + 1 if x.data[0] == "+" else -1) % math.ceil(len(group.activities)/6)
    
    if page == page_before:
        return
    
    content, arrows = group.show(params, page)
    
    await bot.edit_message_text(content, x.message.chat.id, x.message.id, reply_markup=arrows)

@bot.callback_query_handler(func=lambda x: "EDIT_LESSON" in x.data)
async def EditLesson(x):
    group = GetChatGroup(x.message)
    
    params = x.data.split("/")
    
    if len(params) == 2:
        major = params[1]
        
        reply, keyboard = group.editLesson(major)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 3:
        major = params[1]
        sub_group = params[2]

        reply, keyboard = group.editLesson(major, sub_group)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 4:
        major = params[1]
        sub_group = params[2]
        day = int(params[3])

        reply, keyboard = group.editLesson(major, sub_group, day)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 5:
        major = params[1]
        sub_group = params[2]
        day = int(params[3])
        idx = int(params[4])

        reply, keyboard = group.editLesson(major, sub_group, day, idx)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 6:
        if params[5] != "subject" and params[5] != "type":
            group.requests[x.from_user.id] = x.data
            group.saveSelf()
            await bot.edit_message_text("Give me the change value (do this in [])", x.message.chat.id, x.message.id)
        else:
            reply, keyboard = group.editLesson(params[1], params[2], int(params[3]), int(params[4]), params[5])
            await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    else:
        group.editLesson(params[1], params[2], int(params[3]), int(params[4]), params[5], params[6])
        await bot.delete_message(x.message.chat.id, x.message.id)
        await bot.send_message(x.message.chat.id, "👍")

@bot.callback_query_handler(func=lambda x: "JOIN" in x.data)
async def Join(x):
    group = GetChatGroup(x.message)
    
    group.requests[x.from_user.id] = x.data
    group.saveSelf()

    await bot.delete_message(x.message.chat.id, x.message.id)
    await bot.send_message(x.message.chat.id, "Please tell me your school index in []")
  
@bot.callback_query_handler(func=lambda x: "EDIT_ACTIVITY" in x.data)
async def EditActivity(x):
    group = GetChatGroup(x.message)
    
    params = x.data.split("/")
    
    if len(params) == 2:
        idx = int(params[1])

        reply, keyboard = group.editActivity(idx)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    else:
        group.requests[x.from_user.id] = x.data
        group.saveSelf()
        await bot.edit_message_text("Give me the change value (do this in [])", x.message.chat.id, x.message.id)

@bot.callback_query_handler(func=lambda x: "ADD_LESSON" in x.data)
async def AddLesson(x):
    group = GetChatGroup(x.message)
    
    params = x.data.split("/")
    
    if len(params) == 2:
        major = params[1]

        reply, keyboard = group.addLesson(major)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 3:
        major = params[1]
        day = int(params[2])

        reply, keyboard = group.addLesson(major, day)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 4:
        major = params[1]
        day = int(params[2])
        sub_group = params[3]

        reply, keyboard = group.addLesson(major, day, sub_group)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 5:
        major = params[1]
        day = int(params[2])
        sub_group = params[3]
        subject = params[4]

        reply, keyboard = group.addLesson(major, day, sub_group, subject)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 6:
        major = params[1]
        day = int(params[2])
        sub_group = params[3]
        subject = params[4]
        type = params[5]

        reply, keyboard = group.addLesson(major, day, sub_group, subject, type)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 7:
        group.requests[x.from_user.id] = x.data
        group.saveSelf()
        await bot.edit_message_text("Give me the lesson details \- beginning, ending and classroom \(do this in `[00:00, 00:00, classroom]`\)", x.message.chat.id, x.message.id, parse_mode="MarkdownV2")

@bot.callback_query_handler(func=lambda x: "REMOVE_LESSON" in x.data)
async def RemoveLesson(x):
    group = GetChatGroup(x.message)
    
    params = x.data.split("/")
    
    if len(params) == 2:
        major = params[1]

        reply, keyboard = group.removeLesson(major)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 3:
        major = params[1]
        sub_group = params[2]

        reply, keyboard = group.removeLesson(major, sub_group)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 4:
        major = params[1]
        sub_group = params[2]
        day = int(params[3])

        reply, keyboard = group.removeLesson(major, sub_group, day)

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=keyboard)
    elif len(params) == 5:
        major = params[1]
        sub_group = params[2]
        day = int(params[3])
        idx = int(params[4])

        group.removeLesson(major, sub_group, day, idx)
        group.saveSelf()

        await bot.edit_message_text("K", x.message.chat.id, x.message.id, reply_markup=None)
    
@bot.callback_query_handler(func=lambda x: "SHOW_PLAN" in x.data)
async def ShowPlan(x):
    group = GetChatGroup(x.message)
    
    params = x.data.split("/")
    
    if len(params) == 2:
        major = params[1]

        reply, buttons = group.show(["/", "plan", major])

        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=buttons)
    elif len(params) == 3:
        major = params[1]
        sub_group = params[2]

        reply, buttons = group.show(["/", "plan", major, sub_group])
        
        await bot.edit_message_text(reply, x.message.chat.id, x.message.id, reply_markup=buttons)

@bot.callback_query_handler(func=lambda x: "ADD_ROLE" in x.data)
async def AddRole(x):
    group = GetChatGroup(x.message)
    
    params = x.data.split("/")
    
    role = params[2]
    
    person_id = int(params[1])
    
    if not hasattr(group.people[person_id], "roles"):
        group.people[person_id].roles = []
    
    group.people[person_id].roles.append(role)
    
    await bot.delete_message(x.message.chat.id, x.message.id)
    await bot.send_message(x.message.chat.id, f"Role {role} added to {group.people[person_id].nick}")
    group.saveSelf()

@bot.callback_query_handler(func=lambda x: "REMOVE_ROLE" in x.data)
async def RemoveRole(x):
    group = GetChatGroup(x.message)
    
    params = x.data.split("/")
    
    role = params[2]
    
    person_id = int(params[1])
    
    group.people[person_id].roles.remove(role)
    
    await bot.delete_message(x.message.chat.id, x.message.id)
    await bot.send_message(x.message.chat.id, f"Role {role} added to {group.people[person_id].nick}")
    group.saveSelf()

@bot.callback_query_handler(func=lambda x: "CANCEL" in x.data)
async def DeleteMessage(x):
    await bot.delete_message(x.message.chat.id, x.message.id)

@bot.message_handler(content_types=['text'], func=lambda x: "[" in x.text and "]" in x.text)
async def ChangeActivity(x):
    group = GetChatGroup(x)
    
    request = group.requests[x.from_user.id]
    
    if request is None:
        return
    
    params = request.split("/")
    
    if params[0] == "EDIT_ACTIVITY":
        idx = int(params[1])
        type = params[2]
        value = x.text.replace("[", "").replace("]", "").replace(" ", "")

        group.editActivity(idx, type, value)
    elif params[0] == "ADD_LESSON":
        major = params[1]
        day = params[2]
        sub_group = params[3]
        subject = params[4]
        type = params[5]
        repeated = int(params[6])
        lesson = x.text.replace("[", "").replace("]", "").replace(" ", "").split(",")
        
        group.addLesson(major, day, sub_group, subject, type, repeated, types.Lesson(lesson[0], lesson[1], subject, type, lesson[2], 1, True, 2 if repeated else 1))
    elif params[0] == "JOIN":
        if x.reply_to_message is not None:
            group.join(params[1], x.reply_to_message.from_user, params[2], x.text.replace("[", "").replace("]", "").replace(" ", ""))
        else:
            await bot.reply_to(x, "Please reply again to the user you want to join")
    elif params[0] == "EDIT_LESSON":
        major = params[1]
        sub_group = params[2]
        day = int(params[3])
        idx = int(params[4])
        type = params[5]
        value = x.text.replace("[", "").replace("]", "").replace(" ", "")
        
        group.editLesson(major, sub_group, day, idx, type, value)

    del group.requests[x.from_user.id]
    group.saveSelf()
    
    await bot.set_message_reaction(x.chat.id, x.id, [ReactionTypeEmoji("👍")])

@bot.message_handler(content_types=['text'], func=lambda x: x.text[0] == '`')
async def StickerAlias(x):
    group = GetChatGroup(x)
    
    try:
        sticker = group.stickers[x.text[1:]]
    except KeyError:
        await bot.reply_to(x, "Sticker not found")
        return
    
    await bot.delete_message(x.chat.id, x.id)
    await bot.send_sticker(x.chat.id, sticker)

@bot.message_handler(content_types=['text'], func=lambda x: x.text[0] == '&')
async def GifAlias(x):
    group = GetChatGroup(x)
    
    try:
        gif = group.gifs[x.text[1:]]
    except KeyError:
        await bot.reply_to(x, "Gif not found")
        return

    await bot.delete_message(x.chat.id, x.id)
    await bot.send_animation(x.chat.id, gif)

@bot.message_handler(content_types=['document', 'video', 'photo', 'text'])
async def SaveFile(message):
    if message.text is not None:
        if "@everyone" in message.text or "@e" in message.text:
            await PingEveryone(message)
        if "@" in message.text:
            await PingRole(message)
    if message.forward_date is not None and message.chat.type == "group" or message.chat.type == "supergroup":
        unique_id = None
        
        if message.document is not None:
            unique_id = message.document.file_unique_id
        elif message.photo is not None:
            unique_id = message.photo[0].file_unique_id
        elif message.video is not None:
            unique_id = message.video.file_unique_id
        
        if unique_id is None:
            return

        group = GetChatGroup(message)
        last_files = ReadData(f"{group.id}/last_files", 1) or {}
        if unique_id in last_files:
            await bot.reply_to(message, f"{last_files[unique_id]}")
            await bot.reply_to(message, f"You retar please keep yourself safe")
            return
        last_files[unique_id] = f"https://t.me/c/{str(message.chat.id)[4:]}/{message.message_id}"
        SaveData(f"{group.id}/last_files", last_files, 1)

@bot.message_handler(content_types=['new_chat_members'])
async def AddPeople(message):
    group = GetChatGroup(message)
    
    for user in message.new_chat_members:
        person = types.CreatePersonFromUser(user)
        group.addPerson(person)
    
    group.saveSelf()

@bot.message_handler(content_types=['left_chat_member'])
async def RemovePeople(message):
    group = GetChatGroup(message)
    
    group.removePeople([message.left_chat_member.id])
    
    group.saveSelf()

@bot.message_handler(content_types=['new_chat_title'])
async def ChangegroupName(message):
    chat_id = message.chat.id
    new_title = message.chat.title
    group = GetChatGroup(chat_id)
    group.name = new_title
    group.saveSelf()

if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())