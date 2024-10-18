from .models import Payment

class TransactionContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unseen_payments"] = Payment.objects.filter(is_seen = False)
        context["all_payments"] = Payment.objects.all()[:25]
        return context