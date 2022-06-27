if __name__ == '__main__':
    from uvicorn import run

    run(app='cookiecutter_fastAPI_v2.core.rule:app', host="0.0.0.0", port=8080, debug=True, reload=True)
