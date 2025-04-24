-- File format of type JSON
CREATE OR REPLACE FILE FORMAT JSON_FORMAT type='json' strip_outer_array = true;

-- Stage for Marketplace data
CREATE OR REPLACE STAGE home_ai_db.home_ai_schema.MARKETPLACE_LISTING_STAGE file_format = JSON_FORMAT;

-- Stage for Craigslist data
CREATE OR REPLACE STAGE home_ai_db.home_ai_schema.CRAIGS_LISTING_STAGE;

-- Stage for WhatsApp data
