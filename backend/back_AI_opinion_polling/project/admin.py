from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Project)
admin.site.register(SiliconePerson)
admin.site.register(Prompt)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(AnalysisResult)
admin.site.register(ModelLog)
admin.site.register(Cost)