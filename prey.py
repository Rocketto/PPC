from multiprocessing import Manager, Process
import os, time, logging


class Prey:
    def __init__(self, grass, grass_lock, prey_infos, parameters : dict, ):
        """
        Initialisation Proie.

        :param self: Proie.
        :param grass: Memoire partagée avec acces a l'herbe.
        :param grass_lock: Protection acces partagé.
        :param args: Parametres pour objet Animal
        """

        self.grass = grass
        self.grass_lock = grass_lock
        self.prey_infos = prey_infos
        self.parameters = parameters
        self.energy = parameters["energy"]

        # On démarre le process de la proie qui a été créée
        p = Process(target=Prey.vivre,args=(self,))
        p.start()
        # On ajoute le PID de la proie au dictionnaire manager et celle-ci nait inactive
        self.prey_infos[p.pid] = False

        
    
    def vivre(self):
        """
        Procedure principale de vie (et du process).
        Tant qu'il y a de l'energie, l'animal vit.

        :param self: animal
        """
        self.pid = os.getpid()
        while self.energy > 0:
            # jour qui passe
            time.sleep(1)
            # metabolisme de l'animal
            self.energy -= 1
            # On essaie de se reproduire
            if self.energy > self.parameters["reproduction"]:
                self.energy -= 20
                # Création de l'enfant
                Prey(self.grass, self.grass_lock, self.prey_infos, self.parameters)
            # On regarde si on a besoin de manger
            if self.energy < self.parameters["hunger"]:
                self.prey_infos[self.pid] = True
                # Manger de l'herbe si disponible
                with self.grass_lock:
                    if self.grass.value > 0:
                        # La proie peut manger entre 1 et 5 herbes (selon disponibilité)
                        quantite = min(5, self.grass.value)
                        self.grass.value -= quantite
                        self.energy += quantite
                        logging.debug(
                            f"ate {quantite} grass, grass left={self.grass.value}")
                    else:
                        self.status("famine!")
            else:
                self.prey_infos[self.pid] = False 
        logging.debug("die")        

