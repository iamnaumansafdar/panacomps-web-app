
### Table: Folios
This table stores detailed information about property folios, including location, ownership, and valuation details. It serves as the primary table for property records.

```sql
CREATE TABLE Folios (
    FOLIO BIGINT NOT NULL,
    MODULO TEXT,
    "CODIGO UBICACIÓN" INTEGER,
    MUNICIPIO TEXT,
    EDIFICIO TEXT NOT NULL,
    PROPIETARIOS TEXT,
    "FOLIO / FINCA / FICHA" TEXT,
    "FECHA DE INSCRIPCIÓN" DATE,
    PROPIETARIO TEXT,
    DOMICILIO TEXT,
    "USO DEL SUELO" TEXT,
    "OTRO TIPO" TEXT,
    DESCRIPCIÓN TEXT,
    "POR EDIFICIO" TEXT,
    "% DE PROINDIVISO" TEXT,
    "CÉDULA CATASTRAL" TEXT,
    VALOR DECIMAL,
    "VALOR DEL TERRENO" DECIMAL,
    "VALOR DE MEJORAS" DECIMAL,
    "VALOR DEL TRASPASO" DECIMAL,
    "NÚMERO DE PLANO" TEXT,
    "FECHA DE CONSTRUCCIÓN" DATE,
    "FECHA DE OCUPACIÓN" DATE,
    LOTE TEXT,
    "SUPERFICIE INICIAL" TEXT,
    "SUPERFICIE / RESTO LIBRE" TEXT,
    COLINDANCIAS TEXT,
    "TIMESTAMP ADDED TO CSV" TIMESTAMP,
    "DERECHOS / ACTOS / OTRAS OPERACIONES" TEXT,
    PRIMARY KEY (FOLIO, EDIFICIO)
);
```

### Table: Metrics
This table is designed to store metrics related to property transactions, including sales data and valuation. It references the `Folios` table for property identification.

```sql
CREATE TABLE Metrics (
    FOLIO BIGINT NOT NULL,
    "CODIGO UBICACIÓN" INTEGER,
    MUNICIPIO TEXT,
    EDIFICIO TEXT NOT NULL,
    "FECHA DE CONSTRUCCIÓN" DATE,
    "FECHA DE OCUPACIÓN" DATE,
    PROPIETARIOS TEXT,
    DOMICILIO TEXT,
    "Sales Transaction Date" DATE,
    VALOR DECIMAL,
    "VALOR DEL TERRENO" DECIMAL,
    "VALOR DE MEJORAS" DECIMAL,
    "VALOR DEL TRASPASO" DECIMAL,
    "SUPERFICIE INICIAL" TEXT,
    "Price per square meter" DECIMAL,
    HIPOTECA BOOLEAN,
    MONTO DECIMAL,
    "TASA EFECTIVA" DECIMAL,
    "TASA NOMINAL" DECIMAL,
    "INTERÉS ANUAL" DECIMAL,
    FECI DECIMAL,
    "INTERÉS ANUAL + FECI" DECIMAL,
    NOMBRE TEXT,
    TIMESTAMP TIMESTAMP,
    "USO DEL SUELO" TEXT,
    FOREIGN KEY (FOLIO, EDIFICIO) REFERENCES Folios(FOLIO, EDIFICIO)
);
```

### Table: PDF_Raw_Data
This table is intended for storing raw data extracted from PDF documents related to property transactions. It includes fields for document metadata and financial details, and it also references the `Folios` table.

```sql
CREATE TABLE PDF_Raw_Data (
    FOLIO BIGINT NOT NULL,
    EDIFICIO TEXT NOT NULL,
    Filename TEXT,
    "PDF Text" TEXT,
    "VALOR DEL TERRENO" DECIMAL,
    "VALOR DE MEJORAS" DECIMAL,
    "VALOR DEL TRASPASO" DECIMAL,
    "SUPERFICIE INICIAL" TEXT,
    "Sales Transaction Date" DATE,
    HIPOTECA BOOLEAN,
    MONTO DECIMAL,
    "TASA EFECTIVA" DECIMAL,
    "TASA NOMINAL" DECIMAL,
    "INTERÉS ANUAL" DECIMAL,
    FECI DECIMAL,
    "INTERÉS ANUAL + FECI" DECIMAL,
    NOMBRE TEXT,
    "Filing Data" DATE,
    FOREIGN KEY (FOLIO, EDIFICIO) REFERENCES Folios(FOLIO, EDIFICIO)
);
```

The SQL schema and triggers for capturing historical changes to the `Folios` table have been successfully implemented. Below is a detailed overview of the components created:

### Table: FoliosHistory
This table is designed to store historical records of changes made to the `Folios` table. It mirrors the structure of the `Folios` table with additional fields to capture the change timestamp and a unique identifier for each historical entry.

```sql
CREATE TABLE FoliosHistory (
    HistoryId SERIAL PRIMARY KEY,
    FOLIO BIGINT NOT NULL,
    MODULO TEXT,
    "CODIGO UBICACIÓN" INTEGER,
    MUNICIPIO TEXT,
    EDIFICIO TEXT NOT NULL,
    PROPIETARIOS TEXT,
    "FOLIO / FINCA / FICHA" TEXT,
    "FECHA DE INSCRIPCIÓN" DATE,
    PROPIETARIO TEXT,
    DOMICILIO TEXT,
    "USO DEL SUELO" TEXT,
    "OTRO TIPO" TEXT,
    DESCRIPCIÓN TEXT,
    "POR EDIFICIO" TEXT,
    "% DE PROINDIVISO" TEXT,
    "CÉDULA CATASTRAL" TEXT,
    VALOR DECIMAL,
    "VALOR DEL TERRENO" DECIMAL,
    "VALOR DE MEJORAS" DECIMAL,
    "VALOR DEL TRASPASO" DECIMAL,
    "NÚMERO DE PLANO" TEXT,
    "FECHA DE CONSTRUCCIÓN" DATE,
    "FECHA DE OCUPACIÓN" DATE,
    LOTE TEXT,
    "SUPERFICIE INICIAL" TEXT,
    "SUPERFICIE / RESTO LIBRE" TEXT,
    COLINDANCIAS TEXT,
    "TIMESTAMP ADDED TO CSV" TIMESTAMP,
    "DERECHOS / ACTOS / OTRAS OPERACIONES" TEXT,
    ChangeTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (FOLIO, EDIFICIO) REFERENCES Folios(FOLIO, EDIFICIO)
);
```

### Trigger Function: log_folios_changes
This function is triggered after an update to the `Folios` table. It captures the state of the record before the update and inserts this historical data into the `FoliosHistory` table.

```sql
CREATE OR REPLACE FUNCTION log_folios_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO FoliosHistory (
        FOLIO,
        MODULO,
        "CODIGO UBICACIÓN",
        MUNICIPIO,
        EDIFICIO,
        PROPIETARIOS,
        "FOLIO / FINCA / FICHA",
        "FECHA DE INSCRIPCIÓN",
        PROPIETARIO,
        DOMICILIO,
        "USO DEL SUELO",
        "OTRO TIPO",
        DESCRIPCIÓN,
        "POR EDIFICIO",
        "% DE PROINDIVISO",
        "CÉDULA CATASTRAL",
        VALOR,
        "VALOR DEL TERRENO",
        "VALOR DE MEJORAS",
        "VALOR DEL TRASPASO",
        "NÚMERO DE PLANO",
        "FECHA DE CONSTRUCCIÓN",
        "FECHA DE OCUPACIÓN",
        LOTE,
        "SUPERFICIE INICIAL",
        "SUPERFICIE / RESTO LIBRE",
        COLINDANCIAS,
        "TIMESTAMP ADDED TO CSV",
        "DERECHOS / ACTOS / OTRAS OPERACIONES"
    )
    VALUES (
        OLD.FOLIO,
        OLD.MODULO,
        OLD."CODIGO UBICACIÓN",
        OLD.MUNICIPIO,
        OLD.EDIFICIO,
        OLD.PROPIETARIOS,
        OLD."FOLIO / FINCA / FICHA",
        OLD."FECHA DE INSCRIPCIÓN",
        OLD.PROPIETARIO,
        OLD.DOMICILIO,
        OLD."USO DEL SUELO",
        OLD."OTRO TIPO",
        OLD.DESCRIPCIÓN,
        OLD."POR EDIFICIO",
        OLD."% DE PROINDIVISO",
        OLD."CÉDULA CATASTRAL",
        OLD.VALOR,
        OLD."VALOR DEL TERRENO",
        OLD."VALOR DE MEJORAS",
        OLD."VALOR DEL TRASPASO",
        OLD."NÚMERO DE PLANO",
        OLD."FECHA DE CONSTRUCCIÓN",
        OLD."FECHA DE OCUPACIÓN",
        OLD.LOTE,
        OLD."SUPERFICIE INICIAL",
        OLD."SUPERFICIE / RESTO LIBRE",
        OLD.COLINDANCIAS,
        OLD."TIMESTAMP ADDED TO CSV",
        OLD."DERECHOS / ACTOS / OTRAS OPERACIONES"
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Trigger: folios_update_trigger
This trigger invokes the `log_folios_changes()` function whenever an update occurs on the `Folios` table, ensuring that all changes are logged.

```sql
CREATE TRIGGER folios_update_trigger
AFTER UPDATE ON Folios
FOR EACH ROW
EXECUTE PROCEDURE log_folios_changes();
```

These components collectively ensure that any updates to the `Folios` table are tracked, providing a comprehensive audit trail of changes. This setup is crucial for maintaining data integrity and facilitating the tracking of historical data changes.

X. Search Criteria and Search Results Mapping

The search criteria and search results parameters can be mapped to the database tables and columns as follows:

**Search Criteria Parameters**:

1. Building List (string): Mapped to the `EDIFICIO` column in the `Folios` and `Metrics` tables.
2. Unit List (string): Mapped to the `DOMICILIO` column in the `Metrics` table.
3. Folio Search (string): Mapped to the `FOLIO` column in the `Folios`, `Metrics`, and `PDF_Raw_Data` tables.
4. Min Sales Price (integer or float): Mapped to the `"VALOR DEL TRASPASO"` column in the `Metrics` table.
5. Max Sales Price (integer or float): Mapped to the `"VALOR DEL TRASPASO"` column in the `Metrics` table.
6. Min Sq. Meters (integer or float): Mapped to the `"SUPERFICIE INICIAL"` column in the `Metrics` table.
7. Max Sq. Meters (integer or float): Mapped to the `"SUPERFICIE INICIAL"` column in the `Metrics` table.
8. Filter by Date Range (date range): Mapped to the `"Sales Transaction Date"` column in the `Metrics` table.

**Search Results Parameters**:

1. Unit (string): Mapped to the `DOMICILIO` column in the `Metrics` table.
2. Folio (integer or string): Mapped to the `FOLIO` column in the `Folios`, `Metrics`, and `PDF_Raw_Data` tables.
3. Sale Date (date): Mapped to the `"Sales Transaction Date"` column in the `Metrics` table.
4. Sale Amount (integer or float): Mapped to the `"VALOR DEL TRASPASO"` column in the `Metrics` table.
5. Square Meters (integer or float): Mapped to the `"SUPERFICIE INICIAL"` column in the `Metrics` table.
6. Price Per Square Meter (integer or float): Mapped to the `"Price per square meter"` column in the `Metrics` table.
7. Date Added (date): Mapped to the `TIMESTAMP` column in the `Metrics` table.

**View Detail Parameters (Pop-up or Modal Window)**:

1. Building Information: Mapped to the `EDIFICIO` column in the `Folios` and `Metrics` tables.
2. Unit Information: Mapped to the `DOMICILIO` column in the `Metrics` table.
3. Sale Details: Mapped to columns like `"Sales Transaction Date"`, `"VALOR DEL TRASPASO"`, `"SUPERFICIE INICIAL"`, and `"Price per square meter"` in the `Metrics` table.
4. Owner Information: Mapped to the `PROPIETARIOS` column in the `Metrics` table.
5. Legal Information: Mapped to columns like `FOLIO`, `"CODIGO UBICACIÓN"`, and `"CÉDULA CATASTRAL"` in the `Folios` table.
6. Additional Metadata: Mapped to various other columns in the `Folios`, `Metrics`, and `PDF_Raw_Data` tables, depending on the specific requirements.

XI. SQL Statements

The following SQL statements are used to retrieve data from the database based on the search criteria and parameters:

### Summary of SQL Statements

#### `buildingSelection`
This query selects distinct building names (`EDIFICIO`) from the `Metrics` table, trimming any leading or trailing spaces from the building names for consistency. It orders the results alphabetically by the trimmed building name.

```sql
SELECT DISTINCT TRIM(EDIFICIO) AS TrimmedEdificio
FROM Metrics
ORDER BY TRIM(EDIFICIO) ASC;
```

#### `filteredBuildings`
This query retrieves a wide range of information about buildings from the `Metrics` table, applying several filters based on user input criteria such as building name, unit address, folio number, sales transaction date range, minimum and maximum sales price, and minimum and maximum initial surface area. The results are ordered by the sales transaction date in descending order.

```sql
SELECT
FOLIO,
"CODIGO UBICACIÓN",
MUNICIPIO,
EDIFICIO,
CAST("FECHA DE CONSTRUCCIÓN" AS DATE),
CAST("FECHA DE OCUPACIÓN" AS DATE),
PROPIETARIOS,
DOMICILIO,
CAST("Sales Transaction Date" AS DATE),
VALOR,
"VALOR DEL TERRENO",
"VALOR DE MEJORAS",
"VALOR DEL TRASPASO",
"SUPERFICIE INICIAL",
"Price per square meter",
HIPOTECA,
MONTO,
"TASA EFECTIVA",
"TASA NOMINAL",
"INTERÉS ANUAL",
FECI,
"INTERÉS ANUAL + FECI",
NOMBRE,
CAST(TIMESTAMP AS DATE)
FROM Metrics
WHERE
(
{{buildingList.value }}
OR EDIFICIO = {{buildingList.value}}
)
AND
(
{{unitSelection.value }}
OR DOMICILIO LIKE {{'%' + unitSelection.value + '%'}}
)
AND
(
{{folioSearch.value || folioSearch.value == '' }}
OR (FOLIO = {{folioSearch.value}} AND {{folioSearch.value}} ~ E'^\\d+$')
)
AND
(
{{!(salesDateRange.value.end && salesDateRange.value.start) }}
OR "Sales Transaction Date" IS NULL
OR (
CAST("Sales Transaction Date" AS DATE) <= {{moment(salesDateRange.value.end).format('YYYY-MM-DD')}}
AND CAST("Sales Transaction Date" AS DATE) >= {{moment(salesDateRange.value.start).format('YYYY-MM-DD')}}
)
)
AND
(
{{!(minSalesPrice.value && maxSalesPrice.value) }}
OR "VALOR DEL TRASPASO" IS NULL
OR (
"VALOR DEL TRASPASO" >= {{minSalesPrice.value}}
AND "VALOR DEL TRASPASO" <= {{maxSalesPrice.value}}
)
)
AND
(
{{!(minSqMeters.value && maxSqMeters.value) }}
OR "SUPERFICIE INICIAL" IS NULL
OR (
CAST("SUPERFICIE INICIAL" AS FLOAT) >= {{minSqMeters.value}}
AND CAST("SUPERFICIE INICIAL" AS FLOAT) <= {{maxSqMeters.value}}
)
)
ORDER BY CAST("Sales Transaction Date" AS DATE) DESC;
```
ADDED/CLARIFIED ON MAY 24TH
#### `viewUnitDetail`(this is used in the View Detail modal box in the header table)
This query retrieves detailed information about a specific unit identified by its folio number (`FOLIO`) from the `Metrics` table. The details include both date and text formats for construction and occupation dates, among other properties. This query is useful for viewing detailed information about a single unit.

```sql
SELECT
FOLIO,
"CODIGO UBICACIÓN",
MUNICIPIO,
EDIFICIO,
CAST("FECHA DE CONSTRUCCIÓN" AS TEXT) AS "FECHA DE CONSTRUCCIÓN",
CAST("FECHA DE OCUPACIÓN" AS TEXT) AS "FECHA DE OCUPACIÓN",
PROPIETARIOS,
DOMICILIO,
CAST("Sales Transaction Date" AS TEXT) AS "Sales Transaction Date",
VALOR,
"VALOR DEL TERRENO",
"VALOR DE MEJORAS",
"VALOR DEL TRASPASO",
"SUPERFICIE INICIAL",
"Price per square meter",
HIPOTECA,
MONTO,
"TASA EFECTIVA",
"TASA NOMINAL",
"INTERÉS ANUAL",
FECI,
"INTERÉS ANUAL + FECI",
NOMBRE,
CAST(TIMESTAMP AS DATE)
FROM Metrics
WHERE FOLIO = {{unitList.selectedRow.data.folio}};
```

ADDED/CLARIFIED ON MAY 24TH

### View Detail Modal Box Field Mapping Specification

#### Front-End Fields and Database Fields Mapping

1. **Folio**
   - **Front-End Field**: `Folio`
   - **Database Field**: `FOLIO`

2. **Municipality**
   - **Front-End Field**: `Municipality`
   - **Database Field**: `MUNICIPIO`

3. **Area Code**
   - **Front-End Field**: `Area Code`
   - **Database Field**: `"CODIGO UBICACIÓN"`

4. **Owner**
   - **Front-End Field**: `Owner`
   - **Database Field**: `PROPIETARIOS`

5. **Construction Date**
   - **Front-End Field**: `Construction Date`
   - **Database Field**: `CAST("FECHA DE CONSTRUCCIÓN" AS TEXT) AS "FECHA DE CONSTRUCCIÓN"`

6. **Date Occupied**
   - **Front-End Field**: `Date Occupied`
   - **Database Field**: `CAST("FECHA DE OCUPACIÓN" AS TEXT) AS "FECHA DE OCUPACIÓN"`

7. **Sales Date**
   - **Front-End Field**: `Sales Date`
   - **Database Field**: `CAST("Sales Transaction Date" AS TEXT) AS "Sales Transaction Date"`

8. **Value**
   - **Front-End Field**: `Value`
   - **Database Field**: `VALOR`

9. **Land Value**
   - **Front-End Field**: `Land Value`
   - **Database Field**: `"VALOR DEL TERRENO"`

10. **Improvement Value**
    - **Front-End Field**: `Improvement Value`
    - **Database Field**: `"VALOR DE MEJORAS"`

11. **Sales Amount**
    - **Front-End Field**: `Sales Amount`
    - **Database Field**: `"VALOR DEL TRASPASO"`

12. **Square Meters**
    - **Front-End Field**: `Square Meters`
    - **Database Field**: `"SUPERFICIE INICIAL"`

13. **Price per Square Meter**
    - **Front-End Field**: `Price per Square Meter`
    - **Database Field**: `"Price per square meter"`

14. **Loan?**
    - **Front-End Field**: `Loan?`
    - **Database Field**: `HIPOTECA`

15. **Loan Amount**
    - **Front-End Field**: `Loan Amount`
    - **Database Field**: `MONTO`

16. **Effective Mortgage Rate**
    - **Front-End Field**: `Effective Mortgage Rate`
    - **Database Field**: `"TASA EFECTIVA"`

17. **Nominal Mortgage Rate**
    - **Front-End Field**: `Nominal Mortgage Rate`
    - **Database Field**: `"TASA NOMINAL"`

18. **Annual Interest Rate**
    - **Front-End Field**: `Annual Interest Rate`
    - **Database Field**: `"INTERÉS ANUAL"`

19. **FECI**
    - **Front-End Field**: `FECI`
    - **Database Field**: `FECI`

20. **Annual Interest Rate + FECI**
    - **Front-End Field**: `Annual Interest Rate + FECI`
    - **Database Field**: `"INTERÉS ANUAL + FECI"`

21. **Lending Entity**
    - **Front-End Field**: `Lending Entity`
    - **Database Field**: `NOMBRE`

22. **Date Added**
    - **Front-End Field**: `Date Added`
    - **Database Field**: `CAST(TIMESTAMP AS DATE)`

#### `unitCount`
This query counts the number of records in the `Metrics` table that match a specific building name (`buildingList.value`), after trimming any leading or trailing spaces from the building name. This can be used to quickly determine how many units are associated with a particular building.

```sql
SELECT COUNT(*) AS record_count
FROM Metrics
WHERE EDIFICIO LIKE TRIM({{buildingList.value}});
```

#### `unitDropdown`
Similar to `unitCount`, this query retrieves a list of distinct unit addresses (`DOMICILIO`) from the `Metrics` table for a specific building (`buildingList.value`). It also applies a date range filter based on the sales transaction date. This can be used to populate a dropdown menu with available units for a selected building and date range.

```sql
SELECT DISTINCT DOMICILIO
FROM Metrics
WHERE
EDIFICIO = {{buildingList.value}}
AND
(
{{!(salesDateRange.value.end && salesDateRange.value.start) }}
OR (
CAST("Sales Transaction Date" AS DATE) <= {{moment(salesDateRange.value.end).format('YYYY-MM-DD')}}
AND CAST("Sales Transaction Date" AS DATE) >= {{moment(salesDateRange.value.start).format('YYYY-MM-DD')}}
)
);
```

#### `viewPDFSummary`
This query retrieves information about a PDF file associated with a specific unit identified by its folio number (`FOLIO`) from the `PDF_Raw_Data` table. This includes the filename and the text content of the PDF, which could be useful for reviewing documents related to a specific property transaction.

```sql
SELECT
FOLIO,
Filename,
"PDF Text"
FROM PDF_Raw_Data
WHERE FOLIO = {{unitList.selectedRow.data.folio}};
```

DETAILED SCHEMA VIEW OF ALL TABLES

### Users Table
Stores user information, including personal details and classification.

```sql
-- Users Table: Stores user information
CREATE TABLE Users (
    UserId SERIAL PRIMARY KEY, -- Unique identifier for each user
    FirstName TEXT NOT NULL, -- User's first name
    LastName TEXT NOT NULL, -- User's last name
    Address TEXT, -- User's address
    Country TEXT, -- User's country
    Email TEXT UNIQUE NOT NULL, -- User's email address (must be unique)
    Password TEXT NOT NULL, -- User's password (hashed)
    Classification TEXT NOT NULL, -- User's classification (e.g., Real Estate Agent, Investor)
    LanguagePreference TEXT DEFAULT 'English', -- User's preferred language
    CurrencyPreference TEXT DEFAULT 'USD', -- User's preferred currency
    SubscriptionLevel TEXT DEFAULT 'Free', -- User's subscription level (Free or Premium)
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the user was created
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp when the user was last updated
);
```

### Roles Table
Defines different roles available in the system.

```sql
-- Roles Table: Defines different roles
CREATE TABLE Roles (
    RoleId SERIAL PRIMARY KEY, -- Unique identifier for each role
    RoleName TEXT UNIQUE NOT NULL, -- Name of the role (must be unique)
    Description TEXT -- Description of the role
);
```

### UserRoles Table
Manages the many-to-many relationship between users and roles.

```sql
-- UserRoles Table: Manages the many-to-many relationship between users and roles
CREATE TABLE UserRoles (
    UserRoleId SERIAL PRIMARY KEY, -- Unique identifier for each user-role relationship
    UserId INT NOT NULL, -- Foreign key to Users table
    RoleId INT NOT NULL, -- Foreign key to Roles table
    FOREIGN KEY (UserId) REFERENCES Users(UserId) ON DELETE CASCADE, -- Cascade delete if user is deleted
    FOREIGN KEY (RoleId) REFERENCES Roles(RoleId) ON DELETE CASCADE -- Cascade delete if role is deleted
);
```

### Permissions Table
Defines various permissions that can be granted to roles.

```sql
-- Permissions Table: Defines various permissions
CREATE TABLE Permissions (
    PermissionId SERIAL PRIMARY KEY, -- Unique identifier for each permission
    PermissionName TEXT UNIQUE NOT NULL, -- Name of the permission (must be unique)
    Description TEXT -- Description of the permission
);
```

### RolePermissions Table
Manages the many-to-many relationship between roles and permissions.

```sql
-- RolePermissions Table: Manages the many-to-many relationship between roles and permissions
CREATE TABLE RolePermissions (
    RolePermissionId SERIAL PRIMARY KEY, -- Unique identifier for each role-permission relationship
    RoleId INT NOT NULL, -- Foreign key to Roles table
    PermissionId INT NOT NULL, -- Foreign key to Permissions table
    FOREIGN KEY (RoleId) REFERENCES Roles(RoleId) ON DELETE CASCADE, -- Cascade delete if role is deleted
    FOREIGN KEY (PermissionId) REFERENCES Permissions(PermissionId) ON DELETE CASCADE -- Cascade delete if permission is deleted
);
```

### Folios Table
Stores detailed information about properties.

```sql
-- Folios Table: Stores detailed information about properties
CREATE TABLE Folios (
    FolioId SERIAL PRIMARY KEY, -- Unique identifier for each folio
    FOLIO BIGINT NOT NULL, -- Folio number
    MODULO TEXT, -- Module information
    "CODIGO UBICACIÓN" INTEGER, -- Location code
    MUNICIPIO TEXT, -- Municipality
    EDIFICIO TEXT NOT NULL, -- Building name
    PROPIETARIOS TEXT, -- Owners
    "FOLIO / FINCA / FICHA" TEXT, -- Folio/Finca/Ficha
    "FECHA DE INSCRIPCIÓN" DATE, -- Registration date
    PROPIETARIO TEXT, -- Owner
    DOMICILIO TEXT, -- Address
    "USO DEL SUELO" TEXT, -- Land use
    "OTRO TIPO" TEXT, -- Other type
    DESCRIPCIÓN TEXT, -- Description
    "POR EDIFICIO" TEXT, -- By building
    "% DE PROINDIVISO" TEXT, -- Percentage of indivisible
    "CÉDULA CATASTRAL" TEXT, -- Cadastral certificate
    VALOR DECIMAL, -- Value
    "VALOR DEL TERRENO" DECIMAL, -- Land value
    "VALOR DE MEJORAS" DECIMAL, -- Improvements value
    "VALOR DEL TRASPASO" DECIMAL, -- Transfer value
    "NÚMERO DE PLANO" TEXT, -- Plan number
    "FECHA DE CONSTRUCCIÓN" DATE, -- Construction date
    "FECHA DE OCUPACIÓN" DATE, -- Occupation date
    LOTE TEXT, -- Lot
    "SUPERFICIE INICIAL" TEXT, -- Initial surface
    "SUPERFICIE / RESTO LIBRE" TEXT, -- Remaining surface
    COLINDANCIAS TEXT, -- Boundaries
    "TIMESTAMP ADDED TO CSV" TIMESTAMP, -- Timestamp added to CSV
    "DERECHOS / ACTOS / OTRAS OPERACIONES" TEXT -- Rights/Acts/Other operations
);
```

### FoliosHistory Table
Captures historical changes made to the `Folios` table.

```sql
-- FoliosHistory Table: Captures historical changes made to the Folios table
CREATE TABLE FoliosHistory (
    HistoryId SERIAL PRIMARY KEY, -- Unique identifier for each history record
    FOLIO BIGINT NOT NULL, -- Folio number
    MODULO TEXT, -- Module information
    "CODIGO UBICACIÓN" INTEGER, -- Location code
    MUNICIPIO TEXT, -- Municipality
    EDIFICIO TEXT NOT NULL, -- Building name
    PROPIETARIOS TEXT, -- Owners
    "FOLIO / FINCA / FICHA" TEXT, -- Folio/Finca/Ficha
    "FECHA DE INSCRIPCIÓN" DATE, -- Registration date
    PROPIETARIO TEXT, -- Owner
    DOMICILIO TEXT, -- Address
    "USO DEL SUELO" TEXT, -- Land use
    "OTRO TIPO" TEXT, -- Other type
    DESCRIPCIÓN TEXT, -- Description
    "POR EDIFICIO" TEXT, -- By building
    "% DE PROINDIVISO" TEXT, -- Percentage of indivisible
    "CÉDULA CATASTRAL" TEXT, -- Cadastral certificate
    VALOR DECIMAL, -- Value
    "VALOR DEL TERRENO" DECIMAL, -- Land value
    "VALOR DE MEJORAS" DECIMAL, -- Improvements value
    "VALOR DEL TRASPASO" DECIMAL, -- Transfer value
    "NÚMERO DE PLANO" TEXT, -- Plan number
    "FECHA DE CONSTRUCCIÓN" DATE, -- Construction date
    "FECHA DE OCUPACIÓN" DATE, -- Occupation date
    LOTE TEXT, -- Lot
    "SUPERFICIE INICIAL" TEXT, -- Initial surface
    "SUPERFICIE / RESTO LIBRE" TEXT, -- Remaining surface
    COLINDANCIAS TEXT, -- Boundaries
    "TIMESTAMP ADDED TO CSV" TIMESTAMP, -- Timestamp added to CSV
    "DERECHOS / ACTOS / OTRAS OPERACIONES" TEXT, -- Rights/Acts/Other operations
    ChangeTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of the change
    FOREIGN KEY (FOLIO, EDIFICIO) REFERENCES Folios(FOLIO, EDIFICIO) -- Foreign key to Folios table
);
```

### Subscriptions Table
Manages user subscriptions and links to Stripe for billing.

```sql
-- Subscriptions Table: Manages user subscriptions and links to Stripe for billing
CREATE TABLE Subscriptions (
    SubscriptionId SERIAL PRIMARY KEY, -- Unique identifier for each subscription
    UserId INT NOT NULL, -- Foreign key to Users table
    SubscriptionLevel TEXT NOT NULL, -- Subscription level (e.g., Free, Premium)
    StripeCustomerId TEXT, -- Stripe customer ID
    StripeSubscriptionId TEXT, -- Stripe subscription ID
    StartDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Subscription start date
    EndDate TIMESTAMP, -- Subscription end date
    FOREIGN KEY (UserId) REFERENCES Users(UserId) -- Foreign key to Users table
);
```

### UserBuildings Table
Restricts the number of buildings a user can view.

```sql
-- UserBuildings Table: Restricts the number of buildings a user can view
CREATE TABLE UserBuildings (
    UserBuildingId SERIAL PRIMARY KEY, -- Unique identifier for each user-building relationship
    UserId INT NOT NULL, -- Foreign key to Users table
    BuildingId INT NOT NULL, -- Foreign key to Folios table
    FOREIGN KEY (UserId) REFERENCES Users(UserId) ON DELETE CASCADE, -- Cascade delete if user is deleted
    FOREIGN KEY (BuildingId) REFERENCES Folios(FolioId) ON DELETE CASCADE -- Cascade delete if building is deleted
);
```

### Example Data Insertion
To illustrate how this schema works, here are some example SQL statements to insert data into these tables:

#### Insert Users
```sql
INSERT INTO Users (FirstName, LastName, Address, Country, Email, Password, Classification)
VALUES ('John', 'Doe', '123 Main St', 'USA', 'john.doe@example.com', 'hashed_password', 'Real Estate Agent');

INSERT INTO Users (FirstName, LastName, Address, Country, Email, Password, Classification)
VALUES ('Jane', 'Smith', '456 Elm St', 'USA', 'jane.smith@example.com', 'hashed_password', 'Investor');
```

#### Insert Buildings
```sql
INSERT INTO Folios (FOLIO, MODULO, "CODIGO UBICACIÓN", MUNICIPIO, EDIFICIO, PROPIETARIOS, "FOLIO / FINCA / FICHA", "FECHA DE INSCRIPCIÓN", PROPIETARIO, DOMICILIO, "USO DEL SUELO", "OTRO TIPO", DESCRIPCIÓN, "POR EDIFICIO", "% DE PROINDIVISO", "CÉDULA CATASTRAL", VALOR, "VALOR DEL TERRENO", "VALOR DE MEJORAS", "VALOR DEL TRASPASO", "NÚMERO DE PLANO", "FECHA DE CONSTRUCCIÓN", "FECHA DE OCUPACIÓN", LOTE, "SUPERFICIE INICIAL", "SUPERFICIE / RESTO LIBRE", COLINDANCIAS, "TIMESTAMP ADDED TO CSV", "DERECHOS / ACTOS / OTRAS OPERACIONES")
VALUES (123456, 'Module1', 1001, 'New York', 'Building A', 'Owner1', 'Folio1', '2022-01-01', 'Owner1', '123 Main St', 'Residential', 'Type1', 'Description1', 'Building1', '50%', '123456789', 1000000, 500000, 300000, 200000, 'Plan1', '2020-01-01', '2021-01-01', 'Lot1', '1000 sqft', '500 sqft', 'North, South, East, West', '2022-01-01 00:00:00', 'Rights1');

INSERT INTO Folios (FOLIO, MODULO, "CODIGO UBICACIÓN", MUNICIPIO, EDIFICIO, PROPIETARIOS, "FOLIO / FINCA / FICHA", "FECHA DE INSCRIPCIÓN", PROPIETARIO, DOMICILIO, "USO DEL SUELO", "OTRO TIPO", DESCRIPCIÓN, "POR EDIFICIO", "% DE PROINDIVISO", "CÉDULA CATASTRAL", VALOR, "VALOR DEL TERRENO", "VALOR DE MEJORAS", "VALOR DEL TRASPASO", "NÚMERO DE PLANO", "FECHA DE CONSTRUCCIÓN", "FECHA DE OCUPACIÓN", LOTE, "SUPERFICIE INICIAL", "SUPERFICIE / RESTO LIBRE", COLINDANCIAS, "TIMESTAMP ADDED TO CSV", "DERECHOS / ACTOS / OTRAS OPERACIONES")
VALUES (789012, 'Module2', 1002, 'Los Angeles', 'Building B', 'Owner2', 'Folio2', '2022-02-01', 'Owner2', '456 Elm St', 'Commercial', 'Type2', 'Description2', 'Building2', '60%', '987654321', 2000000, 1000000, 600000, 400000, 'Plan2', '2019-01-01', '2020-01-01', 'Lot2', '2000 sqft', '1000 sqft', 'North, South, East, West', '2022-02-01 00:00:00', 'Rights2');
```

#### Assign Buildings to Users
```sql
INSERT INTO UserBuildings (UserId, BuildingId)
VALUES (1, 1), (1, 2);  -- User 1 (John Doe) can view Building A and Building B

INSERT INTO UserBuildings (UserId, BuildingId)
VALUES (2, 1), (2, 2), (2, 3);  -- User 2 (Jane Smith) can view Building A, Building B, and Building C
```

### Query to Retrieve Buildings a User Can View
To retrieve the buildings that a specific user can view, you can use the following SQL query:

```sql
SELECT b.EDIFICIO, b.Address, b.City, b.Country
FROM Folios b
JOIN UserBuildings ub ON b.FolioId = ub.BuildingId
WHERE ub.UserId = 1;  -- Replace 1 with the UserId of the user you are querying for
```

### Summary
- **Users Table**: Stores user information.
- **Roles Table**: Defines different roles.
- **UserRoles Table**: Manages the many-to-many relationship between users and roles.
- **Permissions Table**: Defines various permissions.
- **RolePermissions Table**: Manages the many-to-many relationship between roles and permissions.
- **Folios Table**: Stores detailed information about properties.
- **FoliosHistory Table**: Captures historical changes made to the `Folios` table.
- **Subscriptions Table**: Manages user subscriptions and links to Stripe for billing.
- **UserBuildings Table**: Restricts the number of buildings a user can view.

This comprehensive database schema ensures robust user management, role-based access control, detailed audit logging, efficient subscription management, and the ability to restrict users on the number of buildings they can view. This layout is designed to meet the requirements of the Panacomps Web Application while ensuring scalability and security.

