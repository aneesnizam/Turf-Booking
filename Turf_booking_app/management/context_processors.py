from accounts.models import UserMessage

def notifications(request):
    if request.user.is_authenticated:
        # Get all unread messages for the logged-in user
        user_messages = UserMessage.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        unread_count = user_messages.count()
        return {
            'user_messages': user_messages,
            'unread_count': unread_count
        }
    return {}