-- Create table for competency self-assessments
CREATE TABLE IF NOT EXISTS competency_self_assessments (
    id SERIAL PRIMARY KEY,
    user_test_id INTEGER NOT NULL REFERENCES user_specialization_tests(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    competency_id INTEGER NOT NULL REFERENCES competencies(id) ON DELETE CASCADE,
    self_rating INTEGER NOT NULL CHECK (self_rating >= 1 AND self_rating <= 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_test_id, competency_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_self_assessments_user_test ON competency_self_assessments(user_test_id);
CREATE INDEX IF NOT EXISTS idx_self_assessments_user ON competency_self_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_self_assessments_competency ON competency_self_assessments(competency_id);
