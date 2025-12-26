# BOT GPT – DRF Backend

## Setup
export GROQ_API_KEY=your_key
python manage.py migrate
python manage.py runserver

## APIs
POST /api/conversations/
POST /api/conversations/{id}/messages/
GET  /api/conversations/
DELETE /api/conversations/{id}
