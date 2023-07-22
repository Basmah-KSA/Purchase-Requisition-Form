from flask import Flask, render_template, request
from datetime import datetime
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

REFERENCE_NUMBER_FILE = 'reference_number.txt'

def get_next_reference_number():
    with open(REFERENCE_NUMBER_FILE, 'r') as f:
        reference_number = int(f.read().strip())
    with open(REFERENCE_NUMBER_FILE, 'w') as f:
        f.write(str(reference_number + 1))
    return f'BPRF#{reference_number:06}'

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=2, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format='PNG')
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'

@app.route('/', methods=['GET', 'POST'])
def index():
    reference_number = get_next_reference_number()
    qr_code = None
    if request.method == 'POST':
        supplier_name = request.form['supplier_name']
        terms_of_payment = request.form['terms_of_payment']
        part_number = request.form['part_number']
        description = request.form.getlist('description')
        unit_type = request.form['unit_type']
        quantity = request.form['quantity']
        unit_price = request.form['unit_price']
        total = float(quantity) * float(unit_price)
        requested_by = request.form['requested_by']
        
        data = {
            'Reference Number': reference_number,
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Supplier Name': supplier_name,
            'Terms of Payment': terms_of_payment,
            'Part Number': part_number,
            'Description': description,
            'Unit Type': unit_type,
            'Quantity': quantity,
            'Unit Price': unit_price,
            'Total Amount': total,
            'Requested By': requested_by
        }
        
        qr_code = generate_qr_code(data)
        
        # Add code here to handle form submission, such as saving to a database or sending an email
        
    else:
        data = {
            'Reference Number': reference_number,
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Supplier Name': '',
            'Terms of Payment': '',
            'Part Number': '',
            'Description': '',
            'Unit Type': '',
            'Quantity': '',
            'Unit Price': '',
            'Total Amount': '',
            'Requested By': ''
        }
        
        qr_code = generate_qr_code(data)
        
    terms_of_payment_options = ['15 days', '1 Month', '2 Months', '3 Months']
    unit_type_options = ['Centimeter (cm)', 'Meter (m)', 'Kilometer (km)', 'Millimeter (mm)', 'Milligram (mg)', 'Gram (g)', 'Kilogram (kg)', 'Millilitre (ml)', 'Litre (l)', 'Kilolitre (kl)', 'Cubic Centimeter (cm3)']
    return render_template('index.html', date=datetime.now().strftime('%Y-%m-%d'), terms_of_payment_options=terms_of_payment_options, unit_type_options=unit_type_options, reference_number=reference_number, qr_code=qr_code)

if __name__ == '__main__':
    app.run()