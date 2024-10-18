from Messaging.models import Message

class MessageContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unread_messages"] = Message.objects.filter(receiver=self.request.user, is_read = False)
        context["all_messages"] = Message.objects.filter(receiver=self.request.user)
        return context