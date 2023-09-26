insert into Brand Values('WV');
insert into Brand Values('Audi');
insert into Brand Values('Posche');

insert into Model (Brand_name, Model_Name) Values('WV', 'Polo');
insert into Model (Brand_name, Model_Name) Values('WV', 'Golf');
insert into Model (Brand_name, Model_Name) Values('Audi', 'A3');
insert into Model (Brand_name, Model_Name) Values('Posche', '919');
-- select * from model;

insert into options (Modelid, version, year, color, fuel, transmission) Values ('1', 	'TDI', 			2011, 'Orange', 'Petrol', 	'Manual');
insert into options (Modelid, version, year, color, fuel, transmission) Values ('2', 	'e‑Golf', 		2021, 'Blue', 	'Electric', 'Automatic');
insert into options (Modelid, version, year, color, fuel, transmission) Values ('3', 	'Sportback', 	2019, 'Grey', 	'Gas', 		'Manual');
insert into options (Modelid, version, year, color, fuel, transmission) Values ('4', 	'Hybrid Evo', 	2018, 'White', 	'Hybrid', 	'Semi-Auto');
insert into options (Modelid, version, year, color, fuel, transmission) Values ('1', 	'GTI', 			2021, 'White', 	'Gas', 	'Semi-Auto');
-- select * from options;

insert into car Values ('WBAVD33536KV61628', 1, 1);
insert into car Values ('5TDDKRFH2FS042849', 2, 2);
insert into car Values ('1G6KD57Y46U163938', 3, 3);
insert into car Values ('1N6AD0EV6DN713780', 4, 4);
insert into car Values ('1FT7W2BT7DEB74723', 1, 5);
-- select * from car;

insert into Dealer (name, country) Values ('Karenta', 'Greece');
insert into Dealer (name, country) Values ('Luxury_Cars', 'Germany');
insert into Dealer (name, country) Values ('Luxury_Cars', 'Switzerland');
insert into Dealer (name, country) Values ('Kokorikos Cars', 'Japan');
-- select * from Dealer;

insert into Customer (Name, Surname, phone, email, address) VALUES ('Gio', 		'Chalk', 	691234567, 'Gio@aueb.com', 		'evelpidon 1');
insert into Customer (Name, Surname, phone, email, address) VALUES ('Nik', 		'Tsouk', 	691234568, 'Nik@aueb.com', 		'evelpidon 2');
insert into Customer (Name, Surname, phone, email, address) VALUES ('Vas', 		'Tzou', 	691234569, 'Vas@aueb.com', 		'evelpidon 3');
insert into Customer (Name, Surname, phone, email, address) VALUES ('Anas', 	'Bou', 		691234570, 'Anas@aueb.com', 	'evelpidon 4');
insert into Customer (Name, Surname, phone, email, address) VALUES ('Chris', 	'Santo', 	691234571, 'Chris@aueb.com', 	'evelpidon 5');
insert into Customer (Name, Surname, phone, email, address) VALUES ('Sot', 		'Chrys', 	691234572, 'Sot@aueb.com', 		'evelpidon 5');
-- select * from Customer;

update car set dealerid = 1, customerid = 4 where vin = 'WBAVD33536KV61628';
update car set dealerid = 4 where vin = '5TDDKRFH2FS042849';
update car set dealerid = 3, customerid = 1 where vin = '1N6AD0EV6DN713780';
-- select * from car;