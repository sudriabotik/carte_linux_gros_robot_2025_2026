#!/usr/bin/env python3
"""
Script de vérification et configuration automatique de can0

Ce script peut être:
1. Exécuté directement: python check_and_setup_can0.py
2. Importé dans init_interface.py pour vérification automatique
3. Utilisé comme module réutilisable

Usage direct:
    python check_and_setup_can0.py

Usage dans ton code:
    from tests_unitaires.check_and_setup_can0 import ensure_can0_ready
    ensure_can0_ready()
"""

import subprocess
import sys
import time


def check_can0_exists() -> bool:
    """
    Vérifie si l'interface can0 existe

    Returns:
        True si can0 existe, False sinon
    """
    try:
        result = subprocess.run(
            ["ip", "link", "show", "can0"],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_can0_up() -> bool:
    """
    Vérifie si can0 est UP

    Returns:
        True si can0 est UP, False sinon
    """
    try:
        result = subprocess.run(
            ["ip", "link", "show", "can0"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return "UP" in result.stdout and "LOWER_UP" in result.stdout
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def setup_can0(bitrate: int = 500000) -> bool:
    """
    Configure can0 avec le bitrate spécifié et l'active

    Args:
        bitrate: Bitrate en bps (défaut: 500000 = 500 kbps)

    Returns:
        True si la configuration a réussi, False sinon
    """
    try:
        # Étape 1: Configurer le bitrate
        result = subprocess.run(
            ["sudo", "ip", "link", "set", "can0", "type", "can", "bitrate", str(bitrate)],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            print(f"❌ Erreur lors de la configuration du bitrate: {result.stderr}")
            return False

        # Étape 2: Activer l'interface
        result = subprocess.run(
            ["sudo", "ip", "link", "set", "can0", "up"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            print(f"❌ Erreur lors de l'activation de can0: {result.stderr}")
            return False

        # Attendre un peu que l'interface soit vraiment prête
        time.sleep(0.5)

        return True

    except subprocess.TimeoutExpired:
        print("⏱️ Timeout lors de la configuration de can0")
        return False
    except FileNotFoundError:
        print("❌ Commande 'ip' introuvable")
        return False


def ensure_can0_ready(bitrate: int = 500000, auto_setup: bool = True) -> bool:
    """
    Vérifie que can0 est prêt, et le configure si nécessaire

    Args:
        bitrate: Bitrate en bps (défaut: 500000)
        auto_setup: Si True, configure automatiquement can0 s'il n'est pas UP

    Returns:
        True si can0 est prêt, False sinon

    Raises:
        RuntimeError: Si can0 n'existe pas ou ne peut pas être configuré
    """
    # Vérifier que can0 existe
    if not check_can0_exists():
        raise RuntimeError(
            "Interface can0 introuvable!\n"
            "Vérifie que le PCAN-USB est branché.\n"
            "Commande de vérification: ip link show can0"
        )

    # Vérifier que can0 est UP
    if check_can0_up():
        print("✅ Interface can0 déjà configurée et active")
        return True

    # can0 existe mais n'est pas UP
    if not auto_setup:
        raise RuntimeError(
            "Interface can0 existe mais n'est pas active!\n"
            "Configure-la manuellement avec:\n"
            "  sudo ip link set can0 type can bitrate 500000\n"
            "  sudo ip link set can0 up"
        )

    # Tenter de configurer automatiquement
    print("⚙️  Configuration automatique de can0...")
    if setup_can0(bitrate):
        if check_can0_up():
            print(f"✅ can0 configuré et activé ({bitrate} bps)")
            return True
        else:
            raise RuntimeError("can0 configuré mais toujours pas UP!")
    else:
        raise RuntimeError("Impossible de configurer can0 automatiquement")


def main():
    """
    Fonction principale pour exécution en standalone
    """
    print("=" * 60)
    print("🔧 VÉRIFICATION ET CONFIGURATION DE can0")
    print("=" * 60)

    try:
        ensure_can0_ready(bitrate=500000, auto_setup=True)

        # Afficher le statut final
        print("\n" + "=" * 60)
        print("📊 STATUT FINAL")
        print("=" * 60)
        result = subprocess.run(["ip", "link", "show", "can0"], capture_output=True, text=True)
        print(result.stdout)

        print("=" * 60)
        print("✅ can0 est prêt à l'emploi!")
        print("=" * 60)
        return 0

    except RuntimeError as e:
        print(f"\n❌ ERREUR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
