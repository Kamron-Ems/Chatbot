


def chatBot(user_input):
    user_input=user_input.lower()
    print(user_input)
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
    elif 'charge' in user_input:
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
    else:
        return "Sorry, I don't have more information"
print("Welcome to the Rajnish Hotel")
print("Type 'Bye' to exit." )
while True:
    user_input=input("Ask Questions: ")
    response=chatBot(user_input)
    print("ChatBot:" , response)
    if 'bye' in user_input.lower():
        break

