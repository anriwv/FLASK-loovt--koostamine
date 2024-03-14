from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)

# andmebaasi loomine
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///andmebaas.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# andmebaasi kirjeldus
class Domeen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domeen = db.Column(db.String(20), nullable=False)    
    kas_on_r_domeen = db.Column(db.Boolean, default=0)
    r_nimi = db.Column(db.String(100))
    r_teine_nimi = db.Column(db.String(100))
    lipp_url = db.Column(db.String(300))


# andmebaas.db
with app.app_context():
    db.create_all()


# AVALEHT
@app.route('/')
def ava():
    koik_domeenid = Domeen.query.all()
    return render_template('esileht.html', koik_domeenid=koik_domeenid)


# DOMEENI LISAMINE
@app.route('/lisa', methods=['GET', 'POST'])
def lisa_domeen():
    if request.method == 'POST':
        domeen = request.form.get('domeen')
        r_nimi = request.form.get('r_nimi')
        r_teine_nimi = request.form.get('r_teine_nimi')
        lipp_url = request.form.get('lipp_url')

        if r_nimi == '' and lipp_url == '' and r_teine_nimi == '':
            kas_on_r_domeen = 0
        else:
            kas_on_r_domeen = 1

        # kui domeenil puudub '.' lisame.
        if domeen[0] != '.':
            domeen = '.' + domeen

        # Riigi nimi -> algustaht
        r_nimi = r_nimi.capitalize()
        r_teine_nimi = r_teine_nimi.capitalize()

        uus_d = Domeen(domeen=domeen, kas_on_r_domeen=kas_on_r_domeen, r_nimi=r_nimi, r_teine_nimi=r_teine_nimi, lipp_url=lipp_url)
        db.session.add(uus_d)
        db.session.commit()
        return redirect(url_for('lisa_domeen'))
    return render_template('lisa.html')


# OTSING 
@app.route('/<string:nimi>')
def tere(nimi):
    # Otsi domeenide hulgast riigi nime järgi
    otsing = Domeen.query.filter(Domeen.r_nimi.ilike(f'%{nimi}%')).all()
    return render_template('r_kohta.html', otsing=otsing, nimi=nimi)

# OTSING 2
@app.route('/otsi', methods=['GET', 'POST'])
def otsing():
    if request.method == 'POST':

        # Võtame tingimused 
        domeen = request.form.get('domeen')
        tuup = bool(int(request.form.get('o_tuup')))
        r_nimi = request.form.get('r_nimi')
        teine_nimi = request.form.get('teine_nimi')

        # Filtrime Domeenide andmeid 
        tulemused = Domeen.query.filter(
            Domeen.domeen.like(f'%{domeen}%'),
            Domeen.kas_on_r_domeen == tuup,
            Domeen.r_nimi.like(f'%{r_nimi}%'),
            Domeen.r_teine_nimi.like(f'%{teine_nimi}%'),
            ).all()

        return render_template('tulemused.html', tulemused=tulemused)
    return render_template('otsing.html')


# UUENDA
@app.route('/uuenda', methods=['GET'])
def uuenda__domeen():
    koik_domeenid = Domeen.query.all()
    return render_template('uuenda.html', koik_domeenid=koik_domeenid)


# uuenda domeeni andmed 
@app.route('/uuenda/<int:domeeni_id>', methods=['GET', 'POST']) 
def uuendamine(domeeni_id):
    domeen = Domeen.query.get_or_404(domeeni_id)
    if request.method == 'POST':
        uus_domeeni_nimi = request.form.get('uus_domeeni_nimi') 
        r_nimi = request.form.get('r_nimi') 
        r_teine_nimi = request.form.get('r_teine_nimi')
        lipp_url = request.form.get('lipp_url')


        if r_nimi == '' and lipp_url == '' and r_teine_nimi == '':
            domeen.kas_on_r_domeen = 0
        else:
            domeen.kas_on_r_domeen = 1

        if uus_domeeni_nimi[0] != '.':
            uus_domeeni_nimi = '.' + uus_domeeni_nimi

        r_nimi = r_nimi.capitalize()
        r_teine_nimi = r_teine_nimi.capitalize()


        # vahetame andmeid
        domeen.domeen = uus_domeeni_nimi
        domeen.r_nimi = r_nimi
        domeen.r_teine_nimi = r_teine_nimi
        domeen.lipp_url = lipp_url
        
        db.session.commit()
        return redirect(url_for('uuenda__domeen'))
    return render_template('uuendamine.html', domeen=domeen)

# KUSTUTAME DOMEENI
@app.route('/kustutamine/<int:domeeni_id>', methods=['POST'])
def kustutamine(domeeni_id):
    domeen = Domeen.query.get_or_404(domeeni_id)
    db.session.delete(domeen)
    db.session.commit()
    return redirect(url_for('ava'))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  

