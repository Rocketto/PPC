# prey.py
import os
import socket
import time
from multiprocessing.managers import BaseManager

ENV_HOST = "localhost"
TCP_PORT = 50010
MANAGER_PORT = 50020
AUTH = b"PPC"

class EcosystemeManager(BaseManager): pass
EcosystemeManager.register("get_ecosysteme")


def main():
    pid = os.getpid()
    print(f"[prey] Début du processus :{pid}")

    try:
        with socket.create_connection((ENV_HOST, TCP_PORT), timeout=3) as s:
            s.sendall(f"{pid}\n".encode("utf-8"))  # envoi PID + \n
        print(f"[prey] Mon PID est {pid}")
    except Exception as e:
        print(f"[prey] Il n'y a plus de serveur... {e}")

    # Connexion au manager de environment
    m = EcosystemeManager(address=(ENV_HOST, MANAGER_PORT), authkey=AUTH)
    m.connect()
    eco = m.get_ecosysteme()

    # Paramètres prey (tu peux ensuite les récupérer depuis eco si tu veux)
    energy = 25
    hunger_threshold = 20     # si energy < 20 => manger
    energy_loss_per_sec = 1
    eat_amount = 1            # herbe demandée par “bouchée”
    energy_gain_per_grass = 3 # 1 herbe -> +3 énergie

    while True:
        time.sleep(1)
        energy -= energy_loss_per_sec

        if energy < hunger_threshold:
            # Demande à manger : opération atomique côté serveur
            eaten = eco.take_grass(eat_amount)

            if eaten > 0:
                energy += eaten * energy_gain_per_grass
                print(f"[prey {pid}] ate {eaten} grass -> energy={energy} (grass_left={eco.get_grass_count()})")
            else:
                print(f"[prey {pid}] hungry but no grass -> energy={energy}")

        # mort simple
        if energy < 0:
            print(f"[prey {pid}] died (energy<0)")
            break


if __name__ == "__main__":
    main()







    












# from animal import Animal

# class Prey(Animal):
#     def __init__(self, grass, grass_lock, *animal_args):
#         """
#         Initialisation Proie.

#         :param self: Proie.
#         :param grass: Memoire partagée avec acces a l'herbe.
#         :param grass_lock: Protection acces partagé.
#         :param args: Parametres pour objet Animal
#         """
#         super().__init__("proie", *animal_args)
#         self.grass = grass
#         self.grass_lock = grass_lock

#     def fonction_vitale(self):
#         """
#         La proie mange de l'herbe et a une fonction animale (energie).

#         :param self: Description
#         """
#         super().fonction_vitale()
#         if self.energy < self.niveau_faim:
#             # Manger de l'herbe si disponible
#             with self.grass_lock:
#                 if self.grass.value >= 1.0:
#                     quantite = min(5, int(self.grass.value))
#                     self.grass.value -= float(quantite)
#                     self.energy += quantite
#                     self.status(
#                         f"ate {quantite} grass, grass left={self.grass.value}")
#                 else:
#                     self.status("famine!")

