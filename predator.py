from animal import Animal
import time

class Predator(Animal):
    """Predator eats Preys"""

    def __init__(self, reponse_proie, *animal_args):
        """
        Constructeur de Predator

        :param self: predateur
        :param args: Parametres pour objet Animal
        """
        super().__init__("predateur", *animal_args)
        self.reponse_proie = reponse_proie
        
    def fonction_vitale(self):
        super().fonction_vitale()
        # Chercher a manger si necessaire
        if self.energy < self.niveau_faim:
            # demander une proie à l'environnement
            self.requete_env.put(self.id())
            while self.reponse_proie.empty():
                time.sleep(0.01)
            reponse = self.reponse_proie.get()
            if reponse == "proie":
                self.energy += 10
                self.status(
                    f"ate prey {reponse}, energy={self.energy}")
            else:
                self.status("no prey available")
