from .models import Payment
from django.utils import timezone
from Sponsor_App.models import SponsorFamilyRelation

class TransactionContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unseen_payments"] = Payment.objects.filter(is_seen = False)
        context["all_payments"] = Payment.objects.filter(is_seen = False)
        return context
    

class SponsorPaymentNotificationMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overdue_notifications = []
        sponsor_family_relations = SponsorFamilyRelation.objects.all()

        for relation in sponsor_family_relations:
            latest_payment = Payment.objects.filter(
                sponsor=relation.sponsor,
                family=relation.family,
            ).order_by('-payment_date').first()
            
            if latest_payment:
                days_difference = (timezone.now().date() - latest_payment.overdue_payment.date()).days
                if days_difference > 1:
                    overdue_notifications.append({
                        'sponsor': relation.sponsor,
                        'family': relation.family,
                        'days_overdue': days_difference
                    })

        context["overdue_payments"] = overdue_notifications

        print(f"Length of the list is {overdue_notifications}")
                    
        return context