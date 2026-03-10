-- ユーザーテーブル
CREATE TABLE IF NOT EXISTS users (
    user_uuid UUID PRIMARY KEY,
    name TEXT, --NULL許可 管理用
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO users (user_uuid, name) VALUES
('0bc63500-b97a-45cd-9b93-ee7ca7ce50f2', 'user1'),
('29f8bbb3-433b-4fc7-8074-d0bfbadec8a4', 'user2');

CREATE TABLE IF NOT EXISTS events (
    task_id UUID NOT NULL PRIMARY KEY,
    user_uuid UUID NOT NULL REFERENCES users(user_uuid) ON DELETE CASCADE,
    start_date DATE NOT NULL,        -- YYYY-MM-DD
    start_time TIME,                 -- 時間だけ、NULL 許可 HH:MI:SS
    end_date DATE NOT NULL,          -- YYYY-MM-DD
    event_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);