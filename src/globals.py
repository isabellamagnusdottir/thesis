from decimal import Decimal
# This variable determines the type of the weights of the algorithm

WEIGHT_TYPE = float

types = {
        "decimal": Decimal,
        "float": float,
        "int": int
    }

def change_weight_type(weight_type):
    global WEIGHT_TYPE
    if type(weight_type) == str:
        WEIGHT_TYPE = types[weight_type]
    else:
        WEIGHT_TYPE = weight_type
