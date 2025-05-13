# Airtable Manual Setup Guide

Since we're experiencing issues with the Airtable API, let's set up your Airtable structure manually through the Airtable web interface.

## Step 1: Create a New Base

1. Go to [Airtable](https://airtable.com/) and log in to your account.
2. Click on the "Add a base" button.
3. Select "Start from scratch" and name your base "Real Estate API Tracker".

## Step 2: Create the Market Analysis Table

1. Rename the default table to "Market Analysis".
2. Add the following fields to the table:

| Field Name | Field Type |
|------------|------------|
| Region | Single line text |
| Final Score | Number (precision: 1) |
| Market Phase | Single line text |
| Risk Level | Single line text |
| Trend Score | Number (precision: 1) |
| Economic Score | Number (precision: 1) |
| PTR Ratio | Number (precision: 2) |
| Cap Rate | Number (precision: 2) |
| Monthly Sales | Number |
| Inventory Level | Single line text |
| Avg Appreciation | Number (precision: 2) |
| Property Value | Number |
| Monthly Rent | Number |
| Annual Income | Number |
| Timestamp | Single line text |

## Step 3: Create the Properties Table (Optional)

1. Click the "+" button next to the table tabs to create a new table.
2. Name the table "Properties".
3. Add the following fields to the table:

| Field Name | Field Type |
|------------|------------|
| Property Name | Single line text |
| Address | Single line text |
| City | Single line text |
| State | Single line text |
| Zip Code | Single line text |
| Property Type | Single line text |
| Bedrooms | Number |
| Bathrooms | Number (precision: 1) |
| Square Feet | Number |
| Lot Size | Number (precision: 2) |
| Year Built | Number |
| Purchase Price | Number |
| Current Value | Number |
| Monthly Rent | Number |
| Cap Rate | Number (precision: 2) |
| Cash Flow | Number |
| ROI | Number (precision: 2) |
| Notes | Long text |

## Step 4: Get the Base ID and Table Name

1. Open your base in the Airtable web interface.
2. Look at the URL in your browser. It should look something like this:
   ```
   https://airtable.com/appXXXXXXXXXXXXXX/tblYYYYYYYYYYYYYY/viwZZZZZZZZZZZZZZ
   ```
3. The `appXXXXXXXXXXXXXX` part is your Base ID.
4. The table name is simply "Market Analysis" (or the name you chose).

## Step 5: Update Your .env File

After you've created your Airtable structure and obtained the Base ID, run the following command to update your .env file:

```
python update_airtable_config.py
```

When prompted, enter the Base ID and Table Name you obtained in Step 4.

## Step 6: Test the Connection

After updating your .env file, run the following command to test the connection:

```
python simple_airtable_test.py
```

If everything is set up correctly, you should see a successful connection message.
