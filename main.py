
import os
# request フォームから送信した情報を扱うためのモジュール
# redirect  ページの移動
# url_for アドレス遷移
from flask import Flask, request, redirect, url_for , render_template,make_response
# ファイル名をチェックする関数
from werkzeug.utils import secure_filename
# 画像のダウンロード
from flask import send_from_directory
from models import Category,Product,Store,Order,OrderedProduct
from database import db_session
from sqlalchemy import or_
from order_doc import makePDF

import csv
from io import StringIO

UPLOAD_FOLDER = './uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#データベース初期化
dbname = 'database.db'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store')
def store():
    all_store = Store.query.order_by(Store.id.desc()).all()
    return render_template("store.html",stores=all_store)

@app.route('/store/add' ,methods=["GET", "POST"])
def store_add():
    if request.method == "GET":
        return render_template("store_add.html")
    else:
        db_session.add(Store(name = request.form["name"],address = request.form["address"],mail = request.form["mail"],phone = request.form["phone"]))
        db_session.commit()
        return ""
        
@app.route('/store/edit' ,methods=["GET", "POST"])
def store_edit():
    if request.method == "GET":
        store = db_session.query(Store).filter(Store.id==request.args.get("id")).first()
        return render_template("store_edit.html",store = store)
    else:
        print(request.form["id"])
        store = db_session.query(Store).filter(Store.id==request.form["id"]).first()
        store.name = request.form["name"]
        store.address = request.form["address"]
        store.mail = request.form["mail"]
        store.phone = request.form["phone"]
        db_session.commit()
        return ""

@app.route('/store/remove' ,methods=["GET"])
def store_remove():
    store = db_session.query(Store).filter(Store.id==request.args.get("id")).first()
    db_session.delete(store)
    db_session.commit()
    #print(category)
    return redirect("/store")

@app.route('/category')
def category():
    all_category = Category.query.order_by(Category.id.desc()).all()
    return render_template("category.html",categories=all_category)

@app.route('/category/add' ,methods=["GET", "POST"])
def category_add():
    if request.method == "GET":
        return render_template("category_add.html")
    else:
        db_session.add(Category(request.form["name"]))
        db_session.commit()
        return ""
        
@app.route('/category/edit' ,methods=["GET", "POST"])
def category_edit():
    if request.method == "GET":
        category = db_session.query(Category).filter(Category.id==request.args.get("id")).first()
        return render_template("category_edit.html",category = category)
    else:
        print(request.form["id"])
        category = db_session.query(Category).filter(Category.id==request.form["id"]).first()
        category.name = request.form["name"]
        db_session.commit()
        return ""

@app.route('/category/remove' ,methods=["GET"])
def category_remove():
    category = db_session.query(Category).filter(Category.id==request.args.get("id")).first()
    db_session.delete(category)
    db_session.commit()
    #print(category)
    return redirect("/category")

@app.route('/product')
def product():
    all_product = db_session.query(Product,Category,Store).join(Category,Product.category_id==Category.id).join(Store,Product.store_id==Store.id).order_by(Product.id.desc()).all()
    
    return render_template("product.html",products=all_product)

@app.route('/product/add' ,methods=["GET", "POST"])
def product_add():
    if request.method == "GET":
        all_category = db_session.query(Category).all()
        all_store = db_session.query(Store).all()
        print(all_category)
        return render_template("product_add.html",categories=all_category,stores=all_store)
    else:
        db_session.add(Product(name=request.form["name"],identifer=request.form["identifer"],category_id=request.form["category_id"],selling_price=request.form["selling_price"],purchase_price=request.form["purchase_price"],store_id=request.form["store_id"],stock=request.form["stock"]))
        db_session.commit()
        return ""
        
@app.route('/product/edit' ,methods=["GET", "POST"])
def product_edit():
    if request.method == "GET":
        product = db_session.query(Product).filter(Product.id==request.args.get("id")).first()
        all_category = db_session.query(Category).all()
        all_store = db_session.query(Store).all()
        return render_template("product_edit.html",product = product,categories=all_category,stores=all_store)
    else:
        print(request.form["id"])
        product = db_session.query(Product).filter(Product.id==request.form["id"]).first()
        product.name=request.form["name"]
        product.identifer=request.form["identifer"]
        product.selling_price=request.form["selling_price"]
        product.purchase_price=request.form["purchase_price"]
        product.store_id=request.form["store_id"]
        product.stock=request.form["stock"]
        product.category_id=request.form["category_id"]
        db_session.commit()
        return ""

@app.route('/product/remove' ,methods=["GET"])
def product_remove():
    product = db_session.query(Product).filter(Product.id==request.args.get("id")).first()
    db_session.delete(product)
    db_session.commit()
    #print(product)
    return redirect("/product")

@app.route('/order')
def order():
    all_order = db_session.query(Order,Store).join(Store,Order.store_id == Store.id).order_by(Order.id.desc()).all()
    return render_template("order.html",orders=all_order)

@app.route('/order/add',methods=["GET","POST"])
def order_add():
    if request.method == "GET":
        idlist = request.args.get("idstr").split(',')
        products = db_session.query(Product).filter(Product.id.in_(idlist)).all()
        all_store = db_session.query(Store).all()
        return render_template("order_add.html",products=products,stores=all_store)
    else:
        form = dict(request.form)
        total_amount = 0

        order = Order(store_id=int(form["store_id"][0]),total_amount=0)
        db_session.add(order)
        db_session.flush()
        order_id = order.id
        print(order_id)
        for key in form.keys():
            if(key.startswith("num")):
                id = int(key[3:])
                num = int(form[key][0])
                price = db_session.query(Product).filter(Product.id==id).first().purchase_price
                if(price==""):
                    price = 0
                total_amount+=price*num
                if(num == 0):
                    continue
                db_session.add(OrderedProduct(product_id=id,order_id=order_id,num=num))
        
        order.total_amount=total_amount

        db_session.commit()

        return redirect("/order")

@app.route('/order/pdf')
def order_pdf():
    order_id =  request.args.get("id")
    order = db_session.query(Order).filter(Order.id==order_id).first()
    ordered = db_session.query(OrderedProduct,Product).filter(OrderedProduct.order_id==order_id).join(Product,OrderedProduct.product_id==Product.id).all()
    #ordered = db_session.query(OrderedProduct).filter(OrderedProduct.order_id==order_id).all()
    total_amount = order.total_amount
    data =[]
    for o in ordered:
        name =o[1].name
        num = o[0].num
        price = o[1].purchase_price
        if type(price) is not int:
            price = 0
        data.append([name,num,price,num*price])
    print(data)
    output=makePDF(str(order_id),data,total_amount)
    pdf_out = output.getvalue()
    output.close()

    response = make_response(pdf_out)
    response.headers['Content-Disposition'] = "attachment; filename="+str(order_id)+".pdf"
    response.mimetype = 'application/pdf'
    return response

@app.route('/order/detail')
def order_detail():
    order_id =  request.args.get("id")
    ordered = db_session.query(OrderedProduct,Product).filter(OrderedProduct.order_id==order_id).join(Product,OrderedProduct.product_id==Product.id).all()
    order = db_session.query(Order,Store).filter(Order.id==order_id).join(Store,Order.store_id==Store.id).first()
    return render_template("order_detail.html",ordered=ordered,order=order)

@app.route('/setting')
def setting():
    return render_template("setting.html")

@app.route('/setting/csv', methods=['POST'])
def setting_csv():
    print(str(dict(request.files)))
    res = request.files['user_file']
    csv_str = res.stream.read().decode('cp932','replace')
    html=""
    category = []
    store = []
    product = []
    csvlist = list(csv.reader(StringIO(csv_str.strip())))
    for row in csvlist[1:]:
        product.append((row[0],row[1],row[4],row[6],row[10],row[11],row[12]))
        if(not row[12] in store):
            store.append(row[12])
        if(not row[1] in category):
            category.append(row[1])
    return render_template("setting_csv.html",store=store,category=category,product=product)

@app.route('/setting/csv/add', methods=['POST'])
def setting_csv_add():
    store = request.form.getlist('store[]')
    category = request.form.getlist('category[]')
    pname= request.form.getlist('pname[]')
    pcategory = request.form.getlist('pcategory[]')
    num = request.form.getlist('num[]')
    identifer = request.form.getlist('identifer[]')
    selling_price = request.form.getlist('selling_price[]')
    purchase_price = request.form.getlist('purchase_price[]')
    pstore = request.form.getlist('pstore[]')
    store_in = db_session.query(Store).filter(Store.name.in_(store)).all()
    store_name_in = list(map(lambda x:x.name, store_in))
    category_in = db_session.query(Category).filter(Category.name.in_(category)).all()
    category_name_in = list(map(lambda x:x.name, category_in))

    newstore = list(set(store)-set(store_name_in))
    newcategory = list(set(category)-set(category_name_in))

    store_dic = {}
    category_dic = {}

    for name in newstore:
        s = Store(name)
        db_session.add(s)
        store_dic[name]=s
    for name in newcategory:
        c = Category(name)
        db_session.add(c)
        category_dic[name]=c
    db_session.flush()

    for s in store_in:
        store_dic[s.name]=s
    for c in category_in:
        category_dic[c.name]=c
    print(category)
    print(pname)
    for i in range(len(pname)):
        pname= request.form.getlist('pname[]')
        pcategory = request.form.getlist('pcategory[]')
        num = request.form.getlist('num[]')
        identifer = request.form.getlist('identifer[]')
        selling_price = request.form.getlist('selling_price[]')
        purchase_price = request.form.getlist('purchase_price[]')
        pstore = request.form.getlist('pstore[]')
        p = Product(name=pname[i],category_id=category_dic[pcategory[i]].id,stock=num[i],identifer=identifer[i],selling_price=selling_price[i],purchase_price=purchase_price[i],store_id=store_dic[pstore[i]].id)
        db_session.add(p)
    db_session.commit()
    return redirect("/setting")
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
