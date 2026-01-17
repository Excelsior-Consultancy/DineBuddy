-- Users
INSERT INTO users (id, email, password_hash, full_name, role, is_active, is_verified, created_at, updated_at)
VALUES
(1, 'admin@test.com', 'hash', 'Admin User', 'ADMIN', true, true, now(), now()),
(2, 'staff@test.com', 'hash', 'Staff User', 'RESTAURANT_STAFF', true, true, now(), now()),
(3, 'restaurant_admin@test.com', 'hash', 'Restaurant Admin User', 'RESTAURANT_ADMIN', true, true, now(), now());

-- Restaurants
INSERT INTO restaurants (id, name, slug, is_active, created_at, updated_at)
VALUES
(1, 'Yash Cafe', 'yash-cafe', true, now(), now()),
(2, 'Food Point', 'food-point', true, now(), now()),
(3, 'Restaurant 3', 'restaurant-3', true, now(), now());

-- User Restaurants Map
INSERT INTO user_restaurants_map (user_id, restaurant_id)
VALUES
(1, 1),
(2, 1),
(3, 2),
(3, 3);