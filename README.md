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

cp .env.sample .env
