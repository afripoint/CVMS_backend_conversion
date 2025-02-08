from django.contrib import admin

from verifications.models import CACUserVerification

class CACVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'created_at', 'updated_at', )
    list_display_links = ('user', 'email',)



admin.site.register(CACUserVerification, CACVerificationAdmin)