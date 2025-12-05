# bot.py - النسخة المحسنة
import os
import time
import re
import logging
import warnings
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError

# ⬇️ إخفاء تحذيرات الرسائل القديمة
warnings.filterwarnings('ignore', message='Server sent a very old message')
logging.getLogger('telethon').setLevel(logging.ERROR)

# إعداد تسجيل مبسط
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# بيانات البوت
api_id = int(os.environ.get('API_ID', 33523429))
api_hash = os.environ.get('API_HASH', "b293c850e6e916d7a840ac6a5ac0ad09")
session_name = os.environ.get('SESSION_NAME', "ahmed_fixed")
GROUP_ID = int(os.environ.get('GROUP_ID', -1003270915951))

def main():
    """الدالة الرئيسية"""
    logger.info("🤖 بوت وعد - Background Worker Edition")
    
    try:
        # الاتصال
        client = TelegramClient(session_name, api_id, api_hash)
        client.start()
        
        me = client.get_me()
        logger.info(f"✅ متصل: {me.first_name}")
        
        # الحلقة الرئيسية
        cycle = 1
        while True:
            logger.info(f"\n🌀 الدورة {cycle}")
            
            # إرسال الأوامر
            for cmd in ["بخشيش", "راتب", "فلوسي"]:
                logger.info(f"📤 {cmd}")
                client.send_message(GROUP_ID, cmd)
                time.sleep(2)
            
            # انتظار الرد
            time.sleep(5)
            
            # قراءة الردود
            messages = client.get_messages(GROUP_ID, limit=5)
            for msg in messages:
                if msg.text and ("فلوسك" in msg.text or "ريال" in msg.text):
                    # استخراج المبلغ
                    match = re.search(r'`(\d+)`', msg.text)
                    if match:
                        amount = int(match.group(1))
                        logger.info(f"💰 المبلغ: {amount:,} ريال")
                        
                        # الاستثمار
                        logger.info(f"💼 استثمار {amount}")
                        client.send_message(GROUP_ID, f"استثمار {amount}")
                        break
            
            # الانتظار للدورة التالية
            logger.info(f"⏳ انتظار 11 دقيقة...")
            for i in range(11 * 60, 0, -30):
                if i % 60 == 0:
                    logger.info(f"   ⏱️  باقي {i//60} دقيقة")
                time.sleep(30 if i > 30 else i)
            
            cycle += 1
            
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        logger.info("🔄 إعادة التشغيل بعد 30 ثانية...")
        time.sleep(30)
        main()  # إعادة التشغيل

if __name__ == "__main__":
    # إعادة التشغيل التلقائي في حالة أي خطأ
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
        except:
            time.sleep(10)
