#!/bin/env python3
"""
Point d'entrée principal du robot
"""
from core.init_core import initialize_all, deinit_all
from strategy.strat_dynamique import StratDynamique
import core.interface.log_management.logger as logger


def main():
    """
    Fonction principale du robot
    """
    # Initialisation complète du robot
    hw = initialize_all()

    # Création et exécution de la stratégie dynamique
    strat_dyn = StratDynamique(hw.strat, hw.robot_state,(1000,1000),['tas_4', 'tas_8', 'tas_6', 'tas_3', 'tas_5', 'tas_2', 'tas_7', 'tas_1'] )
    #strat_dyn.run_strat_qualif()
    strat_dyn.run_strat_final()

    # Arrêt propre
    deinit_all()
    logger.log_info("Main", "Program finished")
    logger.close()
    print("logger stopped")
    hw.bus.shutdown()


if __name__ == "__main__":
    main()
