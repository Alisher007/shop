# Shop Online Platform

## 🚀 Overview

This repository hosts a comprehensive **online shop platform** built with Django, designed to offer a modern and feature-rich e-commerce experience.

## ✨ Key Features

* **User Authentication:** Secure user registration and login powered by `django-allauth`.
* **Shopping Cart & Sessions:** Robust, session-based shopping cart functionality for seamless user experience.
* **Asynchronous Processing:** Efficient background task management using **Celery** and **Celery Beat**, with real-time monitoring via **Flower**.
* **Payment Integration (Stripe):** Secure and seamless payment processing through **Stripe**, leveraging webhooks for real-time payment notifications and order fulfillment.
* **Order Management:**
    * Flexible order data export to **CSV** files.
    * Dynamic generation of professional **PDF invoices**.
* **Promotional System:** Integrated coupon system to facilitate discounts and special offers.

## 📦 Technologies Used

This project leverages a robust and scalable tech stack:

* **Django:** High-level Python web framework for rapid development and clean design.
* **PostgreSQL:** Powerful, open-source relational database for reliable data storage.
* **Redis:** In-memory data structure store, utilized for caching and as a high-performance message broker for Celery.
* **Celery:** Distributed task queue for handling asynchronous operations, improving application responsiveness.
* **Celery Beat:** Scheduler for periodically executing Celery tasks, enabling automated processes.

### ⚙️ Production Environment Technologies:

* **Docker:** Containerization platform ensuring consistent, isolated, and easily deployable environments across different stages.
* **Gunicorn:** Python WSGI HTTP Server for UNIX, serving as a robust application server for Django.
* **Nginx:** High-performance web server and reverse proxy, efficiently handling requests and serving static files.

## �� Getting Started

To get this project up and running on your local machine, follow these steps:

### Prerequisites

Ensure you have the following installed:

* [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Alisher007/shop.git](https://github.com/Alisher007/shop.git)
    cd shop
    ```

2.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project directory. This file will store your environment variables, including sensitive credentials.
    ```
    # Example .env content (replace with your actual values)
    DJANGO_SECRET_KEY='your_django_secret_key_here'
    STRIPE_PUBLISHABLE_KEY='pk_test_...'
    STRIPE_SECRET_KEY='sk_test_...'
    STRIPE_WEBHOOK_SECRET='whsec_...'
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    # Add other environment variables required by your Django app
    ```
    * **Important:** Never share your `.env` file or commit it to version control.

3.  **Build and run Docker containers:**
    This command will build the Docker images and start all services defined in your `docker-compose.yml` (e.g., Django app, PostgreSQL, Redis, Celery).
    ```bash
    docker-compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode (in the background).

4.  **Run database migrations:**
    Execute Django migrations to set up your database schema.
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Create a superuser (optional, for admin access):**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to create your administrative user.

6.  **Access the application:**
    The application should now be accessible in your web browser at:
    `http://localhost:8000`

    * For the Celery Flower monitor (if configured in your `docker-compose.yml`): `http://localhost:5555`

### Running Celery and Celery Beat (if not auto-started by docker-compose)

If your `docker-compose.yml` doesn't automatically start Celery workers and Celery Beat, you might need specific service names. Assuming `celery_worker` and `celery_beat` as service names:

```bash
# To start Celery worker
docker-compose exec web celery -A core worker -l info

# To start Celery Beat
docker-compose exec web celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler