import subprocess

tirette = "PIN_15"
couleur = "PIN_27"

def read_gpio(pin_name: str) -> int:
    # Récupérer le chip et la ligne via gpiofind
    result = subprocess.run(
        ["/usr/bin/gpiofind", pin_name], # gpiofind
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"GPIO {pin_name} introuvable")

    chip_name, line_number = result.stdout.strip().split()
    line_number = int(line_number)

    # Lire la valeur avec gpioget
    result = subprocess.run(
        ["/usr/bin/gpioget", chip_name, str(line_number)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Impossible de lire {pin_name}")

    return int(result.stdout.strip())

def read_gpio_debug(pin_name: str) -> int:
    import os
    
    # Récupérer le chip et la ligne via gpiofind
    result = subprocess.run(
        ["/usr/bin/gpiofind", pin_name],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"[GPIO DEBUG] gpiofind failed: {result.stderr}")
        raise RuntimeError(f"GPIO {pin_name} introuvable")

    chip_name, line_number = result.stdout.strip().split()
    line_number = int(line_number)

    # Lire la valeur avec gpioget
    result = subprocess.run(
        ["/usr/bin/gpioget", chip_name, str(line_number)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"[GPIO DEBUG] gpioget failed")
        print(f"[GPIO DEBUG] stderr: {result.stderr}")
        print(f"[GPIO DEBUG] PATH: {os.environ.get('PATH')}")
        print(f"[GPIO DEBUG] Groups: {os.getgroups()}")
        raise RuntimeError(f"Impossible de lire {pin_name}")

    return int(result.stdout.strip())


''' 
    Il y a un pull up sur la carte. 
    Lorsque l'interrupteur est ouvert alors l'état est à 1
    Lorsque l'interrupteur est fermé alors l'état est à 0
'''
def read_gpio_tirette():
    ''' 
    tirette inséret = 0
    tirette absente = 1
    '''
    val= read_gpio_debug(tirette)
    return val 


def read_gpio_couleur():
    ''' 
    Equipe Bleu = 0
    Equipe Jaune = 1
    '''
    val= read_gpio(couleur)
    return val 

if __name__ == "__main__":
    read_gpio_tirette()
