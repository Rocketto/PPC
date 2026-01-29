# predator.py
import os
import socket
import time
import signal
from multiprocessing.managers import BaseManager


# --- TCP vers environment pour annoncer PID predator  ---
ENV_HOST = "localhost"
TCP_PORT = 50010

# --- BaseManager pour accéder au monde ---
MANAGER_HOST = "localhost"
MANAGER_PORT = 50020
AUTH = b"PPC"


class EcosystemeManager(BaseManager):
    pass


EcosystemeManager.register("get_ecosysteme")


def announce_pid_to_env(pid: int):
    with socket.create_connection((ENV_HOST, TCP_PORT), timeout=3) as s:
        s.sendall(f"{pid}\n".encode("utf-8"))   # envoi PID + \n


def main():
    pid = os.getpid()

    # 1) annoncer son PID à environment via TCP (optionnel mais tu l'as déjà)
    try:
        announce_pid_to_env(pid)
        print(f"[predator] Mon PID est {pid}")
    except Exception as e:
        print(f"[predator] Il y a plus de serveur TCP... {e}")

    # 2) se connecter au manager (pour accéder à la liste des proies)
    m = EcosystemeManager(address=(MANAGER_HOST, MANAGER_PORT), authkey=AUTH)
    m.connect()
    eco = m.get_ecosysteme()

    # Enregistrement dans la mémoire partagée
    eco.register_predator(pid)

    energy = eco.get_parametres()["predator"]["start_energy"]
    hunger_threshold = eco.get_parametres()["predator"]["hunger_threshold"]
    energy_loss_per_sec = 1

    try:
        while True:
            time.sleep(1)
            energy -= energy_loss_per_sec

            if energy < hunger_threshold:
                prey_pid = eco.pick_mangeable_prey()  # atomique: récupère + retire
                if prey_pid is None:
                    print(f"[predator {pid}] hungry but no prey")
                    continue

                # 3) tuer la proie (PID)
                try:
                    os.kill(prey_pid, signal.SIGTERM)
                    eco.set_prey_mangeable(prey_pid, False)
                    eco.unregister_prey(prey_pid)
                    print(f"[prey] cleanup done pid={prey_pid}")            
                    energy += 70
                    print(
                        f"[predator {pid}] ate prey pid={prey_pid} -> energy={energy}")
                except ProcessLookupError:
                    # la proie était déjà morte
                    print(f"[predator {pid}] prey pid={prey_pid} already dead")
            if energy < 0:
                print(f"[prey {pid}] died (energy<0)")
                break
    finally:
        # Si on meur on enleve le pid de la liste des prédateurs vivants
        eco.unregister_predator(pid)


if __name__ == "__main__":
    main()
