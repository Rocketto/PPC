# environment.py
import time
from multiprocessing import Process, Value, Lock, Queue
from multiprocessing.managers import BaseManager
#from prey import Prey
#from animal import Animal
#from predator import Predator
from display import Display
import socket
import threading

class Ecosysteme:

    def __init__(self):

        self._lock = threading.Lock()  # mutex interne côté serveur

        self.parametres = {
        "predator": {
            "count": 1,
            "energy": 40,
            "hunger": 20,
            "reproduction": 70
        },
        "prey": {
            "count": 2,
            "energy": 25,
            "hunger": 20,
            "reproduction": 60
        },
        "env": {
            "grass": {
                "count": 200,           #valeur initiale de l'herbe
                "max": 300,
                "croissance": 7},
            
            "temps": {
                "tick" : 0},

            "secheresse": {
                "active": False,
                "nombre": 0,
                "duree": 5}
            
        }
        
        }

    def get_parametres(self):
        return self.parametres
    
    def inc_tick(self): # Incrémente le tick et retourne la nouvelle valeur
        self.parametres["env"]["temps"]["tick"] += 1
        return self.parametres["env"]["temps"]["tick"]
    
    def herbe_pousse(self):
        self.parametres["env"]["grass"]["count"] += self.parametres["env"]["grass"]["croissance"]
        return self.parametres["env"]["grass"]["count"]

    def active_secheresse(self):
        self.parametres["env"]["secheresse"]["active"] = True 
        self.parametres["env"]["secheresse"]["nombre"] += 1   
    
    def reset_grass_count(self):
        self.parametres["env"]["grass"]["count"] = 0
        self.parametres["env"]["secheresse"]["active"] = False

    # Partie proies

    def get_grass_count(self):
        with self._lock:
            return self.parametres["env"]["grass"]["count"]

    def take_grass(self, amount: int):
        """Retire jusqu'à 'amount' herbe et retourne la quantité réellement prise."""
        with self._lock:
            g = self.parametres["env"]["grass"]["count"]
            if g <= 0:
                return 0
            eaten = min(g, int(amount))
            self.parametres["env"]["grass"]["count"] = g - eaten
            return eaten

    

# Temps qui passe 

def time_pass(serveur_partage):
    while True:
        time.sleep(1)
        serveur_partage.inc_tick()


def grass_growth(serveur_partage):
    while True:
        while serveur_partage.get_parametres()["env"]["secheresse"]["active"] == False:
            if serveur_partage.get_parametres()["env"]["grass"]["count"] < serveur_partage.get_parametres()["env"]["grass"]["max"]:
                serveur_partage.herbe_pousse()
                time.sleep(1)
                print(f"[env] grass grown to {serveur_partage.get_parametres()['env']['grass']['count']}")

        # si la sécheresse est active
        serveur_partage.reset_grass_count()
        time.sleep(serveur_partage.get_parametres()["env"]["secheresse"]["duree"]) 

def secheresse_event(serveur_partage):
    serveur_partage.active_secheresse()



class EcosystemeManager(BaseManager):  pass # On crée une sous-classe vide

# On enregistre la classe 'MonEcosysteme' sous le nom de clé 'Ecosysteme'
eco_global = Ecosysteme()
EcosystemeManager.register("get_ecosysteme", callable=lambda: eco_global)



import subprocess
import sys
from pathlib import Path

# Chemin d'accès du projet

BASE_DIR = Path(__file__).resolve().parent.parent

# Session TCP pour communication avec les prédateurs

import socket
import threading

MANAGER_HOST = "localhost"
MANAGER_PORT = 50020
TCP_HOST = "localhost"
TCP_PORT = 50010
AUTH = b"PPC"

def tcp_server_loop():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((TCP_HOST, TCP_PORT))
        srv.listen()
        print(f"[env] TCP server listening on {TCP_HOST}:{TCP_PORT}")

        while True:
            conn, addr = srv.accept()
            with conn:
                data = conn.recv(1024).decode("utf-8", errors="replace").strip()
                # ici on attend juste un PID sur une ligne
                if data.isdigit():
                    print(f"[env] connected from {addr}, pid={data}")
                else:
                    print(f"[env] connection from {addr}, invalid pid='{data}'")


#Manager longue distance 

def run_manager_server():
    manager = EcosystemeManager(address=(MANAGER_HOST, MANAGER_PORT), authkey=AUTH)
    server = manager.get_server()
    print(f"[env] EcosystemeManager listening on {MANAGER_HOST}:{MANAGER_PORT}")
    server.serve_forever()



if __name__ == "__main__":

    # TEST serveur longue distance

    threading.Thread(target=run_manager_server, daemon=True).start()


    # Creation de la proie test
    threading.Thread(target=tcp_server_loop, daemon=True).start()
    time.sleep(1)  # Attendre que le serveur démarre
    subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "prey.py")])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[env] stopping")
    

    # with EcosystemeManager() as manager:
    
        # # Création de l'écosystème en mémoire partagée
        # eco_partage = manager.Ecosysteme()
        # # Démarrage du processus de gestion du temps
        # time_process = Process(target=time_pass, args=(eco_partage,))
        # time_process.start()
        
        
        # # Démarrage du processus de croissance de l'herbe
        # herbe_process = Process(target=grass_growth, args=(eco_partage,))
        # herbe_process.start()
        # time.sleep(5)

        # # Test sécheresse
        # séch = Process(target=secheresse_event, args=(eco_partage,))
        # séch.start()
        # time.sleep(5)
        # print("ça repousse")
        # time.sleep(5)

        # # Arrêt des processus
        # herbe_process.terminate()
        # time_process.terminate()
        # séch.terminate()

        # # Test serveur TCP
        # # Démarrage du serveur TCP dans un thread séparé
        # threading.Thread(target=tcp_server_loop, daemon=True).start()
        # time.sleep(1)  # Attendre que le serveur démarre
        # # Creation des proies
        # subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "prey.py")])
        # subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "predator.py")])

        # # Creation des proies
        # threading.Thread(target=tcp_server_loop, daemon=True).start()
        # time.sleep(1)  # Attendre que le serveur démarre
        # for _ in range(eco_partage.get_parametres()["prey"]["count"]):
        #     subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "prey.py")])

        # # Creation des prédateurs
        # for _ in range(eco_partage.get_parametres()["predator"]["count"]):
        #     subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "predator.py")])

        # try:
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     print("[env] stopping")
        














#     # Etat de l'herbe en memoire partagée
#     # Type réel, car facteur de croissance reel
#     grass_lock = Lock()
#     grass_count = Value('i', parameters["env"]["grass"]["init"])
#     grass_growth = parameters["env"]["grass"]["croissance"]
#     grass_max = parameters["env"]["grass"]["max"]
#     # Communication vers le display
#     display_queue = Queue()
#     display_process = Process(target=Display.start,args=(Display(display_queue),))
#     display_process.start()

#     # file communication animal vers environnement
#     requete_env = Queue()  

#     # Creation des proies
#     proies = []
#     for _ in range(parameters["prey"]["count"]):
#         prey = Prey(grass_count, grass_lock, parameters["prey"],requete_env)
#         p = Process(target=Prey.vivre,args=(prey,))
#         p.start()
#         proies.append(p)


#     # Creation des prédateurs
#     reponse_predateur = {}
#     for _ in range(parameters["predator"]["count"]):
#         # l'environnement repont individuellement sur cette file avec le PID de la proie, ou rien
#         reponse_proie = Queue()
#         predator = Predator(reponse_proie,parameters["predator"],requete_env)
#         p = Process(target=Predator.vivre,args=(predator,))
#         p.start()
#         reponse_predateur[p.pid] = reponse_proie

#     try:
#         while True:
#             # Croissance naturelle de l'herbe
#             with grass_lock:
#                 grass_count.value = min(grass_count.value + grass_growth, grass_max)
#                 display_queue.put(f"grass: {grass_count.value}")
#             # Traitement des demandes des prédateurs
#             while not requete_env.empty():
#                 requete_recue = requete_env.get()
#                 if requete_recue == "proie":
#                     prey = Prey(grass_count, grass_lock, parameters["prey"],requete_env)
#                     p = Process(target=Prey.vivre,args=(prey,))
#                     p.start()
#                     proies.append(p)
#                 elif requete_recue == "predateur":
#                     reponse_proie = Queue()
#                     predator = Predator(reponse_proie,parameters["predator"],requete_env)
#                     p = Process(target=Predator.vivre,args=(predator,))
#                     p.start()
#                     reponse_predateur[p.pid] = reponse_proie

#                 # sinon c'est un pid
#                 else:
#                     predator_pid = requete_recue
#                     reponse = "rien"

#                     if proies:
#                         # Prendre la première proie
#                         prey_proc = proies.pop(0)
#                         prey_proc.kill()
#                         # Attendre le que le process a bien été tué
#                         prey_proc.join()
#                         # renvoyer la réponse au prédateur
#                         reponse = "proie"
#                     reponse_predateur[predator_pid].put(reponse)
                    

#             time.sleep(1)
#     except KeyboardInterrupt:
#         display_queue.put("[env] stop")
