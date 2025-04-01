# Google Sheets Setup Guide

## Required Sheets

1. **Market Data Sheet**
   - Sheet Name: `MarketData`
   - Columns:
     - zip_code
     - median_price
     - price_trend
     - days_on_market
     - inventory_level
     - sales_velocity
     - price_per_sqft
     - distress_ratio
     - overall_score
     - last_updated

2. **Property Data Sheet**
   - Sheet Name: `PropertyData`
   - Columns:
     - property_id
     - zip_code
     - address
     - price
     - bedrooms
     - bathrooms
     - square_feet
     - year_built
     - property_type
     - last_sold_date
     - last_sold_price
     - estimated_arv
     - source (ATTOM/Mock)

3. **Config Sheet**
   - Sheet Name: `Config`
   - Tabs:
     - MarketConfig
       - market_type
       - price_change_threshold
       - days_on_market_threshold
       - inventory_threshold
     - DealConfig
       - deal_type
       - min_profit_margin
       - max_repair_cost_ratio
       - min_cash_flow

4. **Usage Log Sheet**
   - Sheet Name: `UsageLog`
   - Columns:
     - timestamp
     - calls_today
     - calls_this_month
     - remaining_calls
     - estimated_cost

5. **Alerts Sheet**
   - Sheet Name: `Alerts`
   - Columns:
     - timestamp
     - alert_count
     - alert_messages

## Setup Instructions

1. Create a new Google Cloud Project
   - Go to https://console.cloud.google.com
   - Create a new project
   - Enable Google Sheets API

2. Create Service Account
   - Go to IAM & Admin > Service Accounts
   - Create new service account
   - Download JSON credentials
   - Save as `credentials/sheets_cred.json`

3. Create Sheets
   - Create 5 separate Google Sheets
   - Share each with the service account email
   - Copy sheet IDs from URLs
   - Update `sheet_ids.json`

4. Configure Sheets
   - Add column headers as specified above
   - Set up data validation where needed
   - Add example data for testing
