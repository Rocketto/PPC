import time, os
from multiprocessing import Process, Queue

class Predator:
    def __init__(self, energy):
        self.energy = energy

    def start(self): 
        while True: 
            print(f"[predator {os.getpid()}] alive: {self.energy}")
            time.sleep(2)



class Prey:
    def __init__(self, energy):
        self.energy = energy

    def start(self): 
        while True: 
            print(f"[prey {os.getpid()}] alive: {self.energy}")
            time.sleep(2)

    def prey_step(grass_count, prey_energy, threshold_H, threshold_R):
        return grass_count - 1, prey_energy + 1


class Display:
    def __init__(self, queue):
        self.queue = queue


    def start(self):
        while True:
            print("[display] alive")
            while not self.queue.empty():
                msg = self.queue.get()
                print("[display] received:", msg)
            time.sleep(1)






def main():
    display_queue = Queue()
    grass_count, prey_count, predator_count = 200, 1, 2
    grass_max = 300
    prey_energy, predator_energy = 50, 80
    threshold_H = 20; threshold_R = 60
    display = Display(display_queue)
    display_process = Process(target = Display.start, args=(display,))
    display_process.start()

    for id in range (prey_count):
        prey = Prey(prey_energy)
        p = Process(target=Prey.start, args = (prey,))
        p.start()

    for id in range (predator_count):
        predator = Predator(predator_energy)
        p = Process(target=Predator.start, args = (predator,))
        p.start()
    try:
        while True: 
            # Croissance naturelle de l'herbe
            grass_count = min(grass_count + 1, grass_max)
            # Décroissance de l'énergie des proies et prédateurs
            prey_energy -= 1
            predator_energy -= 1
            if prey_energy < 0 or predator_energy < 0: 
                display_queue.put("death")
                break
            if prey_energy < threshold_H and grass_count > 0: 
                grass_count, prey_energy = prey_step(grass_count, prey_energy, threshold_H, threshold_R)

            if prey_energy > threshold_R: 
                prey_count += 1
                prey_energy -= 10

            display_queue.put(f"prey_energy ={prey_energy}" )
            display_queue.put(f"predator_energy ={predator_energy}" )
            display_queue.put(f"grass_count ={grass_count}" )
            time.sleep(1)
           

    except KeyboardInterrupt: display_queue.put("[env] stop")

if __name__ == "__main__":
    main()
