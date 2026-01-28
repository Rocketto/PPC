import time, os, signal, logging
from multiprocessing import Process

class Predator:
    """Predator eats Preys"""

    def __init__(self, predator_count, prey_infos, parameters : dict):
        """
        Constructeur de Predator

        :param self: predateur
        :param prey_infos: mémoire partagée dico 
        :param parameters: paramètres de création de la simu
        """

        self.prey_infos = prey_infos
        self.parameters = parameters
        self.energy = parameters["energy"]
        self.predator_count = predator_count

        # On démarre le process du prédateur qui a été créé
        p = Process(target=Predator.vivre,args=(self,))
        p.start()

        

        
        
    def vivre(self):
        self.predator_count.value += 1
        while self.energy > 0:
            # jour qui passe
            time.sleep(1)
            # metabolisme de l'animal
            self.energy -= 1
            # On essaie de se reproduire
            if self.energy > self.parameters["reproduction"]:
                self.energy -= 20
                # Création de l'enfant
                Predator(self.prey_infos, self.parameters)
            # Chercher a manger si necessaire
            if self.energy < self.parameters["hunger"]:
                # demander une proie à l'environnement
                for pid, etat_actif in  self.prey_infos.items():
                    # On teste si la proie est active
                    if etat_actif:
                        try:
                            # Le prédateur tue la proie
                            os.kill(pid, signal.SIGTERM)
                            # Le prédateur récupère de la vie après avoir mangé
                            self.energy += 10
                            del self.prey_infos[pid]
                            logging.debug(f"[predator {os.getpid()}] killed {pid}")
                            break
                        except Exception as e:
                            logging.debug("kill failed:", e)
        logging.debug("die")
        self.predator_count.value -= 1
