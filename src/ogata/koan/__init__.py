# encoding=utf-8
import cookielib
import urllib
import urllib2
import re
from HTMLParser import HTMLParser

from ogata.koan.parser import RishuParser


class KoanClient(object):
    """KOANにアクセスするクラス"""
    
    class LoginException(Exception):
        """ログインエラー"""
        pass
    
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22"
    personal_data = {}
    
    def __init__(self,username,password):
        self.cookie = cookielib.CookieJar()
        self.username = username
        self.password = password
        self.login()
        self.get_student_infomation()
    
    def get_urlopener(self):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        opener.addheaders = [('User-agent', self.user_agent),('Accept-Language','ja,en-us;q=0.7,en;q=0.3')]
        return opener
    
    def get_student_infomation(self):
        """学籍番号等を取得する"""
        opener = self.get_urlopener()
        url = "https://koan.osaka-u.ac.jp/koan/campus?view=view.menu&func=function.rishu.refer"
        response = opener.open(url)
        response = response.read().decode("utf-8")
        keys = (("g_b_cd","gakubu_code"),("g_cd","personnel_number"),)
        for koan_key,key in keys:
            r = re.compile('name="%s" value="(?P<value>[^"]+)"' % koan_key)
            m = r.search(response)
            self.personal_data[key] = m.group("value")
        
        
    
    def login(self):
        """SSOログインして、必要なクッキーを取得する"""
        opener = self.get_urlopener()
        
        #認証に必要なくキーを取る
        url = "https://koan.osaka-u.ac.jp/"
        request = urllib2.Request(url)
        response = opener.open(request)
        
        #SSOログインURLを取得する
        url = "https://koan.osaka-u.ac.jp/koan/campus"
        request = urllib2.Request(url)
        response = opener.open(request)
        #url = response.url
        
        #ログイン情報をPOSTする
        url = "https://sso.auth.osaka-u.ac.jp/idp/authnPwd"
        post = {}
        post["USER_ID"] = self.username
        post["USER_PASSWORD"] = self.password
        post["CHECK_BOX"] = ""
        post["IDButton"] = "Submit"
        request = urllib2.Request(url)
        request.add_data(urllib.urlencode(post))
        response = opener.open(request)
        #print response.read().decode("utf-8")
        
        #SAMLResponseを得るname="SAMLResponse" value="
        r = re.compile('name="SAMLResponse" value="(?P<SAMLResponse>[^"]+)"')
        m = r.search(response.read().decode("utf-8"))
        if m == None:
            raise self.LoginException()
        
        SAMLResponse = m.group("SAMLResponse").replace("\n","").replace("\r","")
        
        #KOANへ移動
        url = "https://koan.osaka-u.ac.jp/Shibboleth.sso/SAML2/POST"
        post = {}
        post["SAMLResponse"] = SAMLResponse
        post["RelayState"] = "https://koan.osaka-u.ac.jp/koanlogin/campus?sso_redirect="
        request = urllib2.Request(url)
        request.add_data(urllib.urlencode(post))
        response = opener.open(request)
        
        #あとはこのクッキーを使えばログインされた状態になる
        return
    
    def get_rishu(self,nendo,gakki):
        opener = self.get_urlopener()
        url = "https://koan.osaka-u.ac.jp/koan/campus?view=view.rishu.refer.html&func=function.rishu.refer.output&o_type=1&g_b_cd=%s&nendo=%d&gakki=%d&check=1&g_cd=%s&fukupro="
        url = url % (self.personal_data["gakubu_code"],nendo,gakki,self.personal_data["personnel_number"])
        response = opener.open(url)
        rishu = RishuParser(response.read())
        return rishu
        
        
        
if __name__ == "__main__":
    import getpass
    roleId = raw_input("Username: ")
    passwd = getpass.getpass("Password: ")
    client = KoanClient(roleId,passwd)
    client.get_rishu(2012,1)
    
    