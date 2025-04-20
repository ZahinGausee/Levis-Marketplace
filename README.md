# Levi's Marketplace E-commerce Website

Welcome to the **Levi's Marketplace**! This is a fully functional e-commerce website built with Django (backend) and React (frontend), offering users an easy and secure shopping experience. Users can browse products, select sizes, make payments, and track orders.

## Key Features

- **User Authentication:** Secure login and registration with email verification.
- **User Profile:** Manage personal details, view order history, and download invoices.
- **Product Browsing & Size Variants:** Easily browse products and select the right size.
- **Shopping Cart:** Add, update, or remove products before checkout.
- **Payment Integration (Razorpay):** Secure payments with Razorpay and invoice generation.
- **Order Management:** Track order status and access invoices from the user’s profile.
- **Admin Dashboard:** Manage products, users, orders, and download reports (7, 30 days, or all orders).

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript (React/Vanilla JS)
- **Backend:** Python with Django
- **Database:** SQL
- **Payment Gateway:** Razorpay

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/levi-marketplace-ecommerce.git
    ```
2. **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```
4. **Run the Django server:**
    ```bash
    python manage.py runserver
    ```
5. **For the frontend, install npm dependencies:**
    ```bash
    cd frontend
    npm install
    npm start
    ```

Now, open your browser to view the site!

## Contributing

1. Fork the repository.
2. Create a new branch.
3. Commit and push changes.
4. Open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
