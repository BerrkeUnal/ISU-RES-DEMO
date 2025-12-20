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
-- ADMINS
('berke.unal@istinye.edu.tr', 'Berke_Admin_2025!', 'Berke', 'Unal', 'admin'),
('sistem.yonetici@istinye.edu.tr', 'Selin_Secure_99!', 'Selin', 'Yilmaz', 'admin'),

-- ACADEMICIANS (Her biri rakam içerecek şekilde güncellendi)
('murat.aksoy@istinye.edu.tr', 'Murat_Academic_12', 'Murat', 'Aksoy', 'academician'),
('deniz.aydin@istinye.edu.tr', 'Deniz_Scholar_44', 'Deniz', 'Aydin', 'academician'),
('asli.tekin@istinye.edu.tr', 'Asli_Research_2025', 'Asli', 'Tekin', 'academician'),
('levent.kaya@istinye.edu.tr', 'Levent_PhD_2025!', 'Levent', 'Kaya', 'academician'),

-- STUDENTS
('220901572@stu.istinye.edu.tr', 'Student_Berke_01', 'Berke', 'Ogrenci', 'student'),
('mert.demir@stu.istinye.edu.tr', 'Mert_Pass_9876', 'Mert', 'Demir', 'student'),
('zeynep.yildiz@stu.istinye.edu.tr', 'Zeynep_Secure_88', 'Zeynep', 'Yildiz', 'student'),
('ali.can@stu.istinye.edu.tr', 'Ali_Can_Success_1', 'Ali', 'Can', 'student'),
('ebru.sahin@stu.istinye.edu.tr', 'Ebru_Pass_2025!', 'Ebru', 'Sahin', 'student'),
('can.ozkan@stu.istinye.edu.tr', 'Can_Ozkan_4433', 'Can', 'Ozkan', 'student'),
('gizem.ak@stu.istinye.edu.tr', 'Gizem_Pass_1234', 'Gizem', 'Ak', 'student'),
('umut.kurt@stu.istinye.edu.tr', 'Umut_Fast_Res_9', 'Umut', 'Kurt', 'student'),
('seda.yilmaz@stu.istinye.edu.tr', 'Seda_Security_22', 'Seda', 'Yilmaz', 'student');

INSERT INTO Rooms (room_id, room_name, type, capacity, features, is_active) VALUES 
(1, 'Vadi Study-1', 'Library Study Room', 6, 'AB Campus, Whiteboard, AC', 1),
(2, 'Vadi Study-2', 'Library Study Room', 10, 'AB Campus, Screen, AC', 1),
(3, 'Halic Study-A', 'Library Study Room', 4, 'H Campus, Quiet Zone', 1),
(4, 'Lab-101', 'Laboratory', 30, 'AB Campus, PC Setup, Linux OS', 1),
(5, 'Lab-205', 'Laboratory', 25, 'H Campus, Electronics Equipment', 1),
(6, 'Class-A302', 'Classroom', 60, 'ANK Campus, Projector', 1),
(7, 'Class-B101', 'Classroom', 80, 'AB Campus, Large Hall', 1),
(8, 'Class-H102', 'Classroom', 45, 'H Campus, Traditional Board', 1),
(9, 'Main Conference', 'Conference Hall', 200, 'AB Campus, Audio System, Stage', 1),
(10, 'Ank-Lab-01', 'Laboratory', 40, 'ANK Campus, High-End Workstations', 1);

INSERT INTO Reservations (user_id, room_id, status, reserv_date, start_time, end_time, purpose) VALUES 
(5, 1, 'Active', '2025-12-21', '10:00:00', '12:00:00', 'Database Project Study'),
(3, 7, 'Confirmed', '2025-12-21', '13:00:00', '15:00:00', 'Algorithm Lecture'),
(6, 4, 'Active', '2025-12-22', '09:00:00', '11:00:00', 'ML Practice'),
(7, 2, 'Cancelled', '2025-12-20', '14:00:00', '16:00:00', 'Group Meeting'),
(5, 9, 'Active', '2025-12-25', '18:00:00', '20:00:00', 'Club Event');

INSERT INTO notifications (user_id, message, is_read) VALUES 
(5, 'Your reservation for Vadi Study-1 is confirmed.', 0),
(7, 'Your reservation for Vadi Study-2 has been cancelled by admin.', 0),
(3, 'New academic priority reservation created.', 1);
 
 ALTER TABLE Reservations ADD COLUMN purpose VARCHAR(100) AFTER end_time;
 
 select * from Users