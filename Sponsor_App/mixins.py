from Messaging.models import Message
from django.utils import timezone
from .models import SponsorFamilyRelation
from Super_Admin_App.models import Payment

class MessageContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unread_messages"] = Message.objects.filter(receiver=self.request.user, is_read = False)
        context["all_messages"] = Message.objects.filter(receiver=self.request.user)
        return context
    
class SponsorPaymentNotificationMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overdue_notifications = []
        sponsor_family_relations = SponsorFamilyRelation.objects.filter(sponsor=self.request.user)

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

        return context