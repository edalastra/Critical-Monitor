from flask import Blueprint, request, jsonify, make_response, flash
from flask.helpers import url_for
from werkzeug.utils import redirect
from app import db
from flask_login import current_user
from app.models.Occurrence import Occurrence
from datetime import datetime

occurrences = Blueprint('occurrences', __name__)

@occurrences.route('/occurrences/<int:config_id>', methods=['GET'])
def occurrences_per_day(config_id):

    sql = """SELECT 
	COUNT(CASE WHEN oc.occurrence_type = 'lotação' THEN 1 END) as capacity,
	COUNT(CASE WHEN oc.occurrence_type = 'distânciamento' THEN 1 END) as distancing,
	DATE(oc.timestamp) as occurrence_date
	FROM occurrence oc
		JOIN config co ON co.id = oc.config_id
		JOIN "user" u ON u.id = co.user_id
	WHERE co.id = :c_id AND u.id = :u_id
	    GROUP BY occurrence_date
	    ORDER BY occurrence_date DESC;"""
    
    result = db.session.execute(sql,  {"u_id": current_user.id, "c_id": config_id})
    occurrences_per_date = []
    for r in result:
        occurrences_per_date.append({
            "capacity_qtd": r[0],
            "distancing_qtd": r[1],
            "occurrency_date": r[2]
        })
    return  make_response(jsonify({"dates":occurrences_per_date}), 200)

@occurrences.route('/occurrences/<int:occurrence_id>/delete', methods=['POST'])
def delete_occurrence(occurrence_id):
    occurrence = Occurrence.query.get_or_404(occurrence_id)
    db.session.delete(occurrence)
    db.session.commit()
    date = datetime.timestamp(occurrence.timestamp)
    # date = datetime(time)
    # date = datetime.timestamp(date)
    # print(time)
    flash('Ocorrência excluída com sucesso!', 'success')
    return redirect(url_for('monitor.list_occurrences', config_id=occurrence.config_id, occ_date=date))