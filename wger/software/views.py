# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import logging

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render

# Third Party
import requests

# wger
from wger.core.forms import WgerSignupForm
from wger.exercises.models import Exercise
from wger.nutrition.models import Ingredient


logger = logging.getLogger(__name__)

CACHE_KEY = 'landing-page-context'
GITHUB_API_URL = 'https://api.github.com/repos/wger-project/wger'
GITHUB_API_TIMEOUT = 5
CACHE_TTL_SUCCESS = 60 * 60 * 24 * 7  # one week
CACHE_TTL_FAILURE = 60 * 60  # one hour


def fetch_github_stats() -> dict:
    context = cache.get(CACHE_KEY)
    if context:
        return context

    context = {
        'nr_users': User.objects.count(),
        'nr_exercises': Exercise.objects.count(),
        'nr_ingredients': Ingredient.objects.count(),
        'nr_stars': 1,
    }

    try:
        result_github_api = requests.get(GITHUB_API_URL, timeout=GITHUB_API_TIMEOUT).json()
    except Exception as e:
        logger.error(f'Error fetching github stats: {e}')
        # Cache the fallback so an unreachable GitHub API is not retried on every visit.
        cache.set(CACHE_KEY, context, CACHE_TTL_FAILURE)
        return context

    context['nr_stars'] = result_github_api.get('stargazers_count', '2000')
    cache.set(CACHE_KEY, context, CACHE_TTL_SUCCESS)

    return context


def features(request):
    """
    Legacy OSS landing — redirect to TriFuel portal.
    """
    from django.http import HttpResponseRedirect
    from django.urls import reverse

    return HttpResponseRedirect(reverse('core:trifuel-home'))
