from django.contrib.auth.decorators import login_required, \
    permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.views.generic import ListView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView
from .models import Profile
from .forms import ProfileForm, UserForm, AboutMeForm


def update_profile(request, *args, **kwargs):
    profile_inst = Profile.objects.get(pk=kwargs["pk"])
    user_inst = User.objects.get(id=profile_inst.user_id)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user_inst)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile_inst)
        if user_form.is_valid() and profile_form.is_valid() and request.user.is_staff:
            user_form.save()
            profile_form.save()
            return redirect(reverse('myauth:account_details', kwargs={"pk": profile_inst.pk}))
    else:
        user_form = UserForm(instance=user_inst)
        profile_form = ProfileForm(instance=profile_inst)
    return render(request, 'myauth/profile_update_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile_inst,
        'profile_login': user_inst.username,
    })


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        # определяем профиль, который привязан к текущему пользователю
        profile = Profile.objects.get(user_id=self.request.user.pk)
        context["profile"] = profile
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.filter(user_id=self.request.user.pk)[0]
        profile_form = AboutMeForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
        return redirect(reverse('myauth:about-me'))


class AccountDetailsView(DetailView):
    template_name = "myauth/profile-details.html"
    model = Profile
    queryset = (
        Profile.objects.select_related("user").prefetch_related("user").all()
    )
    # queryset = Profile.objects.prefetch_related("user")
    context_object_name = "profile"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if request.user.pk == self.object.user_id:
            return redirect(reverse("myauth:about-me"))
        return self.render_to_response(context)


class AccountsListView(LoginRequiredMixin, ListView):
    template_name = 'myauth/accounts-list.html'
    queryset = (
        Profile.objects.select_related("user").order_by("id").prefetch_related("user").all()
    )


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")
        return render(request, "myauth/login.html")

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user=user)
        return redirect("/admin/")

    return render(request, "myauth/login.html", context={"error": "Invalid username or password"})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default_value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'spam': 'eggs'})
