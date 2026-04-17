"""
Contains many constants shared between the different nodes of the canopen network, necessary to request actions ect
"""
#couleur equipe 
BLEU = 0
JAUNE = 1

# presence tirette 
PRESENCE_TIRETTE = 0
ABSENCE_TIRETTE = 1 

#STATUS CAN
CMD_STATUS_IDLE = 0      # Prêt à recevoir une nouvelle commande 
CMD_STATUS_RUNNING = 1   # Commande en cours d'exécution 
CMD_STATUS_COMPLETED = 2 # Commande terminée avec succès 
CMD_STATUS_ERROR = 3     # Erreur pendant l'exécution 
CMD_STATUS_ABORTED = 4    # Commande annulée (arrêt d'urgence) 

#CODE ERREUR CAN
CMD_ERROR_NONE = 0               # Aucune erreur 
CMD_ERROR_INVALID_COMMAND = 1    # ACTION_ID inconnu 
CMD_ERROR_INVALID_PARAMS = 2     # Paramètres invalides 
CMD_ERROR_TIMEOUT = 3            # Timeout lors de l'exécution 
CMD_ERROR_MECHANICAL = 4         # Erreur mécanique (blocage, fin de course) 
CMD_ERROR_EMERGENCY_STOP = 99     # Arrêt d'urgence déclenché 
CMD_ERROR_OBSTACLE = 100          # 100 + le numero du capteur 
CMD_ERROR_OBSTACLE_INCONNU = 110  # Obstacle inconnu
CMD_ERROR_OBTACLE_DISPARUE = 150  # 150 + le numero du capteur
MV_EXIT_OK = 200
MV_EXIT_AVOID = 201
MV_EXIT_BLOCKED = 202

