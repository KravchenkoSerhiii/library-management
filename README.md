Project description
The project was created for library system management with the ability to track user borrowings

Features

- Ability to manage books in the library. 
Adding to the library, editing information about the book, author and price for the book. 
Only administrator can make changes to books, normal users can only read them.
- User management capability. 
Creation, modification of user data. The authentication method used is JWT token.
- Borrowings Management. 
It is possible to create borrowings for a specific user and 
also it is possible to return the book and cancel borrowings. 


Project Setup
Clone the repository:

git clone https://github.com/KravchenkoSerhiii/library-management.git
cd library_system

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate

On Windows use:

.venv\Scripts\activate
Install dependencies:

pip install -r requirements.txt

Apply migrations:

python manage.py migrate

Run the server:

python manage.py runserver

Environment Variables

This project uses environment variables for configuration. Copy the .env.sample file to .env and update the values as necessary.

cp .env-sample .env
