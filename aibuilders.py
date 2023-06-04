from flask import Blueprint,render_template, request, abort
from werkzeug.utils import secure_filename
from time import perf_counter
from base64 import b64encode
from shutil import rmtree
from dotenv import load_dotenv
import os
load_dotenv()

DEBUGMODEENABLED = (os.getenv('debugModeEnabled', 'False') == 'True')

mlDeployment = Blueprint('mlDeployment', __name__, template_folder='templates/ml', url_prefix="ai")

#####
# Functions
#####

def cleanup_images():
  print("Cleaning up old images")
  rmtree("./resources/ai_temporary/")
  os.mkdir("./resources/ai_temporary/")
  print("Done cleaning images.\n")

def prepare_learner():
  global learner
  if not learner:
    print("Starting model preparation.")
    startloadingtime = perf_counter()
    from fastbook import load_learner
    learner = load_learner('models/large-cat-model-v3.5.pkl')
    print(f"Took {round((perf_counter()-startloadingtime)*1000)}ms to load learner")
  else:
    print("Skipped model preparation, model was already loaded.")

learner = None
if not DEBUGMODEENABLED:
  cleanup_images()
  prepare_learner()
#Delay loading learner to make startup faster during development.

def get_topk(model_output, k=3, out_type="nested"):
  predictions = sorted(zip(model_output[2].tolist(), learner.dls.vocab), reverse=True)
  top_k = predictions[:k]
  if out_type == "nested":
    return top_k
  elif out_type == "list":
    return list(dict(top_k).values())
  else:
    raise Exception("Invalid Output Type")

def classify_cat(file):
  if not learner:
    print("Learner haven't been loaded yet, preparing it now...")
    prepare_learner()
  topItems = get_topk(learner.predict(file), out_type="nested", k=4)
  '''Will Return
  [(0.6899399757385254, 'standardissuecat'),
  (0.1083500012755394, 'SeniorCats'),
  (0.09582000225782394, 'Torbie')]'''

  predictionTable = ["<table border='1px'>", "<tr> <th>Prediction</th> <th>Confidence</th> </tr>"]
  alternativesTable = ["<table border='1px'>", "<tr> <th>Prediction</th> <th>Confidence</th> </tr>"]

  for item in topItems:
    confidence, prediction = item
    result = f"<tr> <td> <a href='https://reddit.com/r/{prediction}/top/?t=all' target='_blank'>{prediction}</a> </td> <td>{round(confidence, 4)}</td> </tr>"
    if float(confidence) > 0.6:
      predictionTable.append(result)
    else:
      alternativesTable.append(result)

  predictionTable.append("</table>")
  alternativesTable.append("</table>")
  
  stuffToReturn = []
  #print(len(predictionTable))
  #print(predictionTable)
  if len(predictionTable) > 3:
    print(f"Sent prediction: {topItems[0][1]}")
    stuffToReturn.append("\n".join(predictionTable))
  else:
    print(f"Not confident in any of the predictions, skipping. Prediction was:\n{topItems}")
    stuffToReturn.append(f"""
    <p style='color: salmon; background-color: #161f27; width:fit-content; text-align:center; padding: 0.5em; margin:auto; border-radius: 0.8em;'>
      We aren't quite confident on the prediction results of this image :( <br> Maybe try another one?
    </p>""")

  stuffToReturn.append("\n".join(alternativesTable))

  return stuffToReturn
  
@mlDeployment.route("/prepare_model")
def modelPreparationRoute():
  print("Model preparation requested")
  prepare_learner()

  return f"""<!DOCTYPE HTML>
  <html>
    <head><meta name='color-scheme' content='dark'></head>
    <body><p>Success.</p></body>
  </html>"""

@mlDeployment.route("/", methods=['GET','POST'])
def aibuilders_project():
  if request.method =="POST":
    print("Image Classification requested")
    #print("Post Method")
    #print(request.files)
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    #print(filename)

    if filename == '':
      #rejecting bad uploads
      print(f"\nRejected due to bad file")
      abort(415)

    uploaded_file.save(os.path.join('resources/ai_temporary', filename))
    try:
      predictionTable, alternativesTable = classify_cat(f"resources/ai_temporary/{filename}")
    except Exception as e:
      predictionTable = f"<p>We ran into an error:</p> <code>{e}</code>"

    uploaded_file.stream.seek(0)
    #print(uploaded_file.stream.read())
    image_base64 = b64encode(uploaded_file.stream.read())
    #print(image_base64)
    print("Successfully ent prediction.")
    return render_template("ml.html", predictionTable = predictionTable, alternativesTable = alternativesTable, image_base64 = image_base64.decode('utf-8'), modelStatus = "Fully Loaded.")
    
  
  else:
    print("Normal page load of cat classification page.")
    return render_template("ml.html", modelStatus = "Fully Loaded." if learner else "Not Loaded yet.", detailStatus = "open")
print("Sucessfully imported the AI deployment module")