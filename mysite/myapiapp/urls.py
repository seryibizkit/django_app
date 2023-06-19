from django.urls import path

from .views import hello_world_view, GroupListView, GroupListViewOld


app_name = "myapiapp"

urlpatterns = [
    path("hello/", hello_world_view, name="hello"),
    path("groups_old/", GroupListViewOld.as_view(), name="groupsOld"),
    path("groups/", GroupListView.as_view(), name="groups"),
]
