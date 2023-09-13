# moxerver

A naive way to mock REST APIs based on rules defined in yaml files.

It can:

- extract values from the request
- store values linked to a request in the db
- return a certain response based on the values above
- use the values above in the response body 


## Running locally

Please install the requirements preferably in a virtual environment previously created with your preferred tool. 

E.g. if using `pip`, the requirements would be installed as following:

``` sh
pip install -r requirements.txt
```

Before the first run, you need to setup the db tables:

``` sh
flask init_db
```

Finally you can start the application in debug mode:

``` sh
flask --app app run --debug
```

Please note that you can also run it in a container by using the provided Containerfile.

## Sample app

The files under `flows/testapi` represent an example (albeit a silly one) of using the application.

### Flow configuration

The name of the application (which will be part of the url) is defined at the beginning of the file

``` yaml
api: testapi
```

Then, inside `flows` we can define routing rules. 

``` yaml
  - route: POST /operation
    vars:
      reference: request.ref
      meaning: request.meaning.life.everything
      prev_meaning: history.meaning
    rules:
      - filter:
          vars.meaning: 42
        result: ok.json
      - result: bad_meaning.json
    save:
      meaning: vars.meaning
```

- `route` define the method and url ending applicable
- `vars` section defines variables that can be referred later (in `filter`, in `save` or in response templates)
  - the source of the variables can be either the request, or the data stored in the DB
  - `reference` is a special variable based on which different requests can be known to refer to the same entity
- `rules` defines which result will be returned
  - the result corresponding to the first matching `filter` is returned
  - the result must correspond to a file with the same name under `templates/<app_name>`
- `save` defines what vars are stored to the database.

For instance, the above yaml file defines that when a `POST` request is made to `/mox/testapi/operation`, containing a `"ref"` field and a `"meaning"` object containing a `"life"` object containing a `"everything"` field. If that field is equal to 42, the `ok.json` will be returned. Otherwise, the `bad_meaning.json` will be returned. The `meaning.life.everything` field is saved in the DB, in association with the `ref` field.


### Response templates

The response templates need to be placed in the same directory as the yaml file. The response templates are jinja templates which can contain any of the variables defined above. For instance:

``` json
{
    "hello": "world",
    "everything": "is fine",
    "reference": "{{vars.reference}}",
    "meaning": "{{vars.meaning}}",
    "old_meaning": "{{vars.prev_meaning}}"
}
```

The `ok.json` file (returned as a result if the `meaning.life.everything` field is equal to 42) contains some static values, but also the following dynamic ones:
- `vars.reference`, which is the value of the field `ref` received in request,
- `meaning`, which is the value of the `meaning.life.everything` (in this case, always 42), and 
- `old_meaning`, which is the value of the `meaning.life.everything` received in request in the previous request made with the same `ref`

The `bad_meaning.json` is a static file:

``` json
{
    "error": "Meaning of life and everything incorrect"
}
```

Thus, when the request does not contain a `meaning.life.everything` field, or that field is not equal to 42, the response returned will be the content of the file above.

### See it in action

Let's send out first request.

``` 
> curl -H 'Content-Type: application/json' -d '{"ref": "001", "meaning": {"life": {"everything": 41}}}' http://0.0.0.0:5000/mox/testapi/operation
{
    "error": "Meaning of life and everything incorrect"
}
```

As expected, the meaning of life and everything is incorrect. Everybody knows that it should be 42. Let's try that again.

``` 
> curl -H 'Content-Type: application/json' -d '{"ref": "001", "meaning": {"life": {"everything": 42}}}' http://0.0.0.0:5000/mox/testapi/operation
{
    "hello": "world",
    "everything": "is fine",
    "reference": "001",
    "meaning": "42",
    "old_meaning": "41"
}


```


Super! We got what we expected. Everything is fine. We even got the last value we sent as "meaning". Neat!
But what if we don't send any meaning to start with?

``` 
> curl -H 'Content-Type: application/json' -d '{"ref": "001"}' http://0.0.0.0:5000/mox/testapi/operation
{
    "error": "Meaning of life and everything incorrect"
}
```

Again, as expected, we get the `bad_meaning.json` response.
