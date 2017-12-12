from flask import Flask, request, jsonify
import predict
app = Flask(__name__)

predict.predict_init()

@app.route('/ping')
def ping():
    print('pong')
    return ("", 200)

@app.route('/invocations', methods=["POST"])
def invoke():
    print('invoke!!!')
    data = request.get_json(force=True)
    # ret = predict.predict_and_evaluate("d6733ab274d98d53d6359cc14c579.jpg")
    print(data['url'])
    ret = predict.predict(data['url'])
    print(ret)
    return jsonify(ret)
    # return jsonify(predict.predict_and_evaluate(data['url']))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
