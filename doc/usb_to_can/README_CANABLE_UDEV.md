# Configuration udev pour CANable2 - Nom stable du périphérique USB-CAN

## Problème

Le convertisseur USB-CAN (CANable2) change de nom après chaque déconnexion :
- **Avant** : `/dev/ttyACM0`
- **Après reconnexion** : `/dev/ttyACM1`, `/dev/ttyACM2`, etc.

Cela casse le programme Python qui utilise un nom fixe `/dev/ttyACM0`.

## Solution

Créer une règle udev qui assigne toujours le même nom au CANable2, par exemple : `/dev/canable`

---

## Installation rapide

### Étape 1 : Identifier le périphérique USB

#### 1. Brancher le CANable2

#### 2. Trouver les informations du périphérique

```bash
lsusb
```

Vous devriez voir quelque chose comme :
```
Bus 007 Device 003: ID 16d0:117e MCS CANable2 b158aa7
```

#### 3. Obtenir le numéro de série unique

```bash
udevadm info -a -n /dev/ttyACM0 | grep -E 'ATTRS{idVendor}|ATTRS{idProduct}|ATTRS{serial}'
```

**Résultat attendu :**
```
ATTRS{idVendor}=="16d0"
ATTRS{idProduct}=="117e"
ATTRS{serial}=="209E32884845"
```

⚠️ **Important** : Le numéro de série (`serial`) est unique à votre CANable2. Notez-le !

---

### Étape 2 : Créer la règle udev

#### 1. Créer le fichier de règle udev

```bash
sudo nano /etc/udev/rules.d/99-canable.rules
```

#### 2. Copier cette ligne dans le fichier

⚠️ **Adaptez le `serial` avec le vôtre !**

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="209E32884845", SYMLINK+="canable", MODE="0666"
```

**Explication des paramètres :**

| Paramètre | Description |
|-----------|-------------|
| `SUBSYSTEM=="tty"` | C'est un périphérique série |
| `ATTRS{idVendor}=="16d0"` | Vendor ID du CANable2 |
| `ATTRS{idProduct}=="117e"` | Product ID du CANable2 |
| `ATTRS{serial}=="..."` | **Numéro de série unique (à remplacer !)** |
| `SYMLINK+="canable"` | Crée un lien symbolique `/dev/canable` |
| `MODE="0666"` | Permissions lecture/écriture pour tous |

#### 3. Sauvegarder le fichier

Dans nano :
- `Ctrl+O` → Écrire le fichier
- `Entrée` → Confirmer
- `Ctrl+X` → Quitter

---

### Étape 3 : Recharger les règles udev

#### 1. Recharger les règles

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 2. Débrancher et rebrancher le CANable2

#### 3. Vérifier que le lien a été créé

```bash
ls -l /dev/canable
```

**Résultat attendu :**
```
lrwxrwxrwx 1 root root 7 Apr 21 17:50 /dev/canable -> ttyACM0
```

✅ Cela signifie que `/dev/canable` pointe vers `/dev/ttyACM0` (ou `ttyACM1`, etc.)

---

### Étape 4 : Tester la règle

#### 1. Test de reconnexion

```bash
# Débrancher le CANable2
# Rebrancher le CANable2
# Vérifier que /dev/canable existe toujours
ls -l /dev/canable
```

✅ Même si le vrai nom devient `/dev/ttyACM1`, `/dev/canable` pointera toujours vers le bon périphérique !

---

### Étape 5 : Modifier le code Python

Dans votre fichier Python (par exemple `main.py`), modifier la ligne de création du bus CAN :

**AVANT :**
```python
bus = can.interface.Bus(bustype='slcan', channel='/dev/ttyACM0', bitrate=500000)
```

**APRÈS :**
```python
bus = can.interface.Bus(bustype='slcan', channel='/dev/canable', bitrate=500000)
```

Maintenant, même si le CANable2 se reconnecte et devient `/dev/ttyACM1`, votre programme continuera de fonctionner car `/dev/canable` pointera automatiquement vers le bon périphérique !

---

## Dépannage

### Problème : `/dev/canable` n'est pas créé

**Solution :**

```bash
# 1. Vérifier que la règle est bien présente
cat /etc/udev/rules.d/99-canable.rules

# 2. Vérifier les logs udev
sudo udevadm test /sys/class/tty/ttyACM0

# 3. Vérifier le numéro de série de VOTRE CANable2
udevadm info -a -n /dev/ttyACM0 | grep serial

# Si le serial est différent, modifiez la règle avec le bon serial !
```

### Problème : Permission denied

**Solution :**

```bash
# 1. Vérifier les permissions
ls -l /dev/canable

# 2. Ajouter votre utilisateur au groupe dialout
sudo usermod -a -G dialout $USER

# 3. Se déconnecter/reconnecter pour appliquer les changements
```

### Problème : Le lien pointe vers le mauvais périphérique

**Cause :** Plusieurs CANable2 branchés en même temps avec la même configuration.

**Solution :** Utiliser le numéro de série (`serial`) pour différencier les périphériques.

---

## Résumé des commandes

```bash
# 1. Identifier le périphérique
lsusb
udevadm info -a -n /dev/ttyACM0 | grep -E 'ATTRS{idVendor}|ATTRS{idProduct}|ATTRS{serial}'

# 2. Créer la règle
sudo nano /etc/udev/rules.d/99-canable.rules
# Copier : SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="209E32884845", SYMLINK+="canable", MODE="0666"

# 3. Recharger
sudo udevadm control --reload-rules
sudo udevadm trigger

# 4. Tester
ls -l /dev/canable

# 5. Modifier le code Python
# Remplacer '/dev/ttyACM0' par '/dev/canable'
```

---

## Avantages de cette solution

✅ **Nom stable** : `/dev/canable` reste identique après chaque reconnexion
✅ **Pas de changement de code** : Une fois configuré, le programme Python fonctionne sans modification
✅ **Permissions gérées** : `MODE="0666"` permet l'accès sans `sudo`
✅ **Spécifique au périphérique** : Utilise le numéro de série pour identifier le bon CANable2

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  CANable2 branché sur USB                                       │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Kernel détecte le périphérique                                 │
│  Crée /dev/ttyACM0 (ou ttyACM1, ttyACM2, etc.)                  │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  udev applique la règle 99-canable.rules                        │
│  Vérifie : VendorID, ProductID, Serial                          │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  udev crée le lien symbolique /dev/canable → /dev/ttyACMx       │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Programme Python utilise /dev/canable                          │
│  Fonctionne quel que soit le numéro ACMx                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Informations CANable2

- **Vendor ID** : `16d0` (MCS)
- **Product ID** : `117e` (CANable2)
- **Protocole** : SLCAN (Serial Line CAN)
- **Bitrate typique** : 500000 bps
- **Interface** : `/dev/ttyACMx` (ACM = Abstract Control Model)

---

## Checklist pour nouvelle installation

- [ ] Brancher le CANable2
- [ ] Identifier VendorID, ProductID, Serial avec `lsusb` et `udevadm`
- [ ] Créer `/etc/udev/rules.d/99-canable.rules` avec le bon serial
- [ ] Recharger udev avec `udevadm control --reload-rules`
- [ ] Débrancher/rebrancher le CANable2
- [ ] Vérifier que `/dev/canable` existe avec `ls -l /dev/canable`
- [ ] Modifier le code Python pour utiliser `/dev/canable`
- [ ] Tester la reconnexion plusieurs fois

---

## Désinstallation

Pour supprimer la règle udev :

```bash
# Supprimer la règle
sudo rm /etc/udev/rules.d/99-canable.rules

# Recharger udev
sudo udevadm control --reload-rules

# Le lien /dev/canable ne sera plus créé
```
