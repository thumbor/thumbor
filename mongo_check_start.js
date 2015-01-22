var conn;
try
{
    conn = new Mongo("localhost:7777");
}
catch(Error)
{
    //print(Error);
}
while(conn===undefined)
{
    try
    {
        conn = new Mongo("localhost:7777");
    }
    catch(Error)
    {
        //print(Error);
    }
    sleep(100);
}
DB = conn.getDB("test");
Result = DB.runCommand('buildInfo');
print(Result.version);
