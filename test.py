import rawes

from sqlalchemy import *
from sqlalchemy.pool import NullPool

from uogeneral.venues.post import from_factual
from factual import Factual

factual = Factual("wVqnOx6NohQUrMp9bo5VzF2QwfHxOjvwm3h0yp4b","bvxxlsRr2ouBB7gApzn31E3Aio5npZ4J72CwBySo")

engine = create_engine(
	"mysql+oursql://upout:server-2637483m9@upout.cpmdml6ulj9n.us-east-1.rds.amazonaws.com:3306/UpOut_LIVE",
	pool_recycle=3600,
	poolclass=NullPool
)

es = rawes.Elastic("ec2-23-21-10-146.compute-1.amazonaws.com:9200")

poster = from_factual(factual,"38f0b20f-85f9-4f8e-a15d-bb0ef8efe073",externalIds=[{"source" : "SOURCE","id" : "ID","url" : "url"}],data={"SOURCE" : [{"type":"TYPE","data":"DATA"}]})

conn=engine.connect()
print poster.post(conn,es)
conn.close()