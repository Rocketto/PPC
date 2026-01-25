import time
from multiprocessing import Process


def prey_loop(): 
    while True: print("[prey] alive"); time.sleep(2)



def main():
    grass, prey_count, predator_count = 200, 10, 3
    print(grass, prey_count, predator_count)
    grass_max = 300
    prey_energy, predator_energy = 50, 80
    H = 20; R = 60

    try:
        while True: 
            print("[env] tick")
            grass = min(grass + 1, grass_max)
            prey_energy -= 1; predator_energy -= 1
            if prey_energy < 0 or predator_energy < 0: print("death"); break
            if prey_energy < H and grass > 0: 
                grass, prey_energy = prey_step(grass, prey_energy, H, R)

            if prey_energy > R: 
                prey_count += 1; prey_energy -= 10

            print("prey_energy =", prey_energy)
            
            print("grass =", grass)
            time.sleep(1)
            p = Process(target=prey_loop)
            p.start()

    except KeyboardInterrupt: print("[env] stop")

if __name__ == "__main__":
    main()
