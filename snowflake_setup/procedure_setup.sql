-- Procedure to create embeddings for listings
CREATE OR REPLACE PROCEDURE HOME_AI_DB.HOME_AI_SCHEMA.CREATE_LISTING_EMBEDDINGS()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    execution_time_seconds FLOAT;
    updated_count INTEGER;
    newly_updated_count INTEGER;
    success_message STRING;
BEGIN
    -- Capture start time
    start_time := CURRENT_TIMESTAMP();
    
    -- Update logic
    UPDATE HOME_AI_DB.HOME_AI_SCHEMA.ROOMS_LISTINGS
    SET LISTING_VEC = SNOWFLAKE.CORTEX.EMBED_TEXT_1024(
            'nv-embed-qa-4',
            CONCAT_WS(' ', 
                'Location: ' || COALESCE(LOCATION, ''),
                'Room count: ' || COALESCE(TO_VARCHAR(ROOM_COUNT), ''), 
                'Bath count: ' || COALESCE(TO_VARCHAR(BATH_COUNT), ''),
                'People count: ' || COALESCE(TO_VARCHAR(PEOPLE_COUNT), ''),
                'Description: ' || COALESCE(DESCRIPTION_SUMMARY, ''),
                'Laundry available: ' || COALESCE(LAUNDRY_AVAILABLE, ''),
                'Room type: ' || COALESCE(ROOM_TYPE, ''),
                'Other details: ' || COALESCE(REGEXP_REPLACE(OTHER_DETAILS, '[{}\"]', ''), '')
            )
    )
    WHERE LISTING_VEC IS NULL;
    
    -- Calculate execution time
    end_time := CURRENT_TIMESTAMP();
    execution_time_seconds := TIMESTAMPDIFF(SECOND, start_time, end_time);
    
    -- Get total row counts with vectors
    SELECT COUNT(*) INTO updated_count 
    FROM HOME_AI_DB.HOME_AI_SCHEMA.ROOMS_LISTINGS
    WHERE LISTING_VEC IS NOT NULL;
    
    -- Get newly generated vector row count
    SELECT COUNT(*) INTO newly_updated_count 
    FROM HOME_AI_DB.HOME_AI_SCHEMA.ROOMS_LISTINGS 
    WHERE LISTING_VEC IS NOT NULL 
    AND LISTING_DATE >= CURRENT_DATE;
    
    -- Create success message
    success_message := 'SUCCESS: Vector embeddings updated successfully. Newly processed rows: ' || 
                      newly_updated_count || '. Total rows with embeddings: ' || updated_count || 
                      '. Execution time: ' || execution_time_seconds || ' seconds.';
    
    -- Log the success
    INSERT INTO HOME_AI_DB.HOME_AI_SCHEMA.EMBEDDING_TASK_LOG (TYPE, STATUS_MESSAGE)
    VALUES ('Success', :success_message);
  
    RETURN 'Success';
    
EXCEPTION
    WHEN OTHER THEN
        LET LINE := SQLCODE || ': ' || SQLERRM;
        
        -- Log the error using SQLCODE and SQLERRM
        INSERT INTO HOME_AI_DB.HOME_AI_SCHEMA.EMBEDDING_TASK_LOG (TYPE, STATUS_MESSAGE)
        VALUES ('Error: ', :LINE);

        RETURN 'Error';
END;
$$;