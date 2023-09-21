# Third-Party
from rest_framework import routers

# Local
from govapp.apps.accounts import views


# Router
router = routers.DefaultRouter()
router.register("users", views.UserViewSet)
router.register("groups", views.GroupViewSet)


# Accounts URL Patterns
urlpatterns = router.urls
