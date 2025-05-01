## I.  Introduction

This document provides a comprehensive specification for the optimization and enhancement of the Panacomps Web Application. The application serves as a pivotal tool for real estate professionals, investors, and law enforcement agencies, offering in-depth analysis and data on property transactions within Panama. The upcoming enhancements aim to refine user experience, expand functionality, and ensure the application's adaptability to a broader audience.


## II. Core Enhancements

### 1. **Performance Optimization**

**Database Queries**: Optimize SQL queries to reduce execution time and resource consumption. Implement indexing strategies for frequently queried columns to enhance data retrieval speed.

**Front-End Performance**: Minimize the use of heavy JavaScript libraries and optimize asset loading. Implement lazy loading for images and non-critical resources.

- **Caching Mechanisms**: Utilize caching for frequently accessed data to reduce database load and improve response times.

### 2. **User Interface and Experience**

**Responsive Design**: Ensure the application is fully responsive across various devices and screen sizes, providing a seamless experience on desktops, tablets, and smartphones.

**Intuitive Navigation**: Revamp the navigation structure to facilitate easy access to all application features. Implement a dashboard for quick insights and shortcuts to common tasks.

### 3. **Localization and Internationalization**

**Multi-Language Support**: Integrate a language selection feature, offering English, Spanish, and Brazilian Portuguese. Ensure all UI elements and content are localized.

**Currency Conversion**: Allow users to select their preferred currency for financial data. Implement real-time currency conversion based on the latest exchange rates.

To ensure the Panacomps Web Application is fully responsive and provides a seamless experience across various devices, including desktops, tablets, and smartphones, the following technical specifications and enhancements are proposed:

### 4. Responsive Design Specifications

#### Adaptive Layouts
Implement adaptive layouts using CSS media queries to ensure the application's interface automatically adjusts to the screen size of the device it is being viewed on.Design distinct layouts for key breakpoints (e.g., desktop, tablet, and smartphone) to optimize usability and aesthetics across devices.

## III. User Management

### 1. **User Profiles**

#### User Classifications
The application supports distinct user classifications, each tailored to the specific needs and access requirements of different user groups:

   - **Real Estate Agent**
   - **Broker**
   - **Law Enforcement**
   - **Investor**
   - **Other**
   - **Administrator**: Full access to all system functionalities including user management, data oversight, and system settings.

   ADDED/CLARIFIED MAY 24TH.
   Please add a dropdown for User Groups with possible values of Real Estate Agent, Broker, Law Enforcement, Investor and Other. The default classficiation for a new user is "Real Estate Agent". 


#### User Registration

New users can register through an online form that captures essential information:

   - **Personal Information**: First name, last name, and address with an option to select the country from a dropdown menu.

   - **Contact Details**: Email address which will also serve as the login identifier.

   - **User Classification**: Users choose their classification from a dropdown menu. The "Administrator" classification is not available for selection and is assigned directly by an existing administrator.

   ADDED/CLARIFIED MAY 24TH.
   1.	First Name*
   2.	Last Name*
   3.	Email*
   4.	Language (default to “English”), language options in the dropdown should be English, Spanish, and Portuguese.
   5.	Currency (default to USD), currency options are USD, BRL,EUROS
   6.	Username*
   7.	Password*
   

#### User Information

Each user profile includes comprehensive personal and professional details:
   - **Profile Overview**: Displays the user's full name, email, and address.
   - **Classification and Permissions**: Shows the user's classification and a summary of their access permissions.

   - **Associated Buildings**: Lists buildings associated with the user, with options to view detailed property information directly from the profile.

   - **Edit Profile**: Users can update their personal information and preferences, including password changes and notification settings.

### 2. **Administrator Capabilities**

#### User Management

Administrators can manage user accounts through a dedicated management interface:

   - **View Users**: A searchable list of all users with filters by classification, name, or associated building.

   - **Edit User Details**: Administrators can update user information including classification and associated buildings.

   - **Delete Users**: Option to remove users from the system with a required confirmation step to prevent accidental deletions.

   - **Assign Buildings**: Administrators can associate one or more buildings with a user, enhancing the user's access to specific property data.

#### Admin Search Result Customization

Administrators can customize the visibility of search result fields for different users:
   - **Field Visibility Settings**: A checkbox interface allows administrators to enable or disable visibility of specific data fields in the search results.

   - **User-Specific Customization**: Customization can be applied at the individual user level or based on user classification.

   - **Preview Changes**: Administrators can preview how search results will appear for a user before applying changes.

#### Search Result Export

Control over the export functionality of search results:

   - **Enable/Disable Export**: Administrators can toggle the ability for users to export search results to Excel. This can be set globally or customized for specific user classifications.

   - **Export Settings**: Define the format and data fields included in the export, ensuring users receive precisely the data they need.

   - **Audit Trails**: Maintain logs of all export activities for compliance and monitoring purposes.

These detailed functionalities ensure that the Panacomps Web Application remains adaptable, secure, and highly functional, catering to the diverse needs of its user base while providing administrators with robust tools to manage the system effectively.


## IV. New Functionality


### Historical Data Viewing

To enhance the user's ability to perform comprehensive property analysis, a new feature will be introduced that allows viewing the historical data of a property unit or folio. This feature will leverage an existing database table that captures historical changes in property data, such as sales pricing updates.
Functionality

#### View History Button: 
Each property listing in the search results will include a "View History" button. This button will be contextually placed alongside existing options such as "View Details".
History Modal Window: Upon clicking the "View History" button, a modal window will appear 
displaying the historical data of the selected property unit. This modal will be designed to provide a clear and detailed view of all historical entries related to the property.

       


#### Data Presentation
Timeline View: The historical data will be presented in a chronological timeline format within the modal window. Each entry in the timeline will detail significant changes or updates to the property, such as changes in ownership, sales transactions, and price adjustments.

#### Data Fields: 
The modal will display relevant historical data fields from the database, including but not limited to:
Date of the transaction or update
Old and new values of changed fields
Source of the update (if available)
Any relevant notes or comments associated with the update


## VII. Billing and Subscription Management

To cater to the diverse needs of users and provide a sustainable revenue model, the Panacomps Web Application will introduce a tiered subscription system with a free and premium level. This section outlines the specifications for implementing billing and subscription functionality.

### 1. **User Subscription Levels**

#### Free Level

**Access Limitations**: Users on the free level will have access to a limited number of buildings and property records, with restrictions on advanced features and data exports.

- **Registration Process**: New users will be able to register for the free level by providing their personal and contact information, as outlined in the "User Registration" section.

#### Premium Level

**Expanded Access**: Premium users will have unrestricted access to all buildings and property records, as well as advanced features such as market trend analysis, collaboration tools, and customizable search result exports.

- **Subscription Plans**: Multiple premium subscription plans will be available, offering different levels of access and features at varying price points (e.g., monthly, annual).

### Updated Access Requirements for Free and Premium Levels in Markdown Format

#### Free Level Access

**Access Limitations**: Users on the free level will have restricted visibility and functionality within the application.

- **Registration Process**: New users can register for the free level by providing required personal and contact details.
- **Record Visibility**: Free users can access only the first 2 records in search results. Additional records beyond the first two will be redacted.
- **Field Visibility**:
  - **Visible Fields in Search Results**: `Unit`, `Folio`, `Sales Date`, and `Sales Amount`.
  - **Redacted Fields in Search Results**: All other fields are redacted.
- **Detailed View Accessibility**:
  - Free users can open the detailed view, but critical fields such as `Owner`, `Area Code`, `Value`, `Land Value`, and `Improvement Value` will be redacted.
  - Only basic information like `Building`, `Folio`, and `Sales Date` will be visible.
- **Data Download**: Download functionality is disabled for free users.

#### Premium Level Access

**Expanded Access**: Premium users will enjoy full access to the application without any restrictions.

- **Subscription Plans**: Offers various subscription plans including monthly and annual options, providing different levels of access and features.
- **Record Visibility**: Premium users have access to an unlimited number of records in the search results.
- **Field Visibility**:
  - All fields visible in both search results and detailed views, including `Unit`, `Folio`, `Municipality`, `Area Code`, `Owner`, `Construction Date`, `Date Occupied`, `Sales Date`, `Value`, `Land Value`, `Improvement Value`, and `Sales Amount`.
- **Detailed View Accessibility**:
  - Full access to detailed information including proprietary data fields in the detailed view mode.
- **Data Download**: Premium users have the exclusive ability to download search results and detailed information, which is critical for offline analysis and reporting.

**Advanced Features**:
- **Market Trend Analysis**: Available only to premium users, providing deep insights into market dynamics.
- **Collaboration Tools**: Enable premium users to collaborate with team members within the platform.
- **Customizable Search Result Exports**: Premium users can export search results with flexibility in selecting which fields to include, suitable for reporting and analysis purposes.

### 2. **Billing Integration**

The application will integrate with a third-party billing platform, such as Stripe, to handle secure payment processing and subscription management.

#### Stripe Integration

**Payment Gateway**: Utilize Stripe's payment gateway to securely collect and process user payments for premium subscriptions.

**Subscription Management**: Leverage Stripe's subscription management features to handle recurring billing, plan upgrades/downgrades, and cancellations.

- **Secure Checkout**: Implement Stripe's secure checkout flow, allowing users to enter their payment information and complete the subscription purchase process within the application.

#### User Profile Updates

**Subscription Status**: Upon successful subscription purchase, the user's profile will be updated to reflect their premium status, granting them access to the corresponding features and data.

- **Expiration Handling**: Implement mechanisms to handle subscription expirations, prompting users to renew their subscription or downgrading their access to the free level.

### 3. **Billing User Interface**

A dedicated billing section will be added to the application, accessible from the user's profile or a centralized billing dashboard.

#### Subscription Management

**Plan Selection**: Users will be able to view and select available subscription plans, with clear descriptions of the features and pricing for each plan.

**Billing Information**: Users can update their billing information, including payment methods and billing addresses.

- **Subscription History**: A history of past and current subscriptions will be available, including start and end dates, plan details, and payment records.

#### Notifications and Reminders

**Renewal Reminders**: Users will receive email and in-app notifications when their subscription is nearing expiration, prompting them to renew their plan.

- **Payment Failure Alerts**: In case of failed payments, users will be notified with clear instructions on how to update their payment information or resolve any issues.

### 4. **Reporting and Analytics**

To support business intelligence and decision-making, the application will include reporting and analytics capabilities related to billing and subscriptions.

**Subscription Metrics**: Track key metrics such as the number of active subscribers, subscription revenue, churn rates, and plan popularity.

**Revenue Reporting**: Generate reports on subscription revenue, including breakdowns by plan type, time period, and user segments.

- **User Behavior Analysis**: Analyze user behavior patterns related to subscription purchases, upgrades, and cancellations to identify opportunities for improvement.

By implementing these billing and subscription management features, the Panacomps Web Application will be able to monetize its services effectively, while providing users with flexible options to access the platform's features based on their specific needs and budgets.








### SCREENSHOTS

Below are screenshots of the existing Retool Panacomps Webs solution (in Production and accessible)





























