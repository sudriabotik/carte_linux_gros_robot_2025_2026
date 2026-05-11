"""
AutoWaitWrapper - Wrapper transparent pour attente automatique avant envoi de commandes

Ce module fournit une classe wrapper qui ajoute automatiquement une attente
avant chaque envoi de commande action_* vers les nodes CAN (asserv, autom).

Utilisation:
    wrapped_node = AutoWaitWrapper(node_asserv, wait_asserv_function)
    wrapped_node.action_goto_xy(100, 200)  # Attend automatiquement avant d'envoyer
"""


class AutoWaitWrapper:
    """
    Wrapper transparent qui ajoute une attente automatique avant chaque commande action_*.

    Ce wrapper permet d'éliminer les appels manuels wait_asserv() ou wait_autom()
    avant chaque envoi de commande dans le code stratégie. L'attente est gérée
    automatiquement et de manière transparente.

    Exemple:
        # Sans wrapper (ancien code):
        wait_asserv()
        node_asserv.action_goto_xy(100, 200)
        wait_asserv()

        # Avec wrapper (nouveau code):
        wrapped_asserv = AutoWaitWrapper(node_asserv, wait_asserv)
        wrapped_asserv.action_goto_xy(100, 200)  # Wait automatique !
    """

    def __init__(self, wrapped_node, wait_function):
        """
        Initialise le wrapper avec un node CAN et sa fonction d'attente associée.

        Args:
            wrapped_node: Le node CAN à envelopper (CanAsservNode ou CanAutomNode)
            wait_function: La fonction wait à appeler avant chaque action
                          (ex: wait_asserv ou wait_autom de FunctStrat)
        """
        self._wrapped_node = wrapped_node
        self._wait_function = wait_function
        self._auto_wait_enabled = True  # Permet de désactiver si besoin

    def __getattr__(self, name):
        """
        Intercepte tous les accès aux attributs/méthodes du node enveloppé.

        Si c'est une méthode action_* ET que l'auto-wait est activé,
        on attend automatiquement avant d'appeler la méthode.

        Pour tous les autres attributs/méthodes (is_busy, node_id, etc.),
        on délègue directement au node enveloppé sans attente.

        Args:
            name: Nom de l'attribut/méthode demandé

        Returns:
            L'attribut/méthode du node enveloppé, potentiellement wrappé
            avec une attente automatique si c'est une action_*
        """
        # Récupère l'attribut/méthode du node enveloppé
        attr = getattr(self._wrapped_node, name)

        # Si c'est une méthode action_* ET que l'auto-wait est activé
        if callable(attr) and name.startswith('action_') and self._auto_wait_enabled:
            def wrapped_method(*args, **kwargs):
                # ATTENTE AUTOMATIQUE AVANT ENVOI DE COMMANDE
                self._wait_function()
                # Appel de la vraie méthode du node CAN
                return attr(*args, **kwargs)
            return wrapped_method

        # Pour tout le reste (is_busy, propriétés, constantes, etc.),
        # on retourne l'attribut tel quel sans wrapper
        return attr

    def disable_auto_wait(self):
        """
        Désactive temporairement l'attente automatique.

        Utile dans des cas très spécifiques où on veut envoyer plusieurs
        commandes rapidement sans attendre entre chaque.
        """
        self._auto_wait_enabled = False

    def enable_auto_wait(self):
        """
        Réactive l'attente automatique (activée par défaut).
        """
        self._auto_wait_enabled = True

    @property
    def raw_node(self):
        """
        Accès au node CAN brut sans wrapper.

        Permet d'accéder au node original pour des cas très spéciaux
        où on veut complètement bypasser le mécanisme d'auto-wait.

        Returns:
            Le node CAN original (CanAsservNode ou CanAutomNode)
        """
        return self._wrapped_node
