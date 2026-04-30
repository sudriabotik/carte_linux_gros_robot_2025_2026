# Configuration automatique du PCAN-USB avec udev

## Vue d'ensemble

Cette solution configure automatiquement l'interface CAN (`can0`) dès que le PCAN-USB est branché. Le code Python attend ensuite que `can0` soit prêt avant de démarrer.

## Architecture complète

```
┌─────────────────────────────────────────────────────────────────┐
│  1. BRANCHEMENT PHYSIQUE                                        │
│  Branchement du PCAN-USB sur le port USB                        │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. DÉTECTION UDEV                                              │
│  Fichier : /etc/udev/rules.d/99-pcan-usb.rules                  │
│  Détecte le driver peak_usb + interface can0                    │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. CONFIGURATION AUTOMATIQUE                                   │
│  Script : /usr/local/bin/setup-pcan-helper.sh                   │
│  • Attend 1 seconde que l'interface soit créée                  │
│  • Configure bitrate à 500 kbps                                 │
│  • Active can0 (set UP)                                         │
│  • Écrit dans les logs système                                  │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. VÉRIFICATION PYTHON                                         │
│  Fonction : wait_for_can0() dans init_interface.py              │
│  • Vérifie toutes les 500ms si can0 existe                      │
│  • Vérifie que can0 est UP                                      │
│  • Timeout après 10 secondes                                    │
│  • Retourne True/False selon l'état                             │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. INITIALISATION BUS CAN                                      │
│  Code Python crée le bus socketcan sur can0                     │
│  can.interface.Bus(interface='socketcan', channel='can0', ...)  │
└─────────────────────────────────────────────────────────────────┘
```

## Installation rapide (une seule fois)

### Étape 1 : Copier les fichiers de configuration

```bash
# Se placer dans le dossier du projet
cd ~/carte_linux_gros_robot_2025_2026

# Copier le script de configuration
sudo cp tests_unitaires/setup-pcan-helper.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/setup-pcan-helper.sh

# Copier la règle udev
sudo cp tests_unitaires/99-pcan-usb.rules /etc/udev/rules.d/

# Recharger udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Étape 2 : Vérifier l'installation

```bash
# 1. Vérifier que les fichiers sont bien copiés
ls -la /usr/local/bin/setup-pcan-helper.sh
# Doit afficher : -rwxr-xr-x (exécutable)

ls -la /etc/udev/rules.d/99-pcan-usb.rules
# Doit afficher : -rw-r--r--

# 2. Tester en débranchant/rebranchant le PCAN-USB
# Attendre 2 secondes après le branchement

# 3. Vérifier que can0 est UP
ip link show can0
# Doit afficher : state UP et <NOARP,UP,LOWER_UP,ECHO>

# 4. Voir les logs de configuration
journalctl -n 20 | grep -i pcan
# Doit afficher : "PCAN-USB: Interface can0 configurée automatiquement (500 kbps)"
```

## Fichiers de configuration

### 1. Règle udev : `99-pcan-usb.rules`

Emplacement : `/etc/udev/rules.d/99-pcan-usb.rules`

```bash
# Détecte le PCAN-USB et lance la configuration automatique
ACTION=="add", SUBSYSTEM=="net", ENV{ID_USB_DRIVER}=="peak_usb", ENV{INTERFACE}=="can0", RUN+="/usr/local/bin/setup-pcan-helper.sh"
```

**Déclenchement** :
- Uniquement au **branchement** du PCAN-USB (pas au boot)
- Match sur le driver `peak_usb` ET l'interface `can0`

### 2. Script de configuration : `setup-pcan-helper.sh`

Emplacement : `/usr/local/bin/setup-pcan-helper.sh`

```bash
#!/usr/bin/bash
# Configuration automatique de can0 au branchement du PCAN-USB

# Attendre que l'interface soit prête
sleep 1

# Configurer bitrate et activer can0
/sbin/ip link set can0 type can bitrate 500000
/sbin/ip link set can0 up

# Logger l'événement
logger "PCAN-USB: Interface can0 configurée automatiquement (500 kbps)"

exit 0
```

### 3. Fonction Python : `wait_for_can0()`

Emplacement : `core/interface/init_interface.py`

```python
def wait_for_can0(timeout=10):
    """
    Attend que can0 soit UP et configuré avant de créer le bus CAN.
    Vérifie toutes les 500ms pendant max 10 secondes.

    :param timeout: Temps max d'attente en secondes
    :return: True si can0 est prêt, False sinon
    """
    logger.log_info("Init", "Waiting for can0 interface...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Vérifier si can0 existe et est UP
            result = subprocess.run(
                ['ip', 'link', 'show', 'can0'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                if 'state UP' in result.stdout or 'UP' in result.stdout:
                    logger.log_info("Init", "can0 is UP and ready")
                    return True
                else:
                    logger.log_info("Init", f"can0 exists but not UP yet, waiting...")

        except Exception as e:
            logger.log_warning("Init", f"can0 check failed: {e}")

        time.sleep(0.5)  # Attendre 500ms avant de réessayer

    logger.log_error("Init", f"can0 not ready after {timeout}s")
    return False
```

**Usage dans le code** :

```python
# Attendre que can0 soit prêt AVANT de créer le bus
if not wait_for_can0(timeout=10):
    raise RuntimeError("can0 interface not available - cannot start robot")

# Créer le bus CAN (can0 est maintenant garanti UP)
bus = can.interface.Bus(
    interface='socketcan',
    channel='can0',
    bitrate=500000
)
```

## Scénarios d'utilisation

### Scénario 1 : Boot avec PCAN branché

1. Le système démarre
2. Le driver `peak_usb` charge et crée `can0`
3. La règle udev détecte `can0` et lance `setup-pcan-helper.sh`
4. `can0` est configuré à 500 kbps et activé
5. Le programme Python démarre
6. `wait_for_can0()` trouve `can0` UP immédiatement
7. Le bus CAN est créé ✅

### Scénario 2 : Boot sans PCAN branché

1. Le système démarre
2. Le programme Python démarre
3. `wait_for_can0()` ne trouve pas `can0`
4. **Pendant ce temps**, tu branches le PCAN-USB
5. udev détecte et configure `can0` automatiquement
6. `wait_for_can0()` détecte `can0` UP dans les 500ms suivantes
7. Le bus CAN est créé ✅

### Scénario 3 : Débranchement/rebranchement en cours d'exécution

1. Le robot fonctionne normalement
2. Le PCAN-USB est débranché → Le bus CAN crash
3. Le PCAN-USB est rebranché
4. udev reconfigure `can0` automatiquement
5. Si le code redémarre (après crash), `wait_for_can0()` attend que `can0` soit prêt
6. Le bus CAN est recréé ✅

## Dépannage rapide

### Problème : `can0` ne se configure pas automatiquement

**Solution** :

```bash
# 1. Vérifier que les fichiers sont installés
ls -la /usr/local/bin/setup-pcan-helper.sh  # Doit être exécutable (-rwxr-xr-x)
ls -la /etc/udev/rules.d/99-pcan-usb.rules  # Doit exister

# 2. Vérifier le format du script (pas de CRLF Windows)
file /usr/local/bin/setup-pcan-helper.sh
# Doit afficher "UTF-8 text executable" (PAS de "CRLF")

# Si CRLF détecté, corriger :
sudo sed -i 's/\r$//' /usr/local/bin/setup-pcan-helper.sh

# 3. Tester le script manuellement
sudo /usr/local/bin/setup-pcan-helper.sh
ip link show can0  # Doit afficher "state UP"

# 4. Recharger udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Problème : `RuntimeError: can0 interface not available`

**Cause** : `wait_for_can0()` a timeout après 10 secondes.

**Solution** :

```bash
# 1. Vérifier si le PCAN-USB est détecté
lsusb | grep -i peak
# Doit afficher : "PEAK-System Technik GmbH"

# 2. Vérifier si le driver est chargé
lsmod | grep peak_usb
# Doit afficher : peak_usb

# 3. Vérifier les logs kernel
dmesg | tail -20
# Chercher des erreurs liées à peak_usb ou can0

# 4. Recharger le driver manuellement
sudo rmmod peak_usb
sudo modprobe peak_usb

# 5. Vérifier can0
ip link show can0
```

### Problème : `can0` devient `can1` après plusieurs débranchements

**Cause** : Le kernel incrémente le numéro d'interface.

**Solution** :

```bash
# Solution 1 : Redémarrer le système
sudo reboot

# Solution 2 : Recharger le driver
sudo rmmod peak_usb
sudo modprobe peak_usb
```

### Problème : Erreur "Device or resource busy"

**Cause** : `can0` est déjà configuré et UP. Le script essaie de le reconfigurer.

**Solution** : C'est normal, pas de problème. `can0` fonctionne déjà.

## Commandes utiles

### Vérifier l'état de can0

```bash
# État simple
ip link show can0

# État détaillé avec statistiques
ip -s link show can0

# Voir les trames CAN en temps réel
candump can0

# Envoyer une trame de test
cansend can0 123#DEADBEEF
```

### Voir les logs système

```bash
# Logs récents de udev
journalctl -n 50 | grep -i pcan

# Logs kernel récents
dmesg | tail -30

# Suivre les logs en temps réel
journalctl -f
```

### Débugger udev en temps réel

```bash
# Voir tous les événements udev
sudo udevadm monitor --environment --udev --property

# Débrancher/rebrancher le PCAN-USB et observer les événements
# Chercher : ID_USB_DRIVER=peak_usb, INTERFACE=can0
```

## Désinstallation

Pour revenir à une configuration manuelle :

```bash
# Supprimer la règle udev
sudo rm /etc/udev/rules.d/99-pcan-usb.rules

# Supprimer le script (optionnel)
sudo rm /usr/local/bin/setup-pcan-helper.sh

# Recharger udev
sudo udevadm control --reload-rules
```

## Avantages de cette solution

✅ **Configuration instantanée** : `can0` prêt 1 seconde après le branchement
✅ **Robustesse** : Fonctionne même si le PCAN est branché après le boot
✅ **Synchronisation Python** : `wait_for_can0()` attend que `can0` soit prêt
✅ **Pas d'intervention manuelle** : Aucune commande `ip link` à taper
✅ **Logs centralisés** : Tous les événements dans `journalctl`
✅ **Timeout intelligent** : Le programme Python échoue proprement si `can0` n'est pas prêt

## Configuration actuelle

- **Bitrate** : 500 kbps (500000 bps)
- **Timeout Python** : 10 secondes
- **Vérification Python** : Toutes les 500ms
- **Interface** : `socketcan` sur `can0`
- **Driver** : `peak_usb` (fourni par PCAN-USB)

## Checklist pour nouvelle installation (Rock 5C)

- [ ] Copier `setup-pcan-helper.sh` vers `/usr/local/bin/`
- [ ] Rendre `setup-pcan-helper.sh` exécutable (`chmod +x`)
- [ ] Copier `99-pcan-usb.rules` vers `/etc/udev/rules.d/`
- [ ] Recharger udev (`udevadm control --reload-rules`)
- [ ] Vérifier format du script (pas de CRLF)
- [ ] Tester en débranchant/rebranchant le PCAN-USB
- [ ] Vérifier `ip link show can0` → doit afficher `state UP`
- [ ] Vérifier les logs `journalctl | grep -i pcan`
- [ ] Lancer le programme Python pour tester `wait_for_can0()`
