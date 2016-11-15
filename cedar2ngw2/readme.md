Содержимое ответа сервера cedar:

{"objectID":"A4861590o32437o64177o64171o236899",
"number":15448,
"source":"Моб. приложение",
"sourceID":"",
"applicant":"",
"controller":"",
"region":{"key":"","value":""},
"district":"",
"forestery":"",
"precinct":"",
"territory":[{"quarter":"","vydel":""}],
"geo":[[[[135.85411265514787,46.87672990972753],[135.85411265514787,46.90373347188812],[135.91760967643302,46.90373347188812],[135.91760967643302,46.87672990972753],[135.85411265514787,46.87672990972753]]]],
"violations":[],
"description":"",
"protection":"",
"date":"2015-11-24T00:00:00.000Z",
"time":57,
"status":"Проверка проведена, подтвержден"}

Содержимое слоя в ngw

{
  "id": 23,
  "geom": "MULTIPOINT (4286914.6591160763055086 7573956.2924615610390902)",
  "fields": {
    "mtype": 2,
    "message": "\\u0420\\u0443\\u0431\\u043a\\u0430",
    "author": "\\u042a",
    "contact": "\\u041c",
    "status": 1,
    "stmessage": null,
    "mdate": {
      "year": 2015,
      "month": 9,
      "day": 12,
      "hour": 0,
      "minute": 0,
      "second": 0
    },
    "mtype_str": null,
    "phone": null
  },
  "extensions": {
    "description": null,
    "attachment": null
  }
}


получать изменения и обновлять только записи у которых sourceID равно id из слоя: http://176.9.38.120/fv/resource/64, 
поле status из cedar превращается в цифру по классификатору https://github.com/nextgis/nextgisweb_forest_violations/issues/29 и записывается в поле status. 
Содержимое поля status записывается в ngw в поле stmessage 


почему статус - то текст, то единица?
