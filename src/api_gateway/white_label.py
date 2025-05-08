from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import HTTPException
import json
import os

class WhiteLabelConfig(BaseModel):
    company_name: str
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]
    custom_domain: Optional[str]
    email_template: Optional[str]
    contact_email: str

class WhiteLabelManager:
    def __init__(self):
        self.config_dir = "configs/white_label"
        os.makedirs(self.config_dir, exist_ok=True)

    async def create_config(self, user_id: str, config: WhiteLabelConfig) -> Dict:
        """Create or update white label configuration"""
        try:
            config_path = self._get_config_path(user_id)
            with open(config_path, 'w') as f:
                json.dump(config.dict(), f)
            return {"status": "success", "config": config}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")

    async def get_config(self, user_id: str) -> Optional[WhiteLabelConfig]:
        """Get white label configuration for user"""
        try:
            config_path = self._get_config_path(user_id)
            if not os.path.exists(config_path):
                return None
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return WhiteLabelConfig(**config_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load configuration: {str(e)}")

    async def update_config(self, user_id: str, updates: Dict) -> Dict:
        """Update specific fields in white label configuration"""
        try:
            current_config = await self.get_config(user_id)
            if not current_config:
                raise HTTPException(status_code=404, detail="Configuration not found")

            # Update only provided fields
            updated_config = current_config.copy(update=updates)
            return await self.create_config(user_id, updated_config)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")

    async def delete_config(self, user_id: str) -> Dict:
        """Delete white label configuration"""
        try:
            config_path = self._get_config_path(user_id)
            if os.path.exists(config_path):
                os.remove(config_path)
            return {"status": "success", "message": "Configuration deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete configuration: {str(e)}")

    def _get_config_path(self, user_id: str) -> str:
        """Get path to configuration file"""
        return os.path.join(self.config_dir, f"{user_id}_config.json")

    async def apply_white_label(self, user_id: str, content: Dict) -> Dict:
        """Apply white label configuration to content"""
        config = await self.get_config(user_id)
        if not config:
            return content

        # Apply branding to content
        if isinstance(content, dict):
            if "branding" not in content:
                content["branding"] = {}
            content["branding"].update({
                "company_name": config.company_name,
                "logo_url": config.logo_url,
                "primary_color": config.primary_color,
                "secondary_color": config.secondary_color
            })

            # Apply custom domain if available
            if config.custom_domain:
                content["domain"] = config.custom_domain

            # Apply email template if available
            if "email_content" in content and config.email_template:
                content["email_content"] = self._apply_email_template(
                    content["email_content"],
                    config.email_template
                )

        return content

    def _apply_email_template(self, content: str, template: str) -> str:
        """Apply email template to content"""
        # Replace template placeholders with actual content
        return template.replace("{{content}}", content)
