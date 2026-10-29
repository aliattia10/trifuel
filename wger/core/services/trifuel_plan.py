"""Generate a TriFuel starter nutrition plan for a user (aggressive bulk defaults)."""

from __future__ import annotations

import datetime as dt
import json
import random
from decimal import Decimal
from pathlib import Path

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from wger.core.models import Language, License, UserProfile
from wger.measurements.models import Category, Measurement
from wger.measurements.models.category import MetricType
from wger.measurements.models.measurement import MeasurementSource
from wger.nutrition.models import Ingredient, Meal, MealItem, NutritionPlan

# Prefer server/data (Docker / Render); fall back to monorepo ../data.
_SERVER_ROOT = Path(__file__).resolve().parents[3]
_MEALS_CANDIDATES = (
    _SERVER_ROOT / 'data' / 'noah-perlofit-gym-meals.json',
    _SERVER_ROOT.parent / 'data' / 'noah-perlofit-gym-meals.json',
)
MEALS_JSON = next((p for p in _MEALS_CANDIDATES if p.exists()), _MEALS_CANDIDATES[0])

GOAL_ENERGY = 3000
GOAL_PROTEIN = 150
GOAL_CARBS = 350
GOAL_FAT = 90

GOAL_PRESETS = {
    'aggressive_bulk': {
        'label': 'Aggressive bulk',
        'energy': 3000,
        'protein': 150,
        'carbs': 350,
        'fat': 90,
    },
    'lean_bulk': {
        'label': 'Lean bulk',
        'energy': 2600,
        'protein': 160,
        'carbs': 280,
        'fat': 75,
    },
    'maintain': {
        'label': 'Maintain',
        'energy': 2200,
        'protein': 140,
        'carbs': 220,
        'fat': 70,
    },
}


def estimate_macros(kcal: int | None, protein_g: float | None) -> tuple[int, Decimal, Decimal, Decimal]:
    energy = int(kcal or 400)
    protein = Decimal(str(round(float(protein_g or 25), 3)))
    if protein > Decimal('100'):
        protein = Decimal('100')
    remaining = energy - float(protein) * 4
    if remaining <= 0:
        return energy, protein, Decimal('0'), Decimal('0')
    carbs = Decimal(str(round(min((remaining * 0.7) / 4, 100), 3)))
    fat = Decimal(str(round(min((remaining * 0.3) / 9, 100), 3)))
    return energy, protein, carbs, fat


def category_bucket(category: str) -> str:
    if category == 'breakfast':
        return 'breakfast'
    if category == 'snacks':
        return 'snack'
    return 'main'


def pack_day(pool: dict[str, list], rng: random.Random) -> list[tuple[str, dict, int]]:
    breakfasts = sorted(
        pool['breakfast'][:],
        key=lambda m: int((m.get('per_serving') or {}).get('kcal') or 0),
        reverse=True,
    )
    mains = sorted(
        pool['main'][:],
        key=lambda m: int((m.get('per_serving') or {}).get('kcal') or 0),
        reverse=True,
    )
    snacks = sorted(
        pool['snack'][:],
        key=lambda m: int((m.get('per_serving') or {}).get('kcal') or 0),
        reverse=True,
    )
    rng.shuffle(breakfasts)
    rng.shuffle(mains)
    rng.shuffle(snacks)
    breakfasts.sort(key=lambda m: int((m.get('per_serving') or {}).get('kcal') or 0), reverse=True)
    mains.sort(key=lambda m: int((m.get('per_serving') or {}).get('kcal') or 0), reverse=True)

    slots: list[tuple[str, dict, int]] = []
    if breakfasts:
        slots.append(('Breakfast', breakfasts[0], 2 if int((breakfasts[0].get('per_serving') or {}).get('kcal') or 0) < 500 else 1))
    if snacks:
        slots.append(('Snack AM', snacks[0], 1))
    if mains:
        slots.append(('Lunch', mains[0], 2 if int((mains[0].get('per_serving') or {}).get('kcal') or 0) < 600 else 1))
    if len(snacks) > 1:
        slots.append(('Snack PM', snacks[1], 1))
    if len(mains) > 1:
        slots.append(('Dinner', mains[1], 2 if int((mains[1].get('per_serving') or {}).get('kcal') or 0) < 600 else 1))
    if len(snacks) > 2:
        slots.append(('Snack Eve', snacks[2], 1))
    return slots


def ensure_noah_ingredients() -> dict[str, Ingredient]:
    """Create shared Noah ingredients once; return id → Ingredient map."""
    if not MEALS_JSON.exists():
        return {}

    data = json.loads(MEALS_JSON.read_text())
    meals = data['meals']
    language = Language.objects.get(short_name='en')
    license_obj = License.objects.get(pk=2)
    by_id: dict[str, Ingredient] = {}

    for meal in meals:
        existing = Ingredient.objects.filter(source_name='noahperlofit', remote_id=meal['id'][:200]).first()
        if existing:
            by_id[meal['id']] = existing
            continue
        energy, protein, carbs, fat = estimate_macros(
            (meal.get('per_serving') or {}).get('kcal'),
            (meal.get('per_serving') or {}).get('protein_g'),
        )
        name = meal['name'][:200] or f"Meal {meal['id']}"[:200]
        ingredients_blurb = '; '.join(meal.get('key_ingredients') or [])[:500]
        ing = Ingredient.objects.create(
            language=language,
            license=license_obj,
            license_author='noahperlofit (stated macros)',
            name=f'[Noah] {name}'[:200],
            energy=energy,
            protein=protein,
            carbohydrates=carbs,
            fat=fat,
            remote_id=meal['id'][:200],
            source_name='noahperlofit',
            source_url=(meal.get('source_url') or '')[:200] or None,
            common_name=ingredients_blurb[:200] if ingredients_blurb else None,
        )
        by_id[meal['id']] = ing
    return by_id


def apply_onboarding_profile(
    user: User,
    *,
    first_name: str,
    age: int,
    height_cm: int,
    weight_kg: Decimal,
    goal_key: str = 'aggressive_bulk',
    activity_hours: int = 6,
) -> UserProfile:
    """Persist onboarding fields on User + UserProfile + body-weight measurement."""
    if first_name:
        user.first_name = first_name[:30]
        user.save(update_fields=['first_name'])

    profile: UserProfile = user.userprofile
    today = dt.date.today()
    birth_year = max(1926, today.year - max(10, min(age, 100)))
    profile.birthdate = dt.date(birth_year, 1, 1)
    profile.age = age
    profile.height = height_cm
    profile.weight_unit = UserProfile.UNITS_KG
    profile.sport_hours = activity_hours
    profile.sport_intensity = UserProfile.INTENSITY_HIGH
    profile.work_intensity = UserProfile.INTENSITY_LOW
    profile.num_days_weight_reminder = 2
    # Stash goal key in gym-free text via email? Prefer a lightweight approach:
    # store in userprofile by encoding into notes via unused field — use sport_hours already.
    # We'll keep goal on the nutrition plan description.
    profile.save()

    weight_cat = Category.get_or_create_body_weight(user, unit='kg')
    Measurement.objects.create(
        category=weight_cat,
        date=timezone.now(),
        value=weight_kg,
        notes=f'TriFuel onboarding ({goal_key})',
        source=MeasurementSource.USER,
        extra_data={'unit': 'kg'},
    )
    return profile


def generate_starter_plan(user: User, goal_key: str = 'aggressive_bulk') -> NutritionPlan | None:
    """Create (or refresh) the primary TriFuel nutrition plan for this user."""
    preset = GOAL_PRESETS.get(goal_key, GOAL_PRESETS['aggressive_bulk'])
    ingredient_by_id = ensure_noah_ingredients()
    if not ingredient_by_id:
        return None

    if not MEALS_JSON.exists():
        return None
    meals = json.loads(MEALS_JSON.read_text())['meals']
    pool: dict[str, list] = {'breakfast': [], 'main': [], 'snack': []}
    for meal in meals:
        pool[category_bucket(meal['category'])].append(meal)

    rng = random.Random(user.id * 17 + today_seed())
    times = {
        'Breakfast': dt.time(8, 0),
        'Snack AM': dt.time(10, 30),
        'Lunch': dt.time(12, 30),
        'Snack PM': dt.time(16, 0),
        'Dinner': dt.time(19, 0),
        'Snack Eve': dt.time(21, 0),
    }

    with transaction.atomic():
        NutritionPlan.objects.filter(user=user, description__startswith='TriFuel').delete()
        plan = NutritionPlan.objects.create(
            user=user,
            description=f"TriFuel — {preset['label']}",
            start=dt.date.today(),
            end=dt.date.today() + dt.timedelta(days=28),
            goal_energy=preset['energy'],
            goal_protein=preset['protein'],
            goal_carbohydrates=preset['carbs'],
            goal_fat=preset['fat'],
            has_goal_calories=True,
        )
        for order, (slot_name, meal, servings) in enumerate(pack_day(pool, rng), start=1):
            m = Meal.objects.create(
                plan=plan,
                order=order,
                time=times.get(slot_name),
                name=slot_name[:25],
            )
            MealItem.objects.create(
                meal=m,
                ingredient=ingredient_by_id[meal['id']],
                order=1,
                amount=Decimal(100 * servings),
            )
    return plan


def today_seed() -> int:
    d = dt.date.today()
    return d.toordinal()


def profile_needs_onboarding(user: User) -> bool:
    profile = user.userprofile
    if not profile.height or profile.height < 100:
        return True
    if not profile.birthdate and not profile.age:
        return True
    try:
        weight = profile.weight
    except Exception:
        weight = 0
    if not weight:
        return True
    if not NutritionPlan.objects.filter(user=user).exists():
        return True
    return False
