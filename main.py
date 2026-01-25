#!/usr/bin/env python3
import time
import os
from multiprocessing import Process, Value, Lock, Queue


class Animal:
    def __init__(self, race: str, parameters: dict):
        """
        Initialisation de l'animal de base.

        :param self: Animal object.
        :param race: Type d'animal (pour log)
        :param parameters: Parametres de base.
        """
        self.race = race
        self.energy = parameters["energy"]
        self.niveau_faim = parameters["hunger"]
        self.niveau_reproduction = parameters["reproduction"]

    def id(self):
        return os.getpid()

    def status(self, message: str):
        print(f"{self.id()} {self.race} {message}")

    def vivre(self):
        """
        Procedure principale de vie (et du process).
        Tant qu'il y a de l'energie, l'animal vit.

        :param self: animal
        """
        while self.energy > 0:
            # jour qui passe
            time.sleep(1)
            # metabolisme de l'animal
            self.fonction_vitale()
        self.status("die")

    def fonction_vitale(self):
        """
        Fonction vitale animal de base.
        """
        self.energy -= 1
        if self.energy > 0:
            self.status(f"alive: {self.energy}")


class Predator(Animal):
    """Predator eats Preys"""

    def __init__(self, demande_proie, reponse_proie, *args):
        """
        Constructeur de Predator

        :param self: predateur
        :param args: Parametres pour objet Animal
        """
        super().__init__("predateur", *args)
        self.demande_proie = demande_proie
        self.reponse_proie = reponse_proie

    def fonction_vitale(self):
        # Checher a manger si necessaire
        if self.energy < self.niveau_faim:
            # demander une proie à l'environnement
            self.demande_proie.put(self.id())
            while self.reponse_proie.empty():
                time.sleep(0.01)
            prey_pid = self.reponse_proie.get()
            if prey_pid is not None:
                self.energy += 10
                self.status(
                    f"ate prey {prey_pid}, energy={self.energy}")
            else:
                self.status("no prey available")
        super().fonction_vitale()


class Prey(Animal):
    def __init__(self, grass, grass_lock, *args):
        """
        Initialisation Proie.

        :param self: Proie.
        :param grass: Memoire partagée avec acces a l'herbe.
        :param grass_lock: Protection acces partagé.
        :param args: Parametres pour objet Animal
        """
        super().__init__("proie", *args)
        self.grass = grass
        self.grass_lock = grass_lock

    def fonction_vitale(self):
        """
        La proie mange de l'herbe et a une fonction animale (energie).

        :param self: Description
        """
        if self.energy < self.niveau_faim:
            # Manger de l'herbe si disponible
            with self.grass_lock:
                if self.grass.value >= 1.0:
                    quantite = min(5, int(self.grass.value))
                    self.grass.value -= float(quantite)
                    self.energy += quantite
                    self.status(
                        f"ate {quantite} grass, grass left={self.grass.value}")
                else:
                    self.status("famine!")
        super().fonction_vitale()


class Display:
    def __init__(self, queue):
        self.queue = queue

    def start(self):
        while True:
            while not self.queue.empty():
                msg = self.queue.get()
                print("[display] received:", msg)
            time.sleep(0.2)


def main():
    # Parametres d'execution
    # Peut etre mis dans un JSON externe
    parameters = {
        "predator": {
            "count": 2,
            "energy": 40,
            "hunger": 20,
            "reproduction": 60
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
    grass_count = Value('d', float(parameters["env"]["grass"]["init"]))
    grass_growth = parameters["env"]["grass"]["croissance"]
    grass_max = parameters["env"]["grass"]["max"]
    # Communication vers le display
    display_queue = Queue()
    display_process = Process(target=Display.start,
                              args=(Display(display_queue),))
    display_process.start()
    # Creation des proies
    proies = []
    for _ in range(parameters["prey"]["count"]):
        prey = Prey(grass_count, grass_lock, parameters["prey"])
        p = Process(target=Animal.vivre,
                    args=(prey,))
        p.start()
        proies.append(p)
    # Creation des prédateurs
    # tous les predateurs demandent une proie sur cette file, avec son PID
    demande_proie = Queue()
    reponse_predateur = {}
    for _ in range(parameters["predator"]["count"]):
        # l'environnement repont individuellement sur cette file avec le PID de la proie, ou rien
        reponse_proie = Queue()
        predator = Predator(demande_proie, reponse_proie,
                            parameters["predator"])
        p = Process(target=Animal.vivre,
                    args=(predator,))
        p.start()
        reponse_predateur[p.pid] = reponse_proie

    try:
        while True:
            # Croissance naturelle de l'herbe
            with grass_lock:
                grass_count.value = min(
                    grass_count.value + grass_growth, grass_max)
                display_queue.put(f"grass: {grass_count.value}")
            # Traitement des demandes des prédateurs
            while not demande_proie.empty():
                predator_pid = demande_proie.get()
                prey_pid = None
                if proies:
                    # Prendre la première proie
                    prey_proc = proies.pop(0)
                    prey_pid = prey_proc.pid
                    prey_proc.kill()
                    prey_proc.join()
                # renvoyer la réponse au prédateur
                reponse_predateur[predator_pid].put(prey_pid)

            time.sleep(1)
    except KeyboardInterrupt:
        display_queue.put("[env] stop")


if __name__ == "__main__":
    main()
