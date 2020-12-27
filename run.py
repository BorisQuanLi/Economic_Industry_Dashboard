from api.src import create_app

app = create_app(testing= False, debug= True)
breakpoint()
app.run(debug= True)