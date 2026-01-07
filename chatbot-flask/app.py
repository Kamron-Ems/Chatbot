from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Simple chatbot logic
def chatBot(user_input):
    user_input = user_input.lower()
    if 'hello' in user_input:
        return 'hello, how can I serve you'
    if 'name' in user_input:
        return 'My name is Rajnish'
    elif 'old' in user_input:
        return "i am 22 years old"
    elif 'capital' in user_input:
        return 'Delhi'
    elif 'available' in user_input:
        return 'yes 5 rooms are available'
    elif 'check-out' in user_input:
        return '11.00 AM'
    elif 'check-in' in user_input:
        return '12.00 PM'
    elif 'price' in user_input or 'cost' in user_input or 'rent' in user_input or 'charge' in user_input:
        return '₹1500 for 24 hours'
    elif 'tourist place' in user_input:
        return 'Yes, Taj Mahal , India Gate , Lotus Temple and many more'
    elif 'cab' in user_input:
        return 'Yes, ₹12/KM'
    elif 'food' in user_input:
        return 'Yes'
    elif 'wifi' in user_input:
        return 'yes'
    elif 'payment' in user_input:
        return 'we are accepting UPI or Cash'
    elif 'cancellation' in user_input:
        return 'Free cancellation'
    elif 'parking' in user_input:
        return 'Yes, we are providing parking in front of your room'
    elif 'bye' in user_input:
        return 'Goodbye! Have a great day!'
    elif 'thanks' in user_input or 'thank you' in user_input:
        return 'You are welcome!'
    else:
        return "Sorry, I don't have more information"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    bot_reply = chatBot(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
