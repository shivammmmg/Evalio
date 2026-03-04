-- Enable UUID generation (so PostgreSQL can create IDs)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- COURSES TABLE
-- Stores each course that user creates or extracts

CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- Unique course ID
    name VARCHAR(255) NOT NULL,                      -- Course name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When it was created
);


-- ASSESSMENTS TABLE
-- Stores assessments (midterm, quiz, etc.)
-- Each assessment belongs to one course
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- Unique assessment ID
    
    course_id UUID NOT NULL,                         -- Which course it belongs to
    
    name VARCHAR(255) NOT NULL,                      -- Assessment name
    weight DECIMAL(5,2) NOT NULL CHECK (weight >= 0 AND weight <= 100),  
    -- Weight must be between 0 and 100
    
    -- Foreign key ensures relational integrity
    FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
        -- If a course is deleted, its assessments are deleted automatically
);

-- SCORES TABLE
-- Stores actual grades entered by student

CREATE TABLE scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    assessment_id UUID UNIQUE NOT NULL,

    score DECIMAL(5,2) CHECK (score >= 0 AND score <= 100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (assessment_id)
        REFERENCES assessments(id)
        ON DELETE CASCADE
);


-- RULES TABLE
-- Stores grading rules (best-of, drop lowest, etc.)
-- Uses JSONB for flexible rule storage
CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- Unique rule ID
    
    course_id UUID NOT NULL,                         -- Which course it belongs to
    
    rule_type VARCHAR(100) NOT NULL,                 -- Type of rule
    rule_config JSONB NOT NULL,                      -- Rule details (stored as JSON)
    
    FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
);

-- SCENARIOS TABLE
-- Stores What-If scenarios

CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    course_id UUID NOT NULL,

    name VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
);

-- SCENARIO SCORES TABLE
-- Stores hypothetical scores inside a scenario

CREATE TABLE scenario_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    scenario_id UUID NOT NULL,
    assessment_id UUID NOT NULL,

    simulated_score DECIMAL(5,2),

    FOREIGN KEY (scenario_id)
        REFERENCES scenarios(id)
        ON DELETE CASCADE,

    FOREIGN KEY (assessment_id)
        REFERENCES assessments(id)
        ON DELETE CASCADE,

    UNIQUE (scenario_id, assessment_id)
);

--  INDEXES
-- Makes course lookups faster
CREATE INDEX idx_assessments_course_id
ON assessments(course_id);

CREATE INDEX idx_rules_course_id
ON rules(course_id);

-- INDEXES FOR PERFORMANCE

CREATE INDEX idx_scores_assessment_id
ON scores(assessment_id);

CREATE INDEX idx_scenarios_course_id
ON scenarios(course_id);

