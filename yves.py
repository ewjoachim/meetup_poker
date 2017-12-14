import sys
import os

import logging
import logging.handlers

import itertools
import collections
import struct
import operator

YD = 1 << 6
__author__ = 'yves.duprat'+chr(YD)+'isen-lille.fr'
__date__ = "2017-12-14"

STR_FMT = '%(asctime)s - %(name)-8s - %(levelname)-9s - %(funcName)-15s - %(message)s'
DATE_FMT = '%d-%m-%Y %H:%M:%S'

l_value = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'V', 'D','R','A')
d_internal_value = { v:pos+1 for pos, v in enumerate(l_value) }
d_reverse_value = {  d_internal_value[k]:k for k in d_internal_value }
l_color = ('T', 'P', 'C', 'K')

I_VALUE, I_COLOR=range(2)
SIZE_HAND=5
MASK_KICKER = '%db' % SIZE_HAND
MASK_COMBIVALUE = '2b'
MASK_COMBI = 'b2s%ds' % SIZE_HAND

NOTHING, PAIR, DOUBLE_PAIR, THREE_OF_KIND, COLOR,  QUINTE,  FULL_HOUSE, POKER, QUINTE_FLUSH = range(9) 
str_combis = ("Rien", "Paire", "Double-Paire","Brelan", "Couleur", "Suite", "Full", "Carre", "Quinte Flush")
dict_combi = { pos:str for pos, str in enumerate(str_combis) }


def check_cards(logger, hand):
    """
    """
    # valid cards
    for value, color in hand:
        if value not in l_value or color not in l_color:
            return False
    
    # only distinct cards
    return len(collections.Counter(hand)) == len(hand)


def iter_make_all_combis(logger, hand):
    """
    """ 
    hand_as = list(map(lambda x: ('A' if x[I_VALUE] == '1' else x[I_VALUE] ,x[I_COLOR]), hand))
    if hand_as != list(hand) :
        logger.debug("'1' is in the combinaison %s -> %s", str(hand), str(hand_as))
        return itertools.chain(itertools.combinations(hand, SIZE_HAND), itertools.combinations(hand_as,SIZE_HAND))
    
    return itertools.combinations(hand, SIZE_HAND)


def make_all_combis(logger, hand):
    """
    """    
    return tuple(iter_make_all_combis(logger,hand))

    
def extract_value(logger, hand):
    """
    """
    return tuple(zip(*hand))[I_VALUE]

    
def extract_color(logger, hand):
    """
    """
    return tuple(zip(*hand))[I_COLOR]


def make_kicker(value):
    """
    make a kicker value as 5 best value 
    """
    return struct.pack(MASK_KICKER,  *value[:SIZE_HAND])

    
def make_combi_value(val1, val2):
    """
    """
    return struct.pack(MASK_COMBIVALUE, val1, val2)

    
def make_combi(combi,  strcombivalue,  strkicker):
    """
    """
    return struct.pack(MASK_COMBI, combi, strcombivalue, strkicker)


def is_quinte(logger, ivalue):
    """
    """
    i = len(ivalue) - 1
    nb = 0
    while i > 0 and ivalue[i] + 1 == ivalue[i-1]:
        nb += 1
        i -= 1
    # DO NOT NEED TO SEARCH pair, Three of kind etc ....
    return i == 0 or nb >= 5 

def compute_hand_5cards(logger, hand_not_sort):
    """
    compute a numeric value from combination and kicker
    note: a position is a byte
    - the last 5 positions are for kicker - Describe the ordrer value (descending)
    - the 2 positions before are for value of cards in combinaisons. 
        - Pair, Three of a kind, poker, flush is notice on 1 position (the right one)
        - Double pair and full hand are notice on 2 positions
    - the last left position is for the coimbinations
    cvvkkkkk for a number on 8 bytesv
    """
    # check if ggod cards
    combi = NOTHING
    cvalue = 0, 0
    if not check_cards(logger, hand_not_sort):
        return make_combi(combi, make_combi_value(*cvalue), make_kicker((0, 0, 0, 0, 0)))

    # sort hand
    hand = sorted(map(lambda x: (d_internal_value[x[I_VALUE]], x[I_COLOR]),  hand_not_sort),
                        key=operator.itemgetter(0),
                        reverse=True)
    logger.debug(hand)
    
    # use case for color 
    c = collections.Counter(extract_color(logger, hand))
    if len(c) == 1:
        combi = COLOR
        cvalue = 0, 0 

    # check on quinte
    ivalue = extract_value(logger, hand)
    
    # DO NOT NEED TO SEARCH pair, Three of kind etc ....
    if is_quinte(logger, ivalue):
        logger.debug(ivalue)
        
        # ok it is a quinte 
        # with color -> well done !!
        if combi == COLOR:
            combi = QUINTE_FLUSH
        else:
            # juste a quinte 
            combi = QUINTE
        cvalue = 0,  ivalue[0]
        
        return make_combi(combi, make_combi_value(*cvalue), make_kicker((0, 0, 0, 0, 0)))

    # only a color - bye
    if combi == COLOR:
        return make_combi(combi, make_combi_value(*cvalue), make_kicker(ivalue))
        
    # use case for pair, double pair, triple, full and four
    # test on count same value
    v= collections.Counter(ivalue)     
    for k in v:
        if v[k] == 4:
            combi = POKER
            cvalue =  k, 0
        elif v[k] == 3:
            # combi already set
            if combi == PAIR:
                combi = FULL_HOUSE
                cvalue = k,  cvalue[1]
            else:
                combi = THREE_OF_KIND
                cvalue =  0, k 
        elif v[k] == 2:
            # combi is already set 
            if combi == THREE_OF_KIND:
                combi = FULL_HOUSE
                cvalue = cvalue[1],  k
            elif combi == PAIR:
                combi = DOUBLE_PAIR
                if cvalue[1] > k:
                    cvalue = cvalue[1], k
                else:
                    cvalue = k, cvalue[1]
            else:
                combi = PAIR
                cvalue =  0, k  
            
    return make_combi(combi, make_combi_value(*cvalue), make_kicker(ivalue))


def string_score(logger, combi):
    """
    """
    logger.debug(combi[0])
    logger.debug(dict_combi[0])
    i = combi[0]    
#   python 2.7.x i = binascii.hexlify(combi[0])
    return dict_combi[i]


def get_best_hand_combi_and_combi_str(logger,hands):
    """
    """
    d = { hand:compute_hand_5cards(logger, hand) for hand in iter_make_all_combis(logger, hands) }
    str_best = ""
    for h in d:
        logger.debug("%s  -> %s", str(h), str(d[h]))
        if not str_best or d[h] > d[str_best]:
            str_best = h
    
    # highest combination is
#        logger.info("The best is %s -> %s from %s", str_best, binascii.hexlify(d[str_best]), str(hands) )
    str_combi = string_score(logger, d[str_best])
    logger.debug("The best is %s -> %s", str_best, str_combi)
        
    return str_best, d[str_best], str_combi

    
def main(logger, l_hands):
    """
    """
    for hands in l_hands: 
        str_best, str_combi, str_score = get_best_hand_combi_and_combi_str(logger,hands)
        logger.info("The best is %s -> %s", str_best, str_score)    

        
def test_extract_value(hand):
    """
    """
    pass

    
def test_extract_color(hand):
    """
    """
    pass


def test_make_kicker(value):
    """
    make a kicker value as 5 half byte 
    """
    pass

    
def test_make_combi_value(val1, val2,  str_kicker):
    """
    """
    pass

    
def test_make_combi(combi,  strcombivalue,  strkicker):
    """
    """
    pass

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

def test_hands(logger):
    """
    """
    if not logger:
        logger = logging.getLogger()

    if False:        
        lowest_val = -1
        save = ("", NOTHING, str_combis[NOTHING])
        for res, hand in zip(l_results,l_hands):
            strbest, val, valstr = get_best_hand_combi_and_combi_str(logger, hand)
            try:
                assert( res == val[0] )
                logger.info("assert %s == %s -> %s",res, val[0], valstr)
                logger.info("Combi is: %s",strbest)
            except:
                pass        
            else:
                if val[0] > lowest_val:
                    lowest_val = val[0]
                    save = (strbest, val[0], valstr)
    
        if save[0]:
            logger.info("\t\tThe best is : %s -> %s",save[0], save[2])
        
    # hand1 versus hand2
    for pos, hand in enumerate(zip(m_hands,l_hands)):
        strbest, val, valstr = get_best_hand_combi_and_combi_str(logger, hand[0])
        mstrbest, mval, mvalstr = get_best_hand_combi_and_combi_str(logger, hand[1])
        logger.info(("-"*25) + str(pos) + ("-"*25))
        logger.info("Hands: %s vs %s ",strbest, mstrbest)
        logger.info("Values: %s vs %s", val, mval)
        if val > mval:
            logger.info("Winner is %s (%s) with %s", valstr, mvalstr, strbest)
        elif val < mval:
            logger.info("Winner is %s (%s) with %s", mvalstr, valstr, mstrbest)
        else:
            logger.info("Equal !!")
    
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
    test_hands(None)
