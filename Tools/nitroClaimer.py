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
    printFormat = '[' + str(now) + ']' + ' ' + '[NITRO CLAIMER] '
    return printFormat

class NitroClaimer():
    def __init__(self):
        os.system("title Andromeda - Nitroclaimer")
        print(colored(getPrintFormat() + "Starting nitro claimer.", "green"))

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

    def sendWebhook(self, nitroCode, startTime, success=False, errorCode=None):
        webhook = Webhook(os.environ["discordWebhook"])

        if success == False:
            embedColor = 16724787
            embedTitle = "Failed Claiming Nitro"
        else:
            embedColor = 9881393
            embedTitle = "Claimed Discord Nitro"

        embed = Embed(
            title=embedTitle,
            color=embedColor,
            time="now"
        )
        embed.add_field(name="Nitro Code", value=nitroCode, inline=True)
        embed.add_field(name="Elapsed time", value=str(time.time() - startTime) + " sec", inline=True)

        if success == False and errorCode != None:
            embed.add_field(name="Error code", value=errorCode, inline=True)

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

                    ### Normal Message ###
                    contentWords = data[0]["content"].split(" ")
                    for word in contentWords:
                        if word.startswith("https://discord.gift/") or word.startswith("discord.gift/") or word.startswith("http://discord.gift/") or "discord.gift" in word:
                            discNitroSplit = word.split("/")
                            
                            startTime = time.time()
                            print(colored(getPrintFormat() + "Found new nitro code {}".format(discNitroSplit[3]), "green"))
                            (threading.Thread(target=self.claimNitro, args=(discNitroSplit[3], startTime,))).start()

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
                            if word.startswith("https://discord.gift/") or word.startswith("discord.gift/") or word.startswith("http://discord.gift/") or "discord.gift" in word:
                                discNitroSplit = word.split("/")
                                discNitroSplit = word.split("/")
                                
                                startTime = time.time()
                                print(colored(getPrintFormat() + "Found new nitro code {}".format(discNitroSplit[3]), "green"))
                                (threading.Thread(target=self.claimNitro, args=(discNitroSplit[3], startTime,))).start()

                        for field in embed["fields"]:
                            contentWords = field["value"].split(" ")

                            for word in contentWords:
                                if word.startswith("https://discord.gift/") or word.startswith("discord.gift/") or word.startswith("http://discord.gift/") or "discord.gift" in word:
                                    discNitroSplit = word.split("/")

                                    startTime = time.time()
                                    print(colored(getPrintFormat() + "Found new nitro code {}".format(discNitroSplit[3]), "green"))
                                    (threading.Thread(target=self.claimNitro, args=(discNitroSplit[3],startTime,))).start()

                    time.sleep(int(os.environ["delay"]))
            else:
                print(colored(getPrintFormat() + "Error while requesting last message, status code: {}".format(r.status_code), "red"))
                time.sleep(int(os.environ["delay"]))
                continue

    def claimNitro(self, nitroCode, startTime):
        r = requests.post("https://discordapp.com/api/v6/entitlements/gift-codes/{}/redeem?with_application=false&with_subscription_plan=false".format(nitroCode.replace("-", "").strip()), headers=self.mainHeaders)

        if r.status_code == 200:
            data = json.loads(r.text)
            print(data)
            try:
                if data["code"] != 50050:
                    print(colored(getPrintFormat() + "Claimed nitro with code: {}".format(nitroCode), "magenta"))
                    self.sendWebhook(nitroCode, startTime, True, None)
            except Exception as e:
                print(colored(getPrintFormat() + "This nitro is already claimed. Data: {}".format(data), "red"))
                self.sendWebhook(nitroCode, startTime, False, str(data["code"]))
            return
        else:
            self.sendWebhook(nitroCode, startTime, False, str(json.loads(r.text)["code"]))

            print(colored(getPrintFormat() + "Error while claming a nitro with code {}.".format(nitroCode), "red"))
            print(r.text)
            return