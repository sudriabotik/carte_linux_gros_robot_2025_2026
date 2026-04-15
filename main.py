#!/bin/env python3
"""
Point d'entrée principal du robot
"""
from core.init_core import initialize_all
from strategy.strat_dynamique import StratDynamique
from core.interface.can import canopen_wrapper
from core.interface.log_management import logger


def main():
    """
    Fonction principale du robot
    """
    # Initialisation complète du robot
    hw = initialize_all()

    # Création et exécution de la stratégie dynamique
    strat_dyn = StratDynamique(hw.strat, hw.robot_state,(1000,1000),['tas_4', 'tas_8', 'tas_6', 'tas_3', 'tas_5', 'tas_2', 'tas_7', 'tas_1'] )
    strat_dyn.run_strat()

    # Arrêt propre
    logger.log_info("Main", "Program finished")
    if canopen_wrapper.unified_logger:
        canopen_wrapper.unified_logger.stop()
        logger.log_info("Main", "Unified logger stopped")
    hw.bus.shutdown()


if __name__ == "__main__":
    main()
