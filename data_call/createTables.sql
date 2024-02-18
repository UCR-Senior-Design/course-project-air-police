CREATE TABLE Data (sn VARCHAR(255), pm25 DECIMAL(10,3), pm10 DECIMAL(10,3), timestamp VARCHAR(255), PRIMARY KEY(sn, timestamp));
CREATE TABLE Devices (sn VARCHAR(255), lat DECIMAL(5,2), lon DECIMAL(5,2), pmHealth VARCHAR(20), sdHealth VARCHAR(20), onlne VARHCAR(10), PRIMARY KEY(sn));
CREATE TABLE User (email VARCHAR(255), username VARCHAR(30), pwd TEXT, PRIMARY KEY (username) );