import time
import logging
import os
import signal
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button


class Display:
    def __init__(self, queue, env_pid):
        self.queue = queue
        self.env_pid = env_pid

    def start(self):
        plt.style.use("dark_background")

        fig, ax = plt.subplots()
        ax.set_title("Populations")
        ax.set_xlabel("Temps")
        ax.set_ylabel("Population")

        # buffers (glissants)
        max_len = 200
        t = deque(maxlen=max_len)
        proie = deque(maxlen=max_len)
        predateur = deque(maxlen=max_len)
        herbe = deque(maxlen=max_len)

        line_proie, = ax.plot([], [], color="white", label="Proie")
        line_predateur, = ax.plot([], [], color="red", label="Prédateur")
        line_herbe, = ax.plot([], [], color="green", label="Herbe")

        ax.legend(loc="upper right")

        start = time.time()

        def update(frame):
            while not self.queue.empty():
                population = self.queue.get()
                logging.debug(f"{population}")
                t.append(time.time() - start)
                proie.append(population["prey"])
                predateur.append(population["predator"])
                herbe.append(population["grass"])

            if not t:
                return line_proie, line_predateur, line_herbe

            line_proie.set_data(t, proie)
            line_predateur.set_data(t, predateur)
            line_herbe.set_data(t, herbe)

            ax.set_xlim(max(0, t[0]), t[-1] + 0.1)
            ax.set_ylim(0, max(max(proie), max(predateur), max(herbe)) * 1.2)

            return line_proie, line_predateur, line_herbe

        # Bouton sécheresse
        button_sech_ax = plt.axes([0.05, 0.9, 0.15, 0.05])
        button_sech = Button(button_sech_ax, "Secheresse")
        button_sech.label.set_color("red")

        # Callback du bouton sécheresse
        def activer_secheresse(event):
            os.kill(self.env_pid, signal.SIGUSR1)

        button_sech.on_clicked(activer_secheresse)

        # Bouton proie
        button_proie_ax = plt.axes([0.7, 0.9, 0.15, 0.05])
        button_proie = Button(button_proie_ax, "Proie")
        button_proie.label.set_color("red")

        # Callback du bouton proie
        def add_proie(event):
            os.kill(self.env_pid, signal.SIGUSR2)

        button_proie.on_clicked(add_proie)

        # Bouton prédateur
        button_predateur_ax = plt.axes([0.25, 0.9, 0.15, 0.05])
        button_predateur = Button(button_predateur_ax, "Prédateur")
        button_predateur.label.set_color("red")

        # Callback du bouton prédateur
        def add_predateur(event):
            os.kill(self.env_pid, signal.SIGHUP)

        button_predateur.on_clicked(add_predateur)

        ani = animation.FuncAnimation(fig, update, interval=50)
        plt.show()
