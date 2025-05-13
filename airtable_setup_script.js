// Market Analysis Table Setup Script
// This script will create all the necessary fields for the Market Analysis table

output.markdown("🏢 Market Analysis Table Setup");

// Get the Market Analysis table
const table = base.getTable("Market Analysis");

// Define the fields to create
const fieldsToCreate = [
    { name: "Region", type: "singleLineText" },
    { name: "Score", type: "number", options: { precision: 1 } },
    { name: "Phase", type: "singleLineText" },
    { name: "Risk", type: "singleLineText" },
    { name: "TrendScore", type: "number", options: { precision: 1 } },
    { name: "EconomicScore", type: "number", options: { precision: 1 } },
    { name: "PTRRatio", type: "number", options: { precision: 2 } },
    { name: "CapRate", type: "number", options: { precision: 2 } },
    { name: "MonthlySales", type: "number" },
    { name: "Inventory", type: "singleLineText" },
    { name: "AvgAppreciation", type: "number", options: { precision: 2 } },
    { name: "PropertyValue", type: "number" },
    { name: "MonthlyRent", type: "number" },
    { name: "AnnualIncome", type: "number" },
    { name: "Notes", type: "multilineText" }
];

// Check existing fields to avoid duplicates
const existingFields = table.fields;
const existingFieldNames = existingFields.map(field => field.name);

// Create fields that don't already exist
let createdCount = 0;
let skippedCount = 0;

async function createFields() {
    output.markdown("### Creating fields...");
    
    for (const fieldConfig of fieldsToCreate) {
        if (existingFieldNames.includes(fieldConfig.name)) {
            output.markdown(`- ⏭️ Field **${fieldConfig.name}** already exists, skipping.`);
            skippedCount++;
            continue;
        }
        
        try {
            // Create the field
            await table.createField(fieldConfig.name, fieldConfig.type, fieldConfig.options);
            output.markdown(`- ✅ Created field **${fieldConfig.name}** (${fieldConfig.type}).`);
            createdCount++;
        } catch (error) {
            output.markdown(`- ❌ Error creating field **${fieldConfig.name}**: ${error.message}`);
        }
    }
    
    output.markdown(`\n### Summary`);
    output.markdown(`- Created ${createdCount} new fields`);
    output.markdown(`- Skipped ${skippedCount} existing fields`);
    output.markdown(`- Total fields required: ${fieldsToCreate.length}`);
    
    if (createdCount + skippedCount === fieldsToCreate.length) {
        output.markdown(`\n✅ **Setup complete!** Your Market Analysis table now has all the required fields.`);
    } else {
        output.markdown(`\n⚠️ **Setup incomplete.** Some fields could not be created.`);
    }
}

// Create a sample record with all fields
async function createSampleRecord() {
    output.markdown("\n### Creating sample record...");
    
    try {
        const record = await table.createRecordAsync({
            "Region": "Atlanta",
            "Score": 78.5,
            "Phase": "Growth",
            "Risk": "Moderate",
            "TrendScore": 82.3,
            "EconomicScore": 75.6,
            "PTRRatio": 11.45,
            "CapRate": 6.8,
            "MonthlySales": 1250,
            "Inventory": "Medium",
            "AvgAppreciation": 4.2,
            "PropertyValue": 330000,
            "MonthlyRent": 2400,
            "AnnualIncome": 85000,
            "Notes": "Sample record created by setup script"
        });
        
        output.markdown(`- ✅ Created sample record with ID: ${record.id}`);
        return true;
    } catch (error) {
        output.markdown(`- ❌ Error creating sample record: ${error.message}`);
        return false;
    }
}

// Ask if the user wants to create a sample record
output.markdown("\n### Setup Options");
output.markdown("Do you want to create a sample record after setting up the fields?");

let createSample = await input.buttonsAsync(
    'Create sample record?',
    [{ label: 'Yes', value: true }, { label: 'No', value: false }]
);

// Run the setup
await createFields();

if (createSample) {
    await createSampleRecord();
}

output.markdown("\n### Next Steps");
output.markdown("1. Update your .env file with the following values:");
output.markdown("```");
output.markdown(`AIRTABLE_BASE_ID=${base.id}`);
output.markdown(`AIRTABLE_TABLE_ID=${table.id}`);
output.markdown(`USE_AIRTABLE=true`);
output.markdown("```");
output.markdown("2. Make sure your API key is also set in the .env file.");
output.markdown("3. Update your airtable_sync.py module with the field mappings.");
