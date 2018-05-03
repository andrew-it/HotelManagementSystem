-- GET /search-hotel

wrk.path = "http://localhost:5000/search-hotel?destination=e&checkin=02-05-2018&checkout=03-05-2018&is_bathroom=false&is_tv=false&is_wifi=false&is_bathhub=false&is_airconditioniring=false&sleeps=1&price_from=0&price_to=0&quantity=1"
wrk.method = "GET"