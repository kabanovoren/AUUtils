import win32com.client
import os, sys
import json
import datetime
import base64
from Service import log, get_mdlp_param
import uuid

CADES_BES = 1
CADES_DEFAULT = 0
CAPICOM_ENCODE_BASE64 = 0
CAPICOM_CURRENT_USER_STORE = 2
CAPICOM_MY_STORE = 'My'
CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED = 2


class MDLP():
    def __init__(self):
        self.token = self.get_active_token()
        print(self.token)
        try:
            self.client_id = get_mdlp_param()['client_id']
            self.client_secret = get_mdlp_param()['client_secret']
            self.user_id = get_mdlp_param()['user_id']
            self.url = get_mdlp_param()['url']
            Cert = self.get_sert()
            if Cert == None:
                log("Не найден установленный сертификат")
            self.Cert = Cert
            self.oSigner = self.get_object()
            # self.auth()
            if self.check_token() or self.get_org_info()["status"] == 401:
                self.auth()

        except Exception as ex:
            log(ex)

    def get_message_signature(self, message):
        """Подписание сообщения и получение подписи"""
        oSignedData = win32com.client.Dispatch("CAdESCOM.CadesSignedData")
        oSignedData.ContentEncoding = 1
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        oSignedData.Content = base64_message
        sSignedData = oSignedData.SignCades(self.oSigner, CADES_BES, False, CAPICOM_ENCODE_BASE64)
        return sSignedData

    def get_encoding_doc(self, doc):
        """Кодирование документа"""
        message_bytes = doc.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_doc = base64_bytes.decode('ascii')
        return base64_doc

    def auth(self):
        """Авторизация и получение токена"""
        url = f"{self.url}/auth"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'user_id': self.user_id,
            'auth_type': 'SIGNED_CODE'
        }
        http = win32com.client.Dispatch('WinHTTP.WinHTTPRequest.5.1')
        http.Open("POST", url, False)
        http.SetRequestHeader("Content-Type", "application/json;charset=UTF-8")
        http.SetRequestHeader("Accept", "application/json;charset=UTF-8")
        http.Send(json.dumps(params))
        http.WaitForResponse()
        print(http.ResponseText)

        items = json.loads(http.ResponseText)
        CodeAuth = items['code']
        sSignedData = self.get_message_signature(CodeAuth)

        url = f"{self.url}/token"
        paramskey = {
            'code': CodeAuth,
            'signature': sSignedData
        }
        print(json.dumps(paramskey))
        http.Open("POST", url, False)
        http.SetRequestHeader("Content-Type", "application/json;charset=UTF-8")
        http.SetRequestHeader("Accept", "application/json;charset=UTF-8")
        http.Send(json.dumps(paramskey))
        http.WaitForResponse()
        print(http.ResponseText)
        token_response = json.loads(http.ResponseText)
        with open('token.txt', 'w') as file:
            file.writelines(
                f"{token_response['token']}|{datetime.datetime.now() + datetime.timedelta(minutes=token_response['life_time'] - 5)}")
        self.token = token_response['token']

    def get_sert(self):
        """Поиск установленного сертификата по отпечатку"""
        oStore = win32com.client.Dispatch("CAdESCOM.Store")
        oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED)
        for val in oStore.Certificates:
            if val.Thumbprint.upper() == self.user_id.upper():
                self.Cert = val
                return self.Cert

    def get_object(self):
        """Объект по подписанию на основе сертификата"""
        oSigner = win32com.client.Dispatch("CAdESCOM.CPSigner")
        oSigner.Certificate = self.Cert
        oSigningTimeAttr = win32com.client.Dispatch("CAdESCOM.CPAttribute")
        oSigningTimeAttr.Name = 0
        oSigningTimeAttr.Value = datetime.datetime.now()
        oSigner.AuthenticatedAttributes2.Add(oSigningTimeAttr)
        return oSigner

    def check_token(self):
        with open('token.txt', 'r') as file:
            s = file.readline().split('|')
            if datetime.datetime.strptime(s[1], '%Y-%m-%d %H:%M:%S.%f') > datetime.datetime.now():
                return False
            else:
                return True

    def get_active_token(self):
        with open('token.txt', 'r') as file:
            s = file.readline().split('|')
            return s[0]

    def send_511(self, document):
        if self.check_token():
            self.auth()
        url = f"{self.url}/documents/send"
        http = win32com.client.Dispatch('WinHTTP.WinHTTPRequest.5.1')
        http.Open("POST", url, False)
        http.SetRequestHeader("Content-Type", "application/json;charset=UTF-8")
        http.SetRequestHeader("Accept", "application/json;charset=UTF-8")
        http.SetRequestHeader("Authorization", f"token {self.token}")
        sign = self.get_message_signature(document)
        document = self.get_encoding_doc(document)
        request_id = uuid.uuid4()
        json_data = {
            "document": document,
            "sign": sign,
            "request_id": str(request_id),
            "bulk_processing": False
        }
        print(json_data)
        http.Send(json.dumps(json_data))
        http.WaitForResponse()
        return http.ResponseText

    def get_http_POST(self, url):
        http = win32com.client.Dispatch('WinHTTP.WinHTTPRequest.5.1')
        http.Open("POST", url, False)
        http.SetRequestHeader("Content-Type", "application/json;charset=UTF-8")
        http.SetRequestHeader("Accept", "application/json;charset=UTF-8")
        http.SetRequestHeader("Authorization", f"token {self.token}")
        return http

    def get_http_GET(self, url):
        """Получение данных по организации"""
        http = win32com.client.Dispatch('WinHTTP.WinHTTPRequest.5.1')
        http.Open("GET", url, False)
        http.SetRequestHeader("Content-Type", "application/json;charset=UTF-8")
        http.SetRequestHeader("Accept", "application/json;charset=UTF-8")
        http.SetRequestHeader("Authorization", f"token {self.token}")
        return http

    def get_org_info(self):
        url = f"{self.url}/members/current"
        http = self.get_http_GET(url)
        http.Send()
        http.WaitForResponse()
        return json.loads(http.ResponseText)

    def get_json_response_by_sgtin_list(self, http, sgtin_list):
        json_data = {
            "filter": {"sgtins": sgtin_list}
        }
        http.Send(json.dumps(json_data))
        http.WaitForResponse()
        return json.loads(http.ResponseText)

    def get_sgtin_by_list(self, sgtin_list):
        """Получение данных по SGTIN из реестра"""
        if self.check_token():
            self.auth()
        url = f"{self.url}/reestr/sgtin/sgtins-by-list"
        http = self.get_http_POST(url)
        return self.get_json_response_by_sgtin_list(http, sgtin_list)

    def get_sgtin_by_list_arhiv(self, sgtin_list):
        """Получение данных по SGTIN из архива"""
        if self.check_token():
            self.auth()
        url = f"{self.url}/reestr/sgtin/public/archive/sgtins-by-list"
        http = self.get_http_POST(url)
        return self.get_json_response_by_sgtin_list(http, sgtin_list)

    def get_sgtin_by_list_public(self, sgtin_list):
        """Получение данных по SGTIN публичный"""
        if self.check_token():
            self.auth()
        url = f"{self.url}/reestr/sgtin/public/sgtins-by-list"
        http = self.get_http_POST(url)
        return self.get_json_response_by_sgtin_list(http, sgtin_list)


def main3():
    pass


def main():
    mdlp = MDLP()
    """Тест получения информации по SGTIN"""
    sgtin_list = ["507540413898976BWtn52kGWFcu", "046032760059990AT2EVmf2IOpC", "50754041398767UiGH7ICzHbTWG"]
    print(mdlp.get_sgtin_by_list_arhiv(sgtin_list))
    """Тест 511"""
    # with open('D:/Python/AUUtils/SGTINAccept/out/511.xml', 'r') as file:
    #     xml = file.read()
    #
    # doc = mdlp.send_511(xml)
    # print(doc)

    # ser_num = '4FFA661658AF4C2304556E4F064C4B6E172194F5'
    # oCert = get_sert(ser_num)
    # oSigner = get_object(oCert)
    # auth(oSigner)


if __name__ == '__main__':
    main()
