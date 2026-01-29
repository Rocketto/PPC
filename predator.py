# predator.py
import os
import socket
import time

ENV_HOST = "localhost" 
ENV_PORT = 50010

def main():
    pid = os.getpid()

    try:
        with socket.create_connection((ENV_HOST, ENV_PORT), timeout=3) as s:
            s.sendall(f"{pid}\n".encode("utf-8"))  # envoi PID + \n
        print(f"[predator] Mon PID est {pid}")
    except Exception as e:
        print(f"[predator] Il y a plus de serveur... {e}")

    # boucle pour rester vivant (tu remplaceras par ton comportement)
    while True:
        time.sleep(2)

if __name__ == "__main__":
    main()








# from animal import Animal
# import time

# class Predator(Animal):
#     """Predator eats Preys"""

#     def __init__(self, reponse_proie, *animal_args):
#         """
#         Constructeur de Predator

#         :param self: predateur
#         :param args: Parametres pour objet Animal
#         """
#         super().__init__("predateur", *animal_args)
#         self.reponse_proie = reponse_proie
        
#     def fonction_vitale(self):
#         super().fonction_vitale()
#         # Chercher a manger si necessaire
#         if self.energy < self.niveau_faim:
#             # demander une proie à l'environnement
#             self.requete_env.put(self.id())
#             while self.reponse_proie.empty():
#                 time.sleep(0.01)
#             reponse = self.reponse_proie.get()
#             if reponse == "proie":
#                 self.energy += 10
#                 self.status(
#                     f"ate prey {reponse}, energy={self.energy}")
#             else:
#                 self.status("no prey available")
