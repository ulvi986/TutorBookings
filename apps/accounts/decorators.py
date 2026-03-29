from django.contrib.auth.decorators import user_passes_test


def student_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == "student")(view_func)


def tutor_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == "tutor")(view_func)


def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and (u.is_staff or u.role == "admin"))(view_func)
