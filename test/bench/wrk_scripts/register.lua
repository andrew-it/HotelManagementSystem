wrk.path = "/register"
wrk.method = "POST"
wrk.headers["Content-Type"] = "application/x-www-form-urlencoded"

local charset = {}  do -- [0-9a-zA-Z]
    for c = 48, 57  do table.insert(charset, string.char(c)) end
    for c = 65, 90  do table.insert(charset, string.char(c)) end
    for c = 97, 122 do table.insert(charset, string.char(c)) end
end

local function randomString(length)
    if not length or length <= 0 then return '' end
    math.randomseed(os.clock()^5)
    return randomString(length - 1) .. charset[math.random(1, #charset)]
end

request = function()
    password = randomString(10)
    body = "first_name=" .. randomString(10) ..
            "&last_name=" .. randomString(10) ..
            "&email=" .. randomString(10) .. "@inno.ru" ..
            "&password=" .. password ..
            "&password_confirmation=" .. password ..
            "&telephone=" randomString(10)
    return wrk.format(wrk.method, wrk.path, wrk.headers, body)
end