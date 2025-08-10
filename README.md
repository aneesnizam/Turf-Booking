# GoTurfy: Your Ultimate Turf Booking Platform ⚽

![Work in Progress](https://img.shields.io/badge/status-work%20in%20progress-yellow.svg)

TurfLink is a comprehensive web application designed to connect turf owners with players, simplifying the process of finding and booking sports turfs. Built with Django, this platform provides a seamless experience for both users looking for a place to play and owners looking to manage their facilities.



## Table of Contents

- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Built With](#built-with)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Future Features](#future-features)

---
## About The Project

Finding and booking a local sports turf can be a fragmented process involving phone calls and uncertain availability. TurfLink aims to solve this by creating a centralized marketplace. Users can search for turfs based on location, sport, and availability, while turf owners get a simple platform to list their venues and manage bookings. This project handles complex features like overnight booking schedules, location-based searching, and user reviews to create a reliable and user-friendly service.

---
## Key Features

### For Users
* **User Authentication:** Secure user registration (as a player or a turf owner) and login.
* **Profile Management:** Users can update their personal details and profile picture.
* **Advanced Turf Search:**
    * Search for turfs by city, place, or district.
    * Filter turfs by available sports (e.g., Football, Cricket).
    * Filter by a specific time window, with correct handling for overnight turfs.
* **Location-Based Discovery:** Automatically finds and recommends turfs near the user's current location, displaying the distance in kilometers.
* **Detailed Turf Pages:** View turf photos, amenities, opening hours, cost, and user ratings.
* **Real-time Availability:** A dynamic calendar lets users select a date and see available 30-minute slots in real-time.
* **Booking System:** A seamless booking process with a confirmation modal.
* **Booking Management:** A personal dashboard to view upcoming and past bookings.
* **Favorites:** Users can save their favorite turfs for quick access.
* **Ratings & Reviews:** Users can rate and review their completed bookings to help the community.

### Technical Features
* **AJAX-powered:** The turf list and availability slots update dynamically without page reloads.
* **PDF Invoice Generation:** Users can download a PDF invoice for their bookings.
* **QR Code Generation:** Each booking has a unique QR code that links to the booking details page, perfect for on-site verification.

---
## Built With

This project is built with a modern and robust tech stack:

* **Backend:**
    * [Python](https://www.python.org/)
    * [Django](https://www.djangoproject.com/)
* **Database:**
    * [PostgreSQL](https://www.postgresql.org/)
* **Frontend:**
    * HTML5 & CSS3
    * [Tailwind CSS](https://tailwindcss.com/)
    * [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
* **Key Python Libraries:**
    * `xhtml2pdf` for PDF generation.
    * `qrcode` for QR code creation.
    * `Pillow` for image processing.

---
## Getting Started

To get a local copy up and running, follow these simple steps.

1.  **Clone the repo**
    ```sh
    git clone [https://github.com/your_username/your_project_name.git](https://github.com/your_username/your_project_name.git)
    ```
2.  **Create and Activate a Virtual Environment**
    ```sh
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On Mac/Linux
    source venv/bin/activate
    ```
3.  **Create a `requirements.txt` file**
    If you haven't already, create a file listing all the necessary packages.
    ```sh
    pip freeze > requirements.txt
    ```
4.  **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```
5.  **Set Up Environment Variables**
    Create a `.env` file in the root directory and add your secret keys:
    ```
    SECRET_KEY='your-super-secret-key'
    DEBUG=True
    DATABASE_URL='postgres://user:password@host:port/dbname'
    ```
6.  **Run Database Migrations**
    ```sh
    python manage.py migrate
    ```
7.  **Create a Superuser**
    ```sh
    python manage.py createsuperuser
    ```
8.  **Run the Development Server**
    ```sh
    python manage.py runserver
    ```
    Your project will be available at `http://127.0.0.1:8000/`.

---
## Project Structure

The project is organized into two main Django apps:
* `accounts/`: Handles all models related to users, turfs, and bookings (`User`, `Turf`, `Booking`, `Rating`, etc.) and the registration/login forms.
* `core/`: Contains the main business logic and views for the website (`home`, `turfs`, `turf_details`, etc.).

---
## Future Features

This is an ongoing project with many potential features to add:
* **Payment Gateway Integration:** Integrate Stripe or Razorpay to handle online payments.
* **Real-time Notifications:** Use Django Channels to send real-time notifications for booking confirmations and reminders.
* **Owner's Dashboard Analytics:** Provide turf owners with charts and stats on their earnings and booking frequency.
* **Advanced Filtering:** Add filters for turf amenities (e.g., parking, floodlights).