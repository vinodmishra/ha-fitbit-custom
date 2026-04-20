from datetime import date
from enum import Enum


class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


def get_age(date_of_birth: date) -> int:
    today = date.today()
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age


def get_lbm(age: int, height: float, weight: float, impedance: int) -> float:
    lbm = (height * 9.058 / 100) * (height / 100)
    lbm += weight * 0.32 + 12.226
    lbm -= impedance * 0.0068
    lbm -= age * 0.0542
    return lbm


def check_value_constraints(value: float, min_val: float, max_val: float) -> float:
    if value < min_val:
        return min_val
    return max_val if value > max_val else value


def get_fat_percentage(
    gender: Gender, age: int, weight: float, height: float, lbm: float
) -> float:
    coefficient = 1.0
    if gender == Gender.FEMALE:
        const_value = 9.25 if age <= 49 else 7.25
        if weight > 60:
            coefficient = 0.96
        elif weight < 50:
            coefficient = 1.02

        if height > 160 and (weight < 50 or weight > 60):
            coefficient *= 1.03
    else:
        const_value = 0.8
        if weight < 61:
            coefficient = 0.98

    fat_percentage = (1.0 - ((lbm - const_value) * coefficient) / weight) * 100
    if fat_percentage > 63:
        fat_percentage = 75

    return check_value_constraints(fat_percentage, 5, 75)


def calculate_body_fat(
    gender: Gender,
    date_of_birth: date,
    weight: float,
    height: float,
    impedance: int | None,
) -> float | None:
    if not impedance or height == 0:
        return None

    age = get_age(date_of_birth)
    lbm = get_lbm(age, height, weight, impedance)
    return get_fat_percentage(gender, age, weight, height, lbm)
