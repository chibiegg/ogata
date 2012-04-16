# encoding=utf-8
import random
import datetime
import struct
import base64

from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ManyToManyRel

from Crypto.Cipher import AES

from django.conf import settings
from ogata.koan import KoanClient

class Course(models.Model):
    """科目"""
    created = models.DateTimeField(u"追加日",auto_now_add = True)
    modified = models.DateTimeField(u"編集日",auto_now=True)
    
    year = models.PositiveIntegerField(u"年度")
    code = models.IntegerField(u"授業コード")
    name = models.CharField(u"科目名",max_length=200)
    #name_en = models.CharField(u"Course Name",max_length=200)
    #credits = models.DecimalField(u"単位数",max_digits=2,decimal_places=1)

class Student(User):
    
    PADDING = '{'
    
    """学生"""
    personnel_number = models.CharField(u"学籍番号",max_length=8)
    sso_passwd_encrypted = models.TextField(u"SSOパスワード",max_length=150)
    sso_passwd_iv = models.CharField(u"IV",max_length=16*3)
    
    @classmethod
    def create_iv(cls):
        """Initial Vectorを生成する"""
        random.seed(datetime.datetime.now())
        iv = struct.pack("16B",*[random.randint(0,255) for i in range(16)])
        return iv
        
        
    def get_sso_passwd(self):
        """暗号化を解除する"""
        iv = base64.b64decode(self.sso_passwd_iv)
        cipher = AES.new(settings.SSO_PASSWORD_KEY,AES.MODE_CBC,iv)
        passwd = cipher.decrypt(base64.b64decode(self.sso_passwd_encrypted)).rstrip(self.PADDING)
        return passwd
    
    def set_sso_passwd(self,passwd):
        """暗号化する"""
        iv = self.create_iv()
        cipher = AES.new(settings.SSO_PASSWORD_KEY,AES.MODE_CBC,iv)
        BLOCK_SIZE = 32
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * self.PADDING
        encrypted = base64.b64encode(cipher.encrypt(pad(passwd)))
        
        self.sso_passwd_iv = base64.b64encode(iv)
        self.sso_passwd_encrypted = encrypted
        
    
    sso_passwd = property(get_sso_passwd,set_sso_passwd)
    
    def update_from_sso(self):
        """KOAN等にログインして情報を更新する"""
        try:
            client=KoanClient(self.username,self.sso_passwd)
        except KoanClient.LoginException:
            return
        
        self.personnel_number = client.personal_data["personnel_number"]
        self.save()
        
class Rishu(models.Model):
    """履修"""
    created = models.DateTimeField(u"追加日",auto_now_add = True)
    modified = models.DateTimeField(u"編集日",auto_now=True)
    
    student = models.ForeignKey(Student)
    course = models.ForeignKey(Course)


if __name__ == "__main__":
    
    student = Student()
    student.sso_passwd = ("1234567890")
    print student.sso_passwd_encrypted
    print student.sso_passwd_iv
    print student.sso_passwd
    

    
    
    
    
    