-- Migration: Add proctoring events table for AI-based monitoring
-- This table logs all suspicious activities detected during tests

CREATE TABLE IF NOT EXISTS proctoring_events (
    id SERIAL PRIMARY KEY,
    user_test_id INTEGER NOT NULL REFERENCES user_specialization_tests(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    -- Event types:
    -- 'no_face_detected' - Face disappeared from camera
    -- 'multiple_faces' - More than one person detected
    -- 'looking_away' - Eye gaze not on screen
    -- 'tab_switched' - User switched browser tab
    -- 'window_blur' - Browser window lost focus
    -- 'copy_attempt' - Attempted to copy text
    -- 'paste_attempt' - Attempted to paste text
    -- 'context_menu' - Right-click detected
    -- 'new_tab_blocked' - Attempted to open new tab with Ctrl+T
    -- 'close_tab_blocked' - Attempted to close tab with Ctrl+W
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    -- Severity levels: 'low', 'medium', 'high', 'critical'
    details JSONB,
    -- Additional details about the event (e.g., duration, confidence score)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id),
    notes TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_proctoring_events_user_test ON proctoring_events(user_test_id);
CREATE INDEX IF NOT EXISTS idx_proctoring_events_user ON proctoring_events(user_id);
CREATE INDEX IF NOT EXISTS idx_proctoring_events_type ON proctoring_events(event_type);
CREATE INDEX IF NOT EXISTS idx_proctoring_events_severity ON proctoring_events(severity);
CREATE INDEX IF NOT EXISTS idx_proctoring_events_created ON proctoring_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_proctoring_events_unresolved ON proctoring_events(resolved) WHERE resolved = FALSE;

-- Add proctoring summary to user_specialization_tests
ALTER TABLE user_specialization_tests
ADD COLUMN IF NOT EXISTS proctoring_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS suspicious_events_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS proctoring_risk_level VARCHAR(20) DEFAULT 'low';
-- Risk levels: 'low', 'medium', 'high', 'critical'

-- Create a view for proctoring summary
CREATE OR REPLACE VIEW proctoring_summary AS
SELECT
    ust.id as test_id,
    ust.user_id,
    u.name,
    u.surname,
    s.name as specialization,
    COUNT(pe.id) as total_events,
    COUNT(CASE WHEN pe.severity = 'critical' THEN 1 END) as critical_events,
    COUNT(CASE WHEN pe.severity = 'high' THEN 1 END) as high_events,
    COUNT(CASE WHEN pe.severity = 'medium' THEN 1 END) as medium_events,
    COUNT(CASE WHEN pe.severity = 'low' THEN 1 END) as low_events,
    COUNT(CASE WHEN pe.event_type = 'no_face_detected' THEN 1 END) as no_face_count,
    COUNT(CASE WHEN pe.event_type = 'multiple_faces' THEN 1 END) as multiple_faces_count,
    COUNT(CASE WHEN pe.event_type = 'looking_away' THEN 1 END) as looking_away_count,
    COUNT(CASE WHEN pe.event_type = 'tab_switched' THEN 1 END) as tab_switched_count,
    ust.proctoring_risk_level,
    ust.completed_at
FROM user_specialization_tests ust
JOIN users u ON ust.user_id = u.id
JOIN specializations s ON ust.specialization_id = s.id
LEFT JOIN proctoring_events pe ON pe.user_test_id = ust.id
WHERE ust.proctoring_enabled = TRUE
GROUP BY ust.id, ust.user_id, u.name, u.surname, s.name, ust.proctoring_risk_level, ust.completed_at;

-- Function to update suspicious events count
CREATE OR REPLACE FUNCTION update_suspicious_events_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_specialization_tests
    SET suspicious_events_count = (
        SELECT COUNT(*) FROM proctoring_events
        WHERE user_test_id = NEW.user_test_id
    ),
    proctoring_risk_level = CASE
        WHEN (SELECT COUNT(*) FROM proctoring_events WHERE user_test_id = NEW.user_test_id AND severity IN ('critical', 'high')) >= 10 THEN 'critical'
        WHEN (SELECT COUNT(*) FROM proctoring_events WHERE user_test_id = NEW.user_test_id AND severity IN ('critical', 'high')) >= 5 THEN 'high'
        WHEN (SELECT COUNT(*) FROM proctoring_events WHERE user_test_id = NEW.user_test_id) >= 15 THEN 'medium'
        ELSE 'low'
    END
    WHERE id = NEW.user_test_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update counts
CREATE TRIGGER trigger_update_suspicious_events
    AFTER INSERT ON proctoring_events
    FOR EACH ROW
    EXECUTE FUNCTION update_suspicious_events_count();

COMMENT ON TABLE proctoring_events IS 'Logs all AI-detected suspicious activities during tests';
COMMENT ON COLUMN proctoring_events.event_type IS 'Type of suspicious event detected by AI proctoring';
COMMENT ON COLUMN proctoring_events.severity IS 'Severity level: low, medium, high, critical';
COMMENT ON COLUMN proctoring_events.details IS 'JSON data with additional context (confidence, duration, etc)';
