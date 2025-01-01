from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.utils import timezone
from django.shortcuts import get_object_or_404
from Super_Admin_App.models import Payment, FamilyList
from django.contrib.auth.models import User
from .models import SponsorFamilyRelation
from paypal.standard.models import ST_PP_COMPLETED
import logging

# Logger setup
logger = logging.getLogger(__name__)

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender

    # Check if the payment status is "Completed"
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            # Extract family_id and sponsor_id from the custom field
            family_id, sponsor_id = ipn_obj.custom.split('|')
            user = User.objects.get(id=sponsor_id)
            family_sponsored = get_object_or_404(FamilyList, pk=family_id)

            # Calculate overdue payment date
            if Payment.objects.exists():
                overdue_payment = Payment.objects.first().overdue_payment + timezone.timedelta(days=30)
            else:
                overdue_payment = timezone.now()

            # Create Payment record
            Payment.objects.create(
                sponsor=user,
                family=family_sponsored,
                amount=ipn_obj.mc_gross,
                overdue_payment=overdue_payment
            )

            # Create or get Sponsor-Family relation
            SponsorFamilyRelation.objects.get_or_create(
                sponsor=user,
                family=family_sponsored
            )

            # Mark the family as sponsored if not already
            if not family_sponsored.is_sponsored:
                family_sponsored.is_sponsored = True
                family_sponsored.save()

            logger.info(f"Successfully processed PayPal payment for {family_sponsored.family_name}.")

        except Exception as e:
            logger.error(f"Error processing PayPal IPN: {str(e)}")

    else:
        logger.warning(f"Received IPN with status {ipn_obj.payment_status}. Ignoring.")