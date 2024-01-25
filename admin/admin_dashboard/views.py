import random
import string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

User = get_user_model()

ADMIN_LIST_LIMIT = 10


def get_random_string(size):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


# Admin Login
def LogIn(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST.get("username"))
        if not user:
            messages.info(request, "Invalid Login credentials")
            return HttpResponseRedirect("/admin/")
        user = user[0]

        if not user.check_password(request.POST.get("password")):
            messages.info(request, "Invalid Login credentials")
            return HttpResponseRedirect("/admin/")

        if not user.is_superuser:
            messages.info(request, "You dont have permission to access admin panel")
            return HttpResponseRedirect("/admin/")

        login(request, user)
        messages.info(request, "Login Successfully")
        return HttpResponseRedirect(reverse("admin_dashboard:dashboard"))
    return render(request, "login.html")


def logout_user(request):
    logout(request)
    messages.info(request, "Logout Successfully")
    return HttpResponseRedirect('/admin/')


def data_pagination(request, query_set):
    paginator = Paginator(query_set, ADMIN_LIST_LIMIT)
    page = request.GET.get('page', '1')
    try:
        _paginated_data = paginator.page(page)
    except PageNotAnInteger:
        _paginated_data = paginator.page(1)
    except EmptyPage:
        _paginated_data = paginator.page(paginator.num_pages)
    return _paginated_data, page, (ADMIN_LIST_LIMIT * int(page)) - ADMIN_LIST_LIMIT


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def dashboard(request):
    all_users = User.objects.all().exclude(id=request.user.id)
    dt = {
        "active_users": all_users.filter(is_active=True).count(),
        "total_users": all_users.count(),
        "inactive_users": all_users.filter(is_active=False).count(),
    }
    return render(request, 'admin_dashboard.html', dt)


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def users_listing(request):
    users = User.objects.order_by("-id").exclude(id=request.user.id)

    search, is_active, role, user_type, platform = request.GET.get("search", ""), request.GET.get("is_active",
                                                                                                  "None"), request.GET.get(
        "role", "None"), request.GET.get("user_type", "None"), request.GET.get("platform", "None")

    if search and search != 'None':
        users = users.filter(
            Q(email__icontains=search) |
            Q(email=search)
        )
    if is_active and is_active != 'None':
        if is_active == 'yes':
            users = users.filter(is_active=True)
        else:
            users = users.filter(is_active=False)

    if role and role != "None":
        users = users.filter(role=role)
    if user_type and user_type != "None":
        users = users.filter(user_type=user_type)
    if platform and platform != "None":
        users = users.filter(login_type=platform)

    _paginated_data, page, limit_counts = data_pagination(request, users)
    dt = {
        "users": _paginated_data,
        "page": page,
        "search": search,
        "is_active": is_active,
        "role": role,
        "user_type": user_type,
        "platform": platform,
        "params": "search={}&is_active={}&platform={}".format(search, is_active, role),
        "limit_counts": limit_counts,
    }
    return render(request, "user_lists.html", dt)


# User view,add and update
@user_passes_test(lambda u: u.is_superuser, login_url='/')
def add_update_user(request, id, mode):
    if mode == "new":
        user = User()
    else:
        user = User.objects.get(id=id)

    if request.method == "POST":
        password = None
        if user.email != request.POST.get("email"):
            if User.objects.filter(email=request.POST.get("email")):
                messages.info(request, "User with this email already exist.")
                return HttpResponseRedirect(reverse('admin_dashboard:all_users'))
            else:
                pass
        for key, val in request.POST.items():
            if key not in ["csrfmiddlewaretoken"]:
                setattr(user, key, val)

        if mode == "new":
            password = get_random_string(10)
            user.is_one_time_login = True
            user.set_password(password)  # change to random alphanumeric password.
            messages.info(request, "Successfully save a new-user")
        else:
            messages.info(request, "Successfully update a '{}' user".format(user.email))
        if request.POST.get("is_active") == "on":
            user.is_active = True
        else:
            user.is_active = False
        if request.POST.get("is_pd_distance") == "on":
            user.is_pd_distance = True
        else:
            user.is_pd_distance = False
        if request.POST.get("is_reading_distance") == "on":
            user.is_reading_distance = True
        else:
            user.is_reading_distance = False
        if request.POST.get("is_f_meter") == "on":
            user.is_f_meter = True
        else:
            user.is_f_meter = False
        user.save()

        if mode == "new":
            try:
                message = "Your email '{}' and password '{}' .".format(user.email, password)
                template = render_to_string("user_addingbyadmin.html", {"message": message})
                send_mail(
                    "Zukti Inovations adding you as user", "",
                    settings.EMAIL_FROM_USER, [user.email],
                    html_message=template,
                    fail_silently=False
                )
            except Exception as e:
                pass
        return HttpResponseRedirect(reverse("admin_dashboard:all_users"))
    return render(request, "user_view.html", {
        "user": user,
        "id": id,
        "url_type": mode,
    })


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def delete_user(request, id):
    User.objects.filter(id=id).delete()
    messages.info(request, "Successfully deleting a user.")
    return HttpResponseRedirect(reverse("admin_dashboard:all_users"))
