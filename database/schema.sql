-- LinkedIn Automation Suite Database Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    linkedin_url VARCHAR(500),
    github_username VARCHAR(100),
    settings JSONB DEFAULT '{}'::jsonb,
    automation_enabled BOOLEAN DEFAULT TRUE,
    automation_paused_until TIMESTAMP,
    pause_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- LinkedIn Sessions
CREATE TABLE linkedin_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    cookies JSONB,
    user_agent TEXT,
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI Usage Logs
CREATE TABLE ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50),
    model VARCHAR(100),
    tokens_used INT,
    cost DECIMAL(10, 4),
    purpose VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content Sources
CREATE TABLE content_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50),
    source_data JSONB,
    extracted_points TEXT[],
    tech_tags VARCHAR[],
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content Pillars
CREATE TABLE content_pillars (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100),
    tone VARCHAR(100),
    structure TEXT,
    ai_prompt TEXT,
    example_posts TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generated Posts
CREATE TABLE generated_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source_id UUID REFERENCES content_sources(id) ON DELETE SET NULL,
    pillar_id UUID REFERENCES content_pillars(id) ON DELETE SET NULL,
    hooks JSONB,
    body TEXT,
    cta TEXT,
    hashtags VARCHAR[],
    status VARCHAR(50) DEFAULT 'draft',
    edited_body TEXT,
    selected_hook INT,
    scheduled_for TIMESTAMP,
    published_at TIMESTAMP,
    linkedin_post_id VARCHAR(255),
    image_urls TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Post Analytics
CREATE TABLE post_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES generated_posts(id) ON DELETE CASCADE,
    impressions INT DEFAULT 0,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    shares INT DEFAULT 0,
    saves INT DEFAULT 0,
    clicks INT DEFAULT 0,
    profile_views_spike INT DEFAULT 0,
    engagement_rate DECIMAL(5, 2),
    scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Voice Profile
CREATE TABLE voice_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    avg_sentence_length INT,
    punctuation_style JSONB,
    common_phrases TEXT[],
    favorite_transitions TEXT[],
    avoided_words TEXT[],
    humor_style VARCHAR(100),
    tone_markers JSONB,
    training_posts TEXT[],
    last_trained TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Job Searches
CREATE TABLE job_searches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    keywords VARCHAR[],
    locations VARCHAR[],
    filters JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    max_applications_per_run INT DEFAULT 30,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Target Companies
CREATE TABLE target_companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(255),
    priority VARCHAR(20),
    status VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Jobs
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    search_id UUID REFERENCES job_searches(id) ON DELETE SET NULL,
    linkedin_job_id VARCHAR(255) UNIQUE,
    title VARCHAR(500),
    company VARCHAR(255),
    location VARCHAR(255),
    salary_range VARCHAR(100),
    job_description TEXT,
    job_url TEXT,
    relevance_score DECIMAL(3, 2),
    is_relevant BOOLEAN,
    skip_reason TEXT,
    application_status VARCHAR(50) DEFAULT 'found',
    posted_date DATE,
    found_at TIMESTAMP DEFAULT NOW()
);

-- Applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    resume_version VARCHAR(255),
    cover_letter TEXT,
    answers JSONB,
    applied_at TIMESTAMP,
    application_method VARCHAR(50),
    linkedin_application_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'applied',
    response_received BOOLEAN DEFAULT FALSE,
    response_date TIMESTAMP,
    response_type VARCHAR(50),
    interview_scheduled_at TIMESTAMP,
    interview_completed_at TIMESTAMP,
    interview_notes TEXT,
    offer_amount DECIMAL(10, 2),
    offer_received_at TIMESTAMP,
    offer_accepted BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Application Questions
CREATE TABLE application_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question_text TEXT,
    question_type VARCHAR(50),
    predefined_answer TEXT,
    ai_generated_answer TEXT,
    times_encountered INT DEFAULT 1,
    last_seen TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Custom Resumes
CREATE TABLE custom_resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    file_path VARCHAR(500),
    tailored_skills TEXT[],
    highlighted_projects TEXT[],
    customization_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance Insights
CREATE TABLE performance_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(100),
    insight_data JSONB,
    recommendation TEXT,
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- System Logs
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    level VARCHAR(20),
    module VARCHAR(100),
    message TEXT,
    error_trace TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_content_sources_user ON content_sources(user_id);
CREATE INDEX idx_content_sources_processed ON content_sources(processed);
CREATE INDEX idx_generated_posts_user_status ON generated_posts(user_id, status);
CREATE INDEX idx_generated_posts_scheduled ON generated_posts(scheduled_for);
CREATE INDEX idx_jobs_user_status ON jobs(user_id, application_status);
CREATE INDEX idx_jobs_linkedin_id ON jobs(linkedin_job_id);
CREATE INDEX idx_applications_user_status ON applications(user_id, status);
CREATE INDEX idx_post_analytics_post ON post_analytics(post_id);
CREATE INDEX idx_system_logs_created ON system_logs(created_at DESC);
