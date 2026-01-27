from animal import Animal

class Prey(Animal):
    def __init__(self, grass, grass_lock, *animal_args):
        """
        Initialisation Proie.

        :param self: Proie.
        :param grass: Memoire partagée avec acces a l'herbe.
        :param grass_lock: Protection acces partagé.
        :param args: Parametres pour objet Animal
        """
        super().__init__("proie", *animal_args)
        self.grass = grass
        self.grass_lock = grass_lock

    def fonction_vitale(self):
        """
        La proie mange de l'herbe et a une fonction animale (energie).

        :param self: Description
        """
        super().fonction_vitale()
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

