"""
Contains many constants shared between the different nodes of the canopen network, necessary to request actions ect
"""

CMD_STATUS_IDLE = 0,      # Prêt à recevoir une nouvelle commande 
CMD_STATUS_RUNNING = 1,   # Commande en cours d'exécution 
CMD_STATUS_COMPLETED = 2, # Commande terminée avec succès 
CMD_STATUS_ERROR = 3,     # Erreur pendant l'exécution 
CMD_STATUS_ABORTED = 4    # Commande annulée (arrêt d'urgence) 

CMD_ERROR_NONE = 0,               # Aucune erreur 
CMD_ERROR_INVALID_COMMAND = 1,    # ACTION_ID inconnu 
CMD_ERROR_INVALID_PARAMS = 2,     # Paramètres invalides 
CMD_ERROR_TIMEOUT = 3,            # Timeout lors de l'exécution 
CMD_ERROR_MECHANICAL = 4,         # Erreur mécanique (blocage, fin de course) 
CMD_ERROR_EMERGENCY_STOP = 99     # Arrêt d'urgence déclenché 