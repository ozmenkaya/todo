"""
OneSignal Notification Service
Görev bildirimlerini OneSignal aracılığıyla gönderir.
"""

import requests
import json
from typing import List, Optional, Dict, Any
from onesignal_config import OneSignalConfig
import logging

logger = logging.getLogger(__name__)

class OneSignalService:
    """OneSignal bildiri servisi"""
    
    def __init__(self):
        self.is_enabled = OneSignalConfig.is_configured()
        self.base_url = "https://onesignal.com/api/v1"
        
        if self.is_enabled:
            logger.info("OneSignal service initialized successfully")
        else:
            logger.warning("OneSignal not configured - notifications disabled")
    
    def send_notification(
        self,
        title: str,
        message: str,
        user_ids: Optional[List[str]] = None,
        external_user_ids: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None,
        icon: Optional[str] = None
    ) -> bool:
        """
        Bildirim gönder
        
        Args:
            title: Bildiri başlığı
            message: Bildiri mesajı  
            user_ids: OneSignal player ID'leri
            external_user_ids: Harici kullanıcı ID'leri (uygulamamızdaki user.id)
            data: Ek veri
            url: Tıklandığında açılacak URL
            icon: Bildirim ikonu URL'i
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.is_enabled:
            logger.warning("OneSignal not enabled - notification not sent")
            return False
            
        try:
            # Headers
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Basic {OneSignalConfig.API_KEY}"
            }
            
            # Bildirim payload'ı
            payload = {
                "app_id": OneSignalConfig.APP_ID,
                "contents": {"en": message, "tr": message},
                "headings": {"en": title, "tr": title}
            }
            
            # Hedef kullanıcıları belirle
            if user_ids:
                payload["include_player_ids"] = user_ids
            elif external_user_ids:
                payload["include_external_user_ids"] = external_user_ids
            else:
                # Tüm kullanıcılara gönder
                payload["included_segments"] = ["All"]
            
            # Ek parametreler
            if data:
                payload["data"] = data
                
            if url:
                payload["url"] = url
                
            if icon:
                payload["chrome_icon"] = icon
                payload["firefox_icon"] = icon
                
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}/notifications",
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("id"):
                    logger.info(f"Notification sent successfully: {result['id']}")
                    return True
                else:
                    logger.error(f"Notification sending failed: {result}")
                    return False
            else:
                error_msg = f"OneSignal API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                # API key hatası için özel mesaj
                if response.status_code == 403:
                    logger.error("🔑 OneSignal API Key hatası! Lütfen REST API Key'inizi kontrol edin.")
                    logger.error("💡 OneSignal Dashboard → Settings → Keys & IDs → REST API Key")
                    
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

# Global OneSignal service instance
onesignal_service = OneSignalService()

# Convenience functions
def send_task_notification(task_title: str, message: str, user_ids: List[int], task_id: Optional[int] = None) -> bool:
    """Görev bildirimi gönder - sadece ayarları etkin olan kullanıcılara"""
    from models import User
    
    # Sadece task assignment notifications etkin olan kullanıcıları filtrele
    eligible_users = User.query.filter(
        User.id.in_(user_ids),
        User.push_notifications_enabled == True,
        User.task_assignment_notifications == True
    ).all()
    
    if not eligible_users:
        return False
    
    eligible_ids = [user.id for user in eligible_users]
    
    data = {'type': 'task'}
    url = None
    
    if task_id:
        data['task_id'] = str(task_id)
        # Task detay sayfasının URL'ini oluştur (Flask context'te olduğumuzu varsayıyoruz)
        try:
            from flask import url_for, request
            if request:
                url = request.url_root.rstrip('/') + url_for('task_detail', task_id=task_id)
        except:
            pass
    
    return onesignal_service.send_notification(
        title=f"📋 {task_title}",
        message=message,
        external_user_ids=[str(uid) for uid in eligible_ids],
        data=data,
        url=url,
        icon="/static/icons/icon-192x192.png"
    )

def send_reminder_notification(reminder_title: str, message: str, user_ids: List[int]) -> bool:
    """Anımsatıcı bildirimi gönder - sadece ayarları etkin olan kullanıcılara"""
    from models import User
    
    # Sadece reminder notifications etkin olan kullanıcıları filtrele
    eligible_users = User.query.filter(
        User.id.in_(user_ids),
        User.push_notifications_enabled == True,
        User.reminder_notifications == True
    ).all()
    
    if not eligible_users:
        return False
    
    eligible_ids = [user.id for user in eligible_users]
    
    return onesignal_service.send_notification(
        title=f"⏰ {reminder_title}",
        message=message,
        external_user_ids=[str(uid) for uid in eligible_ids],
        data={'type': 'reminder'},
        icon="/static/icons/icon-192x192.png"
    )

def send_report_notification(report_title: str, message: str, user_ids: List[int], report_id: Optional[int] = None) -> bool:
    """Rapor bildirimi gönder - sadece ayarları etkin olan kullanıcılara"""
    from models import User
    
    # Sadece report notifications etkin olan kullanıcıları filtrele
    eligible_users = User.query.filter(
        User.id.in_(user_ids),
        User.push_notifications_enabled == True,
        User.report_notifications == True
    ).all()
    
    if not eligible_users:
        return False
    
    eligible_ids = [user.id for user in eligible_users]
    
    data = {'type': 'report'}
    url = None
    
    if report_id:
        data['report_id'] = str(report_id)
        try:
            from flask import url_for, request
            if request:
                url = request.url_root.rstrip('/') + url_for('report_detail', report_id=report_id)
        except:
            pass
    
    return onesignal_service.send_notification(
        title=f"📊 {report_title}",
        message=message,
        external_user_ids=[str(uid) for uid in eligible_ids],
        data=data,
        url=url,
        icon="/static/icons/icon-192x192.png"
    )

def send_task_completion_notification(task_title: str, message: str, user_ids: List[int], task_id: Optional[int] = None) -> bool:
    """Görev tamamlanma bildirimi gönder - sadece ayarları etkin olan kullanıcılara"""
    from models import User
    
    # Sadece task completion notifications etkin olan kullanıcıları filtrele
    eligible_users = User.query.filter(
        User.id.in_(user_ids),
        User.push_notifications_enabled == True,
        User.task_completion_notifications == True
    ).all()
    
    if not eligible_users:
        return False
    
    eligible_ids = [user.id for user in eligible_users]
    
    data = {'type': 'task_completion'}
    url = None
    
    if task_id:
        data['task_id'] = str(task_id)
        try:
            from flask import url_for, request
            if request:
                url = request.url_root.rstrip('/') + url_for('task_detail', task_id=task_id)
        except:
            pass
    
    return onesignal_service.send_notification(
        title=f"✅ {task_title}",
        message=message,
        external_user_ids=[str(uid) for uid in eligible_ids],
        data=data,
        url=url,
        icon="/static/icons/icon-192x192.png"
    )