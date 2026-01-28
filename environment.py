# environment.py
import time, logging
from multiprocessing import Process, Value, Lock, Queue, Manager
from prey import Prey
from predator import Predator
from display import Display

def run_environment():
    # Parametres d'execution
    # Peut etre mis dans un JSON externe
    parameters = {
        "predator": {
            "count": 2,
            "energy": 20,
            "hunger": 40,
            "reproduction": 30
        },
        "prey": {
            "count": 10,
            "energy": 20,
            "hunger": 40,
            "reproduction": 30
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
    # On crée un dictionnaire dans lequel on va entrer le nombre d'entités de chaque population
    population = dict()

    # Création du manager
    with Manager() as manager:
        # On crée un dictionnaire dans la mémoire partagée qui contient les infos de preys
        # Ce dictionnaire contient le pid et l'état de chaque proie( actif/passif)
        # clé: PID -> valeur : état
        prey_infos = manager.dict()
        # On crée une valeur qui contient le nombre de prédateurs en vie
        predator_count = manager.Value("i", 0)

        # Creation des proies
        for _ in range(parameters["prey"]["count"]):
            Prey(grass_count, grass_lock,prey_infos , parameters["prey"])

        

        # Creation des prédateurs
        for _ in range(parameters["predator"]["count"]):
            # l'environnement repont individuellement sur cette file avec le PID de la proie, ou rien
            Predator(predator_count, prey_infos, parameters["predator"])

        try:
            while True:
                # Croissance naturelle de l'herbe
                with grass_lock:
                    grass_count.value = min(grass_count.value + grass_growth, grass_max)
                # On met à jour les valeurs du nb de chaque population
                population["grass"] = grass_count.value
                population["prey"] = len(prey_infos)
                population["predator"] = predator_count.value
                display_queue.put(population)
                time.sleep(1)
        except KeyboardInterrupt:
            logging.debug("Interruption Clavier")
