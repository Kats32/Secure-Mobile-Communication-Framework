from auth import register


username = input("Enter username: ")
password = input("Enter password: ")

if register(username, password):

    print("Registration successful")

else:

    print("Username already exists")