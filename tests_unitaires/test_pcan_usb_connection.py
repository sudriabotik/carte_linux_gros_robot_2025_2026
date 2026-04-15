#!/usr/bin/env python3
"""
Test de connexion au bus CAN avec PCAN-USB

Ce script teste différentes configurations pour se connecter au nouveau
adaptateur PCAN-USB (PEAK-System PCAN-USB).

Détecté comme : can0 (via SocketCAN)

Usage:
    1. Configurer l'interface (commandes Linux ci-dessous)
    2. python test_pcan_usb_connection.py
"""

import can
import time
import subprocess
import sys

print("=" * 70)
print("🔧 TEST DE CONNEXION PCAN-USB")
print("=" * 70)

# ============================================================================
# ÉTAPE 0 : CONFIGURATION PRÉALABLE (À FAIRE DANS LE TERMINAL LINUX)
# ============================================================================

print("\n📋 CONFIGURATION PRÉALABLE REQUISE:")
print("-" * 70)
print("Avant de lancer ce script, exécute ces commandes dans le terminal:")
print()
print("  # 1. Configurer le bitrate à 500 kbps")
print("  sudo ip link set can0 type can bitrate 500000")
print()
print("  # 2. Activer l'interface CAN")
print("  sudo ip link set can0 up")
print()
print("  # 3. Vérifier que l'interface est active")
print("  ip link show can0")
print()
print("Tu devrais voir : can0: <NOARP,UP,LOWER_UP,ECHO>")
print("-" * 70)

input("\nAppuie sur ENTRÉE quand c'est fait...")

# ============================================================================
# ÉTAPE 1 : VÉRIFIER QUE L'INTERFACE can0 EXISTE ET EST ACTIVE
# ============================================================================

print("\n" + "=" * 70)
print("ÉTAPE 1 : Vérification de l'interface can0")
print("=" * 70)

try:
    result = subprocess.run(
        ["ip", "link", "show", "can0"],
        capture_output=True,
        text=True,
        timeout=2
    )

    if result.returncode == 0:
        print("✅ Interface can0 trouvée:")
        print(result.stdout)

        if "UP" in result.stdout:
            print("✅ Interface can0 est ACTIVE")
        else:
            print("❌ Interface can0 existe mais n'est PAS active")
            print("   Exécute: sudo ip link set can0 up")
            sys.exit(1)
    else:
        print("❌ Interface can0 introuvable")
        print("   Vérifie que le PCAN-USB est bien branché")
        sys.exit(1)

except subprocess.TimeoutExpired:
    print("⏱️ Timeout lors de la vérification de can0")
    sys.exit(1)
except FileNotFoundError:
    print("❌ Commande 'ip' introuvable")
    sys.exit(1)

# ============================================================================
# ÉTAPE 2 : TEST DE CONNEXION SOCKETCAN (MÉTHODE RECOMMANDÉE POUR PCAN-USB)
# ============================================================================

print("\n" + "=" * 70)
print("ÉTAPE 2 : Test de connexion SocketCAN")
print("=" * 70)

print("\n🔌 Configuration testée:")
print("  • bustype  : 'socketcan'")
print("  • channel  : 'can0'")
print("  • bitrate  : 500000 (500 kbps)")

try:
    bus = can.interface.Bus(
        interface='socketcan',
        channel='can0',
        bitrate=500000
    )
    print("\n✅ CONNEXION RÉUSSIE avec SocketCAN!")
    print(f"   Bus info: {bus}")

except OSError as e:
    print(f"\n❌ ERREUR de connexion: {e}")
    print("\n🔍 Solutions possibles:")
    print("  1. Vérifie que can0 est UP: ip link show can0")
    print("  2. Active l'interface: sudo ip link set can0 up")
    print("  3. Vérifie les permissions: sudo usermod -a -G dialout $USER")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ ERREUR inattendue: {e}")
    sys.exit(1)

# ============================================================================
# ÉTAPE 3 : TEST D'ENVOI D'UNE TRAME CAN
# ============================================================================

print("\n" + "=" * 70)
print("ÉTAPE 3 : Test d'envoi d'une trame CAN")
print("=" * 70)

try:
    # Créer une trame de test (COB-ID 0x123, 8 octets de données)
    test_message = can.Message(
        arbitration_id=0x123,
        data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
        is_extended_id=False
    )

    print(f"\n📤 Envoi de trame test:")
    print(f"   COB-ID : 0x{test_message.arbitration_id:03X}")
    print(f"   Data   : {' '.join(f'{b:02X}' for b in test_message.data)}")

    bus.send(test_message)
    print("✅ Trame envoyée avec succès!")

except can.CanError as e:
    print(f"❌ Erreur CAN lors de l'envoi: {e}")
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")

# ============================================================================
# ÉTAPE 4 : TEST DE RÉCEPTION (avec timeout)
# ============================================================================

print("\n" + "=" * 70)
print("ÉTAPE 4 : Test de réception de trames CAN")
print("=" * 70)

print("\n🔊 Écoute du bus CAN pendant 3 secondes...")
print("   (Envoie des trames depuis un autre node pour tester)")

received_count = 0
timeout = 3.0
start_time = time.time()

try:
    while (time.time() - start_time) < timeout:
        message = bus.recv(timeout=0.5)

        if message is not None:
            received_count += 1
            print(f"\n📥 Trame reçue #{received_count}:")
            print(f"   COB-ID : 0x{message.arbitration_id:03X}")
            print(f"   Data   : {' '.join(f'{b:02X}' for b in message.data)}")
            print(f"   DLC    : {message.dlc}")

    if received_count > 0:
        print(f"\n✅ {received_count} trame(s) reçue(s)")
    else:
        print("\n⚠️  Aucune trame reçue")
        print("   (Normal si aucun autre node n'est actif sur le bus)")

except KeyboardInterrupt:
    print("\n\n⏸️  Test interrompu par l'utilisateur")
except Exception as e:
    print(f"\n❌ Erreur lors de la réception: {e}")

# ============================================================================
# ÉTAPE 5 : FERMETURE PROPRE
# ============================================================================

print("\n" + "=" * 70)
print("ÉTAPE 5 : Fermeture de la connexion")
print("=" * 70)

try:
    bus.shutdown()
    print("✅ Connexion fermée proprement")
except Exception as e:
    print(f"⚠️  Erreur lors de la fermeture: {e}")

# ============================================================================
# RÉSUMÉ ET COMPARAISON
# ============================================================================

print("\n" + "=" * 70)
print("📊 RÉSUMÉ ET CONFIGURATION POUR TON CODE")
print("=" * 70)

print("""
✅ Configuration à utiliser dans init_interface.py :

    # PCAN-USB (SocketCAN)
    bus = can.interface.Bus(
        bustype='socketcan',
        channel='can0',
        bitrate=500000
    )

❌ Ancienne configuration (CANable avec SLCAN) - NE PLUS UTILISER :

    # CANable (SLCAN) - ANCIEN
    bus = can.interface.Bus(
        bustype='slcan',
        channel='/dev/canable',
        bitrate=500000
    )

📋 Commandes Linux à retenir :

    # Activer can0 au démarrage (ajouter à /etc/rc.local ou systemd)
    sudo ip link set can0 type can bitrate 500000
    sudo ip link set can0 up

    # Vérifier l'état
    ip link show can0

    # Désactiver
    sudo ip link set can0 down

    # Voir les trames en temps réel (outil de debug)
    candump can0

📦 Package requis (normalement déjà installé) :

    sudo apt-get install can-utils

🔍 Troubleshooting :

    - "Network is down" → sudo ip link set can0 up
    - "Permission denied" → sudo usermod -a -G dialout $USER (puis reboot)
    - "No such device" → Vérifie que le PCAN-USB est branché (dmesg | grep peak)
""")

print("=" * 70)
print("✅ TEST TERMINÉ")
print("=" * 70)
