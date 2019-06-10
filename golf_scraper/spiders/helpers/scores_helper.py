import numpy as np
import pandas as pd


def test_func():
    print("sup")
    return

def check_if_round(string):
    is_round = True
    try:
        integer = int(string)
    except:
        return False
    # if total score is > 110 it's probably not a round score
    return True if integer < 110 else False










# end
