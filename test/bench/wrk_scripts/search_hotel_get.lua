-- GET /search-hotel

wrk.path = "http://localhost:5000/search-hotel?checkin=25-04-2018&checkout=26-04-2018&destination=e"
wrk.method = "GET"