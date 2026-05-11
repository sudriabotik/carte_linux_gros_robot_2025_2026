"""
EXEMPLE D'UTILISATION DU SYSTÈME DE PARALLÉLISME

Ce fichier montre comment utiliser ParallelExecutor pour exécuter des tâches
d'arrière-plan pendant que d'autres actions s'exécutent au premier plan.

Ce fichier est UNIQUEMENT pour documentation - ne pas exécuter directement.
"""

from strategy.parallel_executor import ParallelExecutor
from core.interface.can import comm_asserv
from core.robot.function_strat import FunctStrat
from core.robot.robot import Robot


def exemple_utilisation_basique(funct: FunctStrat, robot_state: Robot):
    """
    Exemple basique : lancer autom en arrière-plan pendant qu'asserv travaille
    """
    asserv = funct.node_asserv
    autom = funct.node_autom

    # Créer le gestionnaire de parallélisme
    parallel = ParallelExecutor(autom, asserv)

    # Créer des raccourcis pour simplifier l'écriture
    parallel_autom = parallel.parallel_autom
    wait_parallel_autom = parallel.wait_parallel_autom

    # Lancer une séquence autom en arrière-plan (non-bloquant)
    parallel_autom(
        lambda: autom.action_open_pince(),
        lambda: autom.action_grab(),
        lambda: autom.action_deposit()
    )

    # Pendant que autom s'exécute, asserv fait ses mouvements
    asserv.action_lookat(175, 400, comm_asserv.Face.FACE_AVANT)
    asserv.action_goto_xy(175, 400, comm_asserv.Face.FACE_AVANT, 100, 20)

    # Attendre que autom ait fini avant de continuer
    wait_parallel_autom()

    # Maintenant on peut continuer
    asserv.action_goto_xy(1000, 2000, comm_asserv.Face.FACE_AVANT, 100, 20)


def exemple_utilisation_avancee(funct: FunctStrat, robot_state: Robot):
    """
    Exemple avancé : autom ET asserv en arrière-plan simultanément
    """
    asserv = funct.node_asserv
    autom = funct.node_autom

    # Créer le gestionnaire
    parallel = ParallelExecutor(autom, asserv)

    # Lancer AUTOM en arrière-plan
    parallel.parallel_autom(
        lambda: autom.action_grab(),
        lambda: autom.action_deposit(),
        lambda: autom.action_close_pince()
    )

    # Lancer ASSERV en arrière-plan EN MÊME TEMPS
    parallel.parallel_asserv(
        lambda: asserv.action_goto_xy(100, 200, comm_asserv.Face.FACE_AVANT),
        lambda: asserv.action_goto_xy(300, 400, comm_asserv.Face.FACE_AVANT)
    )

    # Les deux s'exécutent en parallèle maintenant !
    # Le code continue ici...

    # Attendre que les deux finissent
    parallel.wait_all()


def exemple_pattern_courant(funct: FunctStrat, robot_state: Robot):
    """
    Pattern courant : préparer autom pendant qu'asserv se déplace
    """
    asserv = funct.node_asserv
    autom = funct.node_autom

    parallel = ParallelExecutor(autom, asserv)

    # Pattern : Pendant qu'on se déplace, préparer les pinces
    parallel.parallel_autom(
        lambda: autom.action_open_pince()
    )

    # Se déplacer vers le tas (pendant que pinces s'ouvrent)
    asserv.action_goto_xy(175, 1200, comm_asserv.Face.FACE_AVANT)

    # Attendre que pinces soient ouvertes
    parallel.wait_parallel_autom()

    # Maintenant on peut attraper
    autom.action_grab()


def exemple_sans_raccourcis(funct: FunctStrat, robot_state: Robot):
    """
    Exemple sans créer de raccourcis (plus verbeux mais tout aussi valide)
    """
    asserv = funct.node_asserv
    autom = funct.node_autom

    # Créer le gestionnaire
    parallel = ParallelExecutor(autom, asserv)

    # Utiliser directement les méthodes (pas de raccourcis)
    parallel.parallel_autom(
        lambda: autom.action_grab(),
        lambda: autom.action_deposit()
    )

    asserv.action_goto_xy(100, 200, comm_asserv.Face.FACE_AVANT)

    parallel.wait_parallel_autom()


# NOTES IMPORTANTES :
#
# 1. Les lambdas sont NÉCESSAIRES :
#    ✅ Correct : lambda: autom.action_grab()
#    ❌ Incorrect : autom.action_grab()  # S'exécute immédiatement !
#
# 2. Les actions d'arrière-plan s'exécutent SÉQUENTIELLEMENT :
#    parallel_autom(action1, action2, action3)
#    → action1 s'exécute, puis action2, puis action3
#
# 3. Autom et asserv peuvent vraiment s'exécuter EN PARALLÈLE :
#    parallel_autom(...)  # Démarre autom
#    parallel_asserv(...) # Démarre asserv EN MÊME TEMPS
#
# 4. Il faut attendre avant d'utiliser le node à nouveau :
#    parallel_autom(lambda: autom.action_grab())
#    wait_parallel_autom()  # ← Important !
#    autom.action_deposit()  # OK maintenant
