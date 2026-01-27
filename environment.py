# environment.py
import time
from multiprocessing import Process, Value, Lock, Queue
from prey import Prey
from animal import Animal
from predator import Predator
from display import Display

def run_environment():
    # Parametres d'execution
    # Peut etre mis dans un JSON externe
    parameters = {
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
        }
    }
    # Etat de l'herbe en memoire partagée
    # Type réel, car facteur de croissance reel
    grass_lock = Lock()
    grass_count = Value('i', parameters["env"]["grass"]["init"])
    grass_growth = parameters["env"]["grass"]["croissance"]
    grass_max = parameters["env"]["grass"]["max"]
    # Communication vers le display
    display_queue = Queue()
    display_process = Process(target=Display.start,args=(Display(display_queue),))
    display_process.start()
    # Creation des proies
    proies = []
    for _ in range(parameters["prey"]["count"]):
        prey = Prey(grass_count, grass_lock, parameters["prey"],requete_env)
        p = Process(target=Prey.vivre,args=(prey,))
        p.start()
        proies.append(p)

    # file communication animal vers environnement
    requete_env = Queue()  

    # Creation des prédateurs
    reponse_predateur = {}
    for _ in range(parameters["predator"]["count"]):
        # l'environnement repont individuellement sur cette file avec le PID de la proie, ou rien
        reponse_proie = Queue()
        predator = Predator(reponse_proie,parameters["predator"],requete_env)
        p = Process(target=Predator.vivre,args=(predator,))
        p.start()
        reponse_predateur[p.pid] = reponse_proie

    try:
        while True:
            # Croissance naturelle de l'herbe
            with grass_lock:
                grass_count.value = min(grass_count.value + grass_growth, grass_max)
                display_queue.put(f"grass: {grass_count.value}")
            # Traitement des demandes des prédateurs
            while not requete_env.empty():
                requete_recue = requete_env.get()
                if requete_recue == "proie":
                    prey = Prey(grass_count, grass_lock, parameters["prey"],requete_env)
                    p = Process(target=Prey.vivre,args=(prey,))
                    p.start()
                    proies.append(p)
                elif requete_recue == "predateur":
                    reponse_proie = Queue()
                    predator = Predator(reponse_proie,parameters["predator"],requete_env)
                    p = Process(target=Predator.vivre,args=(predator,))
                    p.start()
                    reponse_predateur[p.pid] = reponse_proie

                # sinon c'est un pid
                else:
                    predator_pid = requete_recue
                    reponse = "rien"

                    if proies:
                        # Prendre la première proie
                        prey_proc = proies.pop(0)
                        prey_proc.kill()
                        # Attendre le que le process a bien été tué
                        prey_proc.join()
                        # renvoyer la réponse au prédateur
                        reponse = "proie"
                    reponse_predateur[predator_pid].put(reponse)
                    

            time.sleep(1)
    except KeyboardInterrupt:
        display_queue.put("[env] stop")
