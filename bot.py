# bot_wad_render.py - نسخة معدلة للاستضافة على Render
import os
import sys
import time
import re
import logging
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError, 
    FloodWaitError,
    RPCError
)
import socket  # للتعامل مع أخطاء الاتصال العامة

# ========== إعداد التسجيل للأخطاء ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ========== بياناتك (من متغيرات البيئة على Render) ==========
api_id = int(os.environ.get('API_ID', 33523429))
api_hash = os.environ.get('API_HASH', "b293c850e6e916d7a840ac6a5ac0ad09")
session_name = os.environ.get('SESSION_NAME', "ahmed_fixed")
GROUP_ID = int(os.environ.get('GROUP_ID', -1003270915951))

# إعدادات التوقيت (بالثواني)
WAIT_AFTER_COMMANDS = 5
CYCLE_WAIT_MINUTES = 11
MAX_RETRIES = 3

class WadBot:
    def __init__(self):
        self.client = None
        self.cycle_count = 1
        self.is_connected = False
        
    def connect(self):
        """إنشاء اتصال بالتليجرام"""
        try:
            logger.info("🔗 جاري الاتصال بالتليجرام...")
            
            # تأكد من وجود ملف الجلسة
            session_file = f"{session_name}.session"
            if not os.path.exists(session_file):
                logger.warning(f"⚠️  ملف الجلسة {session_file} غير موجود!")
                logger.info("🆕 سيتم إنشاء جلسة جديدة...")
            
            self.client = TelegramClient(session_name, api_id, api_hash)
            self.client.start()
            
            me = self.client.get_me()
            logger.info(f"✅ تم الاتصال بنجاح! الحساب: {me.first_name} (@{me.username})")
            self.is_connected = True
            return True
            
        except SessionPasswordNeededError:
            logger.error("🔐 مطلوب كود التحقق بخطوتين! قم بتشغيل البوت محلياً أولاً.")
            return False
        except Exception as e:
            logger.error(f"❌ فشل الاتصال: {e}")
            return False
    
    def disconnect(self):
        """قطع الاتصال"""
        if self.client:
            self.client.disconnect()
            self.is_connected = False
            logger.info("📴 تم قطع الاتصال")
    
    def send_commands(self):
        """إرسال الأوامر الثلاثة"""
        commands = ["بخشيش", "راتب", "فلوسي"]
        
        for i, cmd in enumerate(commands, 1):
            try:
                logger.info(f"📤 [{i}/3] جاري إرسال: {cmd}")
                self.client.send_message(GROUP_ID, cmd)
                
                if i < len(commands):  # لا تنتظر بعد الأمر الأخير
                    time.sleep(2)
                    
            except FloodWaitError as e:
                logger.warning(f"⏳ انتظار {e.seconds} ثانية بسبب FloodWait...")
                time.sleep(e.seconds)
                continue
            except Exception as e:
                logger.error(f"❌ خطأ في إرسال {cmd}: {e}")
                return False
        
        logger.info("✅ تم إرسال جميع الأوامر")
        return True
    
    def get_last_wad_response(self):
        """الحصول على آخر رد من بوت وعد"""
        try:
            # احصل على آخر 10 رسائل للبحث
            messages = self.client.get_messages(GROUP_ID, limit=10)
            
            # ابحث عن أحدث رسالة من بوت وعد تحتوي على فلوسك
            for msg in messages:
                if not msg.text:
                    continue
                    
                text = msg.text
                
                # تحقق إذا كانت هذه رسالة فلوس من بوت وعد
                if any(keyword in text for keyword in ["فلوسك", "فلوس", "ريال", "ر.س"]):
                    logger.info(f"🎯 وجدت رد بوت وعد: {text[:50]}...")
                    return text
            
            logger.warning("⚠️  لم أجد أي رد من بوت وعد")
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في قراءة الرسائل: {e}")
            return None
    
    def extract_money(self, text):
        """استخراج المبلغ من نص الرد"""
        if not text:
            return 0
        
        patterns = [
            r'فلوسك.*?(\d[\d,]*) ريال',
            r'(\d[\d,]*) ريال.*?فلوسك',
            r'(\d[\d,]*)\s*ريال',
            r'(\d+)\s*ر\.س',
            r'`(\d+)`',
            r'(\d+)\s*ر?ي?ال?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                money_str = match.group(1).replace(',', '').replace(' ', '').replace('`', '')
                try:
                    return int(money_str)
                except ValueError:
                    continue
        
        return 0
    
    def invest_money(self, amount):
        """إرسال أمر الاستثمار"""
        if amount <= 0:
            logger.warning("⚠️  لا يمكن الاستثمار بمبلغ صفري")
            return False
        
        try:
            logger.info(f"💼 جاري الاستثمار: {amount:,} ريال")
            self.client.send_message(GROUP_ID, f"استثمار {amount}")
            logger.info(f"✅ تم الاستثمار بنجاح: {amount:,} ريال")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في الاستثمار: {e}")
            return False
    
    def wait_minutes(self, minutes):
        """انتظار بالعد التنازلي"""
        total_seconds = minutes * 60
        
        for remaining in range(total_seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            
            # تحديث كل 30 ثانية فقط لتقليل الإخراج
            if remaining % 30 == 0 or remaining <= 5:
                logger.info(f"⏱️  انتظار: {time_str} للدورة القادمة")
            
            time.sleep(1)
        
        logger.info("🔄 الانتظار انتهى، بدء الدورة القادمة...")
    
    def run_cycle(self):
        """تشغيل دورة واحدة"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🌀 بدء الدورة رقم: {self.cycle_count}")
        logger.info(f"{'='*60}")
        
        # الخطوة 1: إرسال الأوامر
        if not self.send_commands():
            logger.error("❌ فشل إرسال الأوامر، تخطي الدورة")
            return False
        
        # الخطوة 2: انتظار الرد
        logger.info(f"⏳ انتظار {WAIT_AFTER_COMMANDS} ثواني...")
        time.sleep(WAIT_AFTER_COMMANDS)
        
        # الخطوة 3: قراءة الرد
        response = self.get_last_wad_response()
        
        # الخطوة 4: استخراج المبلغ والاستثمار
        if response:
            amount = self.extract_money(response)
            if amount > 0:
                self.invest_money(amount)
            else:
                logger.warning("⚠️  لم يتم استخراج مبلغ صالح من الرد")
        else:
            logger.warning("⚠️  لم يتم الحصول على رد للاستثمار")
        
        # زيادة العداد
        self.cycle_count += 1
        return True
    
    def run(self):
        """الدورة الرئيسية للبوت"""
        logger.info("🤖 بوت وعد - الإصدار المعدل لـ Render")
        logger.info(f"📊 إعدادات: انتظار {CYCLE_WAIT_MINUTES} دقيقة بين الدورات")
        
        retry_count = 0
        
        while True:
            try:
                # محاولة الاتصال
                if not self.is_connected:
                    if not self.connect():
                        if retry_count >= MAX_RETRIES:
                            logger.error(f"❌ فشل الاتصال بعد {MAX_RETRIES} محاولات")
                            break
                        
                        retry_count += 1
                        wait_time = retry_count * 30  # انتظار متزايد
                        logger.info(f"🔄 إعادة المحاولة {retry_count}/{MAX_RETRIES} بعد {wait_time} ثانية...")
                        time.sleep(wait_time)
                        continue
                    
                    retry_count = 0  # إعادة تعيين عداد المحاولات
                
                # تشغيل الدورة
                self.run_cycle()
                
                # انتظار حتى الدورة التالية
                self.wait_minutes(CYCLE_WAIT_MINUTES)
                
            except KeyboardInterrupt:
                logger.info("\n⏹️  تم إيقاف البوت يدوياً")
                break
            except (socket.error, TimeoutError, RPCError) as e:
                # معالجة أخطاء الاتصال العامة وأخطاء RPC
                logger.warning(f"📡 خطأ في الاتصال: {e}")
                logger.info("🔄 محاولة إعادة الاتصال...")
                self.is_connected = False
                time.sleep(10)
            except FloodWaitError as e:
                logger.warning(f"⏳ FloodWait: انتظار {e.seconds} ثانية...")
                time.sleep(e.seconds)
            except Exception as e:
                logger.error(f"❌ خطأ غير متوقع: {e}")
                logger.info("🔄 إعادة التشغيل بعد 60 ثانية...")
                time.sleep(60)

def main():
    """الدالة الرئيسية"""
    bot = WadBot()
    
    try:
        bot.run()
    except Exception as e:
        logger.error(f"💥 خطأ حرج: {e}")
    finally:
        bot.disconnect()
        logger.info("🎬 تم إنهاء البوت. شكراً لاستخدامك بوت وعد!")

if __name__ == "__main__":
    main()