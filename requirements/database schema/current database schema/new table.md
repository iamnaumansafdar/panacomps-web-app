In short, the objective is to create a profile of a building that will have information describing the building. Each building will have a unique ID and we will use the gmaps_place_id as the unique ID. so in the below table guid will be the same as the gmaps_place_id .

CREATE TABLE buildings (
id SERIAL PRIMARY KEY,
guid BIGINT NOT NULL,
name VARCHAR(255) NOT NULL,
street VARCHAR(255),
address_1 VARCHAR(255),
address_2 VARCHAR(255),
district_id INT,
city_id INT,
location_id INT,
postcode VARCHAR(20),
email VARCHAR(255),
telephone_nr VARCHAR(50),
mobile_nr VARCHAR(50),
fax_nr VARCHAR(50),
youtube_id VARCHAR(50),
latitude DECIMAL(10, 7),
longitude DECIMAL(10, 7),
slug VARCHAR(255),
units INT,
stars INT,
rating DECIMAL(3, 2),
floors_count INT,
construction_year INT,
status VARCHAR(50),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
gmaps_place_id VARCHAR(255) NOT NULL,
building_type VARCHAR(50),
developer VARCHAR(255),
amenities VARCHAR(255),
occupancy_permit_date DATE,
registry_code VARCHAR(50),
energy_certification VARCHAR(50),
security_features VARCHAR(255),
owner_association VARCHAR(255),
rentals_allowed BOOLEAN,
rental_type VARCHAR(50) -- Indicates if short term, long term, or both are allowed
);

Here are the SQL statements for adding the foreign key constraints to link the metrics and folios tables with the buildings table:

ALTER TABLE metrics ADD COLUMN building_id INT;
ALTER TABLE folios ADD COLUMN building_id INT;

ALTER TABLE metrics ADD CONSTRAINT fk_metrics_building FOREIGN KEY (building_id) REFERENCES buildings(id);
ALTER TABLE folios ADD CONSTRAINT fk_folios_building FOREIGN KEY (building_id) REFERENCES buildings(id);

xplanation

•	ALTER TABLE metrics ADD COLUMN building_id INT;: Adds a new column building_id to the metrics table.
•	ALTER TABLE folios ADD COLUMN building_id INT;: Adds a new column building_id to the folios table.
•	ALTER TABLE metrics ADD CONSTRAINT fk_metrics_building FOREIGN KEY (building_id) REFERENCES buildings(id);: Adds a foreign key constraint to the metrics table linking building_id to the id column in the buildings table.
•	ALTER TABLE folios ADD CONSTRAINT fk_folios_building FOREIGN KEY (building_id) REFERENCES buildings(id);: Adds a foreign key constraint to the folios table linking building_id to the id column in the buildings table.
These changes ensure that each entry in the metrics and folios tables can be linked to a corresponding building in the buildings table