-- Users
INSERT INTO users (id, email, password_hash, full_name, role, is_active, is_verified, created_at, updated_at)
VALUES
(1, 'admin@test.com', 'hash', 'Admin User', 'admin', true, true, now(), now()),
(2, 'staff@test.com', 'hash', 'Staff User', 'restaurant_staff', true, true, now(), now());

-- Restaurants
INSERT INTO restaurants (id, name, slug, is_active, created_at, updated_at)
VALUES
(1, 'Yash Cafe', 'yash-cafe', true, now(), now()),
(2, 'Food Point', 'food-point', true, now(), now());