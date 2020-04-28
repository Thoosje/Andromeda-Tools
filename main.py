from colorama import init
from termcolor import colored
import json
import os

def main():
    os.system("title Andromeda")
    print(colored("***********************************************************", "yellow"))
    print(colored("<=                       Andromeda                        =>", "red"))
    print(colored("***************** Made by Thoosje - V0.0.1 ****************", "yellow"))
    print(colored("Dislaimer: I don't recommend using this, it can result into an account ban.", "red"))

    try:
        with open('Data/settings.json', "r") as file:
                data = json.load(file)
                os.environ["monitorAccountToken"] = data["monitorAccountToken"]
                os.environ["mainAccountToken"] = data["mainAccountToken"]
                os.environ["monitorChannel"] = data["monitorChannel"]
                os.environ["delay"] = data["delay"]
                os.environ["discordWebhook"] = data["discordWebhook"]

                file.close()
    except Exception as e:
        print(e)
        print(colored("Error while loading settings.", "red"))
        return False

    print(colored("Choose option:", "magenta"))
    print(colored("1. Nitro claimer", "blue"))
    print(colored("2. Invite Joiner", "blue"))
    userChoise = input()

    if userChoise.strip() == "1":
        import Tools.nitroClaimer as nitroClaimer
        claimer = nitroClaimer.NitroClaimer()
    elif userChoise.strip() == "2":
        import Tools.inviteJoiner as inviteJoiner
        joiner = inviteJoiner.InviteJoiner()
        pass

if __name__ == "__main__":
    main()