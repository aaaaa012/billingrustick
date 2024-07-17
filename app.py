from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from extensions import db
from forms import RegistrationForm, LoginForm
from models import User, Purchase, Sale
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Anusha/Documents/xammm/htdocs/fishtail_warehouse/Billing_System/instance/site.db?timeout=30'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'timeout': 10  # Timeout in seconds
    }
}
db.init_app(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        new_user = User(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
        finally:
            db.session.remove()
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_name = request.form['product_name']
        unit = request.form['unit']
        purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d')
        vendor = request.form['vendor']
        quantity = int(request.form['quantity'])
        per_unit_price = float(request.form['per_unit_price'])
        purchase_price = float(request.form['purchase_price'])
        payment_mode = request.form['payment_mode']
        user_id = session['user_id']

        try:
            new_purchase = Purchase(
                product_name=product_name,
                unit=unit,
                quantity=quantity,
                purchase_date=purchase_date,
                vendor=vendor,
                per_unit_price=per_unit_price,
                purchase_price=purchase_price,
                payment_mode=payment_mode,
                user_id=user_id
            )
            db.session.add(new_purchase)
            db.session.commit()
            flash('Purchase recorded successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('purchase.html')

@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_name = request.form['product_name']
        unit = request.form['unit']
        sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%d')
        quantity = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        total_price = float(request.form['total_price'])
        user_id = session['user_id']

        try:
            new_sale = Sale(
                product_name=product_name,
                unit=unit,
                sale_date=sale_date,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                user_id=user_id
            )
            db.session.add(new_sale)
            db.session.commit()
            flash('Sale recorded successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('sales.html')

@app.route('/stock')
def stock():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    purchases = Purchase.query.all()
    sales = Sale.query.all()
    stock = {}
    
    # Update to use 'unit' instead of 'sku'
    for purchase in purchases:
        key = (purchase.product_name, purchase.unit)
        if key not in stock:
            stock[key] = purchase.quantity
        else:
            stock[key] += purchase.quantity
    
    for sale in sales:
        key = (sale.product_name, sale.unit)
        if key in stock:
            stock[key] -= sale.quantity

    stock_items = [{'product_name': k[0], 'unit': k[1], 'quantity': v} for k, v in stock.items()]
    return render_template('stock.html', stock_items=stock_items)

def get_purchase_sales_details():
    purchases = Purchase.query.all()
    details_dict = {}

    for purchase in purchases:
        key = (purchase.product_name, purchase.unit)
        
        # Initialize details for this product if not already present
        if key not in details_dict:
            details_dict[key] = {
                'purchase': purchase,
                'sales': [],
                'days_diff': None
            }
        
        # Fetch sales related to the current purchase
        sales = Sale.query.filter_by(product_name=purchase.product_name, unit=purchase.unit).all()
        details_dict[key]['sales'] = sales
        
        # Calculate days difference if sales exist
        if sales:
            days_diff = (sales[0].sale_date - purchase.purchase_date).days
            details_dict[key]['days_diff'] = days_diff

    details = list(details_dict.values())

    # Debugging: Print details to verify data
    for d in details:
        print(f"Product: {d['purchase'].product_name}, Sales: {[str(sale) for sale in d['sales']]}, Days Diff: {d['days_diff']}")

    return details




@app.route('/api/chart-data')
def chart_data():
    # Get sales, purchases, and stock data from your database
    sales_data = get_sales_data()
    purchases_data = get_purchases_data()
    stock_data = get_stock_data()

    # Format data for the charts
    data = {
        'sales': {
            'labels': sales_data['labels'],
            'values': sales_data['values']
        },
        'purchases': {
            'labels': purchases_data['labels'],
            'values': purchases_data['values']
        },
        'topSelling': {
            'labels': stock_data['labels'],
            'values': stock_data['values']
        }
    }
    
    return jsonify(data)
def get_sales_data():
    # Query the sales data
    sales = Sale.query.all()
    labels = [sale.product_name for sale in sales]
    values = [sale.total_price for sale in sales]
    return {'labels': labels, 'values': values}

@app.route('/details')
def details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    details = get_purchase_sales_details()
    
    # Debugging: Print details to verify data
    for d in details:
        print(f"Product: {d['purchase'].product_name}, Sales: {d['sales']}, Days Diff: {d['days_diff']}")
    
    return render_template('details.html', details=details)


def get_purchases_data():
    # Query the purchases data
    purchases = Purchase.query.all()
    labels = [purchase.product_name for purchase in purchases]
    values = [purchase.purchase_price for purchase in purchases]
    return {'labels': labels, 'values': values}

def get_stock_data():
    # Query the stock data
    purchases = Purchase.query.all()
    stock = {}
    for purchase in purchases:
        if purchase.product_name in stock:
            stock[purchase.product_name] += purchase.quantity
        else:
            stock[purchase.product_name] = purchase.quantity

    labels = list(stock.keys())
    values = list(stock.values())
    return {'labels': labels, 'values': values}

@app.route('/api/summary')
def api_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    total_sales = db.session.query(db.func.sum(Sale.total_price)).scalar() or 0
    total_purchases = db.session.query(db.func.sum(Purchase.purchase_price)).scalar() or 0

    purchases = Purchase.query.all()
    sales = Sale.query.all()
    stock = {}

    for purchase in purchases:
        key = (purchase.product_name, purchase.unit)
        if key not in stock:
            stock[key] = purchase.quantity
        else:
            stock[key] += purchase.quantity

    for sale in sales:
        key = (sale.product_name, sale.unit)
        if key in stock:
            stock[key] -= sale.quantity

    current_stock = sum(quantity for quantity in stock.values() if quantity > 0)

    return jsonify({
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'current_stock': current_stock
    })

if __name__ == '__main__':
    app.run(debug=True)
