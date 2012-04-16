# encoding=utf-8

from django import forms
from ogata.subject.models import Student
from django.forms.util import ErrorList
from django.utils.datastructures import SortedDict
from ogata.koan import KoanClient



class RegistrationForm(forms.ModelForm):
    """新規登録フォーム"""
    
    class Meta:
        model = Student
        fields = ["username","roleId","email",]
    
    passwd = forms.CharField(label=u"パスワード",widget=forms.PasswordInput(render_value=True))
    sso_passwd = forms.CharField(label=u"SSOパスワード",widget=forms.PasswordInput(render_value=True))
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, 
        initial=None, error_class=ErrorList, label_suffix=':', 
        empty_permitted=False, instance=None):
        
        super(RegistrationForm,self).__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial,
                                               error_class=error_class, label_suffix=label_suffix,
                                                empty_permitted=empty_permitted, instance=instance)
        #一部の表示を変更
        self.fields["username"].label = u"希望ユーザー名"
        self.fields["username"].help_text = u""
        self.fields["email"].label = u"メールアドレス"
        
        #表示順序の並び替え
        new_fields = SortedDict()
        fields = ("username","passwd","email","roleId","sso_passwd")
        for field in fields:
            new_fields[field] = self.fields[field]
        self.fields = new_fields
            
        
    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        
        if "roleId" in cleaned_data and "sso_passwd" in cleaned_data:
            #SSOログインチェック
            try:
                client = KoanClient(cleaned_data["roleId"],cleaned_data["sso_passwd"])
            except KoanClient.LoginException:
                self.errors["roleId"] = self.error_class([u"個人IDまたは、SSOパスワードが異なります"])
        
        return cleaned_data