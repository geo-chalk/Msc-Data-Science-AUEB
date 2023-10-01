CREATE TABLE Brand (
	Brand_name varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY (Brand_name)
);

CREATE TABLE model (
	Modelid 		serial NOT NULL,
	Brand_name 		varchar(255) NOT NULL,
	Model_Name 		varchar(255) NOT NULL unique,
	PRIMARY KEY (Modelid),
	foreign key (Brand_name) references Brand (Brand_name)
		on delete cascade
);


CREATE TABLE Options (
	Optionid 		serial NOT NULL,
	Model_id			integer NOT NULL,
	Version 		varchar(50) NOT NULL,
	Year 			numeric(4,0) NOT NULL,
	Color 			varchar(50) NOT NULL,
	Fuel 			varchar(50) check (Fuel in ('Gas', 'Electric', 'Hybrid', 'Petrol')),
	Transmission 	varchar(50) check (Transmission in ('Manual', 'Automatic', 'Semi-Auto')),
	PRIMARY KEY (Optionid),
	foreign key (Modelid) references model (Modelid)
		on delete cascade
);

	
CREATE TABLE Customer (
	Customerid serial NOT NULL,
	Name 		varchar(255) NOT NULL,
	Surname 	varchar(255) NOT NULL,
	phone 		varchar(255) NOT NULL UNIQUE,
	email 		varchar(255) UNIQUE,
	address 	varchar(255),
	PRIMARY KEY (Customerid)
);
	
CREATE TABLE Dealer (
	Dealerid 	serial NOT NULL,
	Name 		varchar(255) NOT NULL,
	Country 	varchar(255) NOT NULL,
	PRIMARY KEY (Dealerid)
);




CREATE TABLE Car (
	VIN 		char(17) NOT NULL,
	Modelid 	integer NOT NULL,
	Optionid 	integer NOT NULL,
	Dealerid 	integer,
	Customerid 	integer,
	PRIMARY KEY (VIN), 
	foreign key (Modelid) references model (Modelid)
		on delete cascade,
	foreign key (Optionid) references Options (Optionid)
		on delete cascade,
	foreign key (Dealerid) references Dealer (Dealerid)
		on delete set null,
	foreign key (Customerid) references Customer (Customerid)
		on delete set null
);


-- main indexes that are going to be created for each table based on the possible search
CREATE INDEX Brand_name_index ON Brand(Brand_name);
CREATE INDEX Modelid_index ON model(Modelid);
CREATE INDEX Model_Name_index ON model(Model_Name);
CREATE INDEX Optionid_index ON Options(Optionid);
CREATE INDEX VIN_index ON Car(VIN);
CREATE INDEX Dealerod_index ON Dealer(Dealerid);
CREATE INDEX Customerid_index ON Car(Customerid);

-- Most frequent queries
SELECT * FROM model m, brand b
WHERE m.Brand_name = b.Brand_name AND b.Brand_name = 'WV'


SELECT * FROM model m, Options o
WHERE m.Modelid = o.Modelid AND m.Model_name = 'Polo'

SELECT * FROM Car c, model m
WHERE c.Modelid = m.Modelid AND m.Model_name = 'Polo'

SELECT * FROM Customer cu, Car c, model m
WHERE c.Customerid = cu.Customerid AND c.Modelid = m.Modelid AND
m.Model_Name = 'Polo'

SELECT * FROM Dealer d, Car c, model m
WHERE d.dealerid = c.dealerid AND c.Modelid = m.Modelid AND
m.Brand_name = 'Posche'


