import requests
import time
import getpass
import datetime
import base64
from bs4 import BeautifulSoup
import json
import string
import os

commands = {
            "cd",
            "ls",
            "clear",
            "exit",
            "logout",
            "help",
            "",
}

categories = {
            "Accueil",
            "Notes",
            "EDT",
            "Agenda",
            "-help",
}

def date_format_check(var):
    try:
        datetime.strptime(var, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def check_command(commandSeparators, id, token, username, etablissement, command, dir):
        if commandSeparators in commands:
            if commandSeparators == "cd":
                cd(id, token, username, etablissement, command)
            elif commandSeparators == "ls":
                ls(dir, id, token, command)
            elif commandSeparators == "help":
                help()
            elif commandSeparators == "clear":
                clear()
            elif commandSeparators == "logout":
                logout()
            elif commandSeparators == "exit":
                exit()
            elif commandSeparators == "":
                pass
        else:
            print(f"Command '{commandSeparators}' not found.")

def cd(id, token, username, etablissement, command):
        try:
            dir = command.split(" ", 2)[1].lower()
        except IndexError:
            Main(id, token, username, etablissement)

        if dir in [category.lower() for category in categories]:
            if dir == "notes":
                Notes(id, token, username, etablissement)
            elif dir == "edt":
                EDT(id, token, username, etablissement)
            elif dir == "agenda":
                Agenda(id, token, username, etablissement)
            elif dir == "-help":
                print("""DIR HELP DIRECTORIES:
                    The available directories are: Notes, EDT, Agenda""")
            elif dir == "accueil":
                Main(id, token, username, etablissement)
        else:
            print(f"'{dir.capitalize()}' is not a valid directory. Please type 'cd -help' to see the correct directories")

def ls(dir, id, token, command):
        if dir == "Main":
            print("There's nothing to show here... yet")
        elif dir == "Notes":
            url = f"https://api.ecoledirecte.com/v3/eleves/{id}/notes.awp?verbe=get&v=4.46.3"
            
            data = {
                "anneeScolaire": ""
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                "X-Token": token
            }
    
            json_data = json.dumps(data)

            response = requests.post(url, data={'data': json_data}, headers=headers)
            response = response.json()  

            periodes = ["A001", "A002", "A003"]

            periodes_names = []

            for periode_data in response["data"]["periodes"]:
                id_periode = periode_data["idPeriode"]
                if id_periode in periodes:
                    periode_name = periode_data["periode"]
                    periodes_names.append(periode_name)
                    
            subjects = []

            for periode_data in response["data"]["periodes"][0]["ensembleMatieres"]["disciplines"]:
                discipline = periode_data["discipline"]
                subjects.append(discipline)

            subject_values = {subject: {p: [] for p in periodes} for subject in subjects}

            for note in response["data"]["notes"]:
                subject = note["libelleMatiere"]
                valeur = note["valeur"]
                periode = note["codePeriode"]

                if periode in periodes and subject in subject_values:
                    subject_values[subject][periode].append(valeur)

            # Thanks to ChatGPT for this part :

            max_len = max(len(subject) for subject in subject_values.keys())

            column_widths = [max(len(period), max(len(str(grade)) if str(grade) != 'Disp' else len('Disp') for grade in values.values())) for period, values in zip(periodes_names, subject_values.values())]

            print(f"{'Subject':<{max_len}} | {' | '.join([f'{p:^{w}}' for p, w in zip(periodes_names, column_widths)])}")

            for subject, values in subject_values.items():
                grades = []
                for period, grade in values.items():
                    if str(grade) == 'Disp':
                        grades.append('Disp')
                    else:
                        grades.append(", ".join(map(str, grade)) if isinstance(grade, list) else str(grade))

                print(f"{subject:<{max_len}} | {' | '.join([f'{g:^{w}}' for g, w in zip(grades, column_widths)])}")

        elif dir == "Agenda":
            try:
                date = command.split(" ", 2)[1]
                if date_format_check(date) == True:
                    url = f"https://api.ecoledirecte.com/v3/Eleves/{id}/cahierdetexte/{date}.awp?verbe=get&v=4.46.3"

                    data = {}

                    headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                    "X-Token": token
                    }

                    json_data = json.dumps(data)

                    response = requests.post(url, data={'data': json_data}, headers=headers)
                    response = response.json()

                    homeworks_data = response["data"]["matieres"]

                    for homework in homeworks_data:
                        nb = 1
                        subject = homework["matiere"]
                        gaveThe = homework["aFaire"]["donneLe"]
                        test = homework["interrogation"]
                        contenu = homework["aFaire"]["contenu"]
                        enLigne = homework["aFaire"]["rendreEnLigne"]

                        print(f"Subject : {subject}")
                        print(f"Gave the : {gaveThe}")
                        print(f"Test ? : {test}")
                        print(f"Give online ? : {enLigne}")
                        print(f"Homework : {BeautifulSoup(base64.b64decode(contenu).decode('utf-8'), 'html.parser').get_text()}\n----------------------")
                else:
                    print("The date is not valid ! Please type a date in the format YYYY-MM-DD")

            except IndexError:
                url = f"https://api.ecoledirecte.com/v3/Eleves/{id}/cahierdetexte.awp?verbe=get&v=4.46.3"

                data = {}

                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                    "X-Token": token
                }

                json_data = json.dumps(data)

                response = requests.post(url, data={'data': json_data}, headers=headers)
                response = response.json()

                homeworks_data = response["data"]

                for date, homeworks in homeworks_data.items():
                    nb = 1
                    print(f"----------------------\nOn {date}:")
                    for homework in homeworks:
                        subject = homework["matiere"]
                        gaveThe = homework["donneLe"]
                        test = homework["interrogation"]

                        print(f"{nb}. Subject: {subject}")
                        print(f"Test ? : {test}")
                        print(f"Gave the : {gaveThe}\n")

                        nb = nb + 1

        elif dir == "EDT":
            url = f"https://api.ecoledirecte.com/v3/E/{id}/emploidutemps.awp?verbe=get&v=4.46.3"
            try:
                date = command.split(" ", 2)[1]
                if date_format_check(date) == True:
                    pass
                else:
                    print("The date is not valid ! Please type a date in the format YYYY-MM-DD")
            except IndexError:
                aujd = datetime.date.today()

                dateDebut = aujd - datetime.timedelta(days=aujd.weekday())

                dateFIn = dateDebut + datetime.timedelta(days=6)

                data = {
                    "dateDebut": "2024-01-08", # str(dateDebut)
                    "dateFin": "2024-01-14", # str(dateFIn)
                    "avecTrous": False
                }

                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                    "X-Token": token
                }

                json_data = json.dumps(data)

                response = requests.post(url, data={'data': json_data}, headers=headers)
                response = response.json()

                schedule_by_date = {}

                for course in response["data"]:
                    date = course["start_date"].split()[0] 
                    if date in schedule_by_date:
                        schedule_by_date[date].append(course)
                    else:
                        schedule_by_date[date] = [course]

                # Printing the schedule board
                print("Schedule of the current Week")
                print("=" * 80)

                for date, courses in schedule_by_date.items():
                    print(f"Date: {date}")
                    print("-" * 80)
                    print("{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format("Subject", "Start Time", "End Time", "Professor", "Room"))
                    print("-" * 80)
                    for course in courses:
                        subject = course["text"]
                        start_time = course["start_date"].split()[1]
                        end_time = course["end_date"].split()[1]
                        professor = course["prof"]
                        room = course["salle"]
                        print("{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format(subject, start_time, end_time, professor, room))
                    print("=" * 80)


def help():
    print("""LIST OF COMMANDS :
          cd : Use it to change of category, see cd -help for more informations
          ls : See the contenue of the category (like grades, schedule)
          clear : Clear the terminal
          logout : Return to the login page
          exit : Exit the program""")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def logout():
    os.system('cls' if os.name == 'nt' else 'clear')
    Login()

def exit():
    os.system('cls' if os.name == 'nt' else 'clear')
    quit()

class Login():
    def __init__(self):
        try:
            internet_check = requests.get("https://google.com")
        except requests.ConnectionError:
            print("Look like you're not connected to the Internet, please check your Internet connection before restarting the program ...")
            quit()
            
        self.get_credentials()

    def get_credentials(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("""\n\n▓█████  ▄████▄   ▒█████   ██▓    ▓█████    ▓█████▄  ██▓ ██▀███  ▓█████  ▄████▄  ▄▄▄█████▓▓█████     ▄████▄   ██▓     ██▓▓█████  ███▄    █ ▄▄▄█████▓
▓█   ▀ ▒██▀ ▀█  ▒██▒  ██▒▓██▒    ▓█   ▀    ▒██▀ ██▌▓██▒▓██ ▒ ██▒▓█   ▀ ▒██▀ ▀█  ▓  ██▒ ▓▒▓█   ▀    ▒██▀ ▀█  ▓██▒    ▓██▒▓█   ▀  ██ ▀█   █ ▓  ██▒ ▓▒
▒███   ▒▓█    ▄ ▒██░  ██▒▒██░    ▒███      ░██   █▌▒██▒▓██ ░▄█ ▒▒███   ▒▓█    ▄ ▒ ▓██░ ▒░▒███      ▒▓█    ▄ ▒██░    ▒██▒▒███   ▓██  ▀█ ██▒▒ ▓██░ ▒░
▒▓█  ▄ ▒▓▓▄ ▄██▒▒██   ██░▒██░    ▒▓█  ▄    ░▓█▄   ▌░██░▒██▀▀█▄  ▒▓█  ▄ ▒▓▓▄ ▄██▒░ ▓██▓ ░ ▒▓█  ▄    ▒▓▓▄ ▄██▒▒██░    ░██░▒▓█  ▄ ▓██▒  ▐▌██▒░ ▓██▓ ░ 
░▒████▒▒ ▓███▀ ░░ ████▓▒░░██████▒░▒████▒   ░▒████▓ ░██░░██▓ ▒██▒░▒████▒▒ ▓███▀ ░  ▒██▒ ░ ░▒████▒   ▒ ▓███▀ ░░██████▒░██░░▒████▒▒██░   ▓██░  ▒██▒ ░ 
░░ ▒░ ░░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░▓  ░░░ ▒░ ░    ▒▒▓  ▒ ░▓  ░ ▒▓ ░▒▓░░░ ▒░ ░░ ░▒ ▒  ░  ▒ ░░   ░░ ▒░ ░   ░ ░▒ ▒  ░░ ▒░▓  ░░▓  ░░ ▒░ ░░ ▒░   ▒ ▒   ▒ ░░   
 ░ ░  ░  ░  ▒     ░ ▒ ▒░ ░ ░ ▒  ░ ░ ░  ░    ░ ▒  ▒  ▒ ░  ░▒ ░ ▒░ ░ ░  ░  ░  ▒       ░     ░ ░  ░     ░  ▒   ░ ░ ▒  ░ ▒ ░ ░ ░  ░░ ░░   ░ ▒░    ░    
   ░   ░        ░ ░ ░ ▒    ░ ░      ░       ░ ░  ░  ▒ ░  ░░   ░    ░   ░          ░         ░      ░          ░ ░    ▒ ░   ░      ░   ░ ░   ░      
   ░  ░░ ░          ░ ░      ░  ░   ░  ░      ░     ░     ░        ░  ░░ ░                  ░  ░   ░ ░          ░  ░ ░     ░  ░         ░          
       ░                                    ░                          ░                           ░                                               

""")
        self.identifiant = input("\nlogin as : ")
        self.password = getpass.getpass(f"{self.identifiant}'s password : ")

        self.data = {
            "identifiant": self.identifiant,
            "motdepasse": self.password,
            "isReLogin": False,
            "uuid": ""
        }

        self.headers = {
            "Content-Type": "application/form-data",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }

        self.url = "https://api.ecoledirecte.com/v3/login.awp?v=4.38.0"

        self.login()
    
    def login(self):
        json_data = json.dumps(self.data)
        credentials_valid = False

        while not credentials_valid:
            response = requests.post(self.url, data={'data': json_data}, headers=self.headers)

            if response.status_code == 200:
                json_response = json.loads(response.text)

                if json_response["code"] == 200:
                    print(f"You're logged as {self.identifiant}")
                    time.sleep(1)

                    id = json_response["data"]["accounts"][0]["id"]
                    token = json_response["token"]
                    etablissement = json_response["data"]["accounts"][0]["nomEtablissement"]
                    credentials_valid = True

                    os.system('cls' if os.name == 'nt' else 'clear')
                    Main(id, token, self.identifiant, etablissement)

                elif json_response["code"] == 505:
                    print("Invalid username or password")
                    time.sleep(1)
                    self.get_credentials()
            else:
                print(f"Error : {response.status_code}")

class Main():
    def __init__(self, id, token, username, etablissement):
        self.dir = "Main"

        self.id = id
        self.token = token
        self.username = username
        self.etablissement = etablissement

        self.directory = f"[{self.username}@{self.etablissement}] $ "

        self.main()

    def main(self):
        self.command = input(self.directory)
        commandSeparators = self.command.split(" ",1)[0]
        check_command(commandSeparators, self.id, self.token, self.username, self.etablissement, self.command, self.dir)

        self.main()

class Notes():
    def __init__(self, id, token, username, etablissement):
        self.dir = "Notes"

        self.id = id
        self.token = token
        self.username = username
        self.etablissement = etablissement

        self.directory = f"[{self.username}@{self.etablissement}/notes] $ "

        self.main()

    def main(self):
        self.command = input(self.directory)
        commandSeparators = self.command.split(" ",1)[0]
        check_command(commandSeparators, self.id, self.token, self.username, self.etablissement, self.command, self.dir)

        self.main()

class Agenda():
    def __init__(self, id, token, username, etablissement):
        self.dir = "Agenda"

        self.id = id
        self.token = token
        self.username = username
        self.etablissement = etablissement

        self.directory = f"[{self.username}@{self.etablissement}/agenda] $ "

        self.main()

    def main(self):
        self.command = input(self.directory)
        commandSeparators = self.command.split(" ",1)[0]
        check_command(commandSeparators, self.id, self.token, self.username, self.etablissement, self.command, self.dir)

        self.main()

class EDT():
    def __init__(self, id, token, username, etablissement):
        self.dir = "EDT"

        self.id = id
        self.token = token
        self.username = username
        self.etablissement = etablissement

        self.directory = f"[{self.username}@{self.etablissement}/edt] $ "

        self.main()

    def main(self):
        self.command = input(self.directory)
        commandSeparators = self.command.split(" ",1)[0]
        check_command(commandSeparators, self.id, self.token, self.username, self.etablissement, self.command, self.dir)

        self.main()

Login()