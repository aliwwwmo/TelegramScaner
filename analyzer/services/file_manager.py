import json
import os
from datetime import datetime
from typing import Dict, List, Set

from models.data_models import ChatAnalysisResult, UserData, AnalysisResults
from config.settings import AnalysisConfig
from utils.logger import logger

class FileManager:
    """کلاس مدیریت فایل‌ها"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self._create_directories()
    
    def _create_directories(self):
        """ایجاد دایرکتوری‌های مورد نیاز"""
        os.makedirs(self.config.results_dir, exist_ok=True)
        os.makedirs(self.config.users_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def save_results_to_files(self, results: AnalysisResults):
        """ذخیره نتایج در فایل‌ها"""
        logger.info("💾 Saving results to files...")
        
        # 1. ذخیره تحلیل چت‌ها با جزئیات بیشتر
        detailed_analysis = {
            "analysis_metadata": {
                "total_links": len(results.chat_analysis_results),
                "analysis_date": results.analysis_date,
                "link_categories": {}
            },
            "redirect_mappings": results.redirect_mapping,
            "chats": [self._chat_result_to_dict(chat) for chat in results.chat_analysis_results]
        }
        
        # آمار دسته‌بندی لینک‌ها
        categories = {}
        for chat in results.chat_analysis_results:
            category = chat.link_category or "unknown"
            categories[category] = categories.get(category, 0) + 1
        
        detailed_analysis["analysis_metadata"]["link_categories"] = categories
        
        with open(f"{self.config.results_dir}/chat_analysis.json", "w", encoding="utf-8") as f:
            json.dump(detailed_analysis, f, ensure_ascii=False, indent=2)
        
        # 2. ذخیره لینک‌های استخراج شده
        with open(f"{self.config.results_dir}/extracted_links.txt", "w", encoding="utf-8") as f:
            for link in sorted(results.extracted_links):
                f.write(f"{link}\n")
        
        # 3. ذخیره تمام لینک‌ها در فایل JSON هم
        with open(f"{self.config.results_dir}/extracted_links.json", "w", encoding="utf-8") as f:
            json.dump(list(sorted(results.extracted_links)), f, ensure_ascii=False, indent=2)
        
        # 4. ذخیره اطلاعات کاربران در فایل‌های JSON جداگانه
        for user_id, user_data in results.processed_users.items():
            user_filename = f"{self.config.users_dir}/user_{user_id}.json"
            
            with open(user_filename, "w", encoding="utf-8") as f:
                json.dump(self._user_data_to_dict(user_data), f, ensure_ascii=False, indent=2)
        
        # 5. ذخیره خلاصه کلی
        summary = self._create_summary(results, categories)
        
        # 6. ذخیره خلاصه در فایل تعیین شده در .env
        with open(self.config.output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        with open(f"{self.config.results_dir}/analysis_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 7. آمار نهایی
        self._log_final_stats(summary, categories, len(results.processed_users), len(results.extracted_links))
    
    def _chat_result_to_dict(self, chat: ChatAnalysisResult) -> Dict:
        """تبدیل ChatAnalysisResult به dictionary"""
        return {
            "link": chat.link,
            "type": chat.type,
            "status": chat.status,
            "title": chat.title,
            "username": chat.username,
            "members_count": chat.members_count,
            "chat_id": chat.chat_id,
            "error": chat.error,
            "link_category": chat.link_category,
            "is_channel": chat.is_channel,
            "is_group": chat.is_group,
            "is_public": chat.is_public,
            "is_redirect": chat.is_redirect,
            "redirect_source": chat.redirect_source,
            "invite_hash": chat.invite_hash,
            "can_join": chat.can_join
        }
    
    def _user_data_to_dict(self, user: UserData) -> Dict:
        """تبدیل UserData به dictionary"""
        return {
            "user_id": user.user_id,
            "current_username": user.current_username,
            "current_name": user.current_name,
            "username_history": user.username_history,
            "name_history": user.name_history,
            "is_bot": user.is_bot,
            "is_deleted": user.is_deleted,
            "joined_groups": [
                {
                    "group_id": group.group_id,
                    "group_title": group.group_title,
                    "joined_at": group.joined_at,
                    "role": group.role,
                    "is_admin": group.is_admin
                } for group in user.joined_groups
            ],
            "messages": [
                {
                    "group_id": msg.group_id,
                    "message_id": msg.message_id,
                    "text": msg.text,
                    "timestamp": msg.timestamp,
                    "reactions": msg.reactions,
                    "reply_to": msg.reply_to,
                    "edited": msg.edited,
                    "is_forwarded": msg.is_forwarded
                } for msg in user.messages
            ]
        }
    
    def _create_summary(self, results: AnalysisResults, categories: Dict) -> Dict:
        """ایجاد خلاصه نتایج"""
        summary = {
            "analysis_info": {
                "total_chats_analyzed": len(results.chat_analysis_results),
                "accessible_chats": len([c for c in results.chat_analysis_results if c.status in ["public", "accessible"]]),
                "private_chats": len([c for c in results.chat_analysis_results if c.status == "private"]),
                "invalid_chats": len([c for c in results.chat_analysis_results if c.status == "invalid"]),
                "expired_invites": len([c for c in results.chat_analysis_results if c.status == "expired"]),
                "redirect_links": len([c for c in results.chat_analysis_results if c.is_redirect]),
                "total_users": len(results.processed_users),
                "total_extracted_links": len(results.extracted_links),
                "analysis_date": results.analysis_date
            },
            "chat_types": {
                "channels": len([c for c in results.chat_analysis_results if c.is_channel]),
                "groups": len([c for c in results.chat_analysis_results if c.is_group]),
                "invite_links": len([c for c in results.chat_analysis_results if c.link_category == "invite_link"]),
                "public_links": len([c for c in results.chat_analysis_results if c.link_category == "public_link"]),
                "public_chats": len([c for c in results.chat_analysis_results if c.is_public]),
                "unknown": len([c for c in results.chat_analysis_results if c.type == "unknown"])
            },
            "link_categories": categories,
            "user_statistics": {}
        }
        
        # آمار کاربران
        for user_id, user_data in results.processed_users.items():
            summary["user_statistics"][str(user_id)] = {
                "username": user_data.current_username,
                "name": user_data.current_name,
                "total_messages": len(user_data.messages),
                "joined_groups_count": len(user_data.joined_groups),
                "is_bot": user_data.is_bot
            }
        
        return summary
    
    def _log_final_stats(self, summary: Dict, categories: Dict, users_count: int, links_count: int):
        """نمایش آمار نهایی"""
        logger.info("📊 Analysis Results:")
        logger.info(f"   • Total links: {summary['analysis_info']['total_chats_analyzed']}")
        logger.info(f"   • Accessible chats: {summary['analysis_info']['accessible_chats']}")
        logger.info(f"   • Private chats: {summary['analysis_info']['private_chats']}")
        logger.info(f"   • Invalid/expired: {summary['analysis_info']['invalid_chats'] + summary['analysis_info']['expired_invites']}")
        logger.info(f"   • Redirect links resolved: {summary['analysis_info']['redirect_links']}")
        logger.info(f"   • Total users: {users_count}")
        logger.info(f"   • Extracted links: {links_count}")
        
        # آمار دسته‌بندی
        logger.info("📋 Link Categories:")
        for category, count in categories.items():
            logger.info(f"   • {category}: {count}")
    
    def load_links_from_file(self) -> List[str]:
        """بارگذاری لینک‌ها از فایل"""
        if not os.path.exists(self.config.links_file):
            logger.error(f"❌ Links file not found: {self.config.links_file}")
            self._create_sample_links_file()
            return []
        
        chat_links = []
        try:
            with open(self.config.links_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        chat_links.append(line)
            
            if not chat_links:
                logger.error("❌ No valid links found in links.txt")
                return []
                
            logger.info(f"📋 Loaded {len(chat_links)} links from {self.config.links_file}")
            return chat_links
            
        except Exception as e:
            logger.error(f"❌ Error reading links file: {e}")
            return []
    
    def _create_sample_links_file(self):
        """ایجاد فایل نمونه لینک‌ها"""
        print(f"Creating sample {self.config.links_file} file...")
        with open(self.config.links_file, 'w', encoding='utf-8') as f:
            f.write("# Add your Telegram links here, one per line\n")
            f.write("# Examples:\n")
            f.write("# https://t.me/joinchat/abc123\n")
            f.write("# https://t.me/channelname\n")
            f.write("# @username\n")
        print(f"✅ Created {self.config.links_file}. Please add your links and run again.")
