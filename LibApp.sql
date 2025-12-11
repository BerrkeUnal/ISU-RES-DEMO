create database Libapp;
use Libapp;

/* CREATING TABLES */

create table Users(
user_id int auto_increment, -- otomatik her eklenen kişi için id sayısını artırıcak.
school_mail varchar(150) unique not null,
password varchar(30) not null,
first_name varchar(30) not null,
last_name varchar(30) not null,
role varchar(30), -- eğer ki frontend'e getirmede problem olursa enumla tekrardan yazabiliriz. ' role ENUM('ogrenci', 'akademisyen') NOT NULL '.
primary key(user_id),
constraint password_c check (length(password)>=12 -- şifrenin 12 karakterden uzun veya eşit olmasını ister
and REGEXP_LIKE(password,'[A-Z]','c') -- Şifrede en az bir büyük harf olmasını ister
and REGEXP_LIKE(password, '[0-9]') )); -- şifrede en az bir rakam olmasını ister

create table Rooms(
room_id int,
room_name varchar(30),
type varchar(30),
capacity int , 
features varchar(100),
is_active boolean default true , -- aynı şekilde enum fonksiyonu ile yapılabilir. 'is_active enum('Aktif','Kullanılamaz') not null '.
primary key(room_id));

create table Reservations(
reserv_id int auto_increment,
user_id int,
room_id int,
status varchar(50),
check_in_time datetime,
cancellation_reason varchar(100),
reserv_date date,
start_time time,
end_time time,
created_at datetime default current_timestamp , -- işlemin yapıldığı anı tutar.
primary key(reserv_id),
foreign key(user_id) references Users(user_id),
foreign key(room_id) references Rooms(room_id),
constraint check_time_logic check(end_time > start_time),-- bitiş zamanı başlangıçtan yüksek olmalı 
is_reminder_sent BOOLEAN DEFAULT 0 -- hatırlatmanın gidip gitmediğine bakıcak
);

create table notifications(
notif_id int auto_increment,
user_id int,
message varchar(250),
is_read boolean default 0, -- mesajın okunup okunamdığını kontrol edicek
created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- mesajın oluşturulduğu tarihi not edicek
primary key(notif_id),
foreign key (user_id) references Users(user_id)
);

/* INSERTING DEMO VALUES */

INSERT INTO Users (school_mail, password, first_name, last_name, role) VALUES
('ahmet.yilmaz@isures.edu.tr', 'StrongPass2023A', 'Ahmet', 'Yılmaz', 'student'),
('ayse.demir@isures.edu.tr', 'StrongPass2023B', 'Ayşe', 'Demir', 'student'),
('mehmet.kaya@isures.edu.tr', 'StrongPass2023C', 'Mehmet', 'Kaya', 'academician'),
('fatma.celik@isures.edu.tr', 'StrongPass2023D', 'Fatma', 'Çelik', 'student'),
('ali.koc@isures.edu.tr', 'StrongPass2023E', 'Ali', 'Koç', 'student'),
('zeynep.sahina@isures.edu.tr', 'StrongPass2023F', 'Zeynep', 'Şahin', 'student'),
('mustafa.ozturka@isures.edu.tr', 'StrongPass2023G', 'Mustafa', 'Öztürk', 'academician'),
('elif.aydin@isures.edu.tr', 'StrongPass2023H', 'Elif', 'Aydın', 'student'),
('emre.yildiz@isures.edu.tr', 'StrongPass2023I', 'Emre', 'Yıldız', 'student'),
('burak.arslan@isures.edu.tr', 'StrongPass2023J', 'Burak', 'Arslan', 'student'),
('selin.dogan@isures.edu.tr', 'StrongPass2023K', 'Selin', 'Doğan', 'student'),
('can.kilic@isures.edu.tr', 'StrongPass2023L', 'Can', 'Kılıç', 'academician'),
('gamze.aksoy@isures.edu.tr', 'StrongPass2023M', 'Gamze', 'Aksoy', 'student'),
('mert.tas@isures.edu.tr', 'StrongPass2023N', 'Mert', 'Taş', 'student'),
('deniz.unal@isures.edu.tr', 'StrongPass2023O', 'Deniz', 'Ünal', 'student'),
('onur.kurt@isures.edu.tr', 'StrongPass2023P', 'Onur', 'Kurt', 'admin'),
('buse.polat@isures.edu.tr', 'StrongPass2023R', 'Buse', 'Polat', 'student'),
('eren.cakir@isures.edu.tr', 'StrongPass2023S', 'Eren', 'Çakır', 'student'),
('damla.ergin@isures.edu.tr', 'StrongPass2023T', 'Damla', 'Ergin', 'student'),
('kemal.yucel@isures.edu.tr', 'StrongPass2023U', 'Kemal', 'Yücel', 'academician'),
('hande.simsek@isures.edu.tr', 'StrongPass2023V', 'Hande', 'Şimşek', 'student'),
('baris.tekina@isures.edu.tr', 'StrongPass2023Y', 'Barış', 'Tekin', 'student'),
('yasin.ozkan@isures.edu.tr', 'StrongPass2023Z', 'Yasin', 'Özkan', 'student'),
('sena.korkmaz@isures.edu.tr', 'StrongPass2023X', 'Sena', 'Korkmaz', 'student'),
('umut.toprak@isures.edu.tr', 'StrongPass2023W', 'Umut', 'Toprak', 'student');

INSERT INTO Rooms (room_id, room_name, type, capacity, features, is_active) VALUES
(1, 'Room A-101', 'Study Room', 4, 'Whiteboard, Socket', true),
(2, 'Room A-102', 'Study Room', 4, 'Whiteboard, Socket', true),
(3, 'Room A-103', 'Study Room', 6, 'Projector, AC', true),
(4, 'Room B-201', 'Meeting Room', 10, 'Smart Board, Conference Device', true),
(5, 'Room B-202', 'Meeting Room', 8, 'TV, HDMI Cable', true),
(6, 'Room C-301', 'Quiet Room', 1, 'Socket, Lamp', true),
(7, 'Room C-302', 'Quiet Room', 1, 'Socket, Lamp', true),
(8, 'Room C-303', 'Quiet Room', 1, 'Socket, Lamp', true),
(9, 'Room D-401', 'Group Study', 5, 'Round Table', true),
(10, 'Room D-402', 'Group Study', 5, 'Round Table', true),
(11, 'Room E-501', 'Conference Hall', 50, 'Sound System, Stage', false),
(12, 'Room A-104', 'Study Room', 4, 'Window Side', true),
(13, 'Room A-105', 'Study Room', 4, 'Window Side', true),
(14, 'Room B-203', 'Meeting Room', 12, 'Big Screen', true),
(15, 'Room C-304', 'Quiet Room', 1, 'Ergonomic Chair', true),
(16, 'Room C-305', 'Quiet Room', 1, 'Ergonomic Chair', true),
(17, 'Room F-601', 'Lab', 20, 'Computer', true),
(18, 'Room F-602', 'Lab', 20, 'Computer, Printer', true),
(19, 'Room G-701', 'Seminar Room', 30, 'Podium', true),
(20, 'Room H-801', 'Lounge', 10, 'Armchair, Coffee Machine', true),
(21, 'Room A-106', 'Study Room', 2, 'AC', false),
(22, 'Room C-306', 'Quiet Room', 1, 'Sound Insulation', true),
(23, 'Room C-307', 'Quiet Room', 1, 'Sound Insulation', true),
(24, 'Room B-204', 'Meeting Room', 6, 'Glass Wall', true),
(25, 'Room I-901', 'Archive Study', 3, 'Old Resources', true);

INSERT INTO Reservations (user_id, room_id, status, check_in_time, reserv_date, start_time, end_time, cancellation_reason) VALUES
(1, 1, 'Active', NULL, '2023-11-01', '09:00:00', '11:00:00', NULL),
(2, 2, 'Completed', '2023-10-30 10:05:00', '2023-10-30', '10:00:00', '12:00:00', NULL),
(3, 4, 'Cancelled', NULL, '2023-11-02', '14:00:00', '16:00:00', 'User request'),
(4, 3, 'Active', NULL, '2023-11-01', '13:00:00', '15:00:00', NULL),
(5, 6, 'Active', NULL, '2023-11-03', '08:00:00', '10:00:00', NULL),
(1, 2, 'Completed', '2023-10-28 15:00:00', '2023-10-28', '15:00:00', '17:00:00', NULL),
(6, 10, 'Active', NULL, '2023-11-05', '11:00:00', '13:00:00', NULL),
(7, 14, 'Active', NULL, '2023-11-06', '09:00:00', '10:00:00', NULL),
(8, 7, 'Cancelled', NULL, '2023-11-01', '18:00:00', '20:00:00', 'Room under maintenance'),
(9, 8, 'Active', NULL, '2023-11-07', '12:00:00', '14:00:00', NULL),
(10, 1, 'Active', NULL, '2023-11-08', '09:00:00', '12:00:00', NULL),
(11, 5, 'Completed', '2023-10-25 14:00:00', '2023-10-25', '14:00:00', '16:00:00', NULL),
(12, 17, 'Active', NULL, '2023-11-09', '10:00:00', '11:00:00', NULL),
(13, 20, 'Active', NULL, '2023-11-10', '15:00:00', '16:00:00', NULL),
(14, 22, 'Active', NULL, '2023-11-11', '08:30:00', '10:30:00', NULL),
(15, 23, 'Cancelled', NULL, '2023-11-12', '13:00:00', '14:00:00', 'Schedule changed'),
(16, 25, 'Active', NULL, '2023-11-13', '09:00:00', '17:00:00', NULL),
(17, 4, 'Active', NULL, '2023-11-14', '14:00:00', '15:30:00', NULL),
(18, 9, 'Active', NULL, '2023-11-15', '10:00:00', '12:00:00', NULL),
(19, 12, 'Completed', '2023-10-29 11:00:00', '2023-10-29', '11:00:00', '13:00:00', NULL),
(20, 13, 'Active', NULL, '2023-11-16', '16:00:00', '18:00:00', NULL),
(21, 15, 'Active', NULL, '2023-11-17', '09:00:00', '11:00:00', NULL),
(22, 16, 'Active', NULL, '2023-11-18', '12:00:00', '14:00:00', NULL),
(23, 18, 'Cancelled', NULL, '2023-11-19', '10:00:00', '12:00:00', 'Illness'),
(24, 19, 'Active', NULL, '2023-11-20', '14:00:00', '16:00:00', NULL);

INSERT INTO notifications (user_id, message, is_read) VALUES
(1, 'Reservation created successfully.', 1),
(2, 'Room usage time is about to expire.', 0),
(3, 'Your reservation has been cancelled.', 0),
(4, 'Reminder for tomorrow at 13:00.', 0),
(5, 'Your reservation time is approaching.', 1),
(6, 'New study rooms are now available.', 0),
(7, 'Join the library survey.', 1),
(8, 'Your reservation was cancelled by the system.', 0),
(9, 'Do not forget to check-in to the room.', 0),
(10, 'Reservation confirmed.', 1),
(11, 'Rate your past reservation.', 0),
(12, 'Lab rules have been updated.', 1),
(13, 'Your lounge reservation is active.', 0),
(14, 'Reminder for your morning reservation.', 1),
(15, 'Your cancellation has been confirmed.', 0),
(16, 'Your full-day reservation has been defined.', 1),
(17, 'Meeting room is ready.', 0),
(18, 'Room confirmed for group study.', 1),
(19, 'Thanks for leaving the room clean.', 0),
(20, 'Your evening reservation is confirmed.', 0),
(21, 'Please follow the quiet room rules.', 1),
(22, 'Your reservation time has started.', 0),
(23, 'Your cancellation request has been received.', 1),
(24, 'You have a seminar room reservation.', 0),
(25, 'Welcome to the system!', 1);
 