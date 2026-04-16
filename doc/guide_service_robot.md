# Guide du Service Systemd Robot

Ce document explique comment installer, configurer et utiliser le service systemd qui lance automatiquement le programme du robot au démarrage de la Rock 5C.

---

## 📋 Table des matières

- [Installation](#installation)
- [Commandes de gestion](#commandes-de-gestion)
- [Consultation des logs](#consultation-des-logs)
- [Dépannage](#dépannage)
- [Désinstallation](#désinstallation)

---

## 🔧 Installation

### Étape 1 : Copier le fichier service

```bash
# Copier le fichier service dans le répertoire systemd
sudo cp /home/radxa/Repositories/carte_linux_gros_robot_2025_2026/doc/robot.service /etc/systemd/system/

# Vérifier que le fichier est bien copié
ls -l /etc/systemd/system/robot.service
```

### Étape 2 : Recharger systemd

```bash
# Recharger la configuration systemd pour prendre en compte le nouveau service
sudo systemctl daemon-reload
```

### Étape 3 : Activer le service au démarrage

```bash
# Activer le démarrage automatique au boot
sudo systemctl enable robot.service

# Vérifier que le service est activé
systemctl is-enabled robot
# Devrait afficher : enabled
```

### Étape 4 : Démarrer le service immédiatement

```bash
# Démarrer le service maintenant (sans redémarrer la machine)
sudo systemctl start robot.service

# Vérifier que le service tourne
sudo systemctl status robot.service
```

---

## 🎮 Commandes de gestion

### Démarrer le service

```bash
sudo systemctl start robot
```

### Arrêter le service

```bash
sudo systemctl stop robot
```

**Note** : Avec la configuration `Restart=on-failure`, le service **ne redémarre PAS** automatiquement après un arrêt manuel.

### Redémarrer le service

```bash
sudo systemctl restart robot
```

### Voir le statut du service

```bash
sudo systemctl status robot
```

**Codes de sortie** :
- `active (running)` : Le service tourne normalement
- `inactive (dead)` : Le service est arrêté
- `failed` : Le service a crashé
- `activating` : Le service est en cours de démarrage

### Activer le démarrage automatique au boot

```bash
sudo systemctl enable robot
```

### Désactiver le démarrage automatique

```bash
sudo systemctl disable robot
```

### Désactiver ET arrêter immédiatement

```bash
sudo systemctl disable --now robot
```

---

## 📊 Consultation des logs

Le service redirige les sorties `stdout` et `stderr` du programme Python vers **journalctl** (logs systemd).

**Emplacement** : Les logs systemd sont stockés dans `/var/log/journal/` (gérés par systemd).

### Voir les logs en temps réel

```bash
sudo journalctl -u robot -f
```

Appuyer sur `Ctrl+C` pour quitter.

### Voir les 50 dernières lignes

```bash
sudo journalctl -u robot -n 50
```

### Voir les 100 dernières lignes

```bash
sudo journalctl -u robot -n 100
```

### Voir les logs depuis le dernier boot

```bash
sudo journalctl -u robot -b
```

### Voir les logs d'une période spécifique

```bash
# Aujourd'hui
sudo journalctl -u robot --since today

# Dernière heure
sudo journalctl -u robot --since "1 hour ago"

# Entre deux dates
sudo journalctl -u robot --since "2026-04-12 10:00:00" --until "2026-04-12 11:00:00"
```

### Exporter les logs dans un fichier

```bash
sudo journalctl -u robot > ~/robot_logs_$(date +%Y%m%d_%H%M%S).txt
```

### Voir seulement les erreurs

```bash
sudo journalctl -u robot -p err
```

---

## 🛠️ Dépannage

### Le service ne démarre pas

```bash
# Voir le statut détaillé
sudo systemctl status robot

# Voir les erreurs dans les logs
sudo journalctl -u robot -n 100 --no-pager
```

**Problèmes courants** :

1. **Erreur : `can0 interface not available`**
   - Le PCAN-USB n'est pas branché
   - La règle udev pour can0 ne fonctionne pas
   - Vérifier : `ip link show can0`

2. **Erreur : `Permission denied`**
   - L'utilisateur `radxa` n'a pas accès au bus CAN
   - Solution : `sudo usermod -a -G dialout radxa` puis se déconnecter/reconnecter

3. **Erreur : `ModuleNotFoundError`**
   - L'environnement virtuel n'est pas correctement installé
   - Vérifier : `/home/radxa/Documents/virtual_env/canopen-env/bin/python3 --version`

4. **Erreur : `No such file or directory`**
   - Le chemin vers main.py ou Python est incorrect
   - Vérifier : `ls -l /home/radxa/Repositories/carte_linux_gros_robot_2025_2026/main.py`
   - Vérifier : `ls -l /home/radxa/Documents/virtual_env/canopen-env/bin/python3`

### Le service démarre mais crashe immédiatement

```bash
# Voir les logs détaillés
sudo journalctl -u robot -n 200

# Tester le programme manuellement
cd /home/radxa/Repositories/carte_linux_gros_robot_2025_2026
/home/radxa/Documents/virtual_env/canopen-env/bin/python3 main.py
```

### Le service redémarre en boucle

```bash
# Arrêter le service
sudo systemctl stop robot

# Désactiver le démarrage automatique
sudo systemctl disable robot

# Corriger le problème, puis réactiver
sudo systemctl enable robot
sudo systemctl start robot
```

---

## 🗑️ Désinstallation

### Désactiver et arrêter le service

```bash
sudo systemctl disable --now robot
```

### Supprimer le fichier service

```bash
sudo rm /etc/systemd/system/robot.service
```

### Recharger systemd

```bash
sudo systemctl daemon-reload
```

---

## 📌 Configuration du service

### Fichier : `/etc/systemd/system/robot.service`

**Éléments importants** :

| Directive | Valeur | Description |
|-----------|--------|-------------|
| `WorkingDirectory` | `/home/radxa/Repositories/carte_linux_gros_robot_2025_2026` | Répertoire de travail (pour chemins relatifs) |
| `ExecStart` | `/home/radxa/Documents/virtual_env/canopen-env/bin/python3 main.py` | Commande de démarrage |
| `Restart` | `on-failure` | Redémarre seulement en cas d'erreur/crash |
| `RestartSec` | `5s` | Attend 5 secondes avant de redémarrer |
| `User` | `radxa` | Utilisateur qui exécute le service |
| `StandardOutput` | `journal` | Redirige stdout vers journalctl |
| `StandardError` | `journal` | Redirige stderr vers journalctl |
| `SyslogIdentifier` | `robot` | Nom du service dans les logs |

---

## ⚙️ Variables d'environnement

Le service définit automatiquement :

- `PYTHONUNBUFFERED=1` : Désactive le buffering Python (logs en temps réel)
- `PYTHONPATH=/home/radxa/Repositories/carte_linux_gros_robot_2025_2026` : Chemin des imports Python

---

## 🔄 Workflow typique

### Développement

```bash
# Pendant le dev, arrêter le service pour éviter les conflits
sudo systemctl stop robot

# Lancer le programme manuellement
cd /home/radxa/Repositories/carte_linux_gros_robot_2025_2026
/home/radxa/Documents/virtual_env/canopen-env/bin/python3 main.py

# Quand terminé, redémarrer le service
sudo systemctl start robot
```

### Match / Production

```bash
# S'assurer que le service est activé
sudo systemctl enable robot

# Redémarrer la Rock 5C
sudo reboot

# Le service démarre automatiquement au boot
# Vérifier :
sudo systemctl status robot
```

---

## 📞 Commandes rapides (aide-mémoire)

```bash
# Démarrer
sudo systemctl start robot

# Arrêter
sudo systemctl stop robot

# Redémarrer
sudo systemctl restart robot

# Statut
sudo systemctl status robot

# Logs temps réel
sudo journalctl -u robot -f

# Logs dernières 50 lignes
sudo journalctl -u robot -n 50

# Logs dernières 100 lignes
sudo journalctl -u robot -n 100

# Activer démarrage auto
sudo systemctl enable robot

# Désactiver démarrage auto
sudo systemctl disable robot

# Exporter les logs
sudo journalctl -u robot > ~/robot_logs.txt
```

---

## 📝 Notes importantes

- ✅ Le service **ne redémarre PAS** après `systemctl stop` (configuration `Restart=on-failure`)
- ✅ Le service **redémarre automatiquement** en cas de crash
- ✅ Python attend jusqu'à 10 secondes que `can0` soit UP (fonction `wait_for_can0()`)
- ⚠️ Si le PCAN-USB n'est pas branché au boot, le service échoue après 10s

---

## 🔗 Ressources supplémentaires

- Documentation udev (can0) : `doc/README_PCAN_UDEV.md`
- Documentation CANopen : `doc/action_comm.md`
- Code source du service : `doc/robot.service`

---

**Dernière mise à jour** : 2026-04-16
