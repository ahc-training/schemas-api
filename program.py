import uvicorn, ssl


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8443, reload=True, ssl_keyfile='./certs/key.pem', ssl_certfile='./certs/cert.pem')


if __name__ == "__main__":
    main()