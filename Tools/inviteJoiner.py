from colorama import init
from termcolor import colored
import os
import datetime, time
import requests
import json
import threading
from dhooks import Webhook, Embed
init()

def getPrintFormat():
    now = str(datetime.datetime.now())
    now = now.split(' ')[1]
    printFormat = '[' + str(now) + ']' + ' ' + '[INVITE JOINER] '
    return printFormat

class InviteJoiner():
    def __init__(self):
        os.system("title Andromeda - Invitejoiner")
        print(colored(getPrintFormat() + "Starting invite joiner.", "green"))

        self.s = requests.session()
        self.monitorHeaders = {
            "authorization": os.environ["monitorAccountToken"],
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "accept-encoding": "gzip, deflate, br",
            "referer": "https://discordapp.com/channels/{}".format(os.environ["monitorChannel"])
        }
        self.mainHeaders = {
            "authorization": os.environ["mainAccountToken"],
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "accept-encoding": "gzip, deflate, br",
            "referer": "https://discordapp.com/channels/{}".format(os.environ["monitorChannel"])
        }
        self.lastMessageId = ""

        self.monitor()

    def sendWebhook(self, inviteCode, startTime, success=False, guildName=None):
        webhook = Webhook(os.environ["discordWebhook"])

        if success == False:
            embedColor = 16724787
            embedTitle = "Failed Joining Guild"
        else:
            embedColor = 9881393
            embedTitle = "Joined Guild"

        embed = Embed(
            title=embedTitle,
            color=embedColor,
            time="now"
        )
        embed.add_field(name="Invite Code", value=inviteCode, inline=True)
        embed.add_field(name="Elapsed time", value=str(time.time() - startTime) + " sec", inline=True)

        if success == True and guildName != None:
            embed.add_field(name="Guild Name", value=guildName, inline=True)

        embed.set_author(name="Andromeda")
        embed.set_footer(text="Andromeda - Made By Thoosje")

        try:
            webhook.send(embed=embed)
        except Exception:
            print(colored(getPrintFormat() + "Failed to send webhook.", "red"))
        return
        
    def monitor(self):
        while True:
            print(colored(getPrintFormat() + "Monitoring...", "yellow"))

            try:
                r = self.s.get("https://discordapp.com/api/v6/channels/{}/messages?limit=1".format(os.environ["monitorChannel"]), headers=self.monitorHeaders)
            except Exception:
                print(colored(getPrintFormat() + "Error while requesting last messages.", "red"))
                time.sleep(int(os.environ["delay"]))
                continue

            if r.status_code == 200:
                data = json.loads(r.text)
                
                if str(data[0]["id"]) == self.lastMessageId and self.lastMessageId != "": 
                    time.sleep(int(os.environ["delay"]))
                    continue
                elif self.lastMessageId == "":
                    self.lastMessageId = str(data[0]["id"])
                    time.sleep(int(os.environ["delay"]))
                    continue
                else:
                    self.lastMessageId = str(data[0]["id"])
                    print(colored(getPrintFormat() + "Detected new message.", "green"))

                    ## Normal Message ###
                    contentWords = data[0]["content"].split(" ")
                    for word in contentWords:
                        if word.startswith("https://discord.gg/") or word.startswith("discord.gg/") or word.startswith("http://discord.gg/") or "discord.gg" in word:
                            discInviteSplit = word.split("/")
                            
                            startTime = time.time()
                            print(colored(getPrintFormat() + "Found new discord invite {}".format(discInviteSplit[3]), "green"))
                            (threading.Thread(target=self.joinGuild, args=(discInviteSplit[3], startTime,))).start()

                    ### Embed description ###
                    for embed in data[0]["embeds"]:
                        try:
                            contentWords = embed["description"].split(" ")
                        except Exception:
                            contentWords = []

                        try:
                            titleWords = embed["title"].split(" ")
                            for word in titleWords:
                                contentWords.append(word)
                        except Exception:
                            pass

                        for word in contentWords:
                            if word.startswith("https://discord.gg/") or word.startswith("discord.gg/") or word.startswith("http://discord.gg/") or "discord.gg" in word:
                                discInviteSplit = word.split("/")
                                discInviteSplit = word.split("/")
                                
                                startTime = time.time()
                                print(colored(getPrintFormat() + "Found new discord invite {}".format(discInviteSplit[3]), "green"))
                                (threading.Thread(target=self.joinGuild, args=(discInviteSplit[3], startTime,))).start()

                        for field in embed["fields"]:
                            contentWords = field["value"].split(" ")

                            for word in contentWords:
                                if word.startswith("https://discord.gg/") or word.startswith("discord.gg/") or word.startswith("http://discord.gg/") or "discord.gg" in word:
                                    discInviteSplit = word.split("/")

                                    startTime = time.time()
                                    print(colored(getPrintFormat() + "Found new discord invite {}".format(discInviteSplit[3]), "green"))
                                    (threading.Thread(target=self.joinGuild, args=(discInviteSplit[3],startTime,))).start()

                    time.sleep(int(os.environ["delay"]))
            else:
                print(colored(getPrintFormat() + "Error while requesting last message, status code: {}".format(r.status_code), "red"))
                time.sleep(int(os.environ["delay"]))
                continue

    def joinGuild(self, inviteCode, startTime):
        joinReq = requests.post("https://discordapp.com/api/v6/invites/{}".format(inviteCode), headers=self.mainHeaders)

        if joinReq.status_code == 200:
            data = json.loads(joinReq.text)

            print(colored(getPrintFormat() + "Joined {} with code: {}".format(data["guild"]["name"], data["code"]), "green"))
            self.sendWebhook(inviteCode, startTime, True, data["guild"]["name"])
            return
        else:
            print(colored(getPrintFormat() + "Error while joining a server.", "red"))
            print(joinReq.text)
            self.sendWebhook(inviteCode, startTime, False)
            return