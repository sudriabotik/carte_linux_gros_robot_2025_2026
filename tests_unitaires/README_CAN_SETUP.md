# 📘 Configuration automatique de can0 (PCAN-USB)

Ce dossier contient plusieurs méthodes pour configurer automatiquement l'interface CAN du PCAN-USB après débranchement/rebranchement.

## 🎯 Problème résolu

Quand tu débranches/rebranches le PCAN-USB, l'interface `can0` est recréée mais **pas configurée**. Il faut manuellement :
```bash
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up
```

Les scripts ci-dessous automatisent cette configuration.

---

## 📁 Fichiers disponibles

| Fichier | Type | Usage |
|---------|------|-------|
| `setup_can0.sh` | Script shell | Configuration manuelle rapide |
| `check_and_setup_can0.py` | Script Python | Vérification + config automatique |
| `can0-setup.service` | Service systemd | Config au démarrage du système |
| `99-pcan-usb.rules` | Règle udev | Config automatique au branchement USB |
| `setup-pcan-helper.sh` | Helper udev | Script appelé par udev |

---

## 🚀 Méthode 1 : Script shell manuel (le plus simple)

### Utilisation

```bash
# Rendre le script exécutable (une seule fois)
chmod +x tests_unitaires/setup_can0.sh

# Exécuter quand nécessaire
./tests_unitaires/setup_can0.sh
```

### Avantages
- ✅ Simple et rapide
- ✅ Pas d'installation système nécessaire

### Inconvénients
- ⚠️ À exécuter manuellement après chaque débranchement

---

## 🐍 Méthode 2 : Script Python intégré (recommandé pour ton robot)

### Utilisation standalone

```bash
python tests_unitaires/check_and_setup_can0.py
```

### Utilisation dans ton code

Ajoute au début de `init_interface.py` :

```python
# Importer la fonction
from tests_unitaires.check_and_setup_can0 import ensure_can0_ready

def initialize_interfaces() -> InterfacesContext:
    # ... autres lignes ...

    # Vérifier et configurer can0 automatiquement
    try:
        ensure_can0_ready(bitrate=500000, auto_setup=True)
    except RuntimeError as e:
        logger.log_error("Init", f"Impossible de configurer can0: {e}")
        sys.exit(1)

    # Connexion au bus CAN
    bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate=500000)
    # ... reste du code ...
```

### Avantages
- ✅ Configuration automatique avant chaque lancement
- ✅ Gestion d'erreur intégrée
- ✅ Pas besoin d'intervention manuelle

### Inconvénients
- ⚠️ Nécessite que le script Python ait les droits sudo (voir section Permissions)

---

## ⚙️ Méthode 3 : Service systemd (démarrage automatique)

### Installation

```bash
# Copier le service
sudo cp tests_unitaires/can0-setup.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable can0-setup.service

# Démarrer le service maintenant
sudo systemctl start can0-setup.service

# Vérifier le statut
sudo systemctl status can0-setup.service
```

### Vérification

```bash
ip link show can0
# Devrait afficher : <NOARP,UP,LOWER_UP,ECHO>
```

### Avantages
- ✅ Configuration automatique à chaque démarrage du système
- ✅ Redémarrage automatique en cas d'échec
- ✅ Logs centralisés (`journalctl -u can0-setup`)

### Inconvénients
- ⚠️ Ne se déclenche qu'au boot (pas au branchement USB)
- ⚠️ Nécessite une installation système

---

## 🔌 Méthode 4 : Règle udev (déclenchement automatique au branchement)

### Installation

```bash
# 1. Copier le script helper
sudo cp tests_unitaires/setup-pcan-helper.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/setup-pcan-helper.sh

# 2. Copier la règle udev
sudo cp tests_unitaires/99-pcan-usb.rules /etc/udev/rules.d/

# 3. Recharger les règles udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```
cp setup-pcan-helper.sh  /usr/local/bin/
sudo cp 99-pcan-usb.rules /etc/udev/rules.d/
### Test

```bash
# Débrancher le PCAN-USB
# Rebrancher le PCAN-USB
# Attendre 2 secondes

# Vérifier
ip link show can0
# Devrait afficher : <NOARP,UP,LOWER_UP,ECHO>

# Voir les logs
dmesg | tail -20
# ou
journalctl -f | grep PCAN
```

### Avantages
- ✅ Configuration instantanée dès le branchement USB
- ✅ Fonctionne même si le périphérique est branché après le boot
- ✅ Idéal pour robot mobile (déconnexions fréquentes)

### Inconvénients
- ⚠️ Configuration système un peu plus complexe
- ⚠️ Nécessite les droits root pour installer

---

## 🔑 Gestion des permissions sudo

### Problème

Les scripts Python nécessitent `sudo` pour configurer can0. Sur un robot mobile, tu ne veux pas taper le mot de passe à chaque fois.

### Solution : sudoers sans mot de passe

```bash
# Éditer sudoers
sudo visudo
```

Ajouter à la fin :
```
# Autoriser l'utilisateur radxa à configurer can0 sans mot de passe
radxa ALL=(ALL) NOPASSWD: /sbin/ip link set can0 type can bitrate *
radxa ALL=(ALL) NOPASSWD: /sbin/ip link set can0 up
radxa ALL=(ALL) NOPASSWD: /sbin/ip link set can0 down
```

**⚠️ Attention** : Cette méthode réduit la sécurité. Utilise-la uniquement sur le robot.

---

## 🏆 Recommandation pour robot mobile

**Combinaison Méthode 2 + Méthode 4** :

1. **Règle udev** : Configure automatiquement can0 dès le branchement
2. **Script Python** : Filet de sécurité dans `init_interface.py` au cas où

### Pourquoi ?

- ✅ Double sécurité (udev + Python)
- ✅ Fonctionne même si udev échoue
- ✅ Pas besoin d'intervention manuelle
- ✅ Robuste aux déconnexions/reconnexions

---

## 🧪 Test de robustesse

Pour vérifier que ton système résiste aux débranchements :

```bash
# Terminal 1 : Lancer ton programme
python main.py

# Terminal 2 : Simuler des débranchements
while true; do
    echo "Déconnexion can0..."
    sudo ip link set can0 down
    sleep 2
    echo "Reconnexion can0..."
    sudo ip link set can0 type can bitrate 500000
    sudo ip link set can0 up
    sleep 5
done
```

Ton programme devrait continuer à fonctionner.

---

## 📊 Comparaison des méthodes

| Méthode | Automatique | Au boot | Au branchement | Complexité |
|---------|-------------|---------|----------------|------------|
| Script shell | ❌ | ❌ | ❌ | ⭐ |
| Python | ✅ | ❌ | ❌ | ⭐⭐ |
| Systemd | ✅ | ✅ | ❌ | ⭐⭐⭐ |
| Udev | ✅ | ❌ | ✅ | ⭐⭐⭐⭐ |

---

## ❓ FAQ

### Q: Pourquoi can0 change de numéro (can0 → can1) ?

**R:** Cela arrive si tu débranches/rebranches plusieurs fois rapidement. Le kernel Linux incrémente le numéro. Solutions :
- Redémarre le système
- Utilise `sudo rmmod peak_usb && sudo modprobe peak_usb` pour recharger le driver

### Q: Quelle différence avec l'ancien CANable ?

**R:**
- **CANable (SLCAN)** : Interface serial `/dev/ttyACMX` qui change → Besoin de règle udev
- **PCAN-USB (SocketCAN)** : Interface réseau `can0` qui reste fixe → Pas besoin de règle udev pour le nom

### Q: Comment voir si can0 est bien configuré ?

**R:**
```bash
ip link show can0
# Tu dois voir : <NOARP,UP,LOWER_UP,ECHO> state UP
```

### Q: Comment débugger les problèmes CAN ?

**R:**
```bash
# Voir les trames en temps réel
candump can0

# Voir les erreurs
dmesg | grep -i can

# Statistiques
ip -s link show can0
```

---

## 📞 Support

Si tu rencontres des problèmes :
1. Vérifie que le PCAN-USB est branché : `lsusb | grep PEAK`
2. Vérifie le driver : `dmesg | grep peak_usb`
3. Teste la connexion : `python tests_unitaires/test_pcan_usb_connection.py`
