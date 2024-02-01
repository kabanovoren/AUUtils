import win32com.client
import os, sys
import json
import datetime
import base64

CADES_BES = 1
CADES_DEFAULT = 0
CAPICOM_ENCODE_BASE64 = 0
CAPICOM_CURRENT_USER_STORE = 2
CAPICOM_MY_STORE = 'My'
CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED = 2

def get_sert(sSerialNumber):
    oStore = win32com.client.Dispatch("CAdESCOM.Store")
    oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED)
    for val in oStore.Certificates:
        if val.SerialNumber.upper() == sSerialNumber.upper():
            oCert = val
            return oCert


def get_object(oCert):
    oSigner = win32com.client.Dispatch("CAdESCOM.CPSigner")
    oSigner.Certificate = oCert
    oSigningTimeAttr = win32com.client.Dispatch("CAdESCOM.CPAttribute")
    oSigningTimeAttr.Name = 0
    oSigningTimeAttr.Value = datetime.datetime.now()
    oSigner.AuthenticatedAttributes2.Add(oSigningTimeAttr)
    return oSigner


def auth(oSigner):
    url = "https://api.sb.mdlp.crpt.ru/api/v1/auth"

    params = {
        'client_id': 'be7052fb-f891-4d87-8206-6e04b7ce111c',
        'client_secret': 'ca563ad2-0046-4dd5-aebc-bfc6279b0e8b',
        'user_id': '4FFA661658AF4C2304556E4F064C4B6E172194F5',
        'auth_type': 'SIGNED_CODE'
    }
    win_http = win32com.client.Dispatch('WinHTTP.WinHTTPRequest.5.1')
    win_http.Open("POST", url, False)
    win_http.SetRequestHeader("Content-Type", "application/json;charset=UTF-8")
    win_http.SetRequestHeader("Accept", "application/json;charset=UTF-8")
    win_http.Send(json.dumps(params))
    win_http.WaitForResponse()
    print(win_http.ResponseText)
    items = json.loads(win_http.ResponseText)
    CodeAuth = items['code']
    oSignedData = win32com.client.Dispatch("CAdESCOM.CadesSignedData")
    oSignedData.ContentEncoding = 1
    message = CodeAuth
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    oSignedData.Content = base64_message
    sSignedData = oSignedData.SignCades(oSigner, CADES_BES, False, CAPICOM_ENCODE_BASE64)
    url = "https://api.sb.mdlp.crpt.ru/api/v1/token"
    paramskey = {
        'code': CodeAuth,
        'signature': sSignedData
    }
    print(json.dumps(paramskey))
    win_http.Open("POST", url, False)
    win_http.SetRequestHeader("Content-Type", "application/json;charset=UTF-8")
    win_http.SetRequestHeader("Accept", "application/json;charset=UTF-8")
    win_http.Send(json.dumps(paramskey))
    win_http.WaitForResponse()
    print(win_http.ResponseText)


def main():
    ser_num = '120062ef23f4968da7437a60bc00010062ef23'
    oCert = get_sert(ser_num)
    oSigner = get_object(oCert)
    auth(oSigner)



if __name__ == '__main__':
    main()