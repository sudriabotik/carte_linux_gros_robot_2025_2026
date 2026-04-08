#!/bin/bash
# Script de configuration rapide de l'interface can0 pour PCAN-USB
# Usage: ./setup_can0.sh

echo "=========================================="
echo "Configuration de l'interface can0"
echo "=========================================="

# Vérifier si l'interface can0 existe
if ! ip link show can0 &> /dev/null; then
    echo "❌ Erreur: Interface can0 introuvable"
    echo "   Vérifie que le PCAN-USB est branché"
    exit 1
fi

echo "✅ Interface can0 détectée"

# Configurer le bitrate
echo "⚙️  Configuration du bitrate à 500 kbps..."
sudo ip link set can0 type can bitrate 500000

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la configuration du bitrate"
    exit 1
fi

# Activer l'interface
echo "⚙️  Activation de l'interface..."
sudo ip link set can0 up

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'activation de can0"
    exit 1
fi

# Vérifier le statut
echo ""
echo "=========================================="
echo "✅ Configuration terminée!"
echo "=========================================="
ip link show can0

# Vérifier que l'interface est bien UP
if ip link show can0 | grep -q "UP"; then
    echo ""
    echo "✅ can0 est ACTIF et prêt à l'emploi"
else
    echo ""
    echo "⚠️  can0 n'est pas UP, quelque chose s'est mal passé"
    exit 1
fi
