import sys
import os

import logging
import logging.handlers

STR_FMT = '%(asctime)s - %(name)-8s - %(levelname)-9s - %(funcName)-15s - %(message)s'
DATE_FMT = '%d-%m-%Y %H:%M:%S'

import collections

l_value = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'V', 'D', 'R', 'A')
l_color = ('T', 'P', 'C', 'K')


NOTHING, PAIR, DOUBLE_PAIR, THREE_OF_KIND, COLOR,  QUINTE,  FULL_HOUSE, POKER, QUINTE_FLUSH = range(9) 
str_combis = ("Rien", "Paire", "Double-Paire","Brelan", "Couleur", "Suite", "Full", "Carre", "Quinte Flush")
dict_combi = { pos:str for pos, str in enumerate(str_combis) }


def checkCards(logger, hand):
    """
    """
    # valid cards
    for value, color in hand:
        if value not in l_value or color not in l_color:
            return False
    
    # only distinct cards
    return len(collections.Counter(hand)) == len(hand)


def getBestHandCombiAndCombiStr(logger,hands):
    """
    """
    return "", "", str_combis[NOTHING]
    
def main(logger, l_hands):
    """
    """
    for hands in l_hands:
        if( checkCards(logger, hands)):
            str_best, str_combi, str_score = getBestHandCombiAndCombiStr(logger,hands)
            logger.info("The best is %s -> %s", str_best, str_score)

        
l_results = (
            COLOR,
            QUINTE_FLUSH,
            PAIR,
            NOTHING,
            THREE_OF_KIND,
            DOUBLE_PAIR,
            POKER,
            FULL_HOUSE,
            QUINTE
            )
l_hands =   (
            (('1','C'),('7','C'),('10','C'),('D','C'),('5','C')), # couleur à la dame
            (('1','C'),('3','C'),('5','C'),('2','C'),('4','C')), # quinte flush 
            (('6','C'),('3','P'),('5','K'),('2','C'),('6','K'),('7','K')), # Pair de 6 - kicker au 7 
            (('1','C'),('3','P'),('R','K'),('2','C'),('6','K')), # nothing - Kiker à l'AS
            (('V','C'),('1','P'),('V','K'),('D','T'),('R','T'), ('V','T')), # three}  
            (('1','C'),('3','P'),('1','K'),('3','C'),('6','K')),  # two pair
            (('1','C'),('1','P'),('1','K'),('D','T'),('1','T')), # poker
            (('1','C'),('3','P'),('1','K'),('D','C'),('3','K'),('6','C'),('1','T')),  # full house
            (('1','C'),('3','P'),('4','K'),('D','C'),('3','K'),('2','C'),('5','T')) # quinte
            )
m_hands =   (
            (('R','K'),('7','K'),('10','K'),('D','K'),('5','K')), # couleur au roi 
            (('1','C'),('3','C'),('5','C'),('2','C'),('4','C')), # quinte flush 
            (('6','C'),('3','P'),('8','K'),('2','C'),('6','K'),('V','K')), # Pair de 6 - kicker au V
            (('4','C'),('3','P'),('R','K'),('2','C'),('6','K')), # nothing - Kicker au 4
            (('V','C'),('1','P'),('V','K'),('D','T'),('R','T'),('V','T')), # three}  
            (('1','C'),('R','P'),('1','K'),('3','C'),('6','K')),  # two pair
            (('1','C'),('1','P'),('1','K'),('D','T'),('1','T')), # poker
            (('1','C'),('3','P'),('1','K'),('D','C'),('3','K'),('6','C'),('1','T')),  # full house
            (('1','C'),('7','P'),('4','K'),('6','C'),('3','K'),('2','C'),('5','T')) # quinte
            )

    
if __name__ == "__main__":
    """
    """
    logging.basicConfig(format=STR_FMT, datefmt=DATE_FMT, level=logging.INFO) 
    mainlog = logging.getLogger()

    # file handler log
    file_log = os.path.join(os.getcwd(),'file.log')
    hdlr = logging.handlers.TimedRotatingFileHandler(file_log, when='midnight', interval=1, backupCount=7)
    formatter = logging.Formatter(STR_FMT, DATE_FMT)    
    hdlr.setFormatter(formatter)

    # add file handler to logger
    mainlog.addHandler(hdlr)

    main(mainlog, l_hands)
