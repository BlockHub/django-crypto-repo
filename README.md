# django-crypto-repo
Consumes exchange api endpoints (rest and websocket) and adds
the information in a DB.

Todo:
    
    binance:    api (finished)
                db  (finished)
                async library (finished)
                tests
    
    bitfinex:   api (finished)
                db  (finished)
                async library (not needed, has ws)
                tests
    
    bittrex:    api (finished)
                db  (finished)
                async library (finished)
                tests
                
    gdax:       api (finished)
                db  (finished)
                async library (not needed, has ws)
                tests
    
    kraken:     api 
                db 
                async library (not needed, harsh rate limit)
                tests
                
    kraken:     api (ws done, rest still needed)
                db 
                async library (not needed, has ws)
                tests
                
General approach:

    1. Create an api interface using an open source library, preferably using WS or aiohttp.
    2. Periodically add orderbooks to db, either continously or periodically add ticker data (depending on rest or WS)
    3. Create a class Bot with method run()
    4. Daemonize process using a management command
    5. Run daemons using supervisorctl.
    
Data model (example: gdax):

    table:  markets (contains contants on pairs)                      
            tickers (snapshot price snapshot data, FK to markets)
            orderbook (refresh times, FK to markets)
            orders (quantity, rate and more per order, FK to orderbook)