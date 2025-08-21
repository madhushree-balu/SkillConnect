from flask import (
    Flask
)

app = Flask(__name__)
app.secret_key = "My Secret Key"



@app.get("/")
def index():
    return {
        "success": True,
        
    }



if __name__ == "__main__":
    app.run(debug=True)