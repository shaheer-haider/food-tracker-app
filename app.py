from typing import List, Any

from flask import Flask, render_template, url_for, g, request
import sqlite3
from datetime import datetime

app = Flask(__name__)


# database helpers
# function to create database connection and return it in variable
def connect_db():
    # sqlite(module).connect(function to connect database which take path of data base)
    sql = sqlite3.connect(r'D:\Flask with Full Flask Course\4. Food Tracker Flask App\Completed by me but change some better advance thing\database\food_log.db')
    sql.row_factory = sqlite3.Row
    return sql


# we will call this function when we are connecting to database and assign to variable
def get_db():
    # if g(database in flask has not attribute sqlite3) then create sqlite3 attribute in g and
    # assign its value to database connection
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    # if g has attribute sqlite_db which will automatic run after every request because of its decorator
    if hasattr(g, 'sqlite3'):
        g.sqlite_db.close()


# according to date total show karna hai
@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()

    date_warning = ''

    # adding date in database
    if request.method == 'POST':
        date = request.form['date']

        # yyyy/mm/dd
        day = date[-2:]
        month = date[5:7]
        year = date[:4]
        good_date = f"{day}-{month}-{year}"

        if len(good_date) != 10:
            date_warning = 'Cannot add this date. Please date properly'
        # insert dd-mm-yyyy format date into database
        elif len(good_date) == 10:
            try:
                db.execute('insert into date(dates) values(?)', [good_date])
                db.commit()
            except:
                date_warning = 'This date is already added, Please add unique date'

    # fetch date from database
    cur = db.execute('select dates from date')
    all_dates = cur.fetchall()

    # prettifying date that was fetch from database
    # making good date into real date format
    date_lis = []
    link_dates = []
    dno = 0
    dates_to_search = set()
    for ij in range(len(all_dates)):
        real_date_format = datetime.strptime(all_dates[dno]['dates'], '%d-%m-%Y')

        link_date = datetime.strftime(real_date_format, '%Y%m%d')
        link_dates.append(link_date)

        date_to_search = datetime.strftime(real_date_format, '%d-%m-%Y')
        dates_to_search.add(date_to_search)
        dno += 1

    date_n_id = dict()
    for date_searching in dates_to_search:
        cur = db.execute('select food_id, food_date from date_wise_food where food_date=?', [date_searching])
        id_today = cur.fetchall()

        search_ids = []
        for i in id_today:
            search_ids.append(i['food_id'])
        date_n_id.update({date_searching: search_ids})
    id_n_details = dict()
    for date_val, ids_of_food in date_n_id.items():
        total_protein = 0
        total_carbohydrates = 0
        total_fat = 0
        total_calories = 0
        for x in ids_of_food:
            cur = db.execute('select * from food where id=?', [int(x)])
            one_id_food_data = cur.fetchone()
            total_protein += one_id_food_data['protein']
            total_carbohydrates += one_id_food_data['carbohydrates']
            total_fat += one_id_food_data['fat']
            total_calories += one_id_food_data['calories']

        dated = datetime.strftime(datetime.strptime(date_val, '%d-%m-%Y'), "%B %d, %Y")
        date_link = datetime.strftime(datetime.strptime(date_val, '%d-%m-%Y'), "%Y%m%d")
        id_n_details.update({
            dated:
                [total_protein, total_carbohydrates, total_fat, total_calories, date_link]
        })

    return render_template('home.html', pretty_results=id_n_details, date_warning=date_warning)


@app.route('/view/<date>', methods=['GET', 'POST'])
@app.route('/view', defaults={'date': ""}, methods=['GET', 'POST'])
def view(date):
    db = get_db()
    if date == "":
        formatted_date = f'{datetime.strftime(datetime.now(), "%d-%m-%Y")}'
    else:
        # parsed date in dd-mm-yyyy format
        formatted_date = datetime.strptime(date, '%Y%m%d')
        formatted_date = datetime.strftime(formatted_date, '%d-%m-%Y')
    food_date = formatted_date
    try:
        db.execute('insert into date (dates) values(?)', [food_date])
        db.commit()
    except:
        pass
    if request.method == 'POST':
        # adding food according to food id and date
        # date 'str' 'ddmmyyyy'
        food_id = request.form['food_select']

        db.execute('insert into date_wise_food (food_id, food_date) values(?, ?)', [food_id, food_date])
        db.commit()

    # viewing food name and items into select options
    # viewing food name and items into select options
    # viewing food name and items into select options
    cur = db.execute('select id, name from food')
    food_id_name = cur.fetchall()

    # fetch food data according to date
    # fetch food data according to date
    # fetch food data according to date
    cur = db.execute('select food_id from date_wise_food where food_date = ?', [food_date])
    food_id_of_date = cur.fetchall()

    food_ids_list = []
    for item in food_id_of_date:
        food_ids_list.append(item['food_id'])
    all_food_details_list = []
    sum_protein = int()
    sum_carbohydrates = int()
    sum_fats = int()
    sum_calories = int()

    for one_id in food_ids_list:
        cur = db.execute('select * from food where id=?', [one_id])
        one_food_detail = cur.fetchone()
        one_food_detail = {'id': one_food_detail[0], 'name': one_food_detail[1],
                           'protein': one_food_detail[2], 'carbohydrates': one_food_detail[3],
                           'fats': one_food_detail[4], 'calories': one_food_detail[5]}
        all_food_details_list.append(one_food_detail)

        sum_protein += int(one_food_detail['protein'])
        sum_carbohydrates += int(one_food_detail['carbohydrates'])
        sum_fats += int(one_food_detail['fats'])
        sum_calories += int(one_food_detail['calories'])

    return render_template('view.html', food_id_name=food_id_name, food_details=all_food_details_list,
                           sum_protein=sum_protein, sum_carbohydrates=sum_carbohydrates, sum_fats=sum_fats,
                           sum_calories=sum_calories)


# THIS ROUTE HAS BEEN COMPLETED
@app.route('/the_food', methods=['GET', 'POST'])
def food():
    db = get_db()
    warning = ''
    # when someone fill the form
    if request.method == 'POST':
        food_name = request.form['food-name']
        food_name = str(food_name).capitalize()
        protein = request.form['protein']
        if protein == '':
            protein = 0
        carbohydrates = request.form['carbohydrates']
        if carbohydrates == '':
            carbohydrates = 0
        fats = request.form['fat']
        if fats == '':
            fats = 0

        calories = int(protein) * 4 + int(carbohydrates) * 4 + int(fats) * 9

        # cur = db.execute('select name from food')
        # name_res = cur.fetchall()

        try:
            # is ko try me is lie rakha hai q k name unique hona zaruri hai
            db.execute('insert into food(name, protein, carbohydrates, fat, calories) values(?, ?, ?, ?, ?)',
                       [food_name, protein, carbohydrates, fats, calories])
            db.commit()
        except:
            warning = 'Cannot add item of same name, Please change name and try to add again.'

    cur = db.execute('select * from food')
    results = cur.fetchall()

    return render_template('add_food.html', results=results, warning=warning)


# MAIN APP RUN COMMAND
if __name__ == '__main__':
    app.run()
