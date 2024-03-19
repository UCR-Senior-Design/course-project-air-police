from flask import Flask, jsonify, request
import data as dc
app = Flask(__name__)

# Example route with a simple response
@app.route('/')
def index():
    return 'Welcome to the Flask backend!'
import aqi
# Example route returning JSON data
@app.route('/api/aqi', methods=['GET'])
def get_data():
    description = request.get_json()
    b64String = aqi.generateAqi(description)
    data = {
        'message': 'This is some data from the Flask backend',
        'b64': b64String
    }
    return jsonify(data)


# Example route with URL parameters
@app.route('/api/genMap', methods=['POST'])
def genMap():
    pm_type = request.get_json()
    dc.mapGeneration(pm_type)
    return jsonify({
        "message": "Map is generating please be patient"
    })

    # Here you could retrieve user data from a database based on the username
    # For this example, we'll just return a message with the username


# Example route handling POST requests
@app.route('/api/pushDB', methods=['POST'])
def create_post():
    # Assuming JSON data is sent in the request body
    # req_data = request.get_json()
    # title = req_data.get('title')
    # content = req_data.get('content')
    
    
    dc.checkOffline()
    dc.updateAllHealth()
    dc.pushFullDB()
    dc.updateAllDataFraction()



    # # Here you could save the post to a database
    # # For this example, we'll just return a message with the post data
    # return jsonify({
    #     'message': 'Post created successfully',
    #     'title': title,
    #     'content': content
    # })
    # return null




if __name__ == '__main__':
    app.run(debug=True)
