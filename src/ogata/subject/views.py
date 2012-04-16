# encoding=utf-8
from ogata.subject.forms import RegistrationForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template


def registration(request):
    """新規登録"""
    form = RegistrationForm()
    
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("regist_complete"))
    
    context = {"form":form}
    return direct_to_template(request, "subject/regist.html", context)


def registration_complete(request):
    """新規登録完了"""
    return direct_to_template(request, "subject/regist_complete.html")


