from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import stripe
import os

class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionPlan(BaseModel):
    tier: SubscriptionTier
    price_id: str
    calls_per_hour: int
    features: Dict[str, bool]

class SubscriptionManager:
    def __init__(self):
        self.stripe = stripe.Stripe(os.getenv('STRIPE_SECRET_KEY'))
        self.plans = {
            SubscriptionTier.BASIC: SubscriptionPlan(
                tier=SubscriptionTier.BASIC,
                price_id="price_basic",
                calls_per_hour=100,
                features={
                    "property_search": True,
                    "market_analysis": True,
                    "lead_scoring": False,
                    "custom_reports": False,
                    "white_label": False
                }
            ),
            SubscriptionTier.PRO: SubscriptionPlan(
                tier=SubscriptionTier.PRO,
                price_id="price_pro",
                calls_per_hour=500,
                features={
                    "property_search": True,
                    "market_analysis": True,
                    "lead_scoring": True,
                    "custom_reports": True,
                    "white_label": False
                }
            ),
            SubscriptionTier.ENTERPRISE: SubscriptionPlan(
                tier=SubscriptionTier.ENTERPRISE,
                price_id="price_enterprise",
                calls_per_hour=2000,
                features={
                    "property_search": True,
                    "market_analysis": True,
                    "lead_scoring": True,
                    "custom_reports": True,
                    "white_label": True
                }
            )
        }

    async def create_subscription(self, user_id: str, tier: SubscriptionTier):
        """Create a new subscription for a user"""
        try:
            # Create Stripe customer if not exists
            customer = await self._get_or_create_customer(user_id)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": self.plans[tier].price_id}],
                expand=["latest_invoice.payment_intent"]
            )
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create subscription: {str(e)}")

    async def update_subscription(self, user_id: str, new_tier: SubscriptionTier):
        """Update an existing subscription"""
        try:
            subscription = await self._get_active_subscription(user_id)
            if not subscription:
                raise Exception("No active subscription found")

            # Update subscription
            updated_subscription = stripe.Subscription.modify(
                subscription.id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": self.plans[new_tier].price_id
                }]
            )
            
            return {"subscription_id": updated_subscription.id}
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to update subscription: {str(e)}")

    async def cancel_subscription(self, user_id: str):
        """Cancel a subscription"""
        try:
            subscription = await self._get_active_subscription(user_id)
            if not subscription:
                raise Exception("No active subscription found")

            cancelled_subscription = stripe.Subscription.delete(subscription.id)
            return {"status": "cancelled", "subscription_id": cancelled_subscription.id}
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")

    async def get_subscription_status(self, user_id: str) -> Dict:
        """Get current subscription status and features"""
        subscription = await self._get_active_subscription(user_id)
        if not subscription:
            return {"status": "inactive"}

        tier = self._get_tier_from_price_id(subscription.plan.id)
        return {
            "status": "active",
            "tier": tier,
            "features": self.plans[tier].features,
            "calls_per_hour": self.plans[tier].calls_per_hour,
            "current_period_end": datetime.fromtimestamp(subscription.current_period_end)
        }

    async def _get_or_create_customer(self, user_id: str):
        """Get existing Stripe customer or create new one"""
        # TODO: Implement customer lookup in database
        return stripe.Customer.create(metadata={"user_id": user_id})

    async def _get_active_subscription(self, user_id: str):
        """Get active subscription for user"""
        customer = await self._get_or_create_customer(user_id)
        subscriptions = stripe.Subscription.list(
            customer=customer.id,
            status="active",
            limit=1
        )
        return subscriptions.data[0] if subscriptions.data else None

    def _get_tier_from_price_id(self, price_id: str) -> SubscriptionTier:
        """Convert Stripe price ID to subscription tier"""
        for tier, plan in self.plans.items():
            if plan.price_id == price_id:
                return tier
        raise Exception("Invalid price ID")
