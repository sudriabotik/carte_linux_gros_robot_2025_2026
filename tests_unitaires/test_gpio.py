import subprocess

tirette = "PIN_15"
couleur = "PIN_27"

def read_gpio(pin_name: str) -> int:
    # Récupérer le chip et la ligne via gpiofind
    result = subprocess.run(
        ["gpiofind", pin_name],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"GPIO {pin_name} introuvable")

    chip_name, line_number = result.stdout.strip().split()
    line_number = int(line_number)

    # Lire la valeur avec gpioget
    result = subprocess.run(
        ["gpioget", chip_name, str(line_number)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Impossible de lire {pin_name}")

    return int(result.stdout.strip())

def read_gpio_tirette():
    ''' 
    Par default il y a un pull up sur la pcb. donc l'état de la tirette avec l'interrupteur ouvert est 1
    Lorsque la tirette est insérer alors l'état passe à 0
    '''
    val= read_gpio(tirette)
    return val 


def read_gpio_couleur():
    ''' 
    Lorsque l'interrupteur est ouvert alors l'état est à 1
    Lorsque l'interrupteur est fermé alors l'état est à 0

    Equipe Bleu = 0
    Equipe Jaune = 1
    '''
    val= read_gpio(couleur)
    return val 
