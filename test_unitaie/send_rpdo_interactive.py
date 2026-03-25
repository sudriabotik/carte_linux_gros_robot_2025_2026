##!/usr/bin/env python3
"""
Script interactif pour envoyer des RPDO au Node 2
Usage: python3 send_rpdo_interactive.py --action-id <id>
"""

import canopen
import argparse
import sys

# Configuration
NODE_ID = 1
#DEVICE_PATH = '/dev/ttyACM0'
DEVICE_PATH = 'com12'
BITRATE = 500000
EDS_FILE = 'DS301_profile.eds'

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Envoi interactif de RPDO au Node 2')
    parser.add_argument('--action-id', type=int, required=True, help='Action ID (UINT16)')
    args = parser.parse_args()

    action_id = args.action_id

    # Validation
    if not (0 <= action_id <= 0xFFFF):
        print(f"Erreur: action_id doit être entre 0 et 65535")
        sys.exit(1)

    print("="*60)
    print(f"ENVOI RPDO INTERACTIF - Node {NODE_ID}")
    print("="*60)
    print(f"Action ID: {action_id}")
    print(f"Saisissez les paramètres (ex: '20' ou '10 20 30')")
    print(f"Tapez 'quit' pour quitter\n")

    # Connexion CANopen
    network = canopen.Network()
    try:
        print(f"Connexion au bus CAN...")
        network.connect(interface='slcan', channel=DEVICE_PATH, bitrate=BITRATE)
        print(f"✓ Connecté\n")

        # Ajouter le noeud
        node = network.add_node(NODE_ID, EDS_FILE)
        node.nmt.state = 'OPERATIONAL'

        # Lire configuration RPDO
        node.rpdo.read()
        print(f"✓ RPDO configurés\n")

        # Compteur command_id
        command_id = 1

        # Boucle interactive
        while True:
            try:
                # Saisie utilisateur
                user_input = input(f"[CMD {command_id}] > ").strip()

                if user_input.lower() == 'quit':
                    print("Arrêt...")
                    break

                if not user_input:
                    continue

                # Parse paramètres
                try:
                    params = [int(x) for x in user_input.split()]
                except ValueError:
                    print("Erreur: saisissez des nombres entiers (ex: 10 20 30)")
                    continue

                # Compléter avec des 0
                param_1 = params[0] if len(params) > 0 else 0
                param_2 = params[1] if len(params) > 1 else 0
                param_3 = params[2] if len(params) > 2 else 0

                # Validation INT16 (signé)
                if not all(-32768 <= p <= 32767 for p in [param_1, param_2, param_3]):
                    print("Erreur: paramètres doivent être entre -32768 et 32767")
                    continue

                # Convertir en UINT16 (complément à deux pour les négatifs)
                def to_uint16(value):
                    if value < 0:
                        return value & 0xFFFF  # Complément à deux
                    return value

                param_1_u16 = to_uint16(param_1)
                param_2_u16 = to_uint16(param_2)
                param_3_u16 = to_uint16(param_3)

                # Préparer RPDO1
                rpdo1_data = bytearray([
                    action_id & 0xFF, (action_id >> 8) & 0xFF,
                    param_1_u16 & 0xFF, (param_1_u16 >> 8) & 0xFF,
                    param_2_u16 & 0xFF, (param_2_u16 >> 8) & 0xFF,
                    param_3_u16 & 0xFF, (param_3_u16 >> 8) & 0xFF
                ])

                # Préparer RPDO2
                rpdo2_data = bytearray([
                    0, 0,  # param_4
                    0, 0,  # param_5
                    0, 0,  # param_6
                    command_id & 0xFF, (command_id >> 8) & 0xFF  # command_id
                ])

                # Envoyer RPDO1
                node.rpdo[1].data = rpdo1_data
                node.rpdo[1].transmit()
                print(f"  → RPDO1 (0x202): action_id={action_id}, p1={param_1}, p2={param_2}, p3={param_3}")

                # Envoyer RPDO2
                node.rpdo[2].data = rpdo2_data
                node.rpdo[2].transmit()
                print(f"  → RPDO2 (0x302): command_id={command_id}")

                # Incrémenter command_id
                command_id += 1

            except KeyboardInterrupt:
                print("\nInterruption...")
                break

    except Exception as e:
        print(f"Erreur: {type(e).__name__}: {e}")
    finally:
        network.disconnect()
        print("✓ Déconnecté")

if __name__ == '__main__':
    main()
