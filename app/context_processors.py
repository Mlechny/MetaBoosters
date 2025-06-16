from app.models import Tag
from django.db.models import Count

def popular_tags(request):
    tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]
    return {'popular_tags': tags}
