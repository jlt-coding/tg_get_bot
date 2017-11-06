#
# Created by Klaus Ehrlinger on 31.10.2017.
#
import re

class Telegramuser():
    def __init__(self, user_name, user_id):
        self.name = user_name
        self.id = user_id
        self.mute = 0
        self.gold = 0
        self.silver = 0
        self.gold_received = 0
        self.silver_received = 0

    # Load
    def load(self):
        config_file_path = '/conf/%s' % self.name
        with open (config_file_path, 'r') as fh_config:
            loaded_attributes = fh_config.readline().split()
            self.name = loaded_attributes[0]
            self.gold = loaded_attributes[1]
            self.silver = loaded_attributes[2]
            self.gold_received = loaded_attributes[3]
            self.silver_received = loaded_attributes[4]

    # Save
    def save(self):
        config_file_path = '/conf/%s' % self.name
        save_string = '%s %s %s %s %s' % (self.name, self.gold, self.silver, self.gold_received, self.silver_received)
        with open(config_file_path, 'w') as fh_config:
            fh_config.write(save_string)

    # Gets
    def get_the_gets(self, message_identifier, report_from):
        digit_regex = re.compile(r"(\d)(\1+)")
        inverted_msg_id = str(message_identifier)[::-1]
        try:
            # Search for the regex in the inverted message id
            get = digit_regex.match(inverted_msg_id)
            # If the length of the match is longer than the minimum length GETTHRESHOLD, return True
            if len(get.group()) >= report_from:
                return len(get.group())
                # If the digit_regex does not match in the message id an AttributeError will be raised. Ignore this
        except AttributeError:
            pass

    # Punish
    def punish(self, sentence='mute', severity=5):
        if sentence == 'mute':
            self.mute += severity
            return
        # TODO improve this function

    # Gold
    def receive_gold(self):
        self.gold_received += 1
        return '%s just received gold! You were awarded gold %i times.' % (self.name, self.gold_received)

    def give_gold(self):
        self.gold -= 1
        return '%s gave gold, he has %i gold left to give away.' % (self.name, self.gold)

    # Silver
    def receive_silver(self):
        self.silver_received += 1
        receive_silver_message = '%s just received silver! You were awarded silver %i times.' % (self.name, self.silver_received)
        return receive_silver_message

    def give_silver(self):
        self.silver -= 1
        give_silver_message = '%s gave silver, he has %i silver left to give away.' % (self.name, self.silver)
        return give_silver_message
