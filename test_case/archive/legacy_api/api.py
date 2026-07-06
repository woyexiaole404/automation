import certifi
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# # 禁用 InsecureRequestWarning（可选，但不建议在生产环境中禁用）
# urllib3.disable_warnings(InsecureRequestWarning)
#
# # 创建一个 HTTPS 池，带有证书验证
# http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


url = "https://adv.xiwshijieheping.com/adAlliance/ad/pullAds"

heder = {
    "ad-preference": "fc4270abac12ffa8b3d8ab622d1033656829e6d2d54f5ffbf3ee27b44d19d3712cd9a73829bea9c6998a91f0d94b8a8678f360a4f459c0bfc047a705d455e157",
    "clientauthorization": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJzYWFzIiwiY2xpZW50Q29kZSI6InNhYXMiLCJpZGVudGl0eSI6ImFkbWluIiwiZ3JhbnRDb2RlIjoianJzTVNqbkpqODJSIiwiZXhwIjoxNzIzNzExMzA1LCJpYXQiOjE3MjI4NDczMDV9.DxGxfsWqMx3kAmb-D_XAt9Yn3S_NeVwHXX1Egvx7p3-3D1AYdDHuOQ-0OD_-mqfyZT8k-aoXPK-XAxHmRDd6aA",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"
}
data = {
    "timestamp": 1722843241014,
    "sign": "",
    "adPullPlacementDTO": {
        "adPlacementId": "1813392719627362305",
        "adSceneId": "1813392719652528130",
        "adNum": 1,
        "lastExposureAdIds": [

        ],
        "adPlacementWidth": 400,
        "adPlacementHeight": 765,
        "materialNum": 1
    },
    "adPullApplicationDTO": {
        "appId": "saas_495eddab46d37129",
        "appBundleId": "",
        "appKey": "",
        "sdkVersion": "1.0.83"
    },
    "adPullDeviceDTO": {
        "deviceType": 0,
        "deviceSystem": "ANDROID",
        "brand": "",
        "model": "",
        "os": "android",
        "osVersion": "",
        "deviceCode": "145302e8-6eaf-610b-55c6-20d8298d7cba",
        "imei": "",
        "imeiMd5": "",
        "oaid": "",
        "androidId": "",
        "androidIdMd5": "",
        "idfa": "",
        "idfaMd5": ""
    },
    "adPullNetworkDTO": {
        "connectionType": 0,
        "carrier": 0,
        "ip": "",
        "userAgent": ""
    }
}

req = requests.post(url=url, headers=heder, json=data, verify=False)
print(req.json())
