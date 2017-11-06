#
# Created by Klaus Ehrlinger on 31.10.2017.
#
#
# Created by Klaus Ehrlinger on 30.10.2017.
#
import sys
import time
import telepot
from telepot.loop import MessageLoop
import re
import User
from pprint import pprint

# Function being carried out when receiving a message
def handle(msg):
    # Extract as mauch info as possible and store everything in variables
    content_type, chat_type, chat_identifier = telepot.glance(msg)

    if content_type != 'text':
        return

    chat_dict = msg['chat']
    chat_name = chat_dict['title']
    chat_type = chat_dict['type']
    message_date = msg['date']
    sender_dict = msg['from']
    sender_first_name = sender_dict['first_name']
    sender_identifier = sender_dict['id']
    not_a_person = sender_dict['is_bot']
    sender_username = sender_dict['username']
    message_identifier = msg['message_id']
    message_text = msg['text']
    report_from = 3


    # Create a dict. Keys = username, Value = User object
    if sender_username not in users:
        users[sender_username] = User.Telegramuser(sender_username, sender_identifier)
    # TODO save and load the dict of users in chat

    # Check if sender is on mute list.
    # Delete message if muted.
    # Decrease mute of every muted member if sender is not in muted list.
        #Delete user from muted list if shamer.mute <= 0
    if sender_username in muted_users:
        bot.deleteMessage((chat_identifier, message_identifier))
    if sender_username not in muted_users:
        for shamer in muted_users:
            users[shamer].mute -= 1
        for shamer in muted_users:
            if users[shamer].mute <= 0:
                muted_users.remove(shamer)

    # Check for gets and awards gold/ silver to give away
    get_status = users[sender_username].get_the_gets(message_identifier, report_from)
    if get_status:
        award_message = str()
        if get_status >= 4:
            users[sender_username].gold += 1
            award_message = '%s was awarded gold for this get and has now %i gold to give away.' % (
            sender_username, users[sender_username].gold)
        if get_status <= 3:
            users[sender_username].silver += 1
            award_message = '%s was awarded silver for this get and has now %i silver to give away.' % (sender_username, users[sender_username].silver)
        get_message = 'Message ID: %s\n"%s"\n%s' % (str(message_identifier), message_text, award_message)
        bot.sendMessage(chat_identifier, get_message)

    # Punish
    if '/punish' in message_text:
        punish_message = message_text.split()
        perpetrator = punish_message[1][1:]
        if len(punish_message) == 4:
            sentence = punish_message[2]
            severity = int(punish_message[3])
            users[perpetrator].punish(sentence, severity)
        if perpetrator not in muted_users:
            muted_users.append(perpetrator)
        users[perpetrator].punish() # TODO change this so that only admins or better only luki can punish

    # Give gold
    if '/gold' in message_text:
        if users[sender_username].gold == 0:
            gold_message = 'You do not own gold, therefore you cannot give any. Score digits to get gold.'
            bot.sendMessage(chat_identifier, gold_message)
        else:
            gold_arguments = message_text.split()
            receiver = gold_arguments[1][1:]
            receiver_gold_status = users[receiver].receive_gold()
            giver_gold_status = users[sender_username].give_gold()
            gold_message = '%s\n%s' % (receiver_gold_status, giver_gold_status)
            bot.sendMessage(chat_identifier, gold_message)

    # Give silver
    if '/silver' in message_text:
        if users[sender_username].silver == 0:
            silver_message = 'You do not own silver, therefore you cannot give any. Score digits to get silver.'
            bot.sendMessage(chat_identifier, silver_message)
        else:
            silver_arguments = message_text.split()
            receiver = silver_arguments[1][1:]
            receiver_silver_status = users[receiver].receive_silver()
            giver_silver_status = users[sender_username].give_silver()
            silver_message = '%s\n%s' % (receiver_silver_status, giver_silver_status)
            bot.sendMessage(chat_identifier, silver_message)

    # Load
    #if '/load' in message_text:

TOKEN = ''  # this is the labthings bot
users = {}
muted_users = []
bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')


# Keep the program running.
while 1:
    time.sleep(1)
