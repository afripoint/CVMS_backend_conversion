# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from accounts.models import AgentProfile, CompanyProfile, CustomUser, IndividualProfile


# @receiver(post_save, sender=CustomUser)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         if instance.role == "individual account":
#             IndividualProfile.objects.create(user=instance)
#         elif instance.role == "agent account/freight forwarders":
#             profile_data = getattr(instance, "_profile_data", None)
#             (
#                 AgentProfile.objects.create(user=instance, **profile_data)
#                 if profile_data
#                 else AgentProfile.objects.create(user=instance)
#             )
#         elif instance.role == "company account":
#             profile_data = getattr(instance, "_profile_data", None)
#             (
#                 CompanyProfile.objects.create(user=instance, **profile_data)
#                 if profile_data
#                 else CompanyProfile.objects.create(user=instance)
#             )
