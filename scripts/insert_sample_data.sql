-- Sample data insertion script for FastAPI JWT Template
-- Run this after creating users to populate items table

-- First, let's create some sample users (if they don't exist)
INSERT INTO users (username, email, hashed_password, is_active, created_at) 
VALUES 
    ('john_doe', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJQKqKq', true, NOW()),
    ('jane_smith', 'jane@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJQKqKq', true, NOW()),
    ('admin_user', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJQKqKq', true, NOW())
ON CONFLICT (username) DO NOTHING;

-- Sample items for john_doe (user_id = 1)
INSERT INTO items (title, description, owner_id, created_at) 
VALUES 
    ('Laptop', 'MacBook Pro 16-inch with M2 chip', 1, NOW()),
    ('Phone', 'iPhone 15 Pro Max 256GB', 1, NOW()),
    ('Headphones', 'Sony WH-1000XM5 Wireless Noise Cancelling', 1, NOW()),
    ('Coffee Mug', 'Ceramic coffee mug with company logo', 1, NOW()),
    ('Notebook', 'Moleskine Classic Notebook, Large', 1, NOW());

-- Sample items for jane_smith (user_id = 2)
INSERT INTO items (title, description, owner_id, created_at) 
VALUES 
    ('Desk Chair', 'Ergonomic office chair with lumbar support', 2, NOW()),
    ('Monitor', '27-inch 4K Ultra HD Monitor', 2, NOW()),
    ('Keyboard', 'Mechanical keyboard with RGB backlight', 2, NOW()),
    ('Mouse', 'Wireless gaming mouse with precision sensor', 2, NOW()),
    ('Plant', 'Indoor succulent plant in ceramic pot', 2, NOW()),
    ('Books', 'Collection of programming and design books', 2, NOW());

-- Sample items for admin_user (user_id = 3)
INSERT INTO items (title, description, owner_id, created_at) 
VALUES 
    ('Server', 'Dell PowerEdge R740 Server', 3, NOW()),
    ('Network Switch', 'Cisco Catalyst 2960-X Series', 3, NOW()),
    ('Backup Drive', '4TB External Hard Drive for backups', 3, NOW()),
    ('Security Camera', 'IP Security Camera with night vision', 3, NOW()),
    ('VPN Router', 'Enterprise-grade VPN router', 3, NOW());

-- Display the inserted data
SELECT 
    i.id,
    i.title,
    i.description,
    u.username as owner,
    i.created_at
FROM items i
JOIN users u ON i.owner_id = u.id
ORDER BY i.created_at DESC; 