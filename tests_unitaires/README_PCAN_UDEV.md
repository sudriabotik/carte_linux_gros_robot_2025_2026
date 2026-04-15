# Configuration automatique du PCAN-USB avec udev

## Problème résolu

Quand tu débranches/rebranches le PCAN-USB, l'interface `can0` est recréée mais **pas configurée**. Cette solution configure automatiquement `can0` dès que le PCAN-USB est branché.

## Architecture de la solution

La solution repose sur 2 fichiers :

1. **99-pcan-usb.rules** : Règle udev qui détecte le branchement du PCAN-USB
2. **setup-pcan-helper.sh** : Script qui configure can0 (bitrate + activation)

```
┌─────────────────┐
│  PCAN-USB       │
│  branché        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  udev détecte l'événement       │
│  99-pcan-usb.rules              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Exécute setup-pcan-helper.sh   │
│  • ip link set can0 bitrate     │
│  • ip link set can0 up          │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│  can0 prêt      │
│  (500 kbps)     │
└─────────────────┘
```

## Installation (à faire une seule fois)

### Étape 1 : Copier le script helper

```bash
# Depuis le dossier du projet
sudo cp tests_unitaires/setup-pcan-helper.sh /usr/local/bin/

# Rendre le script exécutable
sudo chmod +x /usr/local/bin/setup-pcan-helper.sh

# Vérifier
ls -la /usr/local/bin/setup-pcan-helper.sh
# Devrait afficher : -rwxr-xr-x
```

### Étape 2 : Copier la règle udev

```bash
# Copier la règle
sudo cp tests_unitaires/99-pcan-usb.rules /etc/udev/rules.d/

# Recharger les règles udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Étape 3 : Test

```bash
# Débrancher le PCAN-USB physiquement
# Attendre 2 secondes
# Rebrancher le PCAN-USB
# Attendre 2 secondes

# Vérifier que can0 est UP
ip link show can0
# Devrait afficher : state UP et <NOARP,UP,LOWER_UP,ECHO>

# Voir les logs
journalctl -n 20 | grep -i pcan
# Devrait afficher : "PCAN-USB: Interface can0 configurée automatiquement (500 kbps)"
```

## Fichiers de configuration

### 99-pcan-usb.rules

```bash
# Méthode : Match sur le driver peak_usb ET l'interface can0
ACTION=="add", SUBSYSTEM=="net", ENV{ID_USB_DRIVER}=="peak_usb", ENV{INTERFACE}=="can0", RUN+="/usr/local/bin/setup-pcan-helper.sh"
```

**Explication** :
- `ACTION=="add"` : Détecte l'ajout d'un périphérique
- `SUBSYSTEM=="net"` : Filtre sur les interfaces réseau
- `ENV{ID_USB_DRIVER}=="peak_usb"` : Vérifie que c'est le driver PCAN
- `ENV{INTERFACE}=="can0"` : Vérifie que c'est l'interface can0
- `RUN+=` : Exécute le script de configuration

### setup-pcan-helper.sh

```bash
#!/usr/bin/bash
# Script helper pour udev - Configure can0 automatiquement

# Attendre que l'interface soit prête
sleep 1

# Configurer can0
/sbin/ip link set can0 type can bitrate 500000
/sbin/ip link set can0 up

# Logger l'événement
logger "PCAN-USB: Interface can0 configurée automatiquement (500 kbps)"

exit 0
```

**Explication** :
- `sleep 1` : Attend que l'interface soit complètement créée
- `ip link set can0 type can bitrate 500000` : Configure le bitrate à 500 kbps
- `ip link set can0 up` : Active l'interface
- `logger` : Envoie un message aux logs système

## Dépannage

### can0 ne se configure pas automatiquement

```bash
# 1. Vérifier que la règle est installée
ls -la /etc/udev/rules.d/99-pcan-usb.rules

# 2. Vérifier que le script est installé et exécutable
ls -la /usr/local/bin/setup-pcan-helper.sh

# 3. Tester le script manuellement
sudo /usr/local/bin/setup-pcan-helper.sh

# 4. Voir les événements udev en temps réel
sudo udevadm monitor --environment --udev --property

# Débrancher/rebrancher le PCAN-USB et observer les événements
```

### Erreur "Device or resource busy"

C'est normal si can0 est déjà configuré. Le script essaie de reconfigurer une interface déjà active. Pas de problème.

### Erreur "command not found" ou "No such file or directory"

Le script a probablement des problèmes de format (line endings CRLF au lieu de LF). Solution :

```bash
# Convertir les line endings
sudo sed -i 's/\r$//' /usr/local/bin/setup-pcan-helper.sh

# Vérifier le format
file /usr/local/bin/setup-pcan-helper.sh
# Devrait afficher "UTF-8 text executable" (sans "CRLF")

# S'assurer que le shebang est correct
head -1 /usr/local/bin/setup-pcan-helper.sh
# Devrait afficher : #!/usr/bin/bash
```

### can0 change de nom (can0 → can1)

Cela arrive si tu débranches/rebranches plusieurs fois rapidement. Solutions :
- Redémarre le système
- `sudo rmmod peak_usb && sudo modprobe peak_usb`

## Vérification de l'état de can0

```bash
# Voir l'état de can0
ip link show can0

# Voir les statistiques
ip -s link show can0

# Tester la communication CAN
candump can0

# Envoyer une trame de test
cansend can0 123#DEADBEEF
```

## Désinstallation

Si tu veux désactiver la configuration automatique :

```bash
# Supprimer la règle udev
sudo rm /etc/udev/rules.d/99-pcan-usb.rules

# Supprimer le script (optionnel)
sudo rm /usr/local/bin/setup-pcan-helper.sh

# Recharger udev
sudo udevadm control --reload-rules
```

## Avantages de cette solution

✅ Configuration instantanée dès le branchement USB
✅ Fonctionne même si le périphérique est branché après le boot
✅ Idéal pour robot mobile (déconnexions fréquentes)
✅ Pas besoin d'intervention manuelle
✅ Logs centralisés pour le debug

## Notes importantes

- Le bitrate est fixé à **500 kbps** (500000 bps)
- Le script utilise `/usr/bin/bash` (vérifie avec `which bash`)
- Les logs sont visibles avec `journalctl` ou `dmesg`
- La règle udev se déclenche uniquement au branchement, pas au boot
