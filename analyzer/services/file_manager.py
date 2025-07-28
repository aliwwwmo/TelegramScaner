import json
import os
from datetime import datetime
from typing import Dict, List, Set

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
    
    def save_results_to_files(self, results: Dict):
        """ذخیره نتایج در فایل‌ها"""
        logger.info("💾 Saving results to files...")
        
        # 1. ذخیره تحلیل چت‌ها
        detailed_analysis = {
            "analysis_metadata": {
                "total_links": len(results.get('chat_analysis_results', [])),
                "analysis_date": datetime.utcnow().isoformat(),
                "link_categories": {}
            },
            "redirect_mappings": results.get('redirect_mapping', {}),
            "chats": results.get('chat_analysis_results', [])
        }
        
        # آمار دسته‌بندی لینک‌ها
        categories = {}
        for chat in results.get('chat_analysis_results', []):
            category = chat.get('link_category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        detailed_analysis["analysis_metadata"]["link_categories"] = categories
        
        with open(f"{self.config.results_dir}/chat_analysis.json", "w", encoding="utf-8") as f:
            json.dump(detailed_analysis, f, ensure_ascii=False, indent=2)
        
        # 2. ذخیره لینک‌های استخراج شده
        extracted_links = results.get('extracted_links', [])
        with open(f"{self.config.results_dir}/extracted_links.txt", "w", encoding="utf-8") as f:
            for link in sorted(extracted_links):
                f.write(f"{link}\n")
        
        # 3. ذخیره تمام لینک‌ها در فایل JSON هم
        with open(f"{self.config.results_dir}/extracted_links.json", "w", encoding="utf-8") as f:
            json.dump(list(sorted(extracted_links)), f, ensure_ascii=False, indent=2)
        
        # 4. ذخیره اطلاعات کاربران در فایل‌های JSON جداگانه
        processed_users = results.get('processed_users', {})
        for user_id, user_data in processed_users.items():
            user_filename = f"{self.config.users_dir}/user_{user_id}.json"
            
            with open(user_filename, "w", encoding="utf-8") as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        # 5. ذخیره خلاصه کلی
        summary = self._create_summary(results, categories)
        
        # 6. ذخیره خلاصه در فایل تعیین شده در .env
        with open(self.config.output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        with open(f"{self.config.results_dir}/analysis_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 7. آمار نهایی
        self._log_final_stats(summary, categories, len(processed_users), len(extracted_links))
    
    def _create_summary(self, results: Dict, categories: Dict) -> Dict:
        """ایجاد خلاصه نتایج"""
        return {
            "summary": {
                "total_chats": len(results.get('chat_analysis_results', [])),
                "total_users": len(results.get('processed_users', {})),
                "total_extracted_links": len(results.get('extracted_links', [])),
                "analysis_date": datetime.utcnow().isoformat()
            },
            "categories": categories,
            "chat_results": results.get('chat_analysis_results', []),
            "extracted_links": list(results.get('extracted_links', []))
        }
    
    def _log_final_stats(self, summary: Dict, categories: Dict, users_count: int, links_count: int):
        """نمایش آمار نهایی"""
        logger.info("📊 Final Analysis Statistics:")
        logger.info(f"   📈 Total chats analyzed: {summary['summary']['total_chats']}")
        logger.info(f"   👥 Total users found: {users_count}")
        logger.info(f"   🔗 Total links extracted: {links_count}")
        
        if categories:
            logger.info("   📋 Link Categories:")
            for category, count in categories.items():
                logger.info(f"      • {category}: {count}")
    
    def load_links_from_file(self) -> List[str]:
        """بارگذاری لینک‌ها از فایل"""
        links_file = self.config.links_file
        
        if not os.path.exists(links_file):
            logger.warning(f"⚠️ Links file not found: {links_file}")
            self._create_sample_links_file()
            return []
        
        try:
            with open(links_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # حذف خطوط خالی و کامنت‌ها
            links = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    links.append(line)
            
            logger.info(f"✅ Loaded {len(links)} links from {links_file}")
            return links
            
        except Exception as e:
            logger.error(f"❌ Error loading links from {links_file}: {e}")
            return []
    
    def _create_sample_links_file(self):
        """ایجاد فایل نمونه لینک‌ها"""
        try:
            with open(self.config.links_file, "w", encoding="utf-8") as f:
                f.write("# Add your Telegram chat links here, one per line\n")
                f.write("# Examples:\n")
                f.write("# https://t.me/example_channel\n")
                f.write("# @example_group\n")
                f.write("# +1234567890  (for private chats)\n")
            
            logger.info(f"✅ Created sample links file: {self.config.links_file}")
            
        except Exception as e:
            logger.error(f"❌ Error creating sample links file: {e}")
