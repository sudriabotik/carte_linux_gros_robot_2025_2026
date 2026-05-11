"""
Gestionnaire de tâches d'arrière-plan pour autom/asserv

Ce module permet de lancer des séquences d'actions en arrière-plan (non-bloquant)
et de continuer à exécuter d'autres actions, puis d'attendre leur complétion.

Utilisation:
    # Dans la stratégie
    parallel = ParallelExecutor(autom, asserv)

    # Lancer autom en arrière-plan
    parallel.parallel_autom(
        lambda: autom.action_grab(),
        lambda: autom.action_deposit()
    )

    # Continuer avec asserv (pendant que autom s'exécute)
    asserv.action_goto_xy(100, 200, Face.FACE_AVANT)

    # Attendre que autom finisse
    parallel.wait_parallel_autom()
"""

import time


class ParallelExecutor:
    """
    Gestionnaire de tâches d'arrière-plan pour autom et asserv.

    Permet de lancer des séquences d'actions qui s'exécutent en arrière-plan
    pendant que d'autres actions s'exécutent au premier plan.
    """

    def __init__(self, node_autom, node_asserv):
        """
        Initialise le gestionnaire de parallélisme.

        Args:
            node_autom: Instance de CanAutomNode
            node_asserv: Instance de CanAsservNode
        """
        self.node_autom = node_autom
        self.node_asserv = node_asserv

        # Queues d'arrière-plan pour stocker les actions à exécuter
        self._bg_queue_autom = []
        self._bg_queue_asserv = []

        # Enregistrer les callbacks CAN pour être notifié des changements de statut
        self.node_autom.set_status_change_callback(self._on_status_change)
        self.node_asserv.set_status_change_callback(self._on_status_change)

    def _on_status_change(self, node_id):
        """
        Callback appelé automatiquement quand un TPDO CAN est reçu.
        Exécute la prochaine action d'arrière-plan si le node est libre.

        Args:
            node_id: ID du node CAN qui a changé de statut
        """
        # Traiter queue autom
        if node_id == self.node_autom.node_id:
            if self._bg_queue_autom and not self.node_autom.is_busy():
                next_action = self._bg_queue_autom.pop(0)
                next_action()

        # Traiter queue asserv
        elif node_id == self.node_asserv.node_id:
            if self._bg_queue_asserv and not self.node_asserv.is_busy():
                next_action = self._bg_queue_asserv.pop(0)
                next_action()

    def parallel_autom(self, *actions):
        """
        Lance des actions autom en arrière-plan (non-bloquant).

        Les actions s'exécutent séquentiellement en arrière-plan pendant que
        le code principal continue son exécution.

        Args:
            *actions: Liste de lambdas ou callables à exécuter

        Example:
            parallel.parallel_autom(
                lambda: autom.action_open_pince(),
                lambda: autom.action_grab(),
                lambda: autom.action_deposit()
            )
            # Le code continue immédiatement ici
            asserv.action_goto_xy(...)  # Pendant que autom s'exécute
        """
        # Ajouter toutes les actions à la queue d'arrière-plan
        self._bg_queue_autom.extend(actions)

        # Lancer la première action si autom est libre
        if self._bg_queue_autom and not self.node_autom.is_busy():
            first_action = self._bg_queue_autom.pop(0)
            first_action()

    def parallel_asserv(self, *actions):
        """
        Lance des actions asserv en arrière-plan (non-bloquant).

        Les actions s'exécutent séquentiellement en arrière-plan pendant que
        le code principal continue son exécution.

        Args:
            *actions: Liste de lambdas ou callables à exécuter

        Example:
            parallel.parallel_asserv(
                lambda: asserv.action_goto_xy(100, 200, Face.FACE_AVANT),
                lambda: asserv.action_goto_xy(300, 400, Face.FACE_AVANT)
            )
            # Le code continue immédiatement ici
            autom.action_grab()  # Pendant que asserv s'exécute
        """
        # Ajouter toutes les actions à la queue d'arrière-plan
        self._bg_queue_asserv.extend(actions)

        # Lancer la première action si asserv est libre
        if self._bg_queue_asserv and not self.node_asserv.is_busy():
            first_action = self._bg_queue_asserv.pop(0)
            first_action()

    def wait_parallel_autom(self):
        """
        Attend que toutes les actions autom d'arrière-plan soient terminées.

        Bloque jusqu'à ce que:
        1. La queue d'arrière-plan autom soit vide
        2. La dernière action autom soit terminée
        """
        # Attendre que la queue se vide
        while self._bg_queue_autom:
            time.sleep(0.01)

        # Attendre que la dernière action finisse
        while self.node_autom.is_busy():
            time.sleep(0.01)

    def wait_parallel_asserv(self):
        """
        Attend que toutes les actions asserv d'arrière-plan soient terminées.

        Bloque jusqu'à ce que:
        1. La queue d'arrière-plan asserv soit vide
        2. La dernière action asserv soit terminée
        """
        # Attendre que la queue se vide
        while self._bg_queue_asserv:
            time.sleep(0.01)

        # Attendre que la dernière action finisse
        while self.node_asserv.is_busy():
            time.sleep(0.01)

    def wait_all(self):
        """
        Attend que toutes les actions d'arrière-plan (autom ET asserv) soient terminées.

        Équivalent à appeler wait_parallel_autom() puis wait_parallel_asserv().
        """
        self.wait_parallel_autom()
        self.wait_parallel_asserv()
