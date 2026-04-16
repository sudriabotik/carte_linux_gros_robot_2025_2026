# Configuration des Permissions GPIO sur Rock 5C

Ce document explique comment configurer les permissions GPIO pour permettre à l'utilisateur `radxa` de lire les GPIO sans `sudo`.

---

## 🔍 Problème

Par défaut, les outils `gpioget` et `gpiofind` nécessitent des privilèges root pour accéder aux GPIO. Le programme Python plante avec l'erreur :

```
RuntimeError: Impossible de lire PIN_15
```

**Test de diagnostic** :
```bash
# Sans sudo (échoue)
python3 -c "from core.interface.gpio.gpio import read_gpio_tirette; print(read_gpio_tirette())"

# Avec sudo (fonctionne)
sudo python3 -c "from core.interface.gpio.gpio import read_gpio_tirette; print(read_gpio_tirette())"
```

---

## ✅ Solution : Règle udev + Groupe gpio

### Étape 1 : Créer la règle udev

```bash
# Créer le fichier de règle udev
sudo nano /etc/udev/rules.d/99-gpio-permissions.rules
```

**Contenu du fichier** :
```
# Règle udev pour donner les permissions GPIO au groupe gpio
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0660"
KERNEL=="gpiochip*", GROUP="gpio", MODE="0660"
```

### Étape 2 : Créer le groupe gpio (si nécessaire)

```bash
# Vérifier si le groupe existe
getent group gpio

# Si le groupe n'existe pas, le créer
sudo groupadd gpio
```

### Étape 3 : Ajouter l'utilisateur radxa au groupe gpio

```bash
# Ajouter radxa au groupe gpio
sudo usermod -a -G gpio radxa

# Vérifier que l'utilisateur est bien dans le groupe
groups radxa
# Devrait afficher : radxa adm dialout cdrom sudo audio video plugdev gpio ...
```

### Étape 4 : Recharger les règles udev

```bash
# Recharger les règles udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Étape 5 : Se déconnecter/reconnecter OU redémarrer

**IMPORTANT** : Les changements de groupe ne sont effectifs qu'après déconnexion/reconnexion.

**Option 1** : Se déconnecter puis se reconnecter en SSH
```bash
exit
# Puis se reconnecter via SSH
```

**Option 2** : Redémarrer la Rock 5C
```bash
sudo reboot
```

---

## 🧪 Vérification

Après reconnexion/redémarrage :

```bash
# Vérifier les groupes
groups
# Devrait afficher "gpio" dans la liste

# Vérifier les permissions des GPIO
ls -l /dev/gpiochip*
# Devrait afficher : crw-rw---- 1 root gpio ...

# Tester la lecture GPIO sans sudo
python3 -c "from core.interface.gpio.gpio import read_gpio_tirette; print(read_gpio_tirette())"
# Devrait retourner 0 ou 1 sans erreur
```

---

## 📝 GPIO utilisés

| Pin Name | Fonction | Valeur |
|----------|----------|--------|
| `PIN_15` | Tirette | 0 = insérée, 1 = absente |
| `PIN_27` | Couleur équipe | 0 = Bleu, 1 = Jaune |

---

## 🐛 Dépannage

### Erreur persiste après reconnexion

1. **Vérifier que le groupe gpio existe** :
   ```bash
   getent group gpio
   ```

2. **Vérifier que radxa est dans le groupe** :
   ```bash
   groups radxa | grep gpio
   ```

3. **Vérifier que les règles udev sont chargées** :
   ```bash
   udevadm info /dev/gpiochip4 | grep gpio
   ```

4. **Vérifier les permissions des device** :
   ```bash
   ls -l /dev/gpiochip*
   # Devrait afficher : crw-rw---- 1 root gpio
   ```

### Solution temporaire (NON RECOMMANDÉE pour production)

Si vous avez besoin de tester rapidement avant de configurer les permissions :

```bash
# Lancer le programme avec sudo (TEMPORAIRE)
sudo python3 main.py
```

---

## 🔗 Fichiers concernés

- Code GPIO : `core/interface/gpio/gpio.py`
- Règle udev : `/etc/udev/rules.d/99-gpio-permissions.rules`

---

**Dernière mise à jour** : 2026-04-16
