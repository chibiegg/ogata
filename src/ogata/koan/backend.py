# encoding=utf-8

from ogata.koan import KoanClient
from django.contrib.auth.models import User
from ogata.subject.models import Student


class SSOBackend:
    def authenticate(self, username=None, password=None):
        # Check the username/password and return a User.
        try:
            koan_client = KoanClient(username,password)
        except KoanClient.LoginException:
            return None
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            #無ければ登録
            user = Student(username=username)
            user.sso_passwd = "%dummy%"
            user.save()
            
        try:
            student = user.student
        except Student.DoesNotExist:
            pass
        else:
            #SSOパスワードの更新
            if student.sso_passwd != password:
                student.sso_passwd = password
                student.save()
            student.update_from_sso() #その他の情報の更新
            
        return user
    