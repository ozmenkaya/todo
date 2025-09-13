"""
OneSignal Configuration
Bu dosyada OneSignal servisinizin bilgileri yer alır.
"""

import os

class OneSignalConfig:
    # OneSignal App ID - OneSignal dashboard'unuzdan alın
    APP_ID = os.getenv('ONESIGNAL_APP_ID', '0047e2bf-7209-4b1c-b222-310e700a9780')
    
    # OneSignal REST API Key - OneSignal dashboard'unuzdan alın  
    API_KEY = os.getenv('ONESIGNAL_API_KEY', 'os_v2_app_abd6fp3sbffrzmrcgehhacuxqcalxza3656u4p5gzxpcmji55xmckrxansybtyo6nvii2pq2onkoguolsra7lj6j3thkrq5sijnesvy')
    
    # OneSignal User Auth Key - Sadece bazı admin işlemler için gerekli
    USER_AUTH_KEY = os.getenv('ONESIGNAL_USER_AUTH_KEY', 'YOUR_USER_AUTH_KEY')
    
    # Web Push bilgileri
    SAFARI_WEB_ID = os.getenv('ONESIGNAL_SAFARI_WEB_ID', '')
    
    # Apple Push Notification service (APNs) bilgileri
    APNS_TEAM_ID = os.getenv('ONESIGNAL_APNS_TEAM_ID', '435XR8VR9X')
    APNS_BUNDLE_ID = os.getenv('ONESIGNAL_APNS_BUNDLE_ID', 'com.helmex')
    APNS_AUTH_TYPE = os.getenv('ONESIGNAL_APNS_AUTH_TYPE', 'p8')  # p8 Auth Key
    
    @classmethod
    def is_configured(cls):
        """OneSignal yapılandırılmış mı kontrol et"""
        return (
            cls.APP_ID != 'YOUR_ONESIGNAL_APP_ID' and 
            cls.API_KEY != 'YOUR_ONESIGNAL_API_KEY' and
            cls.APP_ID and 
            cls.API_KEY
        )
    
    @classmethod
    def get_apns_config(cls):
        """APNs konfigürasyon bilgilerini getir"""
        return {
            'team_id': cls.APNS_TEAM_ID,
            'bundle_id': cls.APNS_BUNDLE_ID,
            'auth_type': cls.APNS_AUTH_TYPE
        }
    
    @classmethod
    def is_apns_configured(cls):
        """APNs yapılandırılmış mı kontrol et"""
        return (
            cls.APNS_TEAM_ID != '' and
            cls.APNS_BUNDLE_ID != '' and
            cls.APNS_TEAM_ID and
            cls.APNS_BUNDLE_ID
        )
    
    @classmethod
    def get_config_dict(cls):
        """OneSignal yapılandırmasını dictionary olarak döndür"""
        return {
            'app_id': cls.APP_ID,
            'rest_api_key': cls.API_KEY,
            'user_auth_key': cls.USER_AUTH_KEY,
            'safari_web_id': cls.SAFARI_WEB_ID
        }