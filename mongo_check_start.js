var retries = 0,
    conn;

while(conn===undefined) {
    sleep(100);
    try
    {
        conn = new Mongo("localhost:7777");
    }
    catch(Error)
    {
        print("Waiting for Mongo.");
        retries++;

        if (retries > 100) {
            print("Mongo not available");
            quit(1);
        }
    }
}
DB = conn.getDB("test");
Result = DB.runCommand('buildInfo');
print(Result.version);
