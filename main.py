from quart import Quart
app = Quart(__name__)

@app.route("/")
def index():
  return "test_op"

if __name__ == "__main__":
  app.run()
