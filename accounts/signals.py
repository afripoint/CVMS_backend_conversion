from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import AgentProfile, CompanyProfile, CustomUser, IndividualProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "individual account":
            IndividualProfile.objects.create(user=instance)
        elif instance.role == "agent account/freight forwarders":
            AgentProfile.objects.create(user=instance)
        elif instance.role == "company account":
            CompanyProfile.objects.create(user=instance)
