#
# Created by Klaus Ehrlinger on 31.10.2017.
#
#
# Created by Klaus Ehrlinger on 30.10.2017.
#
import time
import telepot
from telepot.loop import MessageLoop
import User
import json
import logging
import pathlib

# TODO put this in a function?
# Configure the logger - no idea what i am actually doing
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
    # create a file handler
log_handler = logging.FileHandler('bot.log')
log_handler.setLevel(logging.DEBUG)
    # create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)
    # add the handlers to the logger
logger.addHandler(log_handler)

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

    # Check if sender is on mute list.
    # Delete message if muted.
    # Decrease mute of every muted member if sender is not in muted list.
        #Delete user from muted list if shamer.mute <= 0
    if sender_username in muted_users:
        bot.deleteMessage((chat_identifier, message_identifier))
        return
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
        if sender_username == 'Luciferase':
            punish_message = message_text.split()
            perpetrator = punish_message[1][1:]
            if len(punish_message) == 4:
                sentence = punish_message[2]
                severity = int(punish_message[3])
                users[perpetrator].punish(sentence=sentence, severity=severity)
                punish_answer = '@%s was punished to \'%s\' for the length of %i messages.' % (perpetrator, sentence, severity)
                bot.sendMessage(chat_identifier, punish_answer)
            if perpetrator not in muted_users:
                muted_users.append(perpetrator)
            users[perpetrator].punish()
            punish_answer = '@%s was punished to \'mute\' for the length of 5 messages.' % perpetrator
            bot.sendMessage(chat_identifier, punish_answer)
        else:
            punish_answer = 'Only Luki can mute users, this was decided to prevent mutually assured destruction.'
            bot.sendMessage(chat_identifier, punish_answer)

    # Give gold
    if '/gold' in message_text:
        if users[sender_username].gold == 0:
            gold_message = 'You do not own gold, therefore you cannot give any. Score digits to get gold.'
            bot.sendMessage(chat_identifier, gold_message)
        else:
            gold_arguments = message_text.split()
            # If no receiver is specified, then an error is returned.
            if len(gold_arguments) <= 1:
                missing_receiver = 'You did not specify a receiver for your gold, the correct format is\n' \
                                   '\'/gold @User\''
                bot.sendMessage(chat_identifier, missing_receiver)
                return
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
            if len(silver_arguments) <= 1:
                missing_receiver = 'You did not specify a receiver for your silver, the correct format is\n' \
                                   '\'/silver @User\''
                bot.sendMessage(chat_identifier, missing_receiver)
                return
            receiver = silver_arguments[1][1:]
            receiver_silver_status = users[receiver].receive_silver()
            giver_silver_status = users[sender_username].give_silver()
            silver_message = '%s\n%s' % (receiver_silver_status, giver_silver_status)
            bot.sendMessage(chat_identifier, silver_message)

    if '/pingall' in message_text:
        all_user_ids = ["@"+x for x in users.keys()]
        bot.sendMessage(chat_identifier, "\n".join(all_user_ids))

#Initialise the bot and some variables needed for operation
TOKEN = ''  # this is the token you get from BotFather
users = {}
muted_users = []

# If a save-file exists, create the users dict from it
save_file_location = pathlib.Path('./save.json')
if save_file_location.is_file():
    with open ('save.json', 'r') as fh_load_users:
        loaded_users = json.load(fh_load_users)
        logger.info('Imported from save-file:\n%s' % loaded_users)
        # Load the values of every entry of the save file into the users dict
    for u in loaded_users:
        user = loaded_users[u]
        loaded_user_name = user['name']
        loaded_user_id = user['id']
        loaded_user_mute = user['mute']
        loaded_user_gold = user['gold']
        loaded_user_silver = user['silver']
        loaded_user_gold_rec = user['gold_received']
        loaded_user_silver_rec = user['silver_received']
        users[loaded_user_name] = User.Telegramuser(user_name=loaded_user_name, user_id=loaded_user_id,
                                                    user_mute=loaded_user_mute, user_gold=loaded_user_gold,
                                                    user_silver=loaded_user_silver,
                                                    user_gold_rec=loaded_user_gold_rec,
                                                    user_silver_rec=loaded_user_silver_rec)
        # If the user is being muted, append his name to the muted users list
        if loaded_user_mute > 0:
            muted_users.append(loaded_user_name)
else:
    logger.info('No save-file found, generating and continuing...')
    
# Start the bot and pass every message to the handle function
bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
logger.info('Listening ...')

# Save the status of the users every 150 seconds in a .json-file
while 1:
    time.sleep(180)
    with open ('save.json', 'w') as fh_save_users:
        # default=lambda o: o.__dict__ changes the Telegramuser-object to a dict
        fh_save_users.write(json.dumps(users, default=lambda o: o.__dict__))
        logger.info("saved")
