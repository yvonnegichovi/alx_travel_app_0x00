# ALX Travel App: Milestone 2 – Database Modeling, Serializers, and Seeders

This milestone builds upon the foundational work of the `alx_travel_app` project. It focuses on three core backend elements:

* Designing robust database models
* Defining API data structures with serializers
* Implementing data seeding for development and testing

These are fundamental steps in creating a scalable and testable travel listing platform.

---

## About the Project

Milestone 2 deepens your understanding of Django’s ORM and Django REST Framework (DRF). You'll:

* Create relational data models with proper relationships and constraints
* Build serializers to handle data exchange via API
* Seed your database with realistic mock data using custom Django commands

---

## Learning Objectives

By the end of this milestone, you should be able to:

* **Design Robust Models**: Build Django models like `Listing`, `Booking`, and `Review` with correct fields, foreign key relations, and choices.
* **Create Effective Serializers**: Use DRF serializers to control data input/output, handle nested relationships, and apply validations.
* **Seed Sample Data**: Write a custom Django management command to generate mock users, listings, bookings, and reviews with the `Faker` library.
* **Follow Best Practices**: Apply industry standards in ORM modeling, serialization, and management command structure.

---

## Requirements

Ensure the following before beginning:

* A copy of the project folder: `alx_travel_app_0x00` duplicated from Milestone 1
* Familiarity with Django models and DRF
* Basic understanding of relational database design
* `Faker` library installed (`pip install Faker`)
* All Milestone 1 dependencies installed and working

---

## Task 0: Modeling, Serializers, and Seeder

### Objective

Establish your data structure and populate your development database with mock data.

---

### Instructions Followed

#### Project Duplication

Duplicated `alx_travel_app` as `alx_travel_app_0x00`.

#### Models: `listings/models.py`

Defined the following models:

* **Listing**

  * `listing_id`: UUID (Primary Key)
  * `host`: ForeignKey → `AUTH_USER_MODEL`
  * `name`, `description`, `location`, `price_per_night`, timestamps

* **Booking**

  * `booking_id`: UUID (PK)
  * `listing`: ForeignKey → `Listing`
  * `guest`: ForeignKey → `AUTH_USER_MODEL`
  * `start_date`, `end_date`, `total_price`, `status` (ChoiceField), timestamps

* **Review**

  * `review_id`: UUID (PK)
  * `listing`: FK → `Listing`
  * `guest`: FK → `AUTH_USER_MODEL`
  * `rating` (1–5), `comment`, `created_at`

All models include:

* `__str__` methods
* Appropriate `Meta` class options

---

#### Serializers: `listings/serializers.py`

* **ListingSerializer**

  * Includes `host_username` (readable) and `host` (write-only)

* **BookingSerializer**

  * Includes `guest_username`, `listing_name` (readable)
  * `listing`, `guest` are write-only
  * Validates dates and calculates `total_price` internally

* **ReviewSerializer**

  * Includes `listing_name`, `guest_username`
  * Validates that `rating` is within the 1–5 range

---

#### Seeder Command: `listings/management/commands/seed.py`

Created a Django management command `seed` that:

* Uses `Faker` to generate realistic data
* Supports the following arguments:

  * `--num_users`
  * `--num_listings`
  * `--num_bookings_per_listing`
  * `--num_reviews_per_listing`
  * `--clear` to wipe existing data
* Wraps all database operations in `transaction.atomic()` for data integrity

---

## 🧪 How to Run the Seeder

1. **Activate Virtual Environment**

2. **Install Faker**

   ```bash
   pip install Faker
   ```

3. **Make Migrations**

   ```bash
   python manage.py makemigrations listings
   ```

4. **Apply Migrations**

   ```bash
   python manage.py migrate
   ```

5. **Seed the Database**
   Run with default options:

   ```bash
   python manage.py seed --num_users 20 --num_listings 100 --num_bookings_per_listing 10 --num_reviews_per_listing 5
   ```

   To clear existing data before seeding:

   ```bash
   python manage.py seed --clear
   ```

---

## Solution Files

* `listings/models.py`
* `listings/serializers.py`
* `listings/management/commands/seed.py`
* `README.md` (this file)
