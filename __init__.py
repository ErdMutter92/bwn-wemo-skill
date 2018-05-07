import os
import time
import datetime
from adapt.intent import IntentBuilder
from mycroft.util import extract_datetime
from mycroft.skills.core import MycroftSkill, intent_handler
from ouimeaux.environment import Environment

def timeTill(future):
    current = datetime.datetime.now()
    currentTime = time.mktime(current.timetuple()) + current.microsecond / 1E6
    futureTime = time.mktime(future.timetuple()) + future.microsecond / 1E6

    return futureTime - currentTime

class AdvancedWemoSkill(MycroftSkill):

    def __init__(self):
        super(AdvancedWemoSkill, self).__init__(name="AdvancedWemoSkill")

    def initialize(self):
        self.wemo = Environment(self.on_switch, self.on_motion);
        self.wemo.start();
        self.wemo.discover(seconds=3);

    def on_switch(self, switch):
        self.register_vocabulary(switch.name, "WemoSwitch");

    def on_motion(self, motion):
        self.register_vocabulary(switch.name, "WemoMotion");

    def get_toggle_label(self, state):
        return {
            0: "off",
            1: "on",
        }[state]

    @intent_handler(IntentBuilder("").require('Schedule').require("Toggle").require("WemoSwitch").require("Switch"))
    def handle_schedule_switch(self, message):
        utterence = message.data.get('utterance')
        eventTime = extract_datetime(utterence)
        self.schedule_event(self.handle_switch, eventTime[0], data=message.data)

        name = message.data.get('WemoSwitch')
        device = self.wemo.get_switch(name)
        self.speak_dialog('schedule.switch.toggle', data={"light": device.name, "toggle": method})

    @intent_handler(IntentBuilder("").require("Toggle").require("WemoSwitch").require("Switch"))
    def handle_switch(self, message):
        name = message.data.get('WemoSwitch')
        method = message.data.get('Toggle')
        device = self.wemo.get_switch(name)
        state = device.get_state()
        command = getattr(device, method)

        if self.get_toggle_label(state) == method:
            self.speak_dialog("switch.active", data={"light": device.name, "toggle": method})
        elif method == 'toggle':
            self.speak('Toggling ' + device.name)
            command()
        else:
            self.speak_dialog("switch.toggle", data={"light": device.name, "toggle": method})
            command()

    @intent_handler(IntentBuilder("").require("Find").require("WemoDevices"))
    def handle_discover(self, message):
        self.speak('Looking for wemo switches...')
        self.wemo.start();
        self.wemo.discover(seconds=5);
        switches = self.wemo.list_switches();
        self.speak_dialog('switch.found', data={"count": len(switches)})

    @intent_handler(IntentBuilder("").require("List").require("WemoDevices"))
    def handle_list_switches(self, message):
        switches = self.wemo.list_switches();
        self.speak_dialog("switch.known", data={"count": len(switches)});
        for index, switch in enumerate(switches, start=1):
            if (index == len(switches)):
                self.speak('and ' + switch)
            else:
                self.speak(switch)

    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, there is no need to override it.  If you DO
    # need to implement stop, you should return True to indicate you handled
    # it.
    def stop(self):
       return False

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return AdvancedWemoSkill()
