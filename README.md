# Scoring API

OTUS Python 2020-02 lession-3

## Purpose
Calculating score and interests, using User data.

## Usage
Start server:
```bash
python api.py
```

## Request examples
```
http://127.0.0.1:8080/method/
Body:
{
	"account": "horns&hoofs", 
	"login": "h&f", 
	"method": "online_score", 
	"token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
	"arguments": 
	{
		"phone": "79175002040", 
		"email": "stupnikov@otus.ru", 
		"first_name": "Стансилав", 
		"last_name": "Ступников", 
		"birthday": "01.01.1990", 
		"gender": 1
	}
}

Response:
{
    "response": {
        "score": 5.0
    },
    "code": 200
}
```

```
http://127.0.0.1:8080/method/
Body:
{
	"account": "horns&hoofs", 
	"login": "h&f", 
	"token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
	"arguments": 
	{
		"first_name": "Стансилав", 
		"last_name": "Ступников"
	}
}

Response:
{
    "error": "Validation error - require field \"method\"",
    "code": 422
}
```

## Testing
Start unittests:
```bash
python -m unittest -v
```

## Author
Frantsev Matvey

24.03.2020