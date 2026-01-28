# environment.py
import time
from multiprocessing import Process, Value, Lock, Queue
from multiprocessing.managers import BaseManager
from prey import Prey
from animal import Animal
from predator import Predator
from display import Display


class Ecosysteme:

    def __init__(self):
        parametres = {
        "predator": {
            "count": 2,
            "energy": 40,
            "hunger": 20,
            "reproduction": 70
        },
        "prey": {
            "count": 10,
            "energy": 25,
            "hunger": 20,
            "reproduction": 60
        },
        "env": {
            "grass": {
                "init": 200,
                "max": 300,
                "croissance": 7
            }
        }}

    def ngrasse(self): return self.parametres["env"]["grass"]["init"]
    def nprey(self): return self.parametres["prey"]["count"]
    def npredators(self): return self.parametres["predator"]["count"]



class EcosystemeManager(BaseManager):  pass # On crée une sous-classe vide

# On enregistre la classe 'MonEcosysteme' sous le nom de clé 'Ecosysteme'
EcosystemeManager.register('Ecosysteme', Ecosysteme) #le nom de la mémoire partagée est 'Ecosysteme'


import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent



if __name__ == "__main__":
    with EcosystemeManager() as manager:
        # Création de l'instance partagée
        eco_partage = manager.Ecosysteme()

        # Creation des proies
        
        for _ in range(eco_partage.nprey()):
            subprocess.Popen([sys.executable, str(BASE_DIR / "prey.py")])

        # Creation des prédateurs
        for _ in range(eco_partage.npredators()):
            subprocess.Popen([sys.executable, str(BASE_DIR / "predator.py")])





# def run_environment():
#     # Parametres d'execution
#     # Peut etre mis dans un JSON externe
#     parameters = {
#         "predator": {
#             "count": 2,
#             "energy": 40,
#             "hunger": 20,
#             "reproduction": 70
#         },
#         "prey": {
#             "count": 10,
#             "energy": 25,
#             "hunger": 20,
#             "reproduction": 60
#         },
#         "env": {
#             "grass": {
#                 "init": 200,
#                 "max": 300,
#                 "croissance": 7
#             }
#         }
#     }



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
