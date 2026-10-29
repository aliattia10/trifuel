"""TriFuel web portal — onboarding + personalized dashboard."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from wger.core.services.trifuel_plan import (
    GOAL_PRESETS,
    apply_onboarding_profile,
    generate_starter_plan,
    profile_needs_onboarding,
)
from wger.nutrition.models import Meal, NutritionPlan


def home(request: HttpRequest) -> HttpResponse:
    """Public TriFuel entry — replaces OSS features brochure for logged-out users."""
    if request.user.is_authenticated:
        if profile_needs_onboarding(request.user):
            return HttpResponseRedirect(reverse('core:trifuel-onboarding'))
        return HttpResponseRedirect(reverse('core:trifuel-dashboard'))
    return render(request, 'trifuel/home.html')


@login_required
@require_http_methods(['GET', 'POST'])
def onboarding(request: HttpRequest) -> HttpResponse:
    errors: dict[str, str] = {}
    profile = request.user.userprofile
    values = {
        'first_name': request.user.first_name or '',
        'age': str(profile.age or ''),
        'height_cm': str(profile.height or ''),
        'weight_kg': str(profile.weight or '') if profile.weight else '',
        'goal': 'aggressive_bulk',
        'activity_hours': str(profile.sport_hours or 6),
    }

    if request.method == 'POST':
        values.update({k: (request.POST.get(k) or '').strip() for k in values})
        try:
            age = int(values['age'])
            if age < 10 or age > 100:
                raise ValueError('age')
        except ValueError:
            errors['age'] = 'Enter your age (10–100).'
            age = 0
        try:
            height_cm = int(values['height_cm'])
            if height_cm < 120 or height_cm > 250:
                raise ValueError('height')
        except ValueError:
            errors['height_cm'] = 'Enter height in cm (120–250).'
            height_cm = 0
        try:
            weight_kg = Decimal(values['weight_kg'])
            if weight_kg < 30 or weight_kg > 300:
                raise ValueError('weight')
        except (InvalidOperation, ValueError):
            errors['weight_kg'] = 'Enter weight in kg.'
            weight_kg = Decimal('0')
        goal = values['goal'] if values['goal'] in GOAL_PRESETS else 'aggressive_bulk'
        try:
            activity_hours = max(0, min(int(values['activity_hours'] or '6'), 40))
        except ValueError:
            activity_hours = 6

        if not errors:
            apply_onboarding_profile(
                request.user,
                first_name=values['first_name'] or request.user.username,
                age=age,
                height_cm=height_cm,
                weight_kg=weight_kg,
                goal_key=goal,
                activity_hours=activity_hours,
            )
            plan = generate_starter_plan(request.user, goal_key=goal)
            if plan:
                messages.success(request, 'Your TriFuel plan is ready.')
            else:
                messages.warning(request, 'Profile saved — meal library not available yet.')
            return HttpResponseRedirect(reverse('core:trifuel-dashboard'))

    return render(
        request,
        'trifuel/onboarding.html',
        {
            'values': values,
            'errors': errors,
            'goals': GOAL_PRESETS,
        },
    )


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    if profile_needs_onboarding(request.user):
        return HttpResponseRedirect(reverse('core:trifuel-onboarding'))

    profile = request.user.userprofile
    plan = (
        NutritionPlan.objects.filter(user=request.user)
        .order_by('-id')
        .first()
    )
    meals: list[Meal] = []
    if plan:
        meals = list(plan.meal_set.select_related().prefetch_related('mealitem_set__ingredient').order_by('order', 'time'))

    # Next reminder slot in waking hours (2–4h cadence)
    now = dt.datetime.now().time()
    reminder_slots = [dt.time(8, 0), dt.time(10, 0), dt.time(12, 0), dt.time(14, 0), dt.time(16, 0), dt.time(18, 0), dt.time(20, 0), dt.time(22, 0)]
    next_reminder = next((t for t in reminder_slots if t > now), reminder_slots[0])

    display_name = request.user.first_name or request.user.username
    return render(
        request,
        'trifuel/dashboard.html',
        {
            'display_name': display_name,
            'profile': profile,
            'plan': plan,
            'meals': meals,
            'next_reminder': next_reminder,
            'weight': profile.weight,
            'age': profile.age,
        },
    )
