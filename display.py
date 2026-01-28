import time, logging
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Display:
    def __init__(self, queue):
        self.queue = queue

    def start(self):
        plt.style.use("dark_background")

        fig, ax = plt.subplots()
        ax.set_title("Populations (temps réel)")
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
                logging.error(f"{population}")
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

        ani = animation.FuncAnimation(fig, update, interval=50)
        plt.show()