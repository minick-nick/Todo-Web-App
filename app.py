from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = 'ssdfdsfsdfsdfsdfsf'
db = SQLAlchemy(app)


# models
class TodoItem(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  content = db.Column(db.String(length=30), nullable=False, unique=True)
  status = db.Column(db.Integer(), nullable=False, default=0)

  def update_status(self, status):
    self.status = status
    db.session.commit()

  def __repr__(self):
    return f'{self.id} -> {self.content} -> {self.status}'  

# forms
class AddTodoForm(FlaskForm):
  content = StringField(label="Content", validators=[DataRequired(), Length(min=5, max=20)])
  submit = SubmitField(label="Save")

  def validate_content(self, content_to_check):
    if TodoItem.query.filter_by(content=content_to_check.data).first():
      raise ValidationError('Content should be unique')

class DoneForm(FlaskForm):
  submit = SubmitField(label="Done")

class UndoneForm(FlaskForm):
  submit = SubmitField(label="Undone")

@app.route('/', methods=['POST', 'GET'])
def main():
  add_todo_form = AddTodoForm()
  done_form = DoneForm()
  undone_form = UndoneForm()

  todo_items = TodoItem.query.filter_by(status=0)  
  done_todo_items = TodoItem.query.filter_by(status=1)

  if  request.method == 'POST':
    if request.form.get('submit') == 'Save':
      if add_todo_form.validate_on_submit():
        todo = TodoItem(content=add_todo_form.content.data)

        db.session.add(todo)
        db.session.commit()

      if add_todo_form.errors != {}:
        for error in add_todo_form.errors.values():
          flash(f'{error}', category='warning')


    if done_form.validate_on_submit():
      done_todo = request.form.get('done-todo')

      d_todo_object = TodoItem.query.filter_by(id=done_todo).first()
      
      if d_todo_object:
        d_todo_object.update_status(1)


    if undone_form.validate_on_submit():
      undone_todo = request.form.get('undone-todo')

      ud_todo_object = TodoItem.query.filter_by(id=undone_todo).first()
      
      if ud_todo_object:
        ud_todo_object.update_status(0)

    return redirect(url_for('main'))

  if request.method == 'GET':
    return render_template('main.html',
      form=add_todo_form,
      todo_items=todo_items,
      done_todo_items=done_todo_items,
      done_form=done_form,
      undone_form=undone_form)

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
  todo = TodoItem.query.get_or_404(id)

  db.session.delete(todo)
  db.session.commit()

  return redirect(url_for('main'))

if __name__ == '__main__':
  app.run()
  
