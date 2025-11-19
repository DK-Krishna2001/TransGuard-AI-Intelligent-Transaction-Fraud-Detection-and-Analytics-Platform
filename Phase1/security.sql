-- TransGuard AI - Basic Role-Based Access Control

-- Read-only analyst role
CREATE ROLE analyst NOINHERIT LOGIN PASSWORD 'analyst_password';
GRANT CONNECT ON DATABASE transguard TO analyst;
GRANT USAGE ON SCHEMA public TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO analyst;

-- Read-write application user role
CREATE ROLE app_user NOINHERIT LOGIN PASSWORD 'app_user_password';
GRANT CONNECT ON DATABASE transguard TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
