version = 1.3

try:
    import requests
    import time
    import getpass
    import datetime
    import base64
    from bs4 import BeautifulSoup
    import json
    import os
except ModuleNotFoundError:
    print("A module couldn't be find, please check the requirements.txt file, and install the missing modules\nAuto quit.")
    quit()

def isDirExist(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def createLogFile(version):
    logPath = os.path.expanduser(f"~\\AppData\\Roaming\\Ecoledirecte {version}")
    isDirExist(logPath)
    
    log_file_path = os.path.join(logPath, "log.txt")
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            log_file.write(f"Log file created for Ecoledirecte {version}\nProgram by Thefern (thefern_off on Discord)")

createLogFile(version)

def get_log_date():
    clock = time.localtime()
    clock = f"{clock.tm_hour}h:{clock.tm_min}min:{clock.tm_sec}sec"

    logTime = f"[{datetime.date.today()} {clock}]"
    return logTime

def write_log(str):
    try:
        with open(f"C:/Users/{os.getlogin()}/AppData/Roaming/Ecoledirecte {version}/log.txt", "a") as log:
            logText = f"\n{get_log_date()} {str}"
            log.write(logText)
            log.close()
    except FileNotFoundError:
        createLogFile(version)

write_log("All modules are loaded")
time.sleep(1)

def createConfFile():
    confPath = os.path.expanduser(f"~\\AppData\\Roaming\\Ecoledirecte {version}")
    isDirExist(confPath)
    
    conf_file_path = os.path.join(confPath, "config.json")
    if not os.path.exists(conf_file_path):
        with open(conf_file_path, "w") as conf_file:
            confFile = {
                "cn":"",
                "cv":""
            }

            json_data = json.dumps(confFile, indent=4)

            conf_file.write(json_data)

            conf_file.close()
            write_log("Config file created")

createConfFile()

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
            "Messages",
            "-help",
}

def date_format_check(var):
    try:
        datetime.datetime.strptime(var, '%Y-%m-%d')
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
            write_log(f"{commandSeparators} : Command not found")

def cd(id, token, username, etablissement, command):
        try:
            dir = command.split(" ", 2)[1].lower()
        except IndexError:
            Main(id, token, username, etablissement)

        if dir in [category.lower() for category in categories]:
            if dir == "notes":
                Notes(id, token, username, etablissement)
                write_log(f"Going in {dir} section")

            elif dir == "edt":
                EDT(id, token, username, etablissement)
                write_log(f"Going in {dir} section")

            elif dir == "agenda":
                Agenda(id, token, username, etablissement)
                write_log(f"Going in {dir} section")

            elif dir == "messages":
                Messages(id, token, username, etablissement)
                write_log(f"Going in {dir} section")

            elif dir == "-help":
                print("""DIR HELP DIRECTORIES:
                    The available directories are: Notes, EDT, Agenda""")
                write_log(f"Sending avalaible directories")

            elif dir == "accueil":
                Main(id, token, username, etablissement)
                write_log(f"Going in {dir} section")
        else:
            print(f"'{dir.capitalize()}' is not a valid directory. Please type 'cd -help' to see the correct directories")
            write_log(f"{dir.capitalize()} : Not a valid directory")

def ls(dir, id, token, command):
        if dir == "Main":
            print("/edt      /agenda       /notes       /messages")
            write_log(f"Printing {dir} contenue")
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
            write_log(f"Printing {dir} contenue")

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

                    try:
                        homeworks_data = response["data"]["matieres"]
                    except KeyError:
                        print("There is no homeworks for this day")
                        

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
                    write_log(f"Printing {dir} contenue")
                else:
                    print("The date is not valid ! Please type a date in the format YYYY-MM-DD")
                    write_log("Date format not valid for homework")

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
                write_log(f"Printing {dir} contenue")

        elif dir == "EDT":
            url = f"https://api.ecoledirecte.com/v3/E/{id}/emploidutemps.awp?verbe=get&v=4.46.3"
            try:
                date = command.split(" ", 2)[1]
                if date_format_check(date) == True:
                    date = datetime.datetime.strptime(date, '%Y-%m-%d')
                    dateDebut = date - datetime.timedelta(days=date.weekday())
                    dateFin = dateDebut + datetime.timedelta(days=6)

                    data = {
                        "dateDebut": str(dateDebut),
                        "dateFin": str(dateFin),
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

                    print("Schedule of the selected Week")
                    print("=" * 80)

                    for date, courses in schedule_by_date.items():
                        courses_sorted = sorted(courses, key=lambda x: x["start_date"])

                        print(f"Date: {date}")
                        print("-" * 80)
                        print("{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format("Subject", "Start Time", "End Time", "Professor", "Room"))
                        print("-" * 80)
                        
                        for course in courses_sorted:
                            subject = course["text"]
                            start_time = course["start_date"].split()[1]
                            end_time = course["end_date"].split()[1]
                            professor = course["prof"]
                            room = course["salle"]
                            print("{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format(subject, start_time, end_time, professor, room))
                        print("=" * 80)
                        write_log(f"Printing {dir} contenue")
                else:
                    print("The date is not valid ! Please type a date in the format YYYY-MM-DD")
                    write_log("Date format for schedule not valid")
            except IndexError:
                aujd = datetime.date.today()

                dateDebut = aujd - datetime.timedelta(days=aujd.weekday())

                dateFin = dateDebut + datetime.timedelta(days=6)

                data = {
                    "dateDebut": str(dateDebut),
                    "dateFin": str(dateFin),
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

                print("Schedule of the current Week")
                print("=" * 80)

                for date, courses in schedule_by_date.items():
                    courses_sorted = sorted(courses, key=lambda x: x["start_date"])

                    print(f"Date: {date}")
                    print("-" * 80)
                    print("{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format("Subject", "Start Time", "End Time", "Professor", "Room"))
                    print("-" * 80)
                    
                    for course in courses_sorted:
                        subject = course["text"]
                        start_time = course["start_date"].split()[1]
                        end_time = course["end_date"].split()[1]
                        professor = course["prof"]
                        room = course["salle"]
                        print("{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format(subject, start_time, end_time, professor, room))
                    print("=" * 80)
                write_log(f"Printing {dir} contenue")

        elif dir == "Messages":
            url = f"https://api.ecoledirecte.com/v3/eleves/{id}/messages.awp?force=false&typeRecuperation=received&idClasseur=0&orderBy=date&order=desc&query=&onlyRead=&page=0&itemsPerPage=100&getAll=0&verbe=get&v=4.53.2"

            data = {
                    "anneeMessages": "2023-2024"
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

            for message in response["data"]["messages"]["received"]:
                subject = message["subject"]
                sender = message["from"]["name"]

                print(f"Message from {sender} : {subject}")
            
            write_log(f"Printing {dir} contenue")

def help():
    print("""LIST OF COMMANDS :
          cd : Use it to change of category, see cd -help for more information
          ls : See the contenue of the category (like grades, schedule)
          clear : Clear the terminal
          logout : Return to the login page
          exit : Exit the program""")
    write_log("Sending command list")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    write_log("Clearing the console")

def logout():
    os.system('cls' if os.name == 'nt' else 'clear')
    write_log("User has logout")
    time.sleep(1)
    write_log("------------------------------------------------------------------------")
    Login()

def exit():
    os.system('cls' if os.name == 'nt' else 'clear')
    write_log("User has exited the program")
    time.sleep(1)
    write_log("------------------------------------------------------------------------")
    quit()

class Login():
    def __init__(self):
        try:
            internet_check = requests.get("https://google.com")
        except requests.ConnectionError:
            print("Look like you're not connected to the Internet, please check your Internet connection before restarting the program ...\nAuto quit in 5 seconds")
            write_log("Client not connected to the Internet, auto quit in 5sec")
            time.sleep(5)
            write_log("Client has quit by the program.")
            time.sleep(1)
            write_log("------------------------------------------------------------------------")
            quit()
        except:
            print("The Internet connection check couldn't be done, please report this to the dev")
            write_log("ERROR : The Internet connection check couldn't be done")
            
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

        self.data={
            "identifiant": self.identifiant,
            "motdepasse": self.password,
            "isReLogin": False,
            "uuid": "",
            "fa": []
        }

        self.headers = {
            "Content-Type": "application/form-data",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }

        self.url = "https://api.ecoledirecte.com/v3/login.awp?v=4.53.4"

        self.login()
    
    def login(self):
        json_data = json.dumps(self.data)
        credentials_valid = False

        while not credentials_valid:
            write_log("Sending connection request to Ecoledirecte API")
            response = requests.post(self.url, data={'data': json_data}, headers=self.headers)

            if response.status_code == 200:
                json_response = json.loads(response.text)

                if json_response["code"] == 250:
                    token = json_response["token"]

                    self.headers = {
                        "Content-Type": "application/form-data",
                        "Accept": "application/json, text/plain, */*",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                        "X-Token": token
                    }

                    self.data = {}

                    json_data = json.dumps(self.data)

                    self.url = "https://api.ecoledirecte.com/v3/connexion/doubleauth.awp?verbe=get&v=4.53.4"

                    response = requests.post(self.url, data={'data': json_data}, headers=self.headers)

                    question = response.json()["data"]["question"]
                    question = base64.b64decode(question).decode("utf-8")

                    propositions = response.json()["data"]["propositions"]

                    print(f"For security purposes, please answer this question :\n{question}")

                    nb = 1
                    for proposition in propositions:
                        proposition = base64.b64decode(proposition).decode("utf-8")
                        print(f"Choice n°{nb} {proposition}")
                        nb = nb + 1

                    selection = int(input("Enter the number of your choice: "))
                    selection = base64.b64decode(propositions[selection - 1]).decode("utf-8") # Getting the answer
                    selection = base64.b64encode(selection.encode("utf-8")).decode("utf-8") # Encoding it back to base64

                    self.data = {
                        "choix": selection
                    }
                    json_data = json.dumps(self.data)

                    self.url = "https://api.ecoledirecte.com/v3/connexion/doubleauth.awp?verbe=post&v=4.53.4"

                    response = requests.post(self.url, data={'data': json_data}, headers=self.headers)
                    
                    if not response.json()["code"] == 200:
                        print(f"Invalid answer, please try again")
                        write_log(f"Wrong answer at the security question")
                        time.sleep(2)
                        self.get_credentials()
                    else:
                        cn = response.json()["data"]["cn"]
                        cv = response.json()["data"]["cv"]

                        with open(f"C:/Users/{os.getlogin()}/AppData/Roaming/Ecoledirecte {version}/config.json", "r+") as conf:
                            conf_data = json.load(conf)
                            conf_data["cn"] = cn
                            conf_data["cv"] = cv

                            conf.seek(0)

                            json.dump(conf_data, conf, indent=4)
                            conf.truncate()

                            self.data={
                                "identifiant": self.identifiant,
                                "motdepasse": self.password,
                                "isReLogin": False,
                                "cn": cn,
                                "cv": cv,
                                "uuid": "",
                                "fa": [
                                    {
                                        "cn": cn,
                                        "cv": cv
                                    }
                                ]
                            }
                            json_data = json.dumps(self.data)

                            self.headers = {
                                "Content-Type": "application/form-data",
                                "Accept": "application/json, text/plain, */*",
                                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                                "X-Token": token
                            }

                            self.url = "https://api.ecoledirecte.com/v3/login.awp?v=4.53.4"

                            response = requests.post(self.url, data={'data': json_data}, headers=self.headers)
                            json_response = response.json()

                            print(f"You're logged as {self.identifiant}")
                            write_log(f"Client is connected as {self.identifiant}")
                            time.sleep(1)

                            id = json_response["data"]["accounts"][0]["id"]
                            token = json_response["token"]
                            etablissement = json_response["data"]["accounts"][0]["nomEtablissement"]
                            credentials_valid = True

                            os.system('cls' if os.name == 'nt' else 'clear')
                            Main(id, token, self.identifiant, etablissement)

                elif json_response["code"] == 505:
                    print("Invalid username or password")
                    write_log("The client input incorrect credentials")
                    time.sleep(1)
                    self.get_credentials()
            else:
                print(f"Error : {response.status_code}")
                write_log(f"Unexpected ERROR : {response.status_code}")
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
class Messages():
    def __init__(self, id, token, username, etablissement):
        self.dir = "Messages"

        self.id = id
        self.token = token
        self.username = username
        self.etablissement = etablissement

        self.directory = f"[{self.username}@{self.etablissement}/messages] $ "

        self.main()

    def main(self):
        self.command = input(self.directory)
        commandSeparators = self.command.split(" ",1)[0]
        check_command(commandSeparators, self.id, self.token, self.username, self.etablissement, self.command, self.dir)

        self.main()

Login()