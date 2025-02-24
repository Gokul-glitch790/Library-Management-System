from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils import calculate_rent_fee
from models import db, Book, Member, Transaction

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db.init_app(app)

@app.route('/')
def index():
    books = Book.query.all()
    transactions = Transaction.query.filter_by(return_date=None).all()
    return render_template('index.html', books=books, transactions=transactions) 

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        quantity = request.form['quantity']
        new_book = Book(title=title, author=author, quantity=quantity)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/update_book/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_book.html', book=book)

@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        book = Book.query.get_or_404(book_id)
        member = Member.query.get_or_404(member_id)
        if book.quantity > 0 and member.debt <= 500:
            new_transaction = Transaction(book_id=book_id, member_id=member_id)
            book.quantity -= 1
            db.session.add(new_transaction)
            db.session.commit()
            return redirect(url_for('index'))
    books = Book.query.all()
    members = Member.query.all()
    return render_template('issue_book.html', books=books, members=members)

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        transaction_id = request.form['transaction_id']
        transaction = Transaction.query.get_or_404(transaction_id)
        transaction.return_date = datetime.utcnow()
        transaction.rent_fee = calculate_rent_fee(transaction.issue_date, transaction.return_date)
        book = Book.query.get_or_404(transaction.book_id)
        member = Member.query.get_or_404(transaction.member_id)
        book.quantity += 1
        member.debt += transaction.rent_fee
        db.session.commit()
        return redirect(url_for('index'))
    transactions = Transaction.query.filter_by(return_date=None).all()
    return render_template('return_book.html', transactions=transactions)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    books = Book.query.filter(Book.title.contains(query) | Book.author.contains(query)).all()
    return render_template('index.html', books=books)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        new_member = Member(name=name)
        db.session.add(new_member)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_member.html')

@app.route('/update_member/<int:id>', methods=['GET', 'POST'])
def update_member(id):
    member = Member.query.get_or_404(id)
    if request.method == 'POST':
        member.name = request.form['name']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_member.html', member=member)

@app.route('/delete_member/<int:id>', methods=['POST'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/members')
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)