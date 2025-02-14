from django.urls import path
from . import views

urlpatterns = [
    path('', views.CorrectionListView.as_view(), name='corrections_list'),
    path('edit/<int:pk>/', views.CorrectionEditView.as_view(), name='correction_edit'),
    path('apply/', views.ApplyCorrectionView.as_view(), name='apply_correction'),
]