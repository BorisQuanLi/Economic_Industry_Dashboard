from api.src import create_app

app = create_app(testing= False, debug= True)
app.run(debug= True)