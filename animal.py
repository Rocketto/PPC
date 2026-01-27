import time, os

class Animal:
    def __init__(self, race: str, parameters: dict, requete_env):
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
        self.requete_env = requete_env

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

        if self.energy > self.niveau_reproduction:
            self.requete_env.put(self.race)
            self.energy -= 20