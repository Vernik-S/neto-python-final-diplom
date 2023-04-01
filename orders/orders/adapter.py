
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class ActiveUserAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):

        user = super().populate_user(request, sociallogin, data)

        user.is_active = True

        return user