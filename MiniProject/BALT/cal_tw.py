from scores import *
from math import floor
from typing import Tuple, List
import bisect


def convert_alp_num(alp: str):
    if alp == "A":
        num = 0
    elif alp == "B":
        num = 1
    elif alp == "C":
        num = 2
    elif alp == "D":
        num = 3
    elif alp == "E":
        num = 4
    elif alp == "F":
        num = 5
    elif alp == "G":
        num = 6
    elif alp == "H":
        num = 7
    elif alp == "I":
        num = 8
    else:
        num = -1
    return num


def get_gender_tables(gender):
    if gender == "Male":
        return boy_bone_score, boy_maturity_score, boy_bone_age
    elif gender == "Female":
        return girl_bone_score, girl_maturity_score, girl_bone_age


def binary_search_insert_indices(lst, value):
    insertion_point = bisect.bisect_right(lst, value)
    lower_idx = insertion_point - 1
    upper_idx = insertion_point if insertion_point < len(lst) else None
    return lower_idx, upper_idx


def linear_interpolation(
    maturity_score_table, bone_age_table, sum_bone_score, lower_idx
) -> float:
    low_mat = maturity_score_table[lower_idx]
    up_mat = maturity_score_table[lower_idx + 1]
    low_ba = bone_age_table[lower_idx]
    up_ba = bone_age_table[lower_idx + 1]
    # print((sum_bone_score - low_mat) * ((up_ba - low_ba) / (up_mat - low_mat)))
    # print(low_ba)
    return low_ba + (
        (sum_bone_score - low_mat) * ((up_ba - low_ba) / (up_mat - low_mat))
    )


def convert_y2ym(ba: float) -> Tuple[int, int]:
    ba_flr = floor(ba)
    ba_y = ba_flr + 1 if round((ba - ba_flr) * 12) == 12 else ba_flr
    ba_m = 0 if round((ba - ba_flr) * 12) == 12 else round((ba - ba_flr) * 12)
    return ba_y, ba_m
