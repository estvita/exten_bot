from .models import Tariff, Trial
from datetime import timedelta
from django.utils.timezone import now


def get_date(user):
    try:
        existing_trial = Trial.objects.filter(owner=user).first()
        if existing_trial:
            return now()
        duration = Tariff.objects.filter(trial=True).values_list("duration", flat=True).first()
        if not duration:
            return now()

        expiration_date = now() + timedelta(days=duration)
        Trial.objects.create(owner=user)

        return expiration_date

    except Exception as e:
        return now()