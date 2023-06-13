from time import perf_counter
startTime = perf_counter()
print("Hi!")
import os, waitress, datetime, pytz, dotenv
dotenv.load_dotenv()
print("Imported various stuff")
from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.exceptions import HTTPException
print("Imported flask")
print("Loading AI Module...")
from aibuilders import mlDeployment

DEBUGMODEENABLED = (os.getenv('debugModeEnabled', 'False') == 'True')

print(f"Sucessfully imported stuff in {round((perf_counter() - startTime)*1000, 2)}ms")

#start of flask app
app = Flask(__name__)

app.register_blueprint(mlDeployment, url_prefix="/ai")
#other modules goes here

@app.route('/')
def home():
  return redirect('/ai')

#other routes/pages for your website goes here

#customized error pages
@app.errorhandler(HTTPException)
def handle_exception(e):
  return render_template('/err/generic.html', title=e.name, heading=f"{e.code} - {e.name}", message = f"{e.description}</p><p>Also, ")

#running the thing
if __name__ == '__main__':
  startinguptime = round((perf_counter() - startTime)*1000, 2)
  currenttime = datetime.datetime.now(pytz.timezone('Asia/Bangkok')).strftime('%d/%m/%Y %H:%M:%S')
  print(f'Server started in {startinguptime}ms at \n{currenttime} GMT+7\n')

  if DEBUGMODEENABLED:
    print(f"Debugging mode is enabled!")
    app.run(host="0.0.0.0", debug=True)
  else:
    waitress.serve(app, host="0.0.0.0")