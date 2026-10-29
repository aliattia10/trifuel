"""TriFuel onboarding API for the Flutter app."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wger.core.services.trifuel_plan import (
    GOAL_PRESETS,
    apply_onboarding_profile,
    generate_starter_plan,
    profile_needs_onboarding,
)


class TriFuelOnboardingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = request.user.userprofile
        return Response(
            {
                'needs_onboarding': profile_needs_onboarding(request.user),
                'first_name': request.user.first_name,
                'age': profile.age,
                'height': profile.height,
                'weight': float(profile.weight) if profile.weight else None,
                'goals': {k: {'label': v['label'], 'energy': v['energy'], 'protein': v['protein']} for k, v in GOAL_PRESETS.items()},
            }
        )

    def post(self, request):
        data = request.data or {}
        try:
            age = int(data.get('age'))
            height_cm = int(data.get('height_cm') or data.get('height'))
            weight_kg = Decimal(str(data.get('weight_kg') or data.get('weight')))
        except (TypeError, ValueError, InvalidOperation):
            return Response({'detail': 'age, height_cm, and weight_kg are required numbers'}, status=status.HTTP_400_BAD_REQUEST)

        if age < 10 or age > 100 or height_cm < 120 or height_cm > 250 or weight_kg < 30 or weight_kg > 300:
            return Response({'detail': 'Values out of allowed range'}, status=status.HTTP_400_BAD_REQUEST)

        goal = data.get('goal') or 'aggressive_bulk'
        if goal not in GOAL_PRESETS:
            goal = 'aggressive_bulk'
        try:
            activity_hours = int(data.get('activity_hours') or 6)
        except (TypeError, ValueError):
            activity_hours = 6

        apply_onboarding_profile(
            request.user,
            first_name=(data.get('first_name') or request.user.username)[:30],
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            goal_key=goal,
            activity_hours=activity_hours,
        )
        plan = generate_starter_plan(request.user, goal_key=goal)
        return Response(
            {
                'ok': True,
                'plan_id': plan.id if plan else None,
                'plan_description': plan.description if plan else None,
                'goal_energy': plan.goal_energy if plan else None,
                'goal_protein': plan.goal_protein if plan else None,
            }
        )
