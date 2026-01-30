# environment.py
import threading
import socket
from pathlib import Path
import sys
import subprocess
import time
from multiprocessing import Process, Value, Lock, Queue
from multiprocessing.managers import BaseManager
# from prey import Prey
# from animal import Animal
# from predator import Predator
from display import Display
import socket
import threading
import signal
import os


class Ecosysteme:

    def __init__(self):

        self._lock = threading.Lock()  # mutex interne côté serveur

        self.prey_pids = set()  # PIDs des proies connectées

        self.parametres = {
            "predator": {
                "start_energy": 30,
                "hunger_threshold": 25,
                "count": 3,
                "reproduction": 0,
                "pids": []  # Tous les prédateurs vivants
            },
            "prey": {
                "start_energy": 30,
                "hunger_threshold": 25,                
                "count": 10,
                "reproduction": 0,
                "pids": [],          # toutes les proies vivantes
                "mangeables": []     # proies “actives / mangeables”
            },
            "env": {
                "grass": {
                    "count": 30,  # valeur initiale de l'herbe
                    "max": 60,
                    "croissance": 3},

                "temps": {
                    "tick": 0},

                "secheresse": {
                    "active": False,
                    "nombre": 0,
                    "duree": 5}

            }

        }

    def get_parametres(self):
        return self.parametres

    def inc_tick(self):  # Incrémente le tick et retourne la nouvelle valeur
        with self._lock:
            self.parametres["env"]["temps"]["tick"] += 1
            return self.parametres["env"]["temps"]["tick"]

    def herbe_pousse(self):
        with self._lock:
            self.parametres["env"]["grass"]["count"] += self.parametres["env"]["grass"]["croissance"]
            return self.parametres["env"]["grass"]["count"]

    # Sécheresse

    def active_secheresse(self):
        with self._lock:
            self.parametres["env"]["secheresse"]["active"] = True
            self.parametres["env"]["secheresse"]["nombre"] += 1

    def is_drought_active(self):
        """Renvoie si la sécheresse est active"""
        with self._lock:
            return self.parametres["env"]["secheresse"]["active"]

    def reset_grass_count(self):
        with self._lock:
            self.parametres["env"]["grass"]["count"] = 0

    def stop_secheresse(self):
        with self._lock:
            self.parametres["env"]["secheresse"]["active"] = False

    def get_drought_duration(self):
        with self._lock:
            return self.parametres["env"]["secheresse"]["duree"]

    def get_grass_max(self):
        with self._lock:
            return self.parametres["env"]["grass"]["max"]

    # def active_secheresse(self):
    #     self.parametres["env"]["secheresse"]["active"] = True
    #     self.parametres["env"]["secheresse"]["nombre"] += 1

    # def reset_grass_count(self):
    #     self.parametres["env"]["grass"]["count"] = 0
    #     self.parametres["env"]["secheresse"]["active"] = False

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

    # Partie prédateurs

    def register_prey(self, pid: int):
        with self._lock:
            pid = int(pid)
            if pid not in self.parametres["prey"]["pids"]:
                self.parametres["prey"]["pids"].append(pid)
            return True

    def unregister_prey(self, pid: int):
        with self._lock:
            pid = int(pid)
            if pid in self.parametres["prey"]["pids"]:
                self.parametres["prey"]["pids"].remove(pid)
            if pid in self.parametres["prey"]["mangeables"]:
                self.parametres["prey"]["mangeables"].remove(pid)
            return True

    def register_predator(self, pid: int):
        with self._lock:
            if pid not in self.parametres["predator"]["pids"]:
                self.parametres["predator"]["pids"].append(pid)

    def unregister_predator(self, pid):
        with self._lock:
            if pid in self.parametres["predator"]["pids"]:
                self.parametres["predator"]["pids"].remove(pid)

    def set_prey_mangeable(self, pid: int, mangeable: bool):
        with self._lock:
            pid = int(pid)
            if mangeable:
                if pid in self.parametres["prey"]["pids"] and pid not in self.parametres["prey"]["mangeables"]:
                    self.parametres["prey"]["mangeables"].append(pid)
            else:
                if pid in self.parametres["prey"]["mangeables"]:
                    self.parametres["prey"]["mangeables"].remove(pid)
            return True

    def pick_mangeable_prey(self):
        """Atomique: prend une proie mangeable et l'enlève de la liste."""
        with self._lock:
            if not self.parametres["prey"]["mangeables"]:
                return None
            # ou random, plus tard si on arrive à mettre des semaphores pour plusieurs prédateurs
            pid = self.parametres["prey"]["mangeables"].pop(0)
            return pid


# Temps qui passe

def time_pass(serveur_partage):
    while True:
        time.sleep(1)
        serveur_partage.inc_tick()

# Croissance de l'herbe


def grass_growth(eco):
    while True:
        if not eco.is_drought_active():
            if eco.get_grass_count() < eco.get_grass_max():
                eco.herbe_pousse()
                # print(f"[env] grass grown to {eco.get_grass_count()}")
            time.sleep(1)
        else:
            print("[env] drought ON -> reset grass")
            eco.reset_grass_count()
            time.sleep(eco.get_drought_duration())
            eco.stop_secheresse()
            print("[env] drought OFF")

# def grass_growth(serveur_partage):
#     while True:
#         while serveur_partage.get_parametres()["env"]["secheresse"]["active"] == False:
#             if serveur_partage.get_parametres()["env"]["grass"]["count"] < serveur_partage.get_parametres()["env"]["grass"]["max"]:
#                 serveur_partage.herbe_pousse()
#                 time.sleep(1)
#                 print(f"[env] grass grown to {serveur_partage.get_parametres()['env']['grass']['count']}")

#         # si la sécheresse est active
#         serveur_partage.reset_grass_count()
#         time.sleep(serveur_partage.get_parametres()["env"]["secheresse"]["duree"])


def secheresse_event(eco_global):
    eco_global.active_secheresse()


class EcosystemeManager(BaseManager):
    pass  # On crée une sous-classe vide


# On enregistre la classe 'MonEcosysteme' sous le nom de clé 'Ecosysteme'
eco_global = Ecosysteme()
EcosystemeManager.register("get_ecosysteme", callable=lambda: eco_global)


# Chemin d'accès du projet

BASE_DIR = Path(__file__).resolve().parent.parent

# Session TCP pour communication avec les prédateurs


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
                data = conn.recv(1024).decode(
                    "utf-8", errors="replace").strip()
                # ici on attend juste un PID sur une ligne
                if data.isdigit():
                    print(f"[env] connected from {addr}, pid={data}")
                else:
                    print(
                        f"[env] connection from {addr}, invalid pid='{data}'")


# Manager longue distance

def run_manager_server():
    manager = EcosystemeManager(
        address=(MANAGER_HOST, MANAGER_PORT), authkey=AUTH)
    server = manager.get_server()
    print(
        f"[env] EcosystemeManager listening on {MANAGER_HOST}:{MANAGER_PORT}")
    server.serve_forever()


def handle_display_signal(signum, frame):
    if signum == signal.SIGUSR1:
        eco_global.active_secheresse()
    elif signum == signal.SIGHUP:
        subprocess.Popen([sys.executable, str(
            BASE_DIR / "PPC" / "predator.py")])
    else:
        subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "prey.py")])


if __name__ == "__main__":

    # Réception des signaux envoyés par Display
    signal.signal(signal.SIGUSR1, handle_display_signal)
    signal.signal(signal.SIGUSR2, handle_display_signal)
    signal.signal(signal.SIGHUP, handle_display_signal)

    # Communication vers le display
    display_queue = Queue()
    display_process = Process(target=Display.start, args=(Display(display_queue, os.getpid()),))
    display_process.start()

    # On crée un dictionnaire dans lequel on va entrer le nombre d'entités de chaque population
    population = dict()
    # Démarre le serveur BaseManager (pour prey/predator), serveur longue distance
    threading.Thread(target=run_manager_server, daemon=True).start()
    # Démarre le serveur TCP (pour recevoir PID des predators)
    threading.Thread(target=tcp_server_loop, daemon=True).start()
    time.sleep(1)  # Attendre que le serveur démarre
    # Démarre la "vie du monde" EN THREADS
    time_thread = threading.Thread(
        target=time_pass, args=(eco_global,), daemon=True)
    grass_thread = threading.Thread(
        target=grass_growth, args=(eco_global,), daemon=True)
    time_thread.start()
    grass_thread.start()

    # Creation des proies
    for _ in range(eco_global.get_parametres()["prey"]["count"]):
        subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "prey.py")])
    # Creation des prédateurs
    for _ in range(eco_global.get_parametres()["predator"]["count"]):
        subprocess.Popen([sys.executable, str(
            BASE_DIR / "PPC" / "predator.py")])

    try:
        while True:
            population["grass"] = eco_global.get_parametres()[
                "env"]["grass"]["count"]
            population["prey"] = len(
                eco_global.get_parametres()["prey"]["pids"])
            population["predator"] = len(eco_global.get_parametres()[
                "predator"]["pids"])
            display_queue.put(population)
            print(len(eco_global.get_parametres()["prey"]["mangeables"]))
            time.sleep(1)
    except KeyboardInterrupt:
        print("[env] stopping")

    # ## Test de la sécheresse forcée
    # # Démarre le serveur BaseManager (pour prey/predator), serveur longue distance
    # threading.Thread(target=run_manager_server, daemon=True).start()
    # # Démarre le serveur TCP (pour recevoir PID des predators)
    # threading.Thread(target=tcp_server_loop, daemon=True).start()
    # time.sleep(1)  # Attendre que le serveur démarre
    # # Démarre la "vie du monde" EN THREADS
    # time_thread = threading.Thread(target=time_pass, args=(eco_global,), daemon=True)
    # grass_thread = threading.Thread(target=grass_growth, args=(eco_global,), daemon=True)
    # time_thread.start()
    # grass_thread.start()
    # # Spawn une proie test
    # subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "prey.py")])
    # # Test sécheresse (dans le même process => pas de copie)
    # time.sleep(5)
    # print("[env] forcing drought")
    # eco_global.active_secheresse()
    # time.sleep(5)
    # print("ça repousse")
    # # Boucle principale
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("[env] stopping")

    # ## Test serveur TCP
    # # Démarrage du serveur TCP dans un thread séparé
    # threading.Thread(target=tcp_server_loop, daemon=True).start()
    # time.sleep(1)  # Attendre que le serveur démarre
    # # Creation des proies
    # subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "prey.py")])
    # subprocess.Popen([sys.executable, str(BASE_DIR / "PPC" / "predator.py")])
