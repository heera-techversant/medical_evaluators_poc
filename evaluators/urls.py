from django.urls import path
from evaluators import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.LoginView.as_view(), name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.SignUpView.as_view(), name='signup'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('doc_save/', views.DocsaveView.as_view(), name='doc-save'),
    path('doc_list/', views.DocumentListView.as_view(), name='doc-list'),
    path('detail/<slug:doc_id>/', views.DocumentDetailView.as_view(), name='doc-detail'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)