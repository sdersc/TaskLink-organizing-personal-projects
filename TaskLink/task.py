from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from TaskLink.auth import login_required
from TaskLink.database import get_database

bp = Blueprint('task', __name__)

@bp.route('/')
@login_required
def index():
    database = get_database()
    tasks = database.execute( 
        'SELECT *'
        ' FROM task'
        ' WHERE user_id = ?'
        ' ORDER BY task_id ASC',
        (g.user['user_id'],)
    ).fetchall()
    roots = get_roots()
    html_tree = ''
    for root in roots:
        partial_tree = ''
        partial_tree += '<ul>'
        partial_tree = parse_children(partial_tree, root)
        partial_tree += '</ul><br/><br/>'
        html_tree += partial_tree
    return render_template('task/index.html', tasks=tasks, roots=roots, html_tree=html_tree)

def get_roots():
    database = get_database()
    root = database.execute(
        'SELECT *'
        ' FROM task'
        ' WHERE user_id = ?'
        ' AND (task_id NOT IN ('
        '   SELECT finish_task_id'
        '   FROM link)'
        ' OR task_id IN ('
        '   SELECT finish_task_id'
        '   FROM link'
        '   WHERE start_task_id = 0))'
        ' ORDER BY task_id DESC',
        (g.user['user_id'],)
    ).fetchall()
    return root

def parse_children(html_tree, node):
    database = get_database()
    complet = database.execute(
        'SELECT completed'
        ' FROM task'
        ' WHERE task_id = ?',
        (node["task_id"], )
    ).fetchone()
    if complet["completed"] is not None:
        check = "&#10003;"
    else:
        check = ""
    html_tree += '<li><span class="tf-nc"><a href="/' + str(node["task_id"]) + '/view" >' + node["name"] + check + '</a></span>'
    children = database.execute(
        'SELECT *'
        ' FROM link'
        ' WHERE start_task_id = ?',
        (node["task_id"],)
    ).fetchall()
    if len(children) > 0:
        html_tree += '<ul>'
        for child in children:
            child_task = database.execute(
                'SELECT *'
                ' FROM task'
                ' WHERE task_id = ?',
                (child["finish_task_id"], )
            ).fetchone()
            html_tree = parse_children(html_tree, child_task)
        html_tree += '</ul>'
    html_tree += '</li>'
    return html_tree

@bp.route('/<int:task_id>/view', methods=('GET', 'POST'))
@login_required
def view(task_id):
    full = get_task(task_id)
    return render_template('task/view.html', full=full)

@bp.route('/<int:task_id>/check', methods=('GET', 'POST'))
@login_required
def check(task_id):
    database = get_database()
    completed = database.execute(
        'UPDATE task SET completed = 1'
        ' WHERE task_id = ?',
        (task_id, )
    )
    database.commit()
    return redirect(url_for('task.view', task_id=task_id))

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_name = request.form['start_name']
        error = None

        if not name:
            error = 'name is required.'

        if error is not None:
            flash(error)
        else:
            database = get_database()
            database.execute(
                'INSERT INTO task (name, description, user_id)'
                ' VALUES (?, ?, ?)',
                (name, description, g.user['user_id'])
            )
            database.commit()
            database.execute(
                'INSERT INTO link (start_task_id, finish_task_id)'
                ' SELECT task_id, (SELECT task_id FROM task ORDER BY task_id DESC LIMIT 1) FROM task'
                ' WHERE name LIKE ?',
                (start_name,)
            )
            database.commit()
            return redirect(url_for('task.index'))

    database = get_database()
    tasks = database.execute(
        'SELECT name, user_id'
        ' FROM task'
        ' WHERE user_id = ?'
        ' ORDER BY name ASC',
        (g.user['user_id'],)
    ).fetchall()

    return render_template('task/create.html', tasks=tasks)

def get_task(task_id, check_task=True):
    task = get_database().execute(
        'SELECT *'
        ' FROM task a JOIN user b ON a.user_id = b.user_id'
        ' WHERE a.task_id = ?',
        (task_id,)
    ).fetchone()
    
    if task is None:
        abort(404, "Task id {0} doesn't exist.".format(user_id))

    if check_task and task['user_id'] != g.user['user_id']:
        abort(403)

    return task

@bp.route('/<int:task_id>/update', methods=('GET', 'POST'))
@login_required
def update(task_id):
    database = get_database()
    task = get_task(task_id)
    tasks = database.execute(
        'SELECT name'
        ' FROM task'
        ' WHERE user_id = ?'
        ' EXCEPT'
        '  SELECT name'
        '  FROM task'
        '  WHERE task_id = ?'
        ' ORDER BY name ASC',
        (g.user['user_id'], task_id,)
    ).fetchall()
    link = database.execute(
        'SELECT finish_task_id'
        ' FROM link'
        ' WHERE finish_task_id = ?',
        (task_id,)
    ).fetchall()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        dependence = request.form['start_name']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            database = get_database()
            database.execute(
                'UPDATE task SET name = ?, description = ?'
                ' WHERE task_id = ?',
                (name, description, task_id)
            )
            if dependence == '0':
                database.execute(
                'UPDATE link SET start_task_id = 0'
                ' WHERE finish_task_id = ?',
                (task_id,)
                )
                database.commit()
            elif len(link) != 0:
                database.execute(
                    'UPDATE link SET start_task_id = ('
                    ' SELECT task_id'
                    ' FROM task'
                    ' WHERE name = ?)'
                    ' WHERE finish_task_id = ?',
                    (dependence, task_id,)
                )
                database.commit()
            else:
                database.execute(
                    'INSERT INTO link (start_task_id, finish_task_id)'
                    ' SELECT task_id, (SELECT task_id FROM task ORDER BY task_id DESC LIMIT 1) FROM task'
                    ' WHERE name LIKE ?',
                    (dependence,)
                )
                database.commit()
            return redirect(url_for('task.index'))

    return render_template('task/update.html', task=task, tasks=tasks)

@bp.route('/<int:task_id>/delete', methods=('POST',))
@login_required
def delete(task_id):
    get_task(task_id)
    database = get_database()
    database.execute('DELETE FROM link WHERE start_task_id = ? OR finish_task_id = ?', (task_id,task_id,))
    database.execute('DELETE FROM task WHERE task_id = ?', (task_id,))
    database.commit()
    return redirect(url_for('task.index'))