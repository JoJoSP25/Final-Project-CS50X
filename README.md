# CS50 Final Project - Subsend

#### Video Demo: <https://youtu.be/zSO1Hspcors>

## Description:

This is my final project for CS50, where I created a web application that allows users to share their opinions and vote for their favorite problem sets from Week 0 to Week 9. Users can also view other people’s comments in a structured 2x2 grid layout. Additionally, I implemented a Stock Finder feature that enables users to search for stocks by their symbols. Each stock has its own dedicated page displaying relevant details, including the company logo, name, symbol, a brief description, and key financial information such as Market Cap, Open, Close, and more.

## Technologies Used
- **Flask** (Python web framework)
- **SQLite** (CS50 SQL for database management)
- **HTML, CSS, JavaScript** (Frontend development)
- **Jinja** (Templating for dynamic pages)
- **Brandfetch API** (Fetching brand logos)
- **Yahoo Finance API** (A Python library to interact with the Yahoo Finance API, used to fetch real-time stock data.)
- **AJAX** (Asynchronous JavaScript and XML for dynamic updates)

## Features
- **User Authentication**: Users can log in and submit forms securely.
- **Database Storage**: Submitted data is stored in an SQLite database.
- **Validation**: Ensures that users input correct and complete data before submission.
- **API Integration**: Uses external APIs for added functionality (e.g., Brandfetch API for brand logos).
- **AJAX Implementation**: Enables asynchronous form submission for a smoother user experience without page reloads.


## Project Structure
```
/project-folder
│── app.py          # Main Flask application
│── templates/      # HTML templates for rendering pages
│── static/         # CSS (styles.css)
│── project.db        # SQLite database for storing form data
│── requirements.txt # Dependencies for the project
```

## How to Run
1. **Clone the repository:**
   ```bash
   git clone https://github.com/JoJoSP25/Final-Project-CS50X
   cd project
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up the database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
4. **Run the application:**
   ```bash
   flask run
   ```
5. Open `http://127.0.0.1:5000` in your browser.

## Challenges Faced
- **Form Validation:** Ensuring all input fields were properly validated before submission.
- **Database Integration:** Properly storing and retrieving user-submitted data.
- **Responsive Design:** Making sure forms work well on different screen sizes.
- **AJAX Implementation:** Handling asynchronous requests efficiently while updating the UI dynamically.

## Future Improvements
- Implementing **user roles** (e.g., admin, regular user).
- Adding an **export feature** to download submitted data as CSV.
- Enhancing UI/UX with better design and error handling.

## Conclusion
This project provided valuable hands-on experience with Flask, database management, and API integration. It serves as a foundation for more advanced web applications that require form submissions and data processing.

---

**Created by:** Joseph Ponce  
**GitHub Repository:** [https://github.com/JoJoSP25/Final-Project-CS50X](https://github.com/JoJoSP25/Final-Project-CS50X)
