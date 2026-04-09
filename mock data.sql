-- ================================================================
-- 1. USERS  –  1 admin + 10 khách hàng
--    password = scrypt của chuỗi "Demo@1234"
-- ================================================================
INSERT INTO users
  (username, full_name, email, password_hash, phone, address, role, created_at)
VALUES
-- admin
('admin',
 'Quản Lý',
 'admin@gmail.com',
 'scrypt:32768:8:1$mT4kQpWxSalt$6a7f2b3c4d5e8f9a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4',
 '0988888888',
 'Hàng Bài, Tràng Tiền, Cửa Nam, Hoàn Kiếm, Hà Nội',
 'admin',
 '2024-08-01 07:00:00'),

-- khách hàng
('minh_hai',
 'Nông Minh Hải',
 'hai@gmail.com',
 'scrypt:32768:8:1$nQ5rRsSalt$7b8c3d4e5f6a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b',
 '0112223334',
 'Ngõ Quỳnh, Bạch Mai, Hai Bà Trưng, Hà Nội',
 'customer',
 '2024-09-12 09:15:00'),

('thu_trang',
 'Đặng Thu Trang',
 'trang.dang95@gmail.com',
 'scrypt:32768:8:1$pR6sStSalt$8c9d4e5f6a7b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c',
 '0933445566',
 'Đường Láng, Láng Thượng, Đống Đa, Hà Nội',
 'customer',
 '2024-09-25 14:30:00'),

('quoc_huy',
 'Trần Quốc Huy',
 'huytq.dev@gmail.com',
 'scrypt:32768:8:1$qS7tTuSalt$9d0e5f6a7b8c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d',
 '0944556677',
 'Xuân Thủy, Dịch Vọng Hậu, Cầu Giấy, Hà Nội',
 'customer',
 '2024-10-08 11:00:00'),

('lan_anh',
 'Nguyễn Thị Lan Anh',
 'lananh.nguyen@gmail.com',
 'scrypt:32768:8:1$rT8uUvSalt$0e1f6a7b8c9d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e',
 '0955667788',
 'Tây Sơn, Trung Liệt, Đống Đa, Hà Nội',
 'customer',
 '2024-10-22 16:45:00'),

('van_duc',
 'Lê Văn Đức',
 'ducle.arch@gmail.com',
 'scrypt:32768:8:1$sU9vVwSalt$1f2a7b8c9d0e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f',
 '0966778899',
 'Khâm Thiên, Phương Liên, Đống Đa, Hà Nội',
 'customer',
 '2024-11-05 08:20:00'),

('bich_ngoc',
 'Vũ Thị Bích Ngọc',
 'ngoc.vu.makeup@gmail.com',
 'scrypt:32768:8:1$tV0wWxSalt$2a3b8c9d0e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a',
 '0977889900',
 'Hoàng Cầu, Ô Chợ Dừa, Đống Đa, Hà Nội',
 'customer',
 '2024-11-18 13:10:00'),

('thanh_son',
 'Đinh Thanh Sơn',
 'son.dinh.music@gmail.com',
 'scrypt:32768:8:1$uW1xXySalt$3b4c9d0e1f2a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b',
 '0988990011',
 'Mai Dịch, Mai Dịch, Cầu Giấy, Hà Nội',
 'customer',
 '2024-12-01 10:05:00'),

('phuong_linh',
 'Cao Phương Linh',
 'linh.cao.photo@gmail.com',
 'scrypt:32768:8:1$vX2yYzSalt$4c5d0e1f2a3b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c',
 '0999001122',
 'Hào Nam, Trung Phụng, Đống Đa, Hà Nội',
 'customer',
 '2024-12-15 17:30:00'),

('hoang_nam',
 'Phạm Hoàng Nam',
 'namph.biz@gmail.com',
 'scrypt:32768:8:1$wY3zZaSalt$5d6e1f2a3b4c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d',
 '0900112233',
 'Linh Lang, Cống Vị, Ba Đình, Hà Nội',
 'customer',
 '2025-01-10 09:00:00'),

('khanh_linh',
 'Bùi Khánh Linh',
 'buikhanh.hr@gmail.com',
 'scrypt:32768:8:1$xZ4aAbSalt$6e7f2a3b4c5d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e',
 '0911223344',
 'Nghi Tàm, Quảng An, Tây Hồ, Hà Nội',
 'customer',
 '2025-01-25 14:00:00');

-- ================================================================
-- 2. CATEGORIES  (8 danh mục)
-- ================================================================
INSERT INTO categories (category_code, name, description) VALUES
('PZ', 'Pizza', 'Pizza đế giòn nướng lò đá, sốt cà chua thuần, phô mai mozzarella kéo sợi – size S/M/L'),
('BG', 'Burger', 'Patty bò Úc xay thủ công hoặc gà marinate 24 giờ, bánh brioche nướng bơ'),
('PA', 'Pasta', 'Pasta Ý nhập khẩu De Cecco, sốt tự nấu mỗi ngày – carbonara, bolognese, aglio e olio, kem nấm'),
('GA', 'Gà Rán', 'Gà tươi tẩm 11 loại gia vị bí truyền, chiên ngập dầu 170°C – giòn ngoài mọng trong'),
('DU', 'Đồ Uống', 'Nước ngọt, nước ép trái cây tươi, sinh tố và cà phê phục vụ suốt giờ mở cửa'),
('TD', 'Tráng Miệng', 'Dessert tự làm hàng ngày – kem soft serve, mousse, tiramisu và pudding caramel'),
('DN', 'Đồ Ăn Nhẹ', 'Khai vị và snack giòn: khoai tây chiên, mozzarella sticks, salad, cánh gà – lý tưởng chia sẻ'),
('CB', 'Combo', 'Bộ đôi & bộ gia đình tiết kiệm 10–20% so với gọi lẻ từng món');

-- ================================================================
-- 3. PRODUCTS  (33 sản phẩm)
-- ================================================================
INSERT INTO products (sku, category_id, name, description, image_url, is_available, created_at) VALUES

-- PIZZA (category_id = 1 | product_id 1–5) --------------------
('PZ-001', 1, 'Pizza Margherita', 'Đế giòn sốt cà chua San Marzano, mozzarella tươi fior di latte, lá basil Ý và dầu olive nguyên chất – vị cổ điển Naples', 'https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('PZ-002', 1, 'Pizza BBQ Gà & Nấm', 'Ức gà nướng BBQ + nấm portobello xào bơ tỏi + hành tây caramelized, mozzarella kéo sợi và sốt BBQ smoky', 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('PZ-003', 1, 'Pizza Hải Sản Tổng Hợp', 'Tôm sú, mực ống, ngao, crab stick tươi trên sốt cream cà chua, mozzarella và rắc parmesan + ngò tây', 'https://images.unsplash.com/photo-1565299507177-b0ac66763828?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('PZ-004', 1, 'Pizza Pepperoni Cay', 'Xúc xích pepperoni nhập Mỹ, sốt cà chua cay, mozzarella và ớt chuông xanh đỏ – vị đậm đà mạnh miệng', 'https://images.unsplash.com/photo-1628840042765-356cda07504e?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('PZ-005', 1, 'Pizza Phô Mai 4 Loại', 'Mozzarella + Cheddar + Gorgonzola + Parmesan trên nền sốt béchamel – thiên đường của người yêu phô mai', 'https://images.unsplash.com/photo-1571407970349-bc81e73b27b4?q=80&w=800&auto=format&fit=crop', 1, '2024-09-01 ₀₈:₀₀:₀₀'),

-- BURGER (category_id = 2 | product_id 6–9) -------------------
('BG-001', 2, 'Burger Bò Phô Mai', '180g patty bò Úc xay thủ công, cheddar tan chảy, dưa chuột muối, xà lách, sốt burger đặc trưng của quán', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('BG-002', 2, 'Burger Gà Giòn', 'Đùi gà marinate buttermilk 24 giờ, chiên giòn, coleslaw tự trộn, mayo mù tạt mật ong và dưa leo muối', 'https://images.unsplash.com/photo-1606755962773-d324e0a13086?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('BG-003', 2, 'Burger Tôm Tempura', 'Tôm sú tẩm bột tempura chiên xù + sốt tartar wasabi + xà lách romaine + dưa leo – thanh mát, khác biệt', 'https://images.unsplash.com/photo-1586816001966-79b736744398?q=80&w=800&auto=format&fit=crop', 1, '2024-10-01 08:00:00'),
('BG-004', 2, 'Burger Nấm Truffle', 'Patty bò phết truffle butter, nấm portobello áp chảo, arugula, phô mai gruyère và mayo truffle cao cấp', 'https://images.unsplash.com/photo-1553979459-d2229ba7433b?q=80&w=800&auto=format&fit=crop', 1, '2024-10-01 08:00:00'),

-- PASTA (category_id = 3 | product_id 10–13) ------------------
('PA-001', 3, 'Pasta Carbonara', 'Spaghetti De Cecco #5, pancetta xông khói, trứng lòng đào, pecorino Romano – carbonara kiểu Roma, không dùng kem', 'https://images.unsplash.com/photo-1612874742237-6450113ba049?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('PA-002', 3, 'Pasta Bolognese', 'Tagliatelle tươi, sốt bò bằm hầm 3 tiếng với vang đỏ + cà chua pelati + rau thơm, ăn kèm parmesan bào', 'https://images.unsplash.com/photo-1598866594230-a7c12756260f?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('PA-003', 3, 'Pasta Aglio e Olio Tôm', 'Spaghetti xào tỏi dầu olive, tôm sú tươi, ớt khô Calabria, lá mùi tây – đơn giản mà đậm đà kiểu Naples', 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('PA-004', 3, 'Pasta Kem Nấm Hương', 'Fettuccine sốt kem Pháp, nấm hương Nhật thái lát, tỏi, hành tây, parmesan bào – béo ngậy thơm nồng', 'https://images.unsplash.com/photo-1621996311228-7fa0ebc1975e?q=80&w=800&auto=format&fit=crop', 1, '2024-09-01 08:00:00'),

-- GÀ RÁN (category_id = 4 | product_id 14–17) -----------------
('GA-001', 4, 'Gà Rán Giòn Kiểu Mỹ', 'Gà tươi tẩm hỗn hợp 11 loại gia vị bí truyền, chiên ngập dầu 170°C cho vỏ giòn vàng ươm, thịt mọng nước', 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('GA-002', 4, 'Gà Rán Cay Hàn Quốc', 'Gà chiên giòn phủ sốt gochujang + mật ong + tỏi băm, rắc mè rang – cay ngọt chuẩn vị yangnyeom Korean', 'https://images.unsplash.com/photo-1587595431973-3f41052ce3d3?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('GA-003', 4, 'Cốt Lết Gà Nướng Sả', 'Cốt lết gà ướp sả + gừng + nước mắm ngon, nướng than hoa – ăn kèm cơm trắng hoặc salad rau xanh tươi', 'https://images.unsplash.com/photo-1598514982205-fbaa9dcbdc69?q=80&w=800&auto=format&fit=crop', 1, '2024-09-15 08:00:00'),
('GA-004', 4, 'Cánh Gà Sốt Buffalo', 'Cánh gà chiên giòn phủ sốt buffalo cay nồng + bơ + giấm táo Mỹ, ăn kèm bleu cheese dip và cần tây', 'https://images.unsplash.com/photo-1608039755473-39211f4229b4?q=80&w=800&auto=format&fit=crop', 1, '2024-09-15 08:00:00'),

-- ĐỒ UỐNG (category_id = 5 | product_id 18–22) ----------------
('DU-001', 5, 'Nước Ngọt Có Gas', 'Pepsi / 7UP / Mirinda cam tùy chọn – lon 330ml hoặc ly đá đầy, uống kèm bữa ăn giảm cảm giác ngán', 'https://images.unsplash.com/photo-1622483767028-fd16753ce391?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('DU-002', 5, 'Nước Cam Vắt Tươi', '3–4 trái cam Vinh vắt tại chỗ, không thêm đường hay nước – vitamin C tự nhiên, uống trong 15 phút', 'https://images.unsplash.com/photo-1600271886742-f049cd451bba?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('DU-003', 5, 'Trà Đào Cam Sả', 'Oolong ủ lạnh + đào ngâm đường + cam tươi + lá sả + hạt chia, đá viên – thức uống hè bán chạy nhất', 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('DU-004', 5, 'Sinh Tố Bơ Mật Ong', 'Bơ Đắk Lắk chín mềm + sữa tươi Vinamilk không đường + mật ong rừng Tây Nguyên – xay đặc, không pha loãng', 'https://images.unsplash.com/photo-1622241740925-fb3d67963283?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('DU-005', 5, 'Cà Phê Đen Đá', 'Robusta Cầu Đất phin đậm, rót qua đá viên – vị đắng nồng đặc trưng người Hà Nội, tỉnh ngủ tức thì', 'https://images.unsplash.com/photo-1517701550927-30cf0ba29d82?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),

-- TRÁNG MIỆNG (category_id = 6 | product_id 23–26) ------------
('TD-001', 6, 'Kem Vani Soft Serve', 'Kem mềm soft serve, sữa Nhật ít đường, cuộn ốc quế giòn – ăn ngay kẻo chảy, best seller mùa hè', 'https://images.unsplash.com/photo-1563805042-7684c8f9e412?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('TD-002', 6, 'Bánh Tiramisu', 'Mascarpone Galbani + ladyfinger ngâm espresso đậm + cacao Valrhona rắc dày – không dùng rượu, hợp mọi tuổi', 'https://images.unsplash.com/photo-1571115177098-24edf2f11f9f?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('TD-003', 6, 'Chocolate Lava Cake', 'Vỏ ngoài xốp mềm, cắt ra lòng chocolate đen 70% chảy ra – ăn nóng kèm kem vani là đỉnh cao cuộc đời', 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?q=80&w=800&auto=format&fit=crop', 1, '2024-10-01 08:00:00'),
('TD-004', 6, 'Pudding Caramel Flan', 'Flan kiểu Pháp nướng bain-marie, caramel đắng nhẹ – lạnh mát mịn màng, no cũng không ngán', 'https://images.unsplash.com/photo-1501443762994-6e1bebd037c8?q=80&w=800&auto=format&fit=crop', 1, '2024-10-01 08:00:00'),

-- ĐỒ ĂN NHẸ (category_id = 7 | product_id 27–30) -------------
('DN-001', 7, 'Khoai Tây Chiên Giòn', 'Khoai tây cắt que chiên ngập dầu, lắc muối biển + paprika, ăn kèm tương cà và sốt phô mai cheddar tự làm', 'https://images.unsplash.com/photo-1576107232684-1279f390859f?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('DN-002', 7, 'Mozzarella Sticks', 'Phô mai mozzarella cắt que, tẩm bột breadcrumb chiên vàng, kéo sợi cực đỉnh – ăn kèm sốt marinara', 'https://images.unsplash.com/photo-1536510233921-8e5043fce771?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('DN-003', 7, 'Salad Caesar Gà Nướng', 'Rau romaine + ức gà nướng thái lát + crouton nướng bơ tỏi + parmesan bào + sốt Caesar tự làm', 'https://images.unsplash.com/photo-1550304943-4f24f54bfde9?q=80&w=800&auto=format&fit=crop', 1, '2024-09-01 08:00:00'),
('DN-004', 7, 'Cánh Gà Chiên Giòn', 'Cánh gà tươi tẩm gia vị chiên giòn – vỏ ngoài giòn rụm, thịt mềm bên trong, ăn kèm tương ớt ngọt Thái', 'https://images.unsplash.com/photo-1567620832968-ebbc7b4b1a80?q=80&w=800&auto=format&fit=crop', 1, '2024-09-01 08:00:00'),

-- COMBO (category_id = 8 | product_id 31–33) ------------------
('CB-001', 8, 'Combo Gia Đình', '1 pizza L + 2 phần gà rán 5 miếng + 4 nước ngọt + 2 khoai tây vừa – tiết kiệm ~20% so với gọi lẻ', 'https://images.unsplash.com/photo-1615719413546-5078c1871a25?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('CB-002', 8, 'Combo Đôi', '1 burger bò + 1 burger gà + 2 nước uống tùy chọn + 1 khoai tây vừa – tiết kiệm ~15%', 'https://images.unsplash.com/photo-1594212848118-eec32eb04b8b?q=80&w=800&auto=format&fit=crop', 1, '2024-08-10 08:00:00'),
('CB-003', 8, 'Combo Học Sinh', '1 burger gà + 1 khoai tây nhỏ + 1 nước ngọt S – vừa túi tiền, đủ no cho bữa xế chiều', 'https://images.unsplash.com/photo-1610440042744-f8b89417efc6?q=80&w=800&auto=format&fit=crop', 1, '2024-09-01 08:00:00');

-- ================================================================
-- 4. PRODUCT_VARIANTS  (73 biến thể)
-- ----------------------------------------------------------------
-- ID mapping nhanh (tham chiếu khi viết order_items / cart_items)
-- Pizza S/M/L:
--   PZ-001 → v1/2/3 | PZ-002 → v4/5/6 | PZ-003 → v7/8/9
--   PZ-004 → v10/11/12 | PZ-005 → v13/14/15
-- Burger Regular/Double:
--   BG-001 → v16/17 | BG-002 → v18/19
--   BG-003 → v20/21 | BG-004 → v22/23
-- Pasta Vừa/Lớn:
--   PA-001 → v24/25 | PA-002 → v26/27
--   PA-003 → v28/29 | PA-004 → v30/31
-- Gà Rán:
--   GA-001(3/5/9 miếng) → v32/33/34
--   GA-002(3/5/9 miếng) → v35/36/37
--   GA-003(1/2 cốt lết)  → v38/39
--   GA-004(6/12/18 cánh) → v40/41/42
-- Đồ Uống:
--   DU-001(Lon/Ly lớn)  → v43/44
--   DU-002(M/L)         → v45/46
--   DU-003(S/M/L)       → v47/48/49
--   DU-004(M/L)         → v50/51
--   DU-005(S/M/L)       → v52/53/54
-- Tráng Miệng:
--   TD-001(1/2 phần)    → v55/56
--   TD-002(1 miếng/hộp 4) → v57/58
--   TD-003(1 phần)      → v59
--   TD-004(1/2 phần)    → v60/61
-- Đồ Ăn Nhẹ:
--   DN-001(Nhỏ/Vừa/Lớn) → v62/63/64
--   DN-002(5 cái/10 cái) → v65/66
--   DN-003(Nhỏ/Lớn)     → v67/68
--   DN-004(6/12 cánh)   → v69/70
-- Combo:
--   CB-001 → v71 | CB-002 → v72 | CB-003 → v73
-- ================================================================
INSERT INTO product_variants (product_id, size_name, price, stock) VALUES
-- PIZZA (Đường kính: S=20cm / M=25cm / L=30cm)
(1, 'Size S – 20cm', 120000, 50),
(1, 'Size M – 25cm', 159000, 50),
(1, 'Size L – 30cm', 199000, 50),
(2, 'Size S – 20cm', 135000, 50),
(2, 'Size M – 25cm', 175000, 50),
(2, 'Size L – 30cm', 215000, 50),
(3, 'Size S – 20cm', 149000, 40),
(3, 'Size M – 25cm', 189000, 40),
(3, 'Size L – 30cm', 239000, 40),
(4, 'Size S – 20cm', 130000, 50),
(4, 'Size M – 25cm', 169000, 50),
(4, 'Size L – 30cm', 209000, 50),
(5, 'Size S – 20cm', 139000, 40),
(5, 'Size M – 25cm', 179000, 40),
(5, 'Size L – 30cm', 219000, 40),

-- BURGER (Regular = 1 patty / Double = 2 patties)
(6, 'Regular (1 patty)', 89000, 80),
(6, 'Double Patty', 119000, 80),
(7, 'Regular (1 patty)', 79000, 80),
(7, 'Double Patty', 109000, 80),
(8, 'Regular (1 patty)', 89000, 60),
(8, 'Double Patty', 119000, 60),
(9, 'Regular (1 patty)', 99000, 60),
(9, 'Double Patty', 129000, 60),

-- PASTA
(10, 'Phần Vừa (~350g)', 99000, 60),
(10, 'Phần Lớn (~500g)', 129000, 60),
(11, 'Phần Vừa (~350g)', 89000, 60),
(11, 'Phần Lớn (~500g)', 119000, 60),
(12, 'Phần Vừa (~350g)', 99000, 60),
(12, 'Phần Lớn (~500g)', 129000, 60),
(13, 'Phần Vừa (~350g)', 95000, 60),
(13, 'Phần Lớn (~500g)', 125000, 60),

-- GÀ RÁN
(14, '3 miếng', 69000, 100),
(14, '5 miếng', 109000, 100),
(14, '9 miếng', 179000, 80),
(15, '3 miếng', 79000, 100),
(15, '5 miếng', 119000, 100),
(15, '9 miếng', 199000, 80),
(16, '1 cốt lết', 65000, 60),
(16, '2 cốt lết', 119000, 60),
(17, '6 cánh', 89000, 100),
(17, '12 cánh', 159000, 100),
(17, '18 cánh', 229000, 60),

-- ĐỒ UỐNG
(18, 'Lon 330ml', 20000, 200),
(18, 'Ly đá lớn 500ml', 25000, 200),
(19, 'Size M – 300ml', 39000, 80),
(19, 'Size L – 450ml', 49000, 80),
(20, 'Size S – 360ml', 35000, 120),
(20, 'Size M – 480ml', 45000, 120),
(20, 'Size L – 600ml', 55000, 120),
(21, 'Size M – 350ml', 49000, 80),
(21, 'Size L – 500ml', 59000, 80),
(22, 'Size S – 240ml', 25000, 150),
(22, 'Size M – 360ml', 30000, 150),
(22, 'Size L – 480ml', 35000, 150),

-- TRÁNG MIỆNG
(23, '1 phần', 35000, 50),
(23, '2 phần', 65000, 50),
(24, '1 miếng', 55000, 30),
(24, 'Hộp 4 miếng', 199000, 15),
(25, '1 phần', 65000, 30),
(26, '1 phần', 45000, 40),
(26, '2 phần', 85000, 40),

-- ĐỒ ĂN NHẸ
(27, 'Phần Nhỏ', 35000, 100),
(27, 'Phần Vừa', 45000, 100),
(27, 'Phần Lớn', 55000, 100),
(28, '5 cái', 59000, 60),
(28, '10 cái', 109000, 60),
(29, 'Salad Nhỏ (không gà)', 55000, 40),
(29, 'Salad Lớn (có gà nướng)', 85000, 40),
(30, '6 cánh', 79000, 80),
(30, '12 cánh', 149000, 80),

-- COMBO
(31, '1 set – Combo Gia Đình', 399000, 30),
(32, '1 set – Combo Đôi', 249000, 40),
(33, '1 set – Combo Học Sinh', 149000, 60);

-- ================================================================
-- 5. CARTS & CART_ITEMS  (7 giỏ hàng đang mở)
-- ================================================================
INSERT INTO carts (user_id, updated_at) VALUES
(2, '2025-04-10 08:30:00'), -- cart 1: minh_hai
(3, '2025-04-10 09:15:00'), -- cart 2: thu_trang
(4, '2025-04-10 10:05:00'), -- cart 3: quoc_huy
(5, '2025-04-10 11:40:00'), -- cart 4: lan_anh
(7, '2025-04-10 13:00:00'), -- cart 5: bich_ngoc
(9, '2025-04-10 14:20:00'), -- cart 6: phuong_linh
(10, '2025-04-10 15:55:00'); -- cart 7: hoang_nam

-- cart 1 – minh_hai: BG-001 Double + Trà Đào M + Khoai Tây Lớn
INSERT INTO cart_items (cart_id, product_id, variant_id, quantity) VALUES
(1, 6,  17, 1),   -- BG-001 Double Patty (v17)
(1, 20, 48, 1),   -- DU-003 Trà Đào M (v48)
(1, 27, 64, 1),   -- DN-001 Khoai Tây Lớn (v64)

-- cart 2 – thu_trang: PZ-002 L + 2 Lon nước ngọt + Tiramisu
(2, 2,  6,  1),   -- PZ-002 Size L (v6)
(2, 18, 43, 2),   -- DU-001 Lon 330ml (v43)
(2, 24, 57, 1),   -- TD-002 Tiramisu 1 miếng (v57)

-- cart 3 – quoc_huy: PA-001 Lớn + Cà Phê Đen M
(3, 10, 25, 1),   -- PA-001 Phần Lớn (v25)
(3, 22, 53, 1),   -- DU-005 Cà Phê M (v53)

-- cart 4 – lan_anh: GA-002 5 miếng + Trà Đào L x2 + Mozzarella + Kem
(4, 15, 36, 1),   -- GA-002 5 miếng (v36)
(4, 20, 49, 2),   -- DU-003 Trà Đào L (v49)
(4, 28, 65, 1),   -- DN-002 Mozzarella 5 cái (v65)
(4, 23, 55, 2),   -- TD-001 Kem Vani 1 phần (v55)

-- cart 5 – bich_ngoc: Combo Gia Đình + 4 Ly nước ngọt lớn
(5, 31, 71, 1),   -- CB-001 Combo Gia Đình (v71)
(5, 18, 44, 4),   -- DU-001 Ly đá lớn (v44)

-- cart 6 – phuong_linh: PZ-005 M + Lava Cake x2 + Sinh Tố Bơ L
(6, 5,  14, 1),   -- PZ-005 Size M (v14)
(6, 25, 59, 2),   -- TD-003 Lava Cake (v59)
(6, 21, 51, 1),   -- DU-004 Sinh Tố Bơ L (v51)

-- cart 7 – hoang_nam: Cánh Gà 12 cánh + BG-004 Double + Cà Phê L x2
(7, 30, 70, 1),   -- DN-004 Cánh Gà 12 cánh (v70)
(7, 9,  23, 1),   -- BG-004 Double Patty (v23)
(7, 22, 54, 2);   -- DU-005 Cà Phê L (v54)

-- ================================================================
-- 6. ORDERS  (18 đơn hàng với 5 trạng thái đa dạng)
-- ================================================================
INSERT INTO orders
  (order_code, user_id, total_price, status, shipping_address, note, created_at)
VALUES
-- DELIVERED ---------------------------------------------------------
('QAE-20250115-001', 2, 215000, 'delivered', 'Ngõ Quỳnh, Bạch Mai, Hai Bà Trưng, Hà Nội', 'Gọi điện trước khi giao nhé', '2025-01-15 11:20:00'),
('QAE-20250122-002', 3, 268000, 'delivered', 'Đường Láng, Láng Thượng, Đống Đa, Hà Nội', NULL, '2025-01-22 19:05:00'),
('QAE-20250205-003', 4, 499000, 'delivered', 'Xuân Thủy, Dịch Vọng Hậu, Cầu Giấy, Hà Nội', 'Để ở sảnh tòa nhà, gọi lên sau khi đặt ở sảnh nha', '2025-02-05 12:00:00'),
('QAE-20250214-004', 5, 234000, 'delivered', 'Tây Sơn, Trung Liệt, Đống Đa, Hà Nội', 'Sinh nhật mình, đóng gói đẹp giúp mình với', '2025-02-14 17:30:00'),
('QAE-20250228-005', 6, 359000, 'delivered', 'Khâm Thiên, Phương Liên, Đống Đa, Hà Nội', NULL, '2025-02-28 20:15:00'),
('QAE-20250310-006', 7, 217000, 'delivered', 'Hoàng Cầu, Ô Chợ Dừa, Đống Đa, Hà Nội', 'Không cần túi ni lông, cảm ơn', '2025-03-10 12:45:00'),
('QAE-20250318-007', 8, 304000, 'delivered', 'Mai Dịch, Mai Dịch, Cầu Giấy, Hà Nội', NULL, '2025-03-18 18:00:00'),
('QAE-20250325-008', 9, 314000, 'delivered', 'Hào Nam, Trung Phụng, Đống Đa, Hà Nội', 'Giao cổng số 2 nhé anh/chị ơi', '2025-03-25 19:30:00'),
('QAE-20250401-009', 10, 307000, 'delivered', 'Linh Lang, Cống Vị, Ba Đình, Hà Nội', NULL, '2025-04-01 13:10:00'),
('QAE-20250404-010', 11, 229000, 'delivered', 'Nghi Tàm, Quảng An, Tây Hồ, Hà Nội', 'Mình đặt cho 2 người, đóng gói riêng từng phần', '2025-04-04 11:55:00'),
('QAE-20250405-011', 2, 209000, 'delivered', 'Ngõ Quỳnh, Bạch Mai, Hai Bà Trưng, Hà Nội', NULL, '2025-04-05 20:00:00'),

-- CANCELLED ---------------------------------------------------------
('QAE-20250406-012', 3, 249000, 'cancelled', 'Đường Láng, Láng Thượng, Đống Đa, Hà Nội', 'Hủy vì đặt nhầm địa chỉ', '2025-04-06 14:00:00'),

-- CONFIRMED ---------------------------------------------------------
('QAE-20250408-013', 4, 244000, 'confirmed', 'Xuân Thủy, Dịch Vọng Hậu, Cầu Giấy, Hà Nội', NULL, '2025-04-08 10:30:00'),

-- PREPARING ---------------------------------------------------------
('QAE-20250409-014', 5, 378000, 'preparing', 'Tây Sơn, Trung Liệt, Đống Đa, Hà Nội', 'Gà cay mức 1 thôi nha, mình ăn không được cay nhiều', '2025-04-09 18:45:00'),

-- PENDING -----------------------------------------------------------
('QAE-20250410-015', 6, 149000, 'pending', 'Khâm Thiên, Phương Liên, Đống Đa, Hà Nội', NULL, '2025-04-10 07:30:00'),
('QAE-20250410-016', 7, 269000, 'pending', 'Hoàng Cầu, Ô Chợ Dừa, Đống Đa, Hà Nội', 'Giao sau 9h sáng giúp mình', '2025-04-10 08:05:00'),

-- CONFIRMED ---------------------------------------------------------
('QAE-20250409-017', 8, 274000, 'confirmed', 'Mai Dịch, Mai Dịch, Cầu Giấy, Hà Nội', NULL, '2025-04-09 20:00:00'),

-- PREPARING ---------------------------------------------------------
('QAE-20250410-018', 9, 338000, 'preparing', 'Hào Nam, Trung Phụng, Đống Đa, Hà Nội', 'Tiramisu để đông lạnh đến lúc giao nhé', '2025-04-10 09:15:00');

-- ================================================================
-- 7. ORDER_ITEMS
-- ================================================================
INSERT INTO order_items
  (order_id, product_id, variant_id, quantity, price_at_purchase)
VALUES
-- Đơn 1 (minh_hai): PZ-002 M + 2 Lon nước ngọt
(1, 2, 5, 1, 175000),
(1, 18, 43, 2, 20000),

-- Đơn 2 (thu_trang): BG-001 Regular x2 + Trà Đào M + Khoai Tây Vừa
(2, 6, 16, 2, 89000),
(2, 20, 48, 1, 45000),
(2, 27, 63, 1, 45000),

-- Đơn 3 (quoc_huy): CB-001 Combo GĐ + 4 Ly nước lớn
(3, 31, 71, 1, 399000),
(3, 18, 44, 4, 25000),

-- Đơn 4 (lan_anh): GA-001 5 miếng + Trà Đào L + Kem Vani x2
(4, 14, 33, 1, 109000),
(4, 20, 49, 1, 55000),
(4, 23, 55, 2, 35000),

-- Đơn 5 (van_duc): PZ-004 L + Tiramisu x2 + 2 Lon nước ngọt
(5, 4, 12, 1, 209000),
(5, 24, 57, 2, 55000),
(5, 18, 43, 2, 20000),

-- Đơn 6 (bich_ngoc): PA-001 Vừa + BG-002 Regular + Cam Vắt M
(6, 10, 24, 1, 99000),
(6, 7, 18, 1, 79000),
(6, 19, 45, 1, 39000),

-- Đơn 7 (thanh_son): GA-002 9 miếng + Khoai Tây Lớn + 2 Ly nước lớn
(7, 15, 37, 1, 199000),
(7, 27, 64, 1, 55000),
(7, 18, 44, 2, 25000),

-- Đơn 8 (phuong_linh): CB-002 Combo Đôi + Lava Cake
(8, 32, 72, 1, 249000),
(8, 25, 59, 1, 65000),

-- Đơn 9 (hoang_nam): PZ-003 M + Sinh Tố Bơ L + Mozzarella 5 cái
(9, 3, 8, 1, 189000),
(9, 21, 51, 1, 59000),
(9, 28, 65, 1, 59000),

-- Đơn 10 (khanh_linh): BG-004 Double + Trà Đào L + Pudding Flan
(10, 9, 23, 1, 129000),
(10, 20, 49, 1, 55000),
(10, 26, 60, 1, 45000),

-- Đơn 11 (minh_hai lần 2): GA-004 6 cánh + Salad Lớn + Cà Phê L
(11, 17, 40, 1, 89000),
(11, 29, 68, 1, 85000),
(11, 22, 54, 1, 35000),

-- Đơn 12 (thu_trang – cancelled): PZ-001 L + 2 Ly nước lớn
(12, 1, 3, 1, 199000),
(12, 18, 44, 2, 25000),

-- Đơn 13 (quoc_huy – confirmed): PA-003 Lớn + Salad Lớn + Cà Phê M
(13, 12, 29, 1, 129000),
(13, 29, 68, 1, 85000),
(13, 22, 53, 1, 30000),

-- Đơn 14 (lan_anh – preparing): GA-002 5 miếng x2 + 3 Ly nước lớn + Kem 2 phần
(14, 15, 36, 2, 119000),
(14, 18, 44, 3, 25000),
(14, 23, 56, 1, 65000),

-- Đơn 15 (van_duc – pending): CB-003 Combo HS
(15, 33, 73, 1, 149000),

-- Đơn 16 (bich_ngoc – pending): PZ-005 M + Trà Đào M x2
(16, 5, 14, 1, 179000),
(16, 20, 48, 2, 45000),

-- Đơn 17 (thanh_son – confirmed): GA-004 12 cánh + Khoai Vừa + Cà Phê L x2
(17, 17, 41, 1, 159000),
(17, 27, 63, 1, 45000),
(17, 22, 54, 2, 35000),

-- Đơn 18 (phuong_linh – preparing): PA-002 Lớn + Lon nước ngọt + Tiramisu Hộp
(18, 11, 27, 1, 119000),
(18, 18, 43, 1, 20000),
(18, 24, 58, 1, 199000);

-- ================================================================
-- 8. PAYMENTS  (18 bản ghi – đa dạng phương thức & trạng thái)
-- ================================================================
INSERT INTO payments
  (order_id, payment_method, amount, payment_status,
   vnp_txn_ref, vnp_transaction_no, vnp_response_code, created_at)
VALUES
-- Đơn 1 – VNPay thành công
(1, 'vnpay', 215000, 'success', 'QAE20250115112035', '14203857001', '00', '2025-01-15 11:21:05'),

-- Đơn 2 – COD thành công (giao xong thu tiền)
(2, 'cod', 268000, 'success', NULL, NULL, NULL, '2025-01-22 20:10:00'),

-- Đơn 3 – MoMo thành công
(3, 'momo', 499000, 'success', 'MOMO20250205120521', '74918263003', '00', '2025-02-05 12:06:00'),

-- Đơn 4 – VNPay thành công
(4, 'vnpay', 234000, 'success', 'QAE20250214173512', '29301748004', '00', '2025-02-14 17:36:00'),

-- Đơn 5 – COD thành công
(5, 'cod', 359000, 'success', NULL, NULL, NULL, '2025-02-28 21:05:00'),

-- Đơn 6 – MoMo thành công
(6, 'momo', 217000, 'success', 'MOMO20250310124831', '38201957006', '00', '2025-03-10 12:49:00'),

-- Đơn 7 – VNPay thành công
(7, 'vnpay', 304000, 'success', 'QAE20250318180255', '55647382007', '00', '2025-03-18 18:03:00'),

-- Đơn 8 – VNPay thành công
(8, 'vnpay', 314000, 'success', 'QAE20250325193118', '67392018008', '00', '2025-03-25 19:32:00'),

-- Đơn 9 – MoMo thành công
(9, 'momo', 307000, 'success', 'MOMO20250401131024', '91827364009', '00', '2025-04-01 13:11:00'),

-- Đơn 10 – COD thành công
(10, 'cod', 229000, 'success', NULL, NULL, NULL, '2025-04-04 12:40:00'),

-- Đơn 11 – VNPay thành công
(11, 'vnpay', 209000, 'success', 'QAE20250405200412', '12948375011', '00', '2025-04-05 20:05:00'),

-- Đơn 12 – VNPay THẤT BẠI (khách huỷ trước khi thanh toán)
-- response_code 24 = Giao dịch không thành công do người mua hủy
(12, 'vnpay', 249000, 'failed', 'QAE20250406140215', '83910275012', '24', '2025-04-06 14:03:00'),

-- Đơn 13 – MoMo thành công (đã confirmed, đã thanh toán online)
(13, 'momo', 244000, 'success', 'MOMO20250408103145', '47263819013', '00', '2025-04-08 10:32:00'),

-- Đơn 14 – VNPay thành công (đang preparing, đã thanh toán trước)
(14, 'vnpay', 378000, 'success', 'QAE20250409184602', '36481920014', '00', '2025-04-09 18:47:00'),

-- Đơn 15 – COD pending (khách chọn COD, chờ xác nhận đơn)
(15, 'cod', 149000, 'pending', NULL, NULL, NULL, '2025-04-10 07:31:00'),

-- Đơn 16 – MoMo pending (khách bấm thanh toán nhưng chưa hoàn thành)
(16, 'momo', 269000, 'pending', 'MOMO20250410080512', NULL, NULL, '2025-04-10 08:06:00'),

-- Đơn 17 – VNPay thành công (confirmed)
(17, 'vnpay', 274000, 'success', 'QAE20250409200318', '58203947017', '00', '2025-04-09 20:04:00'),

-- Đơn 18 – MoMo thành công (preparing)
(18, 'momo', 338000, 'success', 'MOMO20250410091622', '29485710018', '00', '2025-04-10 09:17:00');

-- ================================================================
-- 9. REVIEWS  (11 đánh giá – chỉ cho đơn delivered, đa dạng sao)
-- ================================================================
INSERT INTO reviews
  (user_id, order_id, rating, comment, is_read, created_at)
VALUES
-- Đơn 1 (minh_hai): 5 sao
(2, 1, 5, 'Pizza BBQ Gà ngon hơn mình tưởng nhiều! Phô mai kéo sợi thật sự, không phải loại phô mai rẻ tiền. Giao hàng đúng giờ dù đặt giờ trưa bận. Chắc chắn sẽ order lại vào cuối tuần.', 1, '2025-01-15 14:10:00'),

-- Đơn 2 (thu_trang): 4 sao
(3, 2, 4, 'Burger bò phô mai vừa miệng, patty không bị khô dù giao hơi xa. Khoai tây chiên giòn đúng kiểu. Trừ 1 sao vì sốt burger hơi ít, phải xin thêm mà quán lại không có gói sốt kèm.', 1, '2025-01-22 21:30:00'),

-- Đơn 3 (quoc_huy): 5 sao
(4, 3, 5, 'Combo Gia Đình quá xứng đáng! 4 người ăn thoải mái, pizza vẫn nóng khi nhận vì hộp giữ nhiệt tốt. Đặc biệt thích cái hộp đựng gà rán – giòn từng miếng. Sẽ quay lại vào dịp tiếp theo.', 1, '2025-02-05 15:00:00'),

-- Đơn 4 (lan_anh): 4 sao
(5, 4, 4, 'Gà rán giòn ngon, thịt mọng nước bên trong. Trà đào cam sả uống refreshing lắm. Kem vani soft serve tan chảy tí khi giao nhưng vẫn ngon. Lần sau sẽ thử thêm gà cay Hàn Quốc.', 1, '2025-02-14 20:00:00'),

-- Đơn 5 (van_duc): 3 sao
(6, 5, 3, 'Pizza pepperoni ổn, phô mai vừa đủ. Nhưng tiramisu hơi ít chocolate trên mặt, nhìn không đẹp bằng ảnh quảng cáo. Giao hàng trễ 25 phút so với dự kiến và tài xế không báo trước. Mong quán cải thiện.', 0, '2025-02-28 22:00:00'),

-- Đơn 6 (bich_ngoc): 5 sao
(7, 6, 5, 'Carbonara chuẩn kiểu Rome thật sự – không dùng kem mà vẫn sánh béo ngậy nhờ trứng và pecorino. Burger gà giòn sốt mayo mù tạt mật ong tuyệt vời. Nước cam vắt ngọt thanh mát. Một bữa trưa hoàn hảo!', 1, '2025-03-10 14:30:00'),

-- Đơn 7 (thanh_son): 4 sao
(8, 7, 4, 'Gà rán 9 miếng đủ cho cả nhà ăn, giòn đều. Khoai tây chiên hơi nguội khi nhận nhưng vẫn đạt. Tài xế giao nhanh và lịch sự. Nếu quán dùng túi giữ nhiệt tốt hơn thì mình sẽ 5 sao.', 1, '2025-03-18 20:00:00'),

-- Đơn 8 (phuong_linh): 5 sao
(9, 8, 5, 'Combo Đôi hoàn hảo cho date night ở nhà! Lava Cake ăn kèm kem vani là combo cực đỉnh. Hộp bánh được đóng gói riêng tránh bị nghiêng, quán chu đáo thật. Sẽ giới thiệu cho bạn bè.', 1, '2025-03-25 21:30:00'),

-- Đơn 9 (hoang_nam): 2 sao
(10, 9, 2, 'Pizza hải sản thiếu mực và ngao so với mô tả, chủ yếu là crab stick. Mozzarella sticks nguội lạnh khi nhận, không kéo sợi được nữa. Sinh tố bơ ngon là điểm sáng duy nhất. Mong quán kiểm soát chất lượng tốt hơn.', 0, '2025-04-01 15:00:00'),

-- Đơn 10 (khanh_linh): 4 sao
(11, 10, 4, 'Burger Truffle có vị khác biệt, patty bò thơm mùi truffle butter rất đặc trưng. Pudding flan mịn, vừa ngọt không quá. Trà đào cam sả giải khát tốt. Giao hơi chậm 15 phút nhưng không ảnh hưởng chất lượng.', 0, '2025-04-04 14:00:00'),

-- Đơn 11 (minh_hai – lần 2): 5 sao
(2, 11, 5, 'Cánh gà Buffalo cay vừa ngon, sốt bleu cheese dip ăn kèm béo bùi tuyệt vời. Salad Caesar gà nướng tươi rau, sốt Caesar tự làm khác hẳn sốt đóng chai. Cà phê đen đá đắng nồng chuẩn vị. Quán này ngày càng ngon hơn!', 0, '2025-04-05 22:00:00');
