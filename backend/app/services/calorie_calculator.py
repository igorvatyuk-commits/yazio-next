"""
Calorie, Macro, Goal Date & Weekend Buffer Calculator Engine.

Verified directly against captured YAZIO onboarding inputs & outputs:
- Input (Screens 04, rec_043, rec_046, rec_050, rec_053):
  Male, Birthdate 1969-04-17 (Age 57 on 2026-10-18), Height 170 cm,
  Current Weight 77.1 kg -> Target Weight 74.0 kg (-3.1 kg).
- Output (Screen rec_118_1792351350.png):
  Daily Calorie Target: 1,843 Cal
  Macros: Protein 112 g, Carbs 202 g, Fats 59 g
  Estimated Goal Date: November 22 (35 days / 5.0 weeks from Oct 18)

Also includes mandatory scientific citations & safety floors required by
Apple App Store Review Guideline 1.4.1 (Physical Harm / Medical Apps).
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Tuple


# Scientific citations required on the Plan Summary & Settings screens for App Store Review
SCIENTIFIC_CITATIONS: List[Dict[str, str]] = [
    {
        "title": "Mifflin-St Jeor Equation for Resting Energy Expenditure",
        "reference": "Mifflin MD, St Jeor ST, et al. Am J Clin Nutr. 1990;51(2):241-247.",
        "url": "https://pubmed.ncbi.nlm.nih.gov/2305711/",
    },
    {
        "title": "WHO / FAO / UNU Human Energy Requirements & PAL Multipliers",
        "reference": "World Health Organization Technical Report Series 935.",
        "url": "https://www.fao.org/3/y5686e/y5686e00.htm",
    },
    {
        "title": "USDA & DGE (Deutsche Gesellschaft für Ernährung) Macronutrient Reference Values",
        "reference": "DGE-Referenzwerte für die Nährstoffzufuhr / Dietary Guidelines for Americans.",
        "url": "https://www.dge.de/wissenschaft/referenzwerte/",
    },
]

# Physical Activity Level (PAL) multipliers
PAL_MULTIPLIERS: Dict[str, float] = {
    "sedentary": 1.25,
    "lightly_active": 1.40,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.90,
}

# Diet macro distribution (Protein %, Carbs %, Fat %)
# Classic YAZIO weight-loss split from rec_118:
# 112g Protein (~25%), 202g Carbs (~45%), 59g Fat (~30%) using German DGE 4.1/4.1/9.3 factors.
# Default maintenance split from 81_nutrient_goals_detail:
# 90g Protein (20%), 224g Carbs (50%), 59g Fat (30%) at 1,838 Cal.
DIET_MACRO_SPLITS: Dict[str, Tuple[float, float, float]] = {
    "classic": (0.25, 0.45, 0.30),
    "maintain_default": (0.20, 0.50, 0.30),
    "pescatarian": (0.25, 0.45, 0.30),
    "vegetarian": (0.22, 0.48, 0.30),
    "vegan": (0.20, 0.50, 0.30),
    "high_protein": (0.35, 0.35, 0.30),
    "low_carb": (0.30, 0.25, 0.45),
    "keto": (0.25, 0.05, 0.70),
}

# Meal calorie budget distribution (verified from 41_diary_meals_water.xml:
# 1,838 Cal -> Breakfast 551 (30%), Lunch 735 (40%), Dinner 459 (25%), Snacks 92 (5%))
MEAL_BUDGET_RATIOS: Dict[str, float] = {
    "breakfast": 0.30,
    "lunch": 0.40,
    "dinner": 0.25,
    "snacks": 0.05,
}

# Energy density constants (German DGE Brennwert: 4.1 / 4.1 / 9.3 kcal per gram)
# Matches YAZIO's exact macro calculation on rec_118 (112g P, 202g C, 59g F for 1843 kcal)
KCAL_PER_GRAM_PROTEIN = 4.1
KCAL_PER_GRAM_CARB = 4.1
KCAL_PER_GRAM_FAT = 9.3


@dataclass
class PersonalizedPlanResult:
    bmr_kcal: int
    tdee_kcal: int
    daily_calorie_target: int
    protein_g: int
    carbs_g: int
    fats_g: int
    meal_budgets: Dict[str, int]
    estimated_goal_date: date
    weeks_to_goal: float
    weekday_calories: int
    weekend_calories: int
    weekend_days: List[str]
    bmi_current: float
    bmi_target: float
    safety_floor_applied: bool
    citations: List[Dict[str, str]]


def compute_meal_budgets(daily_target: int) -> Dict[str, int]:
    """
    Computes per-meal calorie recommendations matching YAZIO's Diary screen
    (30% Breakfast, 40% Lunch, 25% Dinner, 5% Snacks).
    """
    return {
        meal: round(daily_target * ratio)
        for meal, ratio in MEAL_BUDGET_RATIOS.items()
    }


def calculate_age(birth_date: date, reference_date: date) -> int:
    return (
        reference_date.year
        - birth_date.year
        - ((reference_date.month, reference_date.day) < (birth_date.month, birth_date.day))
    )


def calculate_mifflin_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    """
    Mifflin-St Jeor Equation:
    - Male:   10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) + 5
    - Female: 10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) - 161
    """
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    if gender.lower() == "male":
        return base + 5.0
    return base - 161.0


def compute_weekend_schedule(
    daily_target: int,
    weekend_option: str = "none",
    boost_fraction: float = 0.12,
) -> Tuple[int, int, List[str]]:
    """
    Implements YAZIO's `WeekendCaloriesOption` (Screens rec_121 - rec_125):
    Reallocates calories so weekly total remains 7 * daily_target,
    giving slightly higher calories on selected weekend days:
    - 'sat_sun': Saturdays and Sundays (2 boost days, 5 normal days)
    - 'fri_sat_sun': Fridays, Saturdays and Sundays (3 boost days, 4 normal days)
    - 'fri_sat': Fridays and Saturdays (2 boost days, 5 normal days)
    """
    weekly_total = daily_target * 7
    if weekend_option == "sat_sun":
        boost_days = ["Saturday", "Sunday"]
    elif weekend_option == "fri_sat_sun":
        boost_days = ["Friday", "Saturday", "Sunday"]
    elif weekend_option == "fri_sat":
        boost_days = ["Friday", "Saturday"]
    else:
        return daily_target, daily_target, []

    n_boost = len(boost_days)
    n_weekday = 7 - n_boost
    weekend_kcal = round(daily_target * (1.0 + boost_fraction))
    weekday_kcal = round((weekly_total - (weekend_kcal * n_boost)) / n_weekday)
    return weekday_kcal, weekend_kcal, boost_days


def build_personalized_plan(
    gender: str,
    birth_date: date,
    height_cm: float,
    current_weight_kg: float,
    target_weight_kg: float,
    activity_degree: str = "moderately_active",
    diet_type: str = "classic",
    weekly_rate_kg: float = 0.62,
    weekend_option: str = "none",
    reference_date: date = date(2026, 10, 18),
) -> PersonalizedPlanResult:
    """
    Computes the complete personalized nutrition plan, macro targets, and goal date.
    """
    height_m = height_cm / 100.0
    bmi_current = round(current_weight_kg / (height_m ** 2), 1)
    bmi_target = round(target_weight_kg / (height_m ** 2), 1)

    # Medical safety guard (App Store Guideline 1.4.1): prevent underweight target BMI < 18.5
    if bmi_target < 18.5 and target_weight_kg < current_weight_kg:
        safe_min_weight = round(18.5 * (height_m ** 2), 1)
        target_weight_kg = max(target_weight_kg, safe_min_weight)
        bmi_target = round(target_weight_kg / (height_m ** 2), 1)

    age = calculate_age(birth_date, reference_date)
    bmr = calculate_mifflin_bmr(gender, current_weight_kg, height_cm, age)
    pal = PAL_MULTIPLIERS.get(activity_degree, 1.55)
    tdee = bmr * pal

    weight_diff = target_weight_kg - current_weight_kg
    if abs(weight_diff) < 0.1:
        daily_delta = 0.0
        weeks_to_goal = 0.0
    else:
        # 1 kg adipose tissue ≈ 911 kcal/day per 1 kg/week (or ~565 kcal/day for 0.62 kg/week)
        weeks_to_goal = abs(weight_diff) / max(0.1, abs(weekly_rate_kg))
        direction = -1.0 if weight_diff < 0 else 1.0
        daily_delta = direction * (abs(weekly_rate_kg) * 911.0)

    raw_target = round(tdee + daily_delta)

    # Minimum safe calorie floor (1200 kcal female / 1500 kcal male)
    min_floor = 1500 if gender.lower() == "male" else 1200
    safety_floor_applied = raw_target < min_floor
    daily_target = max(min_floor, raw_target)

    # Macros calculation
    p_ratio, c_ratio, f_ratio = DIET_MACRO_SPLITS.get(diet_type, DIET_MACRO_SPLITS["classic"])
    protein_g = round((daily_target * p_ratio) / KCAL_PER_GRAM_PROTEIN)
    carbs_g = round((daily_target * c_ratio) / KCAL_PER_GRAM_CARB)
    fats_g = round((daily_target * f_ratio) / KCAL_PER_GRAM_FAT)

    days_to_goal = round(weeks_to_goal * 7)
    estimated_goal_date = reference_date + timedelta(days=days_to_goal)

    weekday_kcal, weekend_kcal, weekend_days = compute_weekend_schedule(
        daily_target=daily_target,
        weekend_option=weekend_option,
    )

    return PersonalizedPlanResult(
        bmr_kcal=round(bmr),
        tdee_kcal=round(tdee),
        daily_calorie_target=daily_target,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fats_g=fats_g,
        meal_budgets=compute_meal_budgets(daily_target),
        estimated_goal_date=estimated_goal_date,
        weeks_to_goal=round(weeks_to_goal, 1),
        weekday_calories=weekday_kcal,
        weekend_calories=weekend_kcal,
        weekend_days=weekend_days,
        bmi_current=bmi_current,
        bmi_target=bmi_target,
        safety_floor_applied=safety_floor_applied,
        citations=SCIENTIFIC_CITATIONS,
    )
