# Configuration TigerVNC Server sur Radxa Rock 5C

## Vue d'ensemble

Ce guide documente la configuration complète d'un serveur VNC sur la Radxa Rock 5C pour accéder au bureau KDE à distance depuis Windows.

**Configuration actuelle :**
- **Serveur VNC** : TigerVNC
- **Desktop Environment** : KDE Plasma
- **Port** : 5901 (display :1)
- **Résolution** : 1920x1200, 24-bit
- **Démarrage automatique** : systemd service
- **Client** : RealVNC Viewer (Windows)
- **Réseau** : LAN local (pas d'accès externe)

---

## Installation rapide

### Étape 1 : Installer TigerVNC

```bash
sudo apt update
sudo apt install tigervnc-standalone-server tigervnc-common
```

### Étape 2 : Configuration initiale du mot de passe VNC

```bash
# Créer le mot de passe VNC (première fois uniquement)
vncpasswd

# Vous serez invité à :
# - Entrer un mot de passe (8 caractères minimum)
# - Confirmer le mot de passe
# - Répondre "n" à la question "view-only password"
```

⚠️ **Note** : Le mot de passe est stocké dans `~/.vnc/passwd`

### Étape 3 : Créer le fichier xstartup

```bash
# Créer le dossier VNC s'il n'existe pas
mkdir -p ~/.vnc

# Copier le fichier xstartup depuis ce repo
cp doc/vnc/xstartup ~/.vnc/xstartup

# Rendre le fichier exécutable
chmod +x ~/.vnc/xstartup
```

**Contenu de `xstartup` (démarre KDE) :**
```bash
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
/etc/X11/xinit/xinitrc
[ -x /etc/vnc/xstartup  ] && exec /etc/vnc/xstartup
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
xsetroot -solid grey
#vncconfig -iconic &
startkde &
```

### Étape 4 : Installer le service systemd

```bash
# Copier le fichier service depuis ce repo
sudo cp doc/vnc/vncserver@.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage (display :1)
sudo systemctl enable vncserver@:1.service

# Démarrer le service maintenant
sudo systemctl start vncserver@:1.service

# Vérifier le statut
sudo systemctl status vncserver@:1.service
```

### Étape 5 : Vérifier que VNC fonctionne

```bash
# Voir les sessions VNC actives
vncserver -list

# Vérifier que le port 5901 écoute
sudo netstat -tulpn | grep 5901

# Voir les processus VNC
ps aux | grep vnc
```

**Résultat attendu :**
```
X DISPLAY #     RFB PORT #      PROCESS ID #    SERVER
1               5901            901             Xtigervnc
```

---

## Connexion depuis Windows

### Méthode 1 : RealVNC Viewer (recommandé)

1. **Télécharger RealVNC Viewer** : https://www.realvnc.com/en/connect/download/viewer/
2. **Installer RealVNC Viewer sur Windows**
3. **Se connecter** :
   - Adresse : `192.168.0.x:5901` (remplacer `x` par l'IP de la Rock 5C)
   - Ou : `192.168.0.x:1` (display :1 = port 5901)
4. **Entrer le mot de passe VNC** configuré précédemment
5. **Le bureau KDE s'affiche** ✅

### Méthode 2 : TigerVNC Viewer

1. **Télécharger TigerVNC Viewer** : https://tigervnc.org/
2. **Installer TigerVNC Viewer sur Windows**
3. **Se connecter** de la même manière

### Trouver l'adresse IP de la Rock 5C

```bash
# Sur la Rock 5C
ip addr show | grep inet

# Ou
hostname -I
```

---

## Configuration avancée

### Changer la résolution

Par défaut : **1920x1200**

```bash
# Arrêter le serveur VNC
vncserver -kill :1

# Redémarrer avec une nouvelle résolution
vncserver :1 -localhost no -geometry 1920x1080 -depth 24

# Ou modifier le service systemd (voir section "Modifier le service")
```

**Résolutions courantes :**
- `1920x1080` (Full HD)
- `1920x1200` (actuel)
- `1280x720` (HD)
- `1024x768` (4:3)

### Autoriser les connexions depuis n'importe quelle IP

⚠️ **ATTENTION : Risque de sécurité !**

Par défaut, VNC écoute sur **toutes les interfaces** (`-localhost no`).

Pour restreindre à localhost uniquement (tunnel SSH requis) :

```bash
vncserver :1 -localhost yes
```

### Supprimer le mot de passe VNC (non recommandé)

⚠️ **DANGER : N'importe qui sur le réseau local peut se connecter !**

```bash
# Arrêter VNC
vncserver -kill :1

# Supprimer le fichier mot de passe
rm ~/.vnc/passwd

# Redémarrer sans authentification
vncserver :1 -localhost no -SecurityTypes None
```

**Modifier le service systemd pour désactiver l'authentification :**

```bash
sudo nano /etc/systemd/system/vncserver@.service
```

Modifier la ligne `ExecStart` :
```ini
ExecStart=/usr/bin/vncserver %i -localhost no -SecurityTypes None
```

---

## Fichiers de configuration

### Fichier service systemd : `/etc/systemd/system/vncserver@.service`

```ini
[Unit]
Description=Start TigerVNC server at startup
After=network.target

[Service]
Type=forking
User=radxa
PAMName=login
PIDFile=/home/radxa/.vnc/%H:%i.pid
ExecStart=/usr/bin/vncserver %i -localhost no
ExecStop=/usr/bin/vncserver -kill %i
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Paramètres importants :**
- `%i` : Numéro du display (`:1` pour le display 1)
- `%H` : Hostname (`rock-5c`)
- `User=radxa` : Utilisateur qui exécute VNC
- `-localhost no` : Accepte les connexions réseau (pas seulement localhost)

### Fichier startup : `~/.vnc/xstartup`

```bash
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
/etc/X11/xinit/xinitrc
[ -x /etc/vnc/xstartup  ] && exec /etc/vnc/xstartup
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
xsetroot -solid grey
#vncconfig -iconic &
startkde &
```

**Alternatives Desktop Environment :**

**XFCE** (plus léger que KDE) :
```bash
#!/bin/sh
startxfce4 &
```

**GNOME** :
```bash
#!/bin/sh
gnome-session &
```

---

## Démarrage et arrêt manuel

### Démarrer VNC manuellement

```bash
vncserver :1 -localhost no
```

Options supplémentaires :
```bash
# Avec résolution personnalisée
vncserver :1 -localhost no -geometry 1920x1080 -depth 24

# Avec nom de session personnalisé
vncserver :1 -localhost no -name "Robot-Rock5C"

# Sans authentification (non recommandé)
vncserver :1 -localhost no -SecurityTypes None
```

### Arrêter VNC manuellement

```bash
# Arrêter le display :1
vncserver -kill :1

# Arrêter tous les displays
vncserver -kill :*
```

### Redémarrer VNC

```bash
vncserver -kill :1 && vncserver :1 -localhost no
```

---

## Gestion du service systemd

### Commandes utiles

```bash
# Démarrer le service
sudo systemctl start vncserver@:1.service

# Arrêter le service
sudo systemctl stop vncserver@:1.service

# Redémarrer le service
sudo systemctl restart vncserver@:1.service

# Voir le statut
sudo systemctl status vncserver@:1.service

# Activer au démarrage
sudo systemctl enable vncserver@:1.service

# Désactiver au démarrage
sudo systemctl disable vncserver@:1.service

# Voir les logs du service
sudo journalctl -u vncserver@:1.service -f
```

### Modifier le service

```bash
# Éditer le fichier
sudo nano /etc/systemd/system/vncserver@.service

# Recharger systemd après modification
sudo systemctl daemon-reload

# Redémarrer le service
sudo systemctl restart vncserver@:1.service
```

---

## Dépannage

### Problème : Le service échoue au démarrage

**Symptôme :**
```bash
sudo systemctl status vncserver@:1.service
# Active: failed (Result: exit-code)
```

**Causes possibles :**

1. **VNC déjà démarré manuellement**
   ```bash
   # Vérifier si VNC tourne déjà
   vncserver -list

   # Tuer le processus manuel
   vncserver -kill :1

   # Redémarrer le service
   sudo systemctl restart vncserver@:1.service
   ```

2. **Fichier PID restant**
   ```bash
   rm ~/.vnc/rock-5c:1.pid
   sudo systemctl restart vncserver@:1.service
   ```

3. **Permissions incorrectes sur xstartup**
   ```bash
   chmod +x ~/.vnc/xstartup
   ```

### Problème : Impossible de se connecter depuis Windows

**Vérifications :**

```bash
# 1. Vérifier que VNC écoute sur le bon port
sudo netstat -tulpn | grep 5901
# Doit afficher : tcp 0.0.0.0:5901 ... LISTEN

# 2. Vérifier que VNC est bien démarré
vncserver -list

# 3. Vérifier l'IP de la Rock 5C
ip addr show | grep inet

# 4. Tester depuis la Rock 5C elle-même
vncviewer localhost:1
```

**Firewall (si activé) :**
```bash
# Ouvrir le port 5901 (si firewall activé)
sudo ufw allow 5901/tcp
```

### Problème : Écran noir ou bureau vide

**Cause** : Le fichier `~/.vnc/xstartup` n'est pas exécutable ou manquant.

**Solution :**
```bash
# Vérifier les permissions
ls -la ~/.vnc/xstartup
# Doit afficher : -rwxr-xr-x

# Rendre exécutable
chmod +x ~/.vnc/xstartup

# Redémarrer VNC
vncserver -kill :1
vncserver :1 -localhost no
```

### Problème : "Too many security failures"

**Cause** : Trop de tentatives de connexion avec un mauvais mot de passe.

**Solution :**
```bash
# Redémarrer le serveur VNC
vncserver -kill :1
vncserver :1 -localhost no

# Ou redéfinir le mot de passe
vncpasswd
```

### Problème : Performance lente

**Solutions :**

1. **Réduire la résolution**
   ```bash
   vncserver -kill :1
   vncserver :1 -localhost no -geometry 1280x720 -depth 24
   ```

2. **Réduire la profondeur de couleur**
   ```bash
   vncserver -kill :1
   vncserver :1 -localhost no -depth 16
   ```

3. **Utiliser un desktop plus léger (XFCE au lieu de KDE)**

---

## Voir les logs

### Logs VNC du serveur

```bash
# Voir le log du display :1
cat ~/.vnc/rock-5c:1.log

# Suivre le log en temps réel
tail -f ~/.vnc/rock-5c:1.log
```

### Logs systemd

```bash
# Logs récents du service
sudo journalctl -u vncserver@:1.service -n 50

# Suivre les logs en temps réel
sudo journalctl -u vncserver@:1.service -f
```

---

## Désinstallation

### Arrêter et désactiver VNC

```bash
# Arrêter le service
sudo systemctl stop vncserver@:1.service

# Désactiver au démarrage
sudo systemctl disable vncserver@:1.service

# Supprimer le service
sudo rm /etc/systemd/system/vncserver@.service
sudo systemctl daemon-reload

# Tuer tous les processus VNC
vncserver -kill :*
```

### Supprimer les fichiers de configuration

```bash
# Supprimer le dossier VNC
rm -rf ~/.vnc

# Désinstaller TigerVNC
sudo apt remove tigervnc-standalone-server tigervnc-common
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DÉMARRAGE SYSTÈME                                           │
│  systemd démarre vncserver@:1.service                           │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. LANCEMENT VNCSERVER                                         │
│  /usr/bin/vncserver :1 -localhost no                            │
│  • Crée le display :1 (port 5901)                               │
│  • Lance Xtigervnc (serveur X11 virtuel)                        │
│  • Résolution : 1920x1200, 24-bit                               │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. EXÉCUTION XSTARTUP                                          │
│  ~/.vnc/xstartup lance startkde &                               │
│  • Démarre KDE Plasma dans le display virtuel                   │
│  • Configure l'environnement X11                                │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. SERVEUR VNC PRÊT                                            │
│  Écoute sur 0.0.0.0:5901 (toutes interfaces)                    │
│  • Attend les connexions clients                                │
│  • Authentification VNC (mot de passe dans ~/.vnc/passwd)       │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. CONNEXION CLIENT (RealVNC Viewer Windows)                   │
│  Connexion depuis 192.168.0.49 → 192.168.0.x:5901               │
│  • Client envoie le mot de passe                                │
│  • Serveur authentifie                                          │
│  • Transmission du bureau KDE via protocole RFB                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Informations techniques

- **Protocole** : RFB (Remote Framebuffer Protocol)
- **Port par défaut** : 5900 + numéro display (5901 pour :1)
- **Authentification** : VncAuth (mot de passe crypté)
- **Encodage** : ZRLE, Hextile, RRE (compression adaptative)
- **Serveur X11** : Xtigervnc (fork de Xvnc optimisé)
- **Format pixel** : 24-bit RGB888 (32bpp) little-endian

---

## Checklist pour nouvelle installation

- [ ] Installer TigerVNC (`apt install tigervnc-standalone-server`)
- [ ] Configurer le mot de passe VNC (`vncpasswd`)
- [ ] Créer `~/.vnc/xstartup` avec le bon desktop (KDE)
- [ ] Rendre `xstartup` exécutable (`chmod +x`)
- [ ] Copier le service systemd vers `/etc/systemd/system/`
- [ ] Recharger systemd (`daemon-reload`)
- [ ] Activer le service (`systemctl enable vncserver@:1`)
- [ ] Démarrer le service (`systemctl start vncserver@:1`)
- [ ] Vérifier que le port 5901 écoute (`netstat -tulpn | grep 5901`)
- [ ] Trouver l'IP de la Rock 5C (`hostname -I`)
- [ ] Installer RealVNC Viewer sur Windows
- [ ] Se connecter : `IP:5901` avec le mot de passe configuré
- [ ] Vérifier que le bureau KDE s'affiche correctement

---

## Références

- **Documentation officielle TigerVNC** : https://tigervnc.org/
- **Documentation Radxa Rock 5** : https://docs.radxa.com/
- **Wiki Arch Linux VNC** : https://wiki.archlinux.org/title/TigerVNC
- **RealVNC Viewer** : https://www.realvnc.com/
