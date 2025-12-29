from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectView.as_view(), name='project'),
    path('silicon_person/', views.SiliconPersonView.as_view(), name='silicon_person'),
    path('question/', views.SamplingViews.as_view(), name='question'),
    path('model-response/', views.ModelResponseView.as_view(), name='model_response'),
    path('quick_answer/', views.QuickAnswerView.as_view(), name='quick_answer'),
    path('upload_silicon_persons_csv/', views.SiliconPersonByCSV.as_view(), name='upload_silicon_persons'),
    path('analyse-results/', views.AnalyseResultsView.as_view(), name='analyse_results'),
    path('upload_questions_csv/', views.QuestionImportByCSV.as_view(), name='upload_questions'),
    path('token-cost/', views.TokenCostEstimationView.as_view(), name='token_cost_estimation'),
    path('silicon_users_statistics/', views.UserStatistics.as_view(), name='silicon_users_statistics'),
    path('ai_models/', views.AImodels.as_view(), name='ai_models'),
]