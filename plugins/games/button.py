# clone of http://willyoupressthebutton.com/
# I make lots of obvious mistakes when I'm sleepy
# inb4 obvious mistakes

import sys
import json
import random
import math
import requests
import re
import random
from util.text import unescape, lineify

from bot.events import Callback, command

class Wyp(Callback):
    QFILE = "wyps.json"

    def __init__(self, server):
        self.qfile = server.get_config_dir(self.QFILE)
        try:
            with open(self.qfile) as f:
                self.wyps = json.load(f)
        except:
            self.wyps = {}
        self.active = {}
        super().__init__(server)

    @command("addbutton makebutton addwyp makewyp", r"(.+)")
    def queue(self, server, msg, item):
        wyp = self.wyps.setdefault(item, {})
        self.active[server.lower(msg.context)] = item
        self.save()
        return "\x0306│\x03 Button added"

    @command("fuckbutton destroy ripbutton attack")
    def destroy(self, server, msg):
        item = self.active.setdefault(server.lower(msg.context), "")
        nick = msg.address.nick
        wyp = self.wyps.setdefault(item, {})
        wyp[server.lower(nick)] = None
        self.save()
        return "\x0306│\x03 You attack the button. " + self.displayPresses(item)    

    @command("destroyforcibly", admin=True)
    def destroyForcibly(self, server, msg):
        item = self.active.setdefault(server.lower(msg.context), "")
        del self.wyps[item]
        self.save()
        return "\x0306│\x03 Critical hit! You managed to destroyForcibly the button."      

    @command("lick")
    def lick(self, server, msg):
        item = self.active.setdefault(server.lower(msg.context), "")
        observations = """tastes slightly salty
is already quite moist
has a metalic tang
was okay
sends a tingle through your tongue
quivers in delight
needs salt
blushes a little
has a rather exquisite texture
has certain fruity notes
licks you back
gives off some smoke
shocks your face
drips
glistens
jiggles
pulses brightly
relents momentarily under the pressure
has a bit of an earthy aftertaste
tastes delightful
smells wonderful
has a rather elegant mouthfeel
twitches like a robotic nipple
smells industrial
tastes unsettlingly creamy
smells buttony
is quite bitter""".split("\n")
        return "\x0306│\x03 You lick the button. It %s. %s" % (random.choice(observations), self.displayPresses(item))
   
    @command("whatton")
    def whatton(self, server, msg):
        return self.fancydisplay(server.lower(msg.context))

    @command("button wyptb wyp willyoupressthebutton willyoupress")
    def button(self, server, msg):
        nick = msg.address.nick
        # Check if we need any new buttons
        if all(i for i in self.wyps.values()):
            page = requests.get("http://m.willyoupressthebutton.com/").text
            cond = unescape(re.findall('<div class="rect" id="cond">(.+)</div>', page)[0])
            res = unescape(re.findall('<div class="rect" id="res">(.+)</div>', page)[0])
            cond = cond[0].upper() + cond[1:].rstrip(" ").rstrip(".")
            res = res[0].lower() + res[1:]
            wyp = self.wyps.setdefault("%s but %s" % (cond, res), {})
            self.save()
        # Reduce probability of already-answered buttons
        buttons = [i for i in self.wyps if (server.lower(nick) not in self.wyps[i] and i != self.active)]
        self.active[server.lower(msg.context)] = random.choice(buttons)
        return self.display(server.lower(msg.context))

    @command("press yes bonk boop touch")
    def press(self, server, msg):
        item = self.active.setdefault(server.lower(msg.context), "")
        nick = msg.address.nick
        wyp = self.wyps.setdefault(item, {})
        wyp[server.lower(nick)] = 1
        self.save()
        return "\x0306│\x03 You pressed the button. " + self.displayPresses(item)

    @command("nopress no")
    def noPress(self, server, msg):
        item = self.active.setdefault(server.lower(msg.context), "")
        nick = msg.address.nick
        wyp = self.wyps.setdefault(item, {})
        wyp[server.lower(nick)] = 0
        self.save()
        return "\x0306│\x03 You chose not to press the button. " + self.displayPresses(item)

    def displayPresses(self, item):
        wyp = self.wyps.get(item)
        num = len(wyp.keys())
        numPress = list(wyp.values()).count(1)
        stats = "%s out of %s people pressed the button (%.2f%%)" % (numPress, num, numPress / num * 100)
        health = 1
        if None in wyp.values():
            health -= (sum(self.force(i) for i in wyp if wyp[i] is None) / self.average()) * (2 - numPress / num)
            if health < 0:
                del self.wyps[item]
                self.save()
                stats += ". The button has been destroyed. RIP, button."
            bar = list("  ʜᴇᴀʟᴛʜ  ")
            bar.insert(max(0, math.ceil(health * 10)), "15,14")
            stats += " 15,06%s" % "".join(bar)
        return stats
            

    def display(self, chan):
        return "\x0306│\x03 Will you press the button? " + self.active.setdefault(chan, "")

    def fancydisplay(self, chan):
        button = """╔═══╕ %s
║ 04● │ %s
╙───┘ Will you press the button?"""
        k = 48
        while True:
            text = lineify(self.active.setdefault(chan, ""), k)
            k += 8
            if len(text) < 3: break
        if len(text) == 1: text.append("")
        return button % tuple(text)

    def average(self):
        return sum(len(i.values()) for i in self.wyps.values()) / len(self.wyps)

    def force(self, user):
        return 0.2 + 0.6 * len([i for i in self.wyps if self.wyps[i].get(user, None) is not None]) / len([i for i in self.wyps if user in self.wyps[i]]) + 0.2 / len([i for i in self.wyps if self.wyps[i].get(user, 1) is None])

    def save(self):
        with open(self.qfile, "w") as f:
            json.dump(self.wyps, f)


__initialise__ = Wyp

"""
╔═════╕
║ RIP │
║  04●  │
║ , .╷│
"""
