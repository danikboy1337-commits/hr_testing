-- Migration: Change manager evaluations from employee-based to competency-based
-- This aligns with the new HR requirements where managers rate by competency

-- Drop old employee_ratings table (single overall rating)
DROP TABLE IF EXISTS employee_ratings CASCADE;

-- Create new manager_competency_ratings table (rate by competency)
CREATE TABLE IF NOT EXISTS manager_competency_ratings (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    manager_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_test_id INTEGER NOT NULL REFERENCES user_specialization_tests(id) ON DELETE CASCADE,
    competency_id INTEGER NOT NULL REFERENCES competencies(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_test_id, competency_id, manager_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_manager_comp_ratings_employee ON manager_competency_ratings(employee_id);
CREATE INDEX IF NOT EXISTS idx_manager_comp_ratings_manager ON manager_competency_ratings(manager_id);
CREATE INDEX IF NOT EXISTS idx_manager_comp_ratings_test ON manager_competency_ratings(user_test_id);
CREATE INDEX IF NOT EXISTS idx_manager_comp_ratings_competency ON manager_competency_ratings(competency_id);

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_manager_competency_ratings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER manager_competency_ratings_updated_at
    BEFORE UPDATE ON manager_competency_ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_manager_competency_ratings_updated_at();
